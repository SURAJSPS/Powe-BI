from __future__ import annotations

from core.errors import (
    AuthorizationError,
    DuplicateError,
    NotFoundError,
    ValidationError,
    streamlit_severity,
)


def test_streamlit_severity_authorization() -> None:
    msg, sev = streamlit_severity(AuthorizationError("no"))
    assert "no" in msg
    assert sev == "warning"


def test_streamlit_severity_not_found() -> None:
    msg, sev = streamlit_severity(NotFoundError("X", "id1"))
    assert "not found" in msg
    assert sev == "info"


def test_streamlit_severity_duplicate() -> None:
    msg, sev = streamlit_severity(DuplicateError("dup"))
    assert sev == "warning"


def test_streamlit_severity_validation() -> None:
    msg, sev = streamlit_severity(ValidationError("bad"))
    assert sev == "error"


def test_app_errors_subclass_valueerror() -> None:
    assert isinstance(ValidationError("x"), ValueError)
    assert isinstance(NotFoundError("R", "1"), ValueError)
    assert isinstance(DuplicateError("d"), ValueError)
