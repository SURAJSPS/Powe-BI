"""MongoDB CRUD for civil operations (scoped by company_id)."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd
from bson import ObjectId

from db.mongo import get_db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _cid(company_id: str) -> ObjectId:
    return ObjectId(company_id)


# --- Clients ---
def clients_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.clients.find({"company_id": _cid(company_id)}).sort("name", 1))


def client_add(company_id: str, name: str, **extra: Any) -> str:
    db = get_db()
    doc = {
        "company_id": _cid(company_id),
        "name": name.strip(),
        "gstin": extra.get("gstin"),
        "contact_person": extra.get("contact_person"),
        "phone": extra.get("phone"),
        "email": extra.get("email"),
        "address": extra.get("address"),
        "created_at": _utcnow(),
    }
    return str(db.clients.insert_one(doc).inserted_id)


# --- Employees (office / staff registry; optional login later) ---
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


# --- OT rules ---
def ot_rules_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.ot_rules.find({"company_id": _cid(company_id)}).sort("rule_id", 1))


def ot_rule_add(company_id: str, rule_id: str, rule_name: str, multiplier: float, max_ot: float | None, notes: str) -> None:
    db = get_db()
    db.ot_rules.update_one(
        {"company_id": _cid(company_id), "rule_id": rule_id},
        {
            "$set": {
                "rule_name": rule_name,
                "multiplier": float(multiplier),
                "max_ot_hrs_per_day": max_ot,
                "notes": notes,
                "updated_at": _utcnow(),
            },
            "$setOnInsert": {"company_id": _cid(company_id), "rule_id": rule_id, "created_at": _utcnow()},
        },
        upsert=True,
    )


# --- Projects ---
def projects_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.projects.find({"company_id": _cid(company_id)}).sort("project_code", 1))


def project_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "updated_at": _utcnow()}
    d.setdefault("created_at", _utcnow())
    db.projects.update_one(
        {"company_id": _cid(company_id), "project_code": d["project_code"]},
        {"$set": d},
        upsert=True,
    )


# --- Sites ---
def sites_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.sites.find({"company_id": _cid(company_id)}).sort("site_code", 1))


def site_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "updated_at": _utcnow()}
    d.setdefault("created_at", _utcnow())
    db.sites.update_one(
        {"company_id": _cid(company_id), "site_code": d["site_code"]},
        {"$set": d},
        upsert=True,
    )


# --- Workers ---
def workers_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.workers.find({"company_id": _cid(company_id)}).sort("worker_id", 1))


def worker_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "updated_at": _utcnow()}
    d.setdefault("created_at", _utcnow())
    db.workers.update_one(
        {"company_id": _cid(company_id), "worker_id": d["worker_id"]},
        {"$set": d},
        upsert=True,
    )


# --- Attendance ---
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


# --- Expenses ---
def expenses_list(company_id: str, limit: int = 500) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.expenses.find({"company_id": _cid(company_id)}).sort("expense_date", -1).limit(limit))


def expense_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    if isinstance(d.get("expense_date"), date):
        d["expense_date"] = d["expense_date"].isoformat()
    db.expenses.insert_one(d)


# --- Payroll ---
def payroll_runs_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.payroll_runs.find({"company_id": _cid(company_id)}).sort("period_start", -1))


def payroll_run_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    for k in ("period_start", "period_end"):
        if isinstance(d.get(k), date):
            d[k] = d[k].isoformat()
    db.payroll_runs.update_one(
        {"company_id": _cid(company_id), "run_id": d["run_id"]},
        {"$set": d},
        upsert=True,
    )


def payroll_lines_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.payroll_lines.find({"company_id": _cid(company_id)}).sort("run_id", 1).limit(2000))


def payroll_line_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    db.payroll_lines.insert_one(d)


# --- Invoices ---
def invoices_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.invoices.find({"company_id": _cid(company_id)}).sort("invoice_date", -1))


def invoice_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d = {**d, "company_id": _cid(company_id), "created_at": _utcnow()}
    if isinstance(d.get("invoice_date"), date):
        d["invoice_date"] = d["invoice_date"].isoformat()
    db.invoices.update_one(
        {"company_id": _cid(company_id), "invoice_no": d["invoice_no"]},
        {"$set": d},
        upsert=True,
    )


# --- Payroll estimate (pandas) ---
def payroll_estimate_df(company_id: str, start: date, end: date) -> pd.DataFrame:
    db = get_db()
    cid = _cid(company_id)
    workers = list(db.workers.find({"company_id": cid, "active": True}))
    rules = {r["rule_id"]: r for r in db.ot_rules.find({"company_id": cid})}
    att = list(
        db.attendance.find(
            {
                "company_id": cid,
                "work_date": {"$gte": start.isoformat(), "$lte": end.isoformat()},
                "status": "Present",
            }
        )
    )
    paid: dict[str, int] = {}
    ot_h: dict[str, float] = {}
    for a in att:
        w = a["worker_id"]
        paid[w] = paid.get(w, 0) + 1
        ot_h[w] = ot_h.get(w, 0.0) + float(a.get("ot_hrs") or 0)
    rows = []
    for w in workers:
        wid = w["worker_id"]
        days = paid.get(wid, 0)
        ot = ot_h.get(wid, 0.0)
        rid = w.get("ot_rule_id")
        mult = float(rules[rid]["multiplier"]) if rid and rid in rules else 2.0
        dr = float(w.get("daily_rate") or 0)
        mg = float(w.get("monthly_gross") or 0)
        pt = w.get("pay_type", "Daily")
        if pt == "Daily":
            ot_pay = ot * (dr / 8.0) * mult
            base = days * dr
        else:
            ot_pay = ot * (mg / 26.0 / 8.0) * mult
            base = (mg / 26.0) * min(days, 26)
        rows.append(
            {
                "worker_id": wid,
                "full_name": w.get("full_name", ""),
                "pay_type": pt,
                "paid_days": days,
                "ot_hrs": ot,
                "est_base": round(base, 2),
                "est_ot": round(ot_pay, 2),
                "est_gross": round(base + ot_pay, 2),
            }
        )
    return pd.DataFrame(rows)


# --- Dashboard metrics ---
def dashboard_stats(company_id: str, p_start: date, p_end: date) -> dict[str, Any]:
    db = get_db()
    cid = _cid(company_id)
    n_proj = db.projects.count_documents({"company_id": cid})
    n_act = db.projects.count_documents({"company_id": cid, "status": "Active"})
    n_w = db.workers.count_documents({"company_id": cid, "active": True})
    att_c = db.attendance.count_documents(
        {
            "company_id": cid,
            "work_date": {"$gte": p_start.isoformat(), "$lte": p_end.isoformat()},
            "status": "Present",
        }
    )
    pipeline = [
        {
            "$match": {
                "company_id": cid,
                "expense_date": {"$gte": p_start.isoformat(), "$lte": p_end.isoformat()},
                "approved": True,
            }
        },
        {"$group": {"_id": None, "s": {"$sum": "$amount"}}},
    ]
    agg = list(db.expenses.aggregate(pipeline))
    exp_sum = float(agg[0]["s"]) if agg else 0.0
    return {
        "projects_total": n_proj,
        "projects_active": n_act,
        "workers_active": n_w,
        "attendance_present_rows": att_c,
        "approved_expenses_sum": exp_sum,
    }
