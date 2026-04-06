"""Attendance and expenses."""
from __future__ import annotations

from datetime import date
from typing import Any

from db.mongo import get_db

from ._util import _cid, _utcnow


def attendance_list(company_id: str, limit: int = 500) -> list[dict[str, Any]]:
    db = get_db()
    cur = db.attendance.find({"company_id": _cid(company_id)}).sort("work_date", -1).limit(limit)
    return list(cur)


def attendance_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    if isinstance(d.get("work_date"), date):
        d["work_date"] = d["work_date"].isoformat()
    db.attendance.insert_one(d)


def expenses_list(company_id: str, limit: int = 500) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.expenses.find({"company_id": _cid(company_id)}).sort("expense_date", -1).limit(limit))


def expense_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    if isinstance(d.get("expense_date"), date):
        d["expense_date"] = d["expense_date"].isoformat()
    db.expenses.insert_one(d)
