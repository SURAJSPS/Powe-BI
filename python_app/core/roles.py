"""Role definitions and page permissions."""
from __future__ import annotations

from typing import FrozenSet

# Ordered from most to least privileged for display
ROLES: tuple[str, ...] = (
    "company_admin",
    "manager",
    "finance",
    "site_ops",
    "viewer",
)

ROLE_LABELS: dict[str, str] = {
    "company_admin": "Company admin",
    "manager": "Manager / PM",
    "finance": "Finance & payroll",
    "site_ops": "Site / operations",
    "viewer": "Viewer (read-only)",
}

# Which sidebar keys each role may access
PAGE_KEYS: dict[str, FrozenSet[str]] = {
    "company_admin": frozenset(
        {
            "home",
            "company",
            "team",
            "clients",
            "ot_rules",
            "projects",
            "workers",
            "attendance",
            "expenses",
            "payroll_est",
            "payroll_runs",
            "invoices",
            "dashboard",
        }
    ),
    "manager": frozenset(
        {
            "home",
            "team",
            "clients",
            "ot_rules",
            "projects",
            "workers",
            "attendance",
            "expenses",
            "payroll_est",
            "payroll_runs",
            "invoices",
            "dashboard",
        }
    ),
    "finance": frozenset(
        {
            "home",
            "clients",
            "projects",
            "workers",
            "expenses",
            "payroll_est",
            "payroll_runs",
            "invoices",
            "dashboard",
        }
    ),
    "site_ops": frozenset(
        {
            "home",
            "projects",
            "workers",
            "attendance",
            "expenses",
            "dashboard",
        }
    ),
    "viewer": frozenset({"home", "projects", "dashboard"}),
}


def can_access(role: str, page: str) -> bool:
    if role not in PAGE_KEYS:
        return False
    return page in PAGE_KEYS[role]


def default_role_for_new_employee() -> str:
    return "site_ops"
