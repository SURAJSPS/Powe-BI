"""MongoDB CRUD for civil operations (scoped by company_id)."""
from __future__ import annotations

from .clients import (
    client_add,
    client_get,
    client_update,
    clients_list,
    clients_summary,
    employee_add,
    employees_list,
)
from .field import (
    ot_rule_add,
    ot_rules_list,
    project_add,
    project_delete,
    project_get,
    project_update,
    projects_list,
    site_add,
    sites_list,
    worker_add,
    workers_list,
)
from .finance import (
    dashboard_stats,
    invoice_add,
    invoices_list,
    payroll_estimate_df,
    payroll_line_add,
    payroll_lines_list,
    payroll_run_add,
    payroll_runs_list,
)
from .ops import attendance_add, attendance_list, expense_add, expenses_list

__all__ = [
    "attendance_add",
    "attendance_list",
    "client_add",
    "client_get",
    "client_update",
    "clients_list",
    "clients_summary",
    "dashboard_stats",
    "employee_add",
    "employees_list",
    "expense_add",
    "expenses_list",
    "invoice_add",
    "invoices_list",
    "ot_rule_add",
    "ot_rules_list",
    "payroll_estimate_df",
    "payroll_line_add",
    "payroll_lines_list",
    "payroll_run_add",
    "payroll_runs_list",
    "project_add",
    "project_delete",
    "project_get",
    "project_update",
    "projects_list",
    "site_add",
    "sites_list",
    "worker_add",
    "workers_list",
]
