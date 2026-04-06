"""MongoDB client — connection pooling and indexes."""
from __future__ import annotations

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError

from config import MONGO_DB_NAME, MONGO_URI

_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI is not set. Add it to .env (see .env.example).")
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=8000)
    return _client


def get_db() -> Database:
    return get_client()[MONGO_DB_NAME]


def ping() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except PyMongoError:
        return False


def ensure_indexes() -> None:
    db = get_db()
    db.companies.create_index([("name", ASCENDING)])
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("company_id", ASCENDING)])
    db.clients.create_index([("company_id", ASCENDING), ("name", ASCENDING)])
    db.employees.create_index([("company_id", ASCENDING), ("employee_code", ASCENDING)])
    db.ot_rules.create_index([("company_id", ASCENDING), ("rule_id", ASCENDING)], unique=True)
    db.projects.create_index([("company_id", ASCENDING), ("project_code", ASCENDING)], unique=True)
    db.sites.create_index([("company_id", ASCENDING), ("site_code", ASCENDING)], unique=True)
    db.workers.create_index([("company_id", ASCENDING), ("worker_id", ASCENDING)], unique=True)
    db.attendance.create_index([("company_id", ASCENDING), ("work_date", ASCENDING), ("worker_id", ASCENDING)])
    db.expenses.create_index([("company_id", ASCENDING), ("expense_date", ASCENDING)])
    db.payroll_runs.create_index([("company_id", ASCENDING), ("run_id", ASCENDING)], unique=True)
    db.invoices.create_index([("company_id", ASCENDING), ("invoice_no", ASCENDING)], unique=True)


def oid(s: str):
    from bson import ObjectId

    return ObjectId(s)
