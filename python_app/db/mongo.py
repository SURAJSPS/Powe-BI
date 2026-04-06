"""MongoDB client — connection pooling and indexes."""
from __future__ import annotations

from pymongo import ASCENDING, MongoClient
from pymongo.database import Database
from pymongo.errors import OperationFailure, PyMongoError, ServerSelectionTimeoutError

from config import get_mongo_db_name, get_mongo_uri

_client: MongoClient | None = None
_uri_bound: str | None = None


def invalidate_client() -> None:
    """Close pooled client (e.g. after auth failure or URI change)."""
    global _client, _uri_bound
    if _client is not None:
        try:
            _client.close()
        except Exception:
            pass
    _client = None
    _uri_bound = None


def get_client() -> MongoClient:
    global _client, _uri_bound
    uri = get_mongo_uri()
    if not uri:
        raise RuntimeError(
            "MongoDB is not configured. Set MONGO_URI or MONGO_USER, MONGO_PASSWORD, "
            "and MONGO_HOST in the project root `.env`."
        )
    if _client is not None and _uri_bound == uri:
        return _client
    invalidate_client()
    _client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    _uri_bound = uri
    return _client


def _auth_failure_message(e: BaseException) -> bool:
    msg = str(e).lower()
    if any(
        x in msg
        for x in (
            "bad auth",
            "authentication failed",
            "unable to authenticate",
            "invalid credentials",
            "scram",
        )
    ):
        return True
    code = getattr(e, "code", None)
    return code in (18, 8000)


def diagnose() -> tuple[bool, str | None]:
    """Try to connect and ping; return (ok, user-facing error markdown or None)."""
    uri = get_mongo_uri()
    if not uri:
        return (
            False,
            "Set `MONGO_USER`, `MONGO_PASSWORD`, and `MONGO_HOST` (or a full `MONGO_URI`) in the project root `.env`.",
        )
    try:
        get_client().admin.command("ping")
        return True, None
    except OperationFailure as e:
        invalidate_client()
        if _auth_failure_message(e):
            return (
                False,
                "**Authentication failed.** In MongoDB Atlas open **Database Access**, confirm the "
                "username matches `MONGO_USER`, then **Edit** the user and set a new password. "
                "Put that password in `MONGO_PASSWORD` in `.env`, save, and restart Streamlit.",
            )
        return False, f"MongoDB error: `{e}`"
    except ServerSelectionTimeoutError:
        invalidate_client()
        return (
            False,
            "**Cannot reach the cluster.** In Atlas → **Network Access**, add your current IP "
            "(or `0.0.0.0/0` for testing). Check `MONGO_HOST` matches **Connect → Drivers**.",
        )
    except PyMongoError as e:
        invalidate_client()
        if _auth_failure_message(e):
            return (
                False,
                "**Authentication failed.** Reset the database user password in Atlas → **Database Access**, "
                "update `MONGO_PASSWORD` (or your full `MONGO_URI`) in `.env`, save, and restart Streamlit.",
            )
        return False, str(e)


def get_db() -> Database:
    return get_client()[get_mongo_db_name()]


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
