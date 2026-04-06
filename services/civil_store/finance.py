"""Payroll, invoices, dashboard metrics, payroll estimate DataFrame."""
from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from db.mongo import get_db

from ._util import _cid, _utcnow


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
