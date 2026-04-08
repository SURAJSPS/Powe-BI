"""Shared form/data validation helpers and messages."""
from __future__ import annotations

import re

from core.errors import ValidationError

REQUIRED_FIELD = "This field is required."

MSG = {
    "company_name_required": "Company display name is required.",
    "admin_name_required": "Administrator full name is required.",
    "email_required": "Email is required.",
    "password_required": "Password is required.",
    "full_name_required": "Full name is required.",
    "display_name_required": "Display name is required.",
    "project_code_required": "Project code is required.",
    "project_name_required": "Project name is required.",
    "site_code_required": "Site code is required.",
    "site_name_required": "Site name is required.",
    "worker_id_required": "Worker ID is required.",
    "run_id_required": "Run ID is required.",
    "component_required": "Component is required.",
    "invoice_no_required": "Invoice number is required.",
    "project_required": "Project is required.",
    "worker_required": "Worker is required.",
    "amount_non_negative": "Amount cannot be negative.",
}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def required_text(value: str | None, *, message: str | None = None) -> str:
    s = (value or "").strip()
    if not s:
        raise ValidationError(message or REQUIRED_FIELD)
    return s


def optional_text(value: str | None) -> str | None:
    s = (value or "").strip()
    return s or None


def email(value: str | None, *, required: bool = True) -> str | None:
    s = (value or "").strip().lower()
    if not s:
        if required:
            raise ValidationError(MSG["email_required"])
        return None
    if not _EMAIL_RE.match(s):
        raise ValidationError("Enter a valid email address.")
    return s


def non_negative(value: float | int, *, field_message: str | None = None) -> float:
    v = float(value)
    if v < 0:
        raise ValidationError(field_message or MSG["amount_non_negative"])
    return v
