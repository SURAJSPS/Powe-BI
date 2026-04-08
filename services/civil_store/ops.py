"""Attendance and expenses."""
from __future__ import annotations

from datetime import date
from typing import Any

from db.mongo import get_db
from services.validators import MSG, non_negative, optional_text, required_text

from ._util import _cid, _utcnow


def attendance_list(company_id: str, limit: int = 500) -> list[dict[str, Any]]:
    db = get_db()
    cur = db.attendance.find({"company_id": _cid(company_id)}).sort("work_date", -1).limit(limit)
    return list(cur)


def attendance_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d["worker_id"] = required_text(d.get("worker_id"), message=MSG["worker_required"])
    d["project_code"] = required_text(d.get("project_code"), message=MSG["project_required"])
    d["site_code"] = required_text(d.get("site_code"), message="Site is required.")
    d["normal_hrs"] = non_negative(d.get("normal_hrs") or 0.0, field_message="Normal hours cannot be negative.")
    d["ot_hrs"] = non_negative(d.get("ot_hrs") or 0.0, field_message="OT hours cannot be negative.")
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    if isinstance(d.get("work_date"), date):
        d["work_date"] = d["work_date"].isoformat()
    db.attendance.insert_one(d)


def expenses_list(company_id: str, limit: int = 500) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.expenses.find({"company_id": _cid(company_id)}).sort("expense_date", -1).limit(limit))


def expense_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d["project_code"] = required_text(d.get("project_code"), message=MSG["project_required"])
    d["category"] = required_text(d.get("category"), message="Category is required.")
    d["amount"] = non_negative(d.get("amount") or 0.0)
    d["gst_amount"] = non_negative(d.get("gst_amount") or 0.0, field_message="GST cannot be negative.")
    d["vendor"] = optional_text(d.get("vendor"))
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    if isinstance(d.get("expense_date"), date):
        d["expense_date"] = d["expense_date"].isoformat()
    db.expenses.insert_one(d)
