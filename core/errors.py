"""Application errors — subclass ValueError so existing ``except ValueError`` in pages still works."""
from __future__ import annotations

import logging
from typing import Any, Literal

logger = logging.getLogger(__name__)

Severity = Literal["error", "warning", "info"]


class AppError(ValueError):
    """User-facing domain error."""

    def __init__(self, message: str, code: str = "APP_ERROR") -> None:
        self.code = code
        super().__init__(message)

    def log(self, extra: dict[str, Any] | None = None) -> None:
        logger.warning("%s: %s", self.code, self, extra=extra or {})


class ValidationError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "VALIDATION")


class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(f"{resource} not found ({resource_id}).", "NOT_FOUND")


class DuplicateError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(message, "DUPLICATE")


class AuthorizationError(AppError):
    def __init__(self, message: str = "You do not have permission for this action.") -> None:
        super().__init__(message, "AUTHORIZATION")


def streamlit_severity(exc: BaseException) -> tuple[str, Severity]:
    """Map exception to (message, Streamlit display level)."""
    if isinstance(exc, AuthorizationError):
        return str(exc), "warning"
    if isinstance(exc, NotFoundError):
        return str(exc), "info"
    if isinstance(exc, DuplicateError):
        return str(exc), "warning"
    if isinstance(exc, AppError):
        return str(exc), "error"
    return str(exc), "error"
