"""Company-level rules for how far in the past (or future) dated entries may be posted."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from core.errors import NotFoundError
from services import auth_service


def get_company_policy(company_id: str) -> dict[str, Any]:
    c = auth_service.get_company(company_id)
    if not c:
        return {}
    return c


def entry_date_window(company: dict[str, Any], user_role: str) -> tuple[date | None, date | None]:
    """Return (min_date, max_date) inclusive for date pickers. None means unbounded on that side."""
    today = date.today()
    allow_future = bool(company.get("allow_future_dated_entries", False))
    max_d: date | None = None if allow_future else today

    if user_role == "company_admin" and company.get("backdate_bypass_admin", True):
        return (None, max_d)

    raw = company.get("backdate_max_days")
    if raw is None:
        return (None, max_d)
    try:
        n = int(raw)
    except (TypeError, ValueError):
        return (None, max_d)
    min_d = today - timedelta(days=n)
    return (min_d, max_d)


def clamp_entry_day(day: date, min_d: date | None, max_d: date | None) -> date:
    """Keep a calendar day inside [min_d, max_d] when bounds are set."""
    out = day
    if max_d is not None and out > max_d:
        out = max_d
    if min_d is not None and out < min_d:
        out = min_d
    return out


def assert_entry_date_allowed(company_id: str, entry_date: date, user_role: str) -> None:
    """Raise ValueError if entry_date violates company backdating / future rules."""
    c = auth_service.get_company(company_id)
    if not c:
        raise NotFoundError("Company", company_id)
    min_d, max_d = entry_date_window(c, user_role)
    if max_d is not None and entry_date > max_d:
        raise ValueError(
            f"Future-dated entries are not allowed (latest allowed date: {max_d.isoformat()}). "
            "Ask a company admin to enable future-dated entries in Company profile if needed."
        )
    if min_d is not None and entry_date < min_d:
        raise ValueError(
            f"Date is too far in the past. Earliest allowed: {min_d.isoformat()} "
            f"({c.get('backdate_max_days')} day window). "
            "Company admins may bypass this in Company profile."
        )
