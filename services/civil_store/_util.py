from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _cid(company_id: str) -> ObjectId:
    return ObjectId(company_id)
