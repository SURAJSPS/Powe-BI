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

# Assignable when inviting a new login (company_admin cannot be created via invite).
ROLES_INVITABLE: tuple[str, ...] = tuple(r for r in ROLES if r != "company_admin")

# Which sidebar keys each role may access
PAGE_KEYS: dict[str, FrozenSet[str]] = {
    "company_admin": frozenset(
        {
            "home",
            "company",
            "team",
            "clients",
            "projects",
            "sites",
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
            "company",
            "team",
            "clients",
            "projects",
            "sites",
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
            "sites",
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
            "sites",
            "workers",
            "attendance",
            "expenses",
            "dashboard",
        }
    ),
    "viewer": frozenset({"home", "projects", "sites", "dashboard"}),
}


def can_access(role: str, page: str) -> bool:
    if role not in PAGE_KEYS:
        return False
    return page in PAGE_KEYS[role]


def can_manage_ot_rules(role: str) -> bool:
    """OT rules UI lives under Company profile — company admin and manager."""
    return role in ("company_admin", "manager")


def default_role_for_new_employee() -> str:
    return "site_ops"
