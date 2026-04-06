"""Authentication and company onboarding."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from core.security import hash_password, verify_password
from db.mongo import get_db


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
    email = admin_email.strip().lower()
    if db.users.find_one({"email": email}):
        raise ValueError("An account with this email already exists.")
    comp = {
        "name": company_name.strip(),
        "legal_name": (legal_name or company_name).strip(),
        "gstin": gstin.strip() if gstin else None,
        "address": address.strip() if address else None,
        "created_at": _utcnow(),
        "updated_at": _utcnow(),
    }
    cr = db.companies.insert_one(comp)
    cid = cr.inserted_id
    user = {
        "email": email,
        "password_hash": hash_password(password),
        "full_name": admin_name.strip(),
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
    email = email.strip().lower()
    if db.users.find_one({"email": email}):
        raise ValueError("Email already registered.")
    doc = {
        "email": email,
        "password_hash": hash_password(password),
        "full_name": full_name.strip(),
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


def get_company(company_id: str) -> dict[str, Any] | None:
    db = get_db()
    c = db.companies.find_one({"_id": ObjectId(company_id)})
    if not c:
        return None
    return {
        "company_id": str(c["_id"]),
        "name": c.get("name", ""),
        "legal_name": c.get("legal_name", ""),
        "gstin": c.get("gstin"),
        "address": c.get("address"),
    }


def update_company(company_id: str, **fields: Any) -> None:
    db = get_db()
    allowed = {k: v for k, v in fields.items() if k in ("name", "legal_name", "gstin", "address") and v is not None}
    if not allowed:
        return
    allowed["updated_at"] = _utcnow()
    db.companies.update_one({"_id": ObjectId(company_id)}, {"$set": allowed})
