from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

import pytest

from core.errors import NotFoundError
from services import entry_policy


def test_entry_date_window_admin_bypass() -> None:
    company = {"backdate_bypass_admin": True, "allow_future_dated_entries": False}
    mn, mx = entry_policy.entry_date_window(company, "company_admin")
    assert mn is None
    assert mx == date.today()


def test_clamp_entry_day() -> None:
    t = date.today()
    assert entry_policy.clamp_entry_day(t + timedelta(days=5), None, t) == t


def test_assert_entry_date_allowed_missing_company() -> None:
    with patch("services.entry_policy.auth_service.get_company", return_value=None):
        with pytest.raises(NotFoundError):
            entry_policy.assert_entry_date_allowed("x" * 24, date.today(), "viewer")
