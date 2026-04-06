"""Clients, employees, client dashboard summary."""
from __future__ import annotations

from typing import Any

from bson import ObjectId

from core.errors import NotFoundError, ValidationError
from db.mongo import get_db

from ._util import _cid, _utcnow
from .field import projects_list


def clients_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.clients.find({"company_id": _cid(company_id)}).sort("name", 1))


def client_get(company_id: str, client_id: str) -> dict[str, Any] | None:
    db = get_db()
    return db.clients.find_one({"_id": ObjectId(client_id), "company_id": _cid(company_id)})


def _client_code_taken(
    db,
    company_id: str,
    code: str,
    *,
    exclude_id: ObjectId | None = None,
) -> bool:
    c = (code or "").strip()
    if not c:
        return False
    q: dict[str, Any] = {"company_id": _cid(company_id), "client_code": c}
    if exclude_id is not None:
        q["_id"] = {"$ne": exclude_id}
    return db.clients.count_documents(q) > 0


def client_add(company_id: str, name: str, **extra: Any) -> str:
    db = get_db()
    code = (extra.get("client_code") or "").strip() or None
    if code and _client_code_taken(db, company_id, code):
        raise ValidationError(f"Client code «{code}» is already in use.")

    def _s(k: str) -> str | None:
        v = extra.get(k)
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    doc = {
        "company_id": _cid(company_id),
        "name": name.strip(),
        "legal_name": _s("legal_name"),
        "client_code": code,
        "gstin": _s("gstin"),
        "pan": _s("pan"),
        "contact_person": _s("contact_person"),
        "phone": _s("phone"),
        "alternate_phone": _s("alternate_phone"),
        "email": _s("email"),
        "billing_email": _s("billing_email"),
        "website": _s("website"),
        "address": _s("address"),
        "city": _s("city"),
        "state": _s("state"),
        "pincode": _s("pincode"),
        "country": _s("country") or "India",
        "payment_terms_days": extra.get("payment_terms_days"),
        "notes": _s("notes"),
        "created_at": _utcnow(),
    }
    if doc["payment_terms_days"] is not None:
        try:
            doc["payment_terms_days"] = int(doc["payment_terms_days"])
        except (TypeError, ValueError):
            doc["payment_terms_days"] = None
    return str(db.clients.insert_one(doc).inserted_id)


def client_update(company_id: str, client_id: str, **fields: Any) -> None:
    db = get_db()
    oid = ObjectId(client_id)
    existing = db.clients.find_one({"_id": oid, "company_id": _cid(company_id)})
    if not existing:
        raise NotFoundError("Client", client_id)

    code = fields.get("client_code")
    if code is not None:
        c = str(code).strip() or None
        if c and _client_code_taken(db, company_id, c, exclude_id=oid):
            raise ValidationError(f"Client code «{c}» is already in use.")
        fields["client_code"] = c

    allowed = {
        "name",
        "legal_name",
        "client_code",
        "gstin",
        "pan",
        "contact_person",
        "phone",
        "alternate_phone",
        "email",
        "billing_email",
        "website",
        "address",
        "city",
        "state",
        "pincode",
        "country",
        "payment_terms_days",
        "notes",
    }
    update: dict[str, Any] = {"updated_at": _utcnow()}
    for k in allowed:
        if k not in fields:
            continue
        v = fields[k]
        if k == "payment_terms_days":
            if v is None or v == "":
                update[k] = None
            else:
                try:
                    update[k] = int(v)
                except (TypeError, ValueError):
                    update[k] = None
            continue
        if v is None:
            update[k] = None
        elif isinstance(v, str):
            s = v.strip()
            update[k] = s or None
        else:
            update[k] = v

    if "name" in update and not (update.get("name") or "").strip():
        raise ValidationError("Display name is required.")

    if "name" in update:
        update["name"] = update["name"].strip()

    db.clients.update_one({"_id": oid, "company_id": _cid(company_id)}, {"$set": update})


def employees_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.employees.find({"company_id": _cid(company_id)}).sort("employee_code", 1))


def employee_add(
    company_id: str,
    employee_code: str,
    full_name: str,
    *,
    department: str | None = None,
    role_title: str | None = None,
    phone: str | None = None,
    email: str | None = None,
) -> str:
    db = get_db()
    doc = {
        "company_id": _cid(company_id),
        "employee_code": employee_code.strip(),
        "full_name": full_name.strip(),
        "department": department,
        "role_title": role_title,
        "phone": phone,
        "email": email,
        "created_at": _utcnow(),
    }
    return str(db.employees.insert_one(doc).inserted_id)


def clients_summary(company_id: str) -> dict[str, Any]:
    """Lightweight stats for the Clients dashboard strip."""
    rows = clients_list(company_id)
    projects = projects_list(company_id)
    names = {(r.get("name") or "").strip().lower() for r in rows if (r.get("name") or "").strip()}
    linked = 0
    for p in projects:
        cn = (p.get("client_name") or "").strip().lower()
        if cn and cn in names:
            linked += 1
    with_gst = sum(1 for r in rows if (r.get("gstin") or "").strip())
    return {
        "total": len(rows),
        "with_gstin": with_gst,
        "projects_linked": linked,
        "projects_total": len(projects),
    }
