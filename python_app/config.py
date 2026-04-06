"""Load settings from environment (.env) or Streamlit secrets."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")
load_dotenv(Path(__file__).resolve().parent / ".env")


def _get(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    if v:
        return v.strip()
    return default


MONGO_URI = _get("MONGO_URI") or _get("MONGODB_URI")
MONGO_DB_NAME = _get("MONGO_DB_NAME", "rnk_civil")

# When False and MONGO_URI missing, app shows setup instructions (SQLite legacy optional).
REQUIRE_MONGO = (_get("REQUIRE_MONGO", "true") or "true").lower() in ("1", "true", "yes")
