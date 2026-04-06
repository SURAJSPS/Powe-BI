"""Load settings from environment (.env).

Builds Mongo URI like Node `buildMongoUriFromEnv` (encodeURIComponent → urllib.parse.quote).
"""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv

# Directory that contains this file = project root (where `app.py` and `.env` live).
_ROOT = Path(__file__).resolve().parent


def refresh_env() -> None:
    load_dotenv(_ROOT / ".env", override=True)


refresh_env()


def _enc(s: str) -> str:
    """Match Node encodeURIComponent for URI components."""
    return quote(s, safe="")


def _get(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v is None:
        return default
    v = v.strip()
    # Strip optional wrapping quotes from .env values
    if len(v) >= 2 and ((v[0] == v[-1] == '"') or (v[0] == v[-1] == "'")):
        v = v[1:-1].strip()
    return v or default


def _normalize_cluster(host: str) -> str:
    h = host.strip()
    for prefix in ("mongodb+srv://", "mongodb://", "https://", "http://"):
        if h.startswith(prefix):
            h = h[len(prefix) :]
    return h.strip().rstrip("/")


def _mongo_uri_from_parts() -> str | None:
    """Build URI the same way as Node: buildMongoUriFromEnv."""
    user = _get("MONGO_USER") or _get("MONGODB_USERNAME")
    password = _get("MONGO_PASSWORD") or _get("MONGODB_PASSWORD")
    cluster = _get("MONGO_HOST") or _get("MONGODB_CLUSTER")
    if not user or not password or not cluster:
        return None

    cluster = _normalize_cluster(cluster)
    database = _get("MONGO_DB_NAME") or _get("MONGODB_DATABASE") or ""
    scheme = _get("MONGO_SCHEME") or _get("MONGODB_SCHEME") or "mongodb+srv"

    params: list[str] = []
    auth_source = _get("MONGO_AUTH_SOURCE") or _get("MONGODB_AUTH_SOURCE")
    if auth_source:
        params.append(f"authSource={_enc(auth_source)}")
    auth_mech = _get("MONGO_AUTH_MECHANISM") or _get("MONGODB_AUTH_MECHANISM")
    if auth_mech:
        params.append(f"authMechanism={_enc(auth_mech)}")
    params.append("retryWrites=true")
    params.append("w=majority")
    app_name = _get("MONGO_APP_NAME") or _get("MONGODB_APP_NAME")
    if app_name:
        params.append(f"appName={_enc(app_name)}")

    query = "&".join(params)
    path = f"/{database}" if database else "/"
    return f"{scheme}://{_enc(user)}:{_enc(password)}@{cluster}{path}?{query}"


def get_mongo_uri() -> str | None:
    refresh_env()
    for key in ("MONGO_URI", "MONGODB_URI", "MONGODB_URL"):
        u = _get(key)
        if u:
            return u.strip()
    return _mongo_uri_from_parts()


def get_mongo_db_name() -> str:
    refresh_env()
    return _get("MONGO_DB_NAME") or _get("MONGODB_DATABASE") or "rnk_civil"


MONGO_URI = get_mongo_uri()
MONGO_DB_NAME = get_mongo_db_name()

REQUIRE_MONGO = (_get("REQUIRE_MONGO", "true") or "true").lower() in ("1", "true", "yes")


def get_app_session_secret() -> str:
    """HMAC secret for signed login cookies. Set APP_SECRET_KEY in `.env` for production."""
    refresh_env()
    s = _get("APP_SECRET_KEY")
    if s:
        return s
    # Stable default per machine/env so dev sessions work without extra config.
    return "rnk-civil-dev-insecure-change-app-secret-key"
