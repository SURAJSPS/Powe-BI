"""Load settings from environment (.env) or Streamlit secrets."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
_APP = Path(__file__).resolve().parent


def refresh_env() -> None:
    """Reload `.env` so password changes apply after save (call before reading Mongo settings)."""
    load_dotenv(_ROOT / ".env", override=True)
    load_dotenv(_APP / ".env", override=True)


refresh_env()


def _get(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v:
        return v.strip()
    return default


def _mongo_uri_from_parts() -> str | None:
    """Build Atlas-style URI from split env vars.

    Supports **RNK / Streamlit** names (`MONGO_*`) and **Node / Tepo-style** names (`MONGODB_*`).
    """
    user = _get("MONGO_USER") or _get("MONGODB_USERNAME")
    password = _get("MONGO_PASSWORD") or _get("MONGODB_PASSWORD")
    host = _get("MONGO_HOST") or _get("MONGODB_CLUSTER")
    if not user or not password or not host:
        return None
    scheme = _get("MONGO_SCHEME") or _get("MONGODB_SCHEME") or "mongodb+srv"
    qs: list[str] = []
    app = _get("MONGO_APP_NAME") or _get("MONGODB_APP_NAME")
    if app:
        qs.append(f"appName={quote_plus(app)}")
    auth_src = _get("MONGO_AUTH_SOURCE") or _get("MONGODB_AUTH_SOURCE")
    if auth_src:
        qs.append(f"authSource={quote_plus(auth_src)}")
    qs.append("retryWrites=true")
    qs.append("w=majority")
    tail = "&".join(qs)
    return f"{scheme}://{quote_plus(user)}:{quote_plus(password)}@{host}/?{tail}"


def get_mongo_uri() -> str | None:
    """Resolve connection string after refreshing env (use this instead of a static constant)."""
    refresh_env()
    return (
        _get("MONGO_URI")
        or _get("MONGODB_URI")
        or _get("MONGODB_URL")
        or _mongo_uri_from_parts()
    )


def get_mongo_db_name() -> str:
    refresh_env()
    return _get("MONGO_DB_NAME") or _get("MONGODB_DATABASE") or "rnk_civil"


# Back-compat: values at import time (prefer get_mongo_uri() in new code).
MONGO_URI = get_mongo_uri()
MONGO_DB_NAME = get_mongo_db_name()

REQUIRE_MONGO = (_get("REQUIRE_MONGO", "true") or "true").lower() in ("1", "true", "yes")
