"""Projects, sites, workers, OT rules."""
from __future__ import annotations

from typing import Any

from db.mongo import get_db

from ._util import _cid, _utcnow


def ot_rules_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.ot_rules.find({"company_id": _cid(company_id)}).sort("rule_id", 1))


def ot_rule_add(
    company_id: str, rule_id: str, rule_name: str, multiplier: float, max_ot: float | None, notes: str
) -> None:
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
