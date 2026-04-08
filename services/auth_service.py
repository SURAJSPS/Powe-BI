"""Authentication and company onboarding."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from core.errors import DuplicateError
from core.security import hash_password, verify_password
from db.mongo import get_db
from services.validators import MSG, email as valid_email, optional_text, required_text

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def register_company(
    company_name: str,
    admin_name: str,
    admin_email: str,
    password: str,
    *,
    legal_name: str | None = None,
    gstin: str | None = None,
    address: str | None = None,
) -> tuple[str, str]:
    db = get_db()
    company_name = required_text(company_name, message=MSG["company_name_required"])
    admin_name = required_text(admin_name, message=MSG["admin_name_required"])
    email = valid_email(admin_email, required=True)
    password = required_text(password, message=MSG["password_required"])
    if db.users.find_one({"email": email}):
        logger.info("register_company: duplicate email %s", email)
        raise DuplicateError("An account with this email already exists.")
    comp = {
        "name": company_name,
        "legal_name": optional_text(legal_name) or company_name,
        "gstin": optional_text(gstin),
        "address": optional_text(address),
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }
    cr = db.companies.insert_one(comp)
    cid = cr.inserted_id
    user = {
        "email": email,
        "password_hash": hash_password(password),
        "full_name": admin_name,
        "company_id": cid,
        "role": "company_admin",
        "active": True,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }
    ur = db.users.insert_one(user)
    return str(cid), str(ur.inserted_id)


def login(email: str, password: str) -> dict[str, Any] | None:
    db = get_db()
    email = email.strip().lower()
    u = db.users.find_one({"email": email, "active": True})
    if not u:
        return None
    if not verify_password(password, u["password_hash"]):
        return None
    comp = db.companies.find_one({"_id": u["company_id"]})
    return {
        "user_id": str(u["_id"]),
        "email": u["email"],
        "full_name": u.get("full_name", ""),
        "role": u.get("role", "viewer"),
        "company_id": str(u["company_id"]),
        "company_name": comp["name"] if comp else "",
    }


def get_user_by_id(user_id: str) -> dict[str, Any] | None:
    db = get_db()
    try:
        oid = ObjectId(user_id)
    except Exception:
        return None
    u = db.users.find_one({"_id": oid, "active": True})
    if not u:
        return None
    comp = db.companies.find_one({"_id": u["company_id"]})
    return {
        "user_id": str(u["_id"]),
        "email": u["email"],
        "full_name": u.get("full_name", ""),
        "role": u.get("role", "viewer"),
        "company_id": str(u["company_id"]),
        "company_name": comp["name"] if comp else "",
    }


def list_users(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    cid = ObjectId(company_id)
    out = []
    for u in db.users.find({"company_id": cid}).sort("email", 1):
        out.append(
            {
                "user_id": str(u["_id"]),
                "email": u["email"],
                "full_name": u.get("full_name", ""),
                "role": u.get("role", "viewer"),
                "active": u.get("active", True),
            }
        )
    return out


def add_user(
    company_id: str,
    email: str,
    password: str,
    full_name: str,
    role: str,
) -> str:
    db = get_db()
    email = valid_email(email, required=True)
    password = required_text(password, message=MSG["password_required"])
    full_name = required_text(full_name, message=MSG["full_name_required"])
    if db.users.find_one({"email": email}):
        logger.info("add_user: duplicate email %s", email)
        raise DuplicateError("Email already registered.")
    doc = {
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name,
        "company_id": ObjectId(company_id),
        "role": role,
        "active": True,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }
    return str(db.users.insert_one(doc).inserted_id)


def update_user_role(company_id: str, user_id: str, role: str) -> None:
    db = get_db()
    db.users.update_one(
        {"_id": ObjectId(user_id), "company_id": ObjectId(company_id)},
        {"$set": {"role": role, "updated_at": _utcnow()}},
    )


_COMPANY_FIELD_KEYS = frozenset(
    {
        "name",
        "legal_name",
        "gstin",
        "address",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "pincode",
        "country",
        "bank_account_holder",
        "bank_name",
        "bank_branch",
        "bank_account_no",
        "bank_ifsc",
        "backdate_max_days",
        "backdate_bypass_admin",
        "allow_future_dated_entries",
    }
)
# Fields that may be cleared (unset in Mongo) when passed as None
_COMPANY_NULLABLE = frozenset(
    {
        "gstin",
        "address",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "pincode",
        "country",
        "bank_account_holder",
        "bank_name",
        "bank_branch",
        "bank_account_no",
        "bank_ifsc",
        "backdate_max_days",
    }
)


def get_company(company_id: str) -> dict[str, Any] | None:
    db = get_db()
    c = db.companies.find_one({"_id": ObjectId(company_id)})
    if not c:
        return None
    line1 = c.get("address_line1")
    if not line1 and isinstance(c.get("address"), str) and (c.get("address") or "").strip():
        line1 = (c.get("address") or "").strip()
    return {
        "company_id": str(c["_id"]),
        "name": c.get("name", ""),
        "legal_name": c.get("legal_name", ""),
        "gstin": c.get("gstin"),
        "address": c.get("address"),
        "address_line1": line1,
        "address_line2": c.get("address_line2"),
        "city": c.get("city"),
        "state": c.get("state"),
        "pincode": c.get("pincode"),
        "country": c.get("country") or "India",
        "bank_account_holder": c.get("bank_account_holder"),
        "bank_name": c.get("bank_name"),
        "bank_branch": c.get("bank_branch"),
        "bank_account_no": c.get("bank_account_no"),
        "bank_ifsc": c.get("bank_ifsc"),
        "backdate_max_days": c.get("backdate_max_days"),
        "backdate_bypass_admin": c.get("backdate_bypass_admin", True),
        "allow_future_dated_entries": c.get("allow_future_dated_entries", False),
    }


def update_company(company_id: str, **fields: Any) -> None:
    db = get_db()
    to_set: dict[str, Any] = {}
    to_unset: list[str] = []
    for k, v in fields.items():
        if k not in _COMPANY_FIELD_KEYS:
            continue
        if v is None and k in _COMPANY_NULLABLE:
            to_unset.append(k)
        elif v is not None:
            to_set[k] = v
    if not to_set and not to_unset:
        return
    oid = ObjectId(company_id)
    now = _utcnow()
    op: dict[str, Any] = {}
    if to_set:
        to_set["updated_at"] = now
        op["$set"] = to_set
    if to_unset:
        op["$unset"] = {k: "" for k in to_unset}
        if "$set" not in op:
            op["$set"] = {"updated_at": now}
        else:
            op["$set"]["updated_at"] = now
    db.companies.update_one({"_id": oid}, op)
