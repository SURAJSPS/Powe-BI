"""Navigation registry, query params, and sidebar."""
from __future__ import annotations

from typing import Callable

import streamlit as st

from core.roles import can_access
from ui.pages.clients import page_clients
from ui.pages.company import page_company
from ui.pages.finance import (
    page_dashboard,
    page_invoices,
    page_payroll_est,
    page_payroll_runs,
)
from ui.pages.field_ops import page_projects, page_sites, page_workers
from ui.pages.home import page_home
from ui.pages.operations import page_attendance, page_expenses
from ui.pages.team import page_team

# Icons for sidebar nav (emoji — consistent with Home “Jump to” quick actions)
NAV_ICONS: dict[str, str] = {
    "home": "🏠",
    "company": "🏢",
    "team": "👥",
    "clients": "🤝",
    "projects": "🏗",
    "sites": "📍",
    "workers": "👷",
    "attendance": "📅",
    "expenses": "💰",
    "payroll_est": "📊",
    "payroll_runs": "📋",
    "invoices": "🧾",
    "dashboard": "📈",
}


# map page key -> (title, renderer)
PAGE_FUNCS: dict[str, tuple[str, Callable[..., None]]] = {
    "home": ("Home", page_home),
    "company": ("Company profile", page_company),
    "team": ("Team & employees", page_team),
    "clients": ("Clients", page_clients),
    "projects": ("Projects", page_projects),
    "sites": ("Sites", page_sites),
    "workers": ("Workers", page_workers),
    "attendance": ("Attendance", page_attendance),
    "expenses": ("Expenses", page_expenses),
    "payroll_est": ("Payroll estimate", page_payroll_est),
    "payroll_runs": ("Payroll runs", page_payroll_runs),
    "invoices": ("Invoices", page_invoices),
    "dashboard": ("Dashboard", page_dashboard),
}


def _nav_label(key: str) -> str:
    """Plain titles — sidebar styling provides hierarchy (no emoji clutter)."""
    return PAGE_FUNCS[key][0]


def _nav_icon_label(key: str) -> str:
    icon = NAV_ICONS.get(key, "◆")
    return f"{icon}  {_nav_label(key)}"


def _set_nav_page(page_key: str) -> None:
    st.session_state["rnk_nav"] = page_key


def _query_param_first(key: str) -> str | None:
    try:
        v = st.query_params.get(key)
        if v is None:
            return None
        if isinstance(v, list):
            return str(v[0]) if v else None
        return str(v)
    except Exception:
        return None


def apply_nav_from_query_params(role: str) -> None:
    """Open `?page=<nav_key>` on first load of a session (reload or deep link). Does not override sidebar after that."""
    keys = [k for k in PAGE_FUNCS if can_access(role, k)]
    if not keys or "rnk_nav" in st.session_state:
        return
    p = _query_param_first("page")
    if p == "ot_rules":
        p = "company"
    if p and p in keys:
        st.session_state["rnk_nav"] = p


def publish_nav_to_query_params(nav: str) -> None:
    """Mirror current screen in the address bar (?page=...) for bookmarks and sharing."""
    try:
        cur = _query_param_first("page")
        if cur != nav:
            st.query_params["page"] = nav
    except Exception:
        pass


def sidebar_nav(role: str) -> str | None:
    keys = [k for k in PAGE_FUNCS if can_access(role, k)]
    if not keys:
        return None
    if "rnk_nav_pending" in st.session_state:
        pending = st.session_state.pop("rnk_nav_pending")
        if pending in keys:
            st.session_state["rnk_nav"] = pending
    if "rnk_nav" not in st.session_state:
        st.session_state["rnk_nav"] = keys[0]
    elif st.session_state["rnk_nav"] not in keys:
        st.session_state["rnk_nav"] = keys[0]

    current = st.session_state["rnk_nav"]
    with st.sidebar.container():
        for key in keys:
            st.button(
                _nav_icon_label(key),
                key=f"rnk_nav_btn_{key}",
                use_container_width=True,
                type="primary" if key == current else "secondary",
                on_click=_set_nav_page,
                args=(key,),
            )

    return current
