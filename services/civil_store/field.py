"""Projects, sites, workers, OT rules."""
from __future__ import annotations

from typing import Any

from core.errors import NotFoundError
from db.mongo import get_db
from services.validators import MSG, optional_text, required_text

from ._util import _cid, _utcnow


def ot_rules_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.ot_rules.find({"company_id": _cid(company_id)}).sort("rule_id", 1))


def ot_rule_add(
    company_id: str, rule_id: str, rule_name: str, multiplier: float, max_ot: float | None, notes: str
) -> None:
    db = get_db()
    rule_id = required_text(rule_id, message="Rule ID is required.")
    rule_name = required_text(rule_name, message="Rule name is required.")
    db.ot_rules.update_one(
        {"company_id": _cid(company_id), "rule_id": rule_id},
        {
            "$set": {
                "rule_name": rule_name,
                "multiplier": float(multiplier),
                "max_ot_hrs_per_day": max_ot,
                "notes": optional_text(notes),
                "updated_at": _utcnow(),
            },
            "$setOnInsert": {"company_id": _cid(company_id), "rule_id": rule_id, "created_at": _utcnow()},
        },
        upsert=True,
    )


def projects_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.projects.find({"company_id": _cid(company_id)}).sort("project_code", 1))


def project_get(company_id: str, project_code: str) -> dict[str, Any] | None:
    db = get_db()
    return db.projects.find_one(
        {"company_id": _cid(company_id), "project_code": (project_code or "").strip()}
    )


def project_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d["project_code"] = required_text(d.get("project_code"), message=MSG["project_code_required"])
    d["name"] = required_text(d.get("name"), message=MSG["project_name_required"])
    d["client_name"] = optional_text(d.get("client_name")) or ""
    d["description"] = optional_text(d.get("description"))
    d = {**d, "company_id": _cid(company_id), "updated_at": _utcnow()}
    d.setdefault("created_at", _utcnow())
    db.projects.update_one(
        {"company_id": _cid(company_id), "project_code": d["project_code"]},
        {"$set": d},
        upsert=True,
    )


def project_update(company_id: str, project_code: str, d: dict[str, Any]) -> None:
    """Update project fields; does not change ``project_code`` (business key)."""
    db = get_db()
    cid = _cid(company_id)
    pc = (project_code or "").strip()
    if "name" in d:
        d["name"] = required_text(d.get("name"), message=MSG["project_name_required"])
    if "client_name" in d:
        d["client_name"] = optional_text(d.get("client_name")) or ""
    if "description" in d:
        d["description"] = optional_text(d.get("description"))
    patch = {k: v for k, v in d.items() if k not in ("_id", "company_id", "project_code", "created_at")}
    patch["updated_at"] = _utcnow()
    res = db.projects.update_one({"company_id": cid, "project_code": pc}, {"$set": patch})
    if res.matched_count == 0:
        raise NotFoundError("Project", pc)


def project_delete(company_id: str, project_code: str) -> None:
    """Remove project and all sites linked to this ``project_code`` for the company."""
    db = get_db()
    cid = _cid(company_id)
    pc = (project_code or "").strip()
    db.sites.delete_many({"company_id": cid, "project_code": pc})
    res = db.projects.delete_one({"company_id": cid, "project_code": pc})
    if res.deleted_count == 0:
        raise NotFoundError("Project", pc)


def sites_list(company_id: str) -> list[dict[str, Any]]:
    db = get_db()
    return list(db.sites.find({"company_id": _cid(company_id)}).sort("site_code", 1))


def site_add(company_id: str, d: dict[str, Any]) -> None:
    db = get_db()
    d["site_code"] = required_text(d.get("site_code"), message=MSG["site_code_required"])
    d["name"] = required_text(d.get("name"), message=MSG["site_name_required"])
    d["project_code"] = required_text(d.get("project_code"), message=MSG["project_required"])
    d["location"] = optional_text(d.get("location"))
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
    d["worker_id"] = required_text(d.get("worker_id"), message=MSG["worker_id_required"])
    d["full_name"] = required_text(d.get("full_name"), message=MSG["full_name_required"])
    d = {**d, "company_id": _cid(company_id), "updated_at": _utcnow()}
    d.setdefault("created_at", _utcnow())
    db.workers.update_one(
        {"company_id": _cid(company_id), "worker_id": d["worker_id"]},
        {"$set": d},
        upsert=True,
    )
