"""Load settings from environment (.env) or Streamlit secrets.

Mongo URI from split vars matches Node `buildMongoUriFromEnv`:
  MONGODB_URI → use as-is
  else mongodb+srv://user:pass@cluster/{database}?authSource&authMechanism&retryWrites&w&appName
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent


def refresh_env() -> None:
    """Reload the single project `.env` (repo root) so edits apply without restarting Python."""
    load_dotenv(_ROOT / ".env", override=True)


refresh_env()


def _get(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v:
        return v.strip()
    return default


def _mongo_uri_from_parts() -> str | None:
    """Build URI the same way as Node: buildMongoUriFromEnv."""
    user = _get("MONGO_USER") or _get("MONGODB_USERNAME")
    password = _get("MONGO_PASSWORD") or _get("MONGODB_PASSWORD")
    cluster = _get("MONGO_HOST") or _get("MONGODB_CLUSTER")
    if not user or not password or not cluster:
        return None

    database = _get("MONGO_DB_NAME") or _get("MONGODB_DATABASE") or ""
    scheme = _get("MONGO_SCHEME") or _get("MONGODB_SCHEME") or "mongodb+srv"

    # Query string order aligned with Node URLSearchParams
    params: list[str] = []
    auth_source = _get("MONGO_AUTH_SOURCE") or _get("MONGODB_AUTH_SOURCE")
    if auth_source:
        params.append(f"authSource={quote_plus(auth_source)}")
    auth_mech = _get("MONGO_AUTH_MECHANISM") or _get("MONGODB_AUTH_MECHANISM")
    if auth_mech:
        params.append(f"authMechanism={quote_plus(auth_mech)}")
    params.append("retryWrites=true")
    params.append("w=majority")
    app_name = _get("MONGO_APP_NAME") or _get("MONGODB_APP_NAME")
    if app_name:
        params.append(f"appName={quote_plus(app_name)}")

    query = "&".join(params)
    # Path: /{database} — Node uses `/${database}` (empty → "...cluster/?...")
    path = f"/{database}" if database else "/"
    return (
        f"{scheme}://{quote_plus(user)}:{quote_plus(password)}@{cluster}{path}?{query}"
    )


def get_mongo_uri() -> str | None:
    """Resolve connection string after refreshing env."""
    refresh_env()
    direct = _get("MONGO_URI") or _get("MONGODB_URI") or _get("MONGODB_URL")
    if direct:
        return direct
    return _mongo_uri_from_parts()


def get_mongo_db_name() -> str:
    """DB name for pymongo get_client()[name]. Align with MONGODB_DATABASE / path in URI."""
    refresh_env()
    return _get("MONGO_DB_NAME") or _get("MONGODB_DATABASE") or "rnk_civil"


MONGO_URI = get_mongo_uri()
MONGO_DB_NAME = get_mongo_db_name()

REQUIRE_MONGO = (_get("REQUIRE_MONGO", "true") or "true").lower() in ("1", "true", "yes")
