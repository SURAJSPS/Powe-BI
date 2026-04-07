"""Projects, sites, workers, and creation modals."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from core.roles import ROLE_LABELS
from services import auth_service, civil_store
from ui.pages.common import _cid
from ui.theme import empty_state, page_header

_SS_PROJ = "_rnk_open_modal_project"
_SS_SITE = "_rnk_open_modal_site"
_MP_TEAM_ORDER = "_mp_proj_team_order"


def _sync_project_team_order() -> None:
    """Keep selection order: first in list = project manager. Called after multiselect (no on_change inside forms)."""
    raw = st.session_state.get("mp_team") or []
    order = [x for x in st.session_state.get(_MP_TEAM_ORDER, []) if x in raw]
    seen = set(order)
    for x in raw:
        if x not in seen:
            order.append(x)
            seen.add(x)
    st.session_state[_MP_TEAM_ORDER] = order


def _user_pick_label(u: dict) -> str:
    """Single-line label: name, role, email (email keeps rows unique in multiselect)."""
    fn = (u.get("full_name") or "").strip() or "—"
    em = (u.get("email") or "").strip()
    role = ROLE_LABELS.get(u.get("role", ""), u.get("role", "") or "—")
    return f"{fn} — {role} · {em}"


def _employee_pick_label(e: dict) -> str:
    code = (e.get("employee_code") or "").strip() or "—"
    fn = (e.get("full_name") or "").strip() or "—"
    return f"{code} — {fn}"


@st.dialog("New project", width="large")
def _modal_add_project() -> None:
    """Modal: create a project with optional PM, team, and office staff links."""
    cid = _cid()
    users = auth_service.list_users(cid)
    emps = civil_store.employees_list(cid)
    user_map = {_user_pick_label(u): u["user_id"] for u in users}
    user_labels = sorted(user_map.keys(), key=str.lower)

    emp_map = {_employee_pick_label(e): str(e["_id"]) for e in emps}
    emp_labels = sorted(emp_map.keys(), key=str.lower)

    st.markdown(
        '<div class="rnk-modal-head"><h3 class="rnk-modal-head__title">Create a project</h3></div>',
        unsafe_allow_html=True,
    )

    clients = civil_store.clients_list(cid)
    client_names = sorted(
        {(c.get("name") or "").strip() for c in clients if (c.get("name") or "").strip()}
    )
    add_new_token = "＋ Add new client"

    submitted = False
    cancel_in = False
    with st.form("modal_form_project", clear_on_submit=False):
        st.markdown('<p class="rnk-modal-section">Identification</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            code = st.text_input("Project code *", placeholder="PRJ-001", key="mp_code")
        with c2:
            name = st.text_input("Project name *", placeholder="e.g. NH package / Block A", key="mp_name")

        st.markdown('<p class="rnk-modal-section">Client</p>', unsafe_allow_html=True)
        pick: str | None = None
        if client_names:
            pick = st.selectbox(
                "Client",
                client_names + [add_new_token],
                key="mp_client_pick",
            )
            if pick == add_new_token:
                client = st.text_input(
                    "New client name",
                    placeholder="As on PO or agreement",
                    key="mp_client_new",
                )
            else:
                client = pick
        else:
            client = st.text_input("New client name", placeholder="As on PO or agreement", key="mp_client_only")

        st.markdown('<p class="rnk-modal-section">Planning</p>', unsafe_allow_html=True)
        r2a, r2b, r2c = st.columns(3, gap="medium")
        with r2a:
            status = st.selectbox(
                "Status",
                ["Planning", "Active", "On Hold", "Completed", "Archived"],
                key="mp_status",
            )
        with r2b:
            priority = st.selectbox(
                "Priority",
                ["Normal", "High", "Critical"],
                index=0,
                key="mp_priority",
            )
        with r2c:
            budget = st.number_input(
                "Budget (₹)",
                min_value=0.0,
                value=0.0,
                step=50_000.0,
                format="%.0f",
                key="mp_budget",
            )
        desc = st.text_area("Description (optional)", placeholder="Scope, notes…", height=88, key="mp_desc")

        st.markdown('<p class="rnk-modal-section">Team</p>', unsafe_allow_html=True)
        if user_labels:
            st.multiselect(
                "Add people (first in the list = project manager)",
                options=user_labels,
                key="mp_team",
            )
            _sync_project_team_order()
            team_order = list(st.session_state.get(_MP_TEAM_ORDER) or [])
            pm_preview = team_order[0] if team_order else "—"
            st.caption(f"Project manager: {pm_preview}")
        else:
            team_order = []
            st.caption("No users in this company yet.")
        emp_pick = st.multiselect("Employees", options=emp_labels, key="mp_emps") if emp_labels else []

        st.divider()
        _sp, _ca, _cr = st.columns([3, 1, 1], gap="small")
        with _ca:
            cancel_in = st.form_submit_button("Cancel", use_container_width=True)
        with _cr:
            submitted = st.form_submit_button("Create", type="primary", use_container_width=True)

    if cancel_in:
        st.session_state[_SS_PROJ] = False
        st.session_state.pop("mp_team", None)
        st.session_state.pop(_MP_TEAM_ORDER, None)
        st.rerun()

    if submitted:
        code_t = (code or "").strip()
        name_t = (name or "").strip()
        client_t = (client if isinstance(client, str) else "") or ""
        client_t = client_t.strip()
        if not code_t or not name_t:
            st.error("Please enter both project code and project name.")
            return
        if pick == add_new_token and not client_t:
            st.error("Please enter a new client name.")
            return
        order = list(st.session_state.get(_MP_TEAM_ORDER) or [])
        team_pick = st.session_state.get("mp_team") or []
        if not order and team_pick:
            order = list(team_pick)
        team_ids = [user_map[lb] for lb in order if lb in user_map]
        pm_uid: str | None = user_map.get(order[0]) if order else None

        emp_ids: list[str] = []
        for lb in emp_pick:
            eid = emp_map.get(lb)
            if eid and eid not in emp_ids:
                emp_ids.append(eid)

        desc_t = (desc or "").strip() or None
        try:
            if client_t:
                existing = {x.strip().lower() for x in client_names}
                if client_t.lower() not in existing:
                    civil_store.client_add(cid, client_t)
            civil_store.project_add(
                cid,
                {
                    "project_code": code_t,
                    "name": name_t,
                    "client_name": client_t,
                    "status": status,
                    "budget": float(budget),
                    "priority": priority,
                    "description": desc_t,
                    "project_manager_user_id": pm_uid,
                    "team_user_ids": team_ids,
                    "linked_employee_ids": emp_ids,
                },
            )
            st.session_state[_SS_PROJ] = False
            st.session_state.pop("mp_team", None)
            st.session_state.pop(_MP_TEAM_ORDER, None)
            st.success("Project created.")
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


@st.dialog("New site", width="large")
def _modal_add_site() -> None:
    """Modal: create a site linked to a project."""
    plist = civil_store.projects_list(_cid())
    if not plist:
        st.warning("Add a project first.")
        if st.button("Close", key="site_modal_close_empty", use_container_width=True):
            st.session_state[_SS_SITE] = False
            st.rerun()
        return

    st.markdown(
        '<div class="rnk-modal-head"><h3 class="rnk-modal-head__title">Create a site</h3></div>',
        unsafe_allow_html=True,
    )
    pcs = [p["project_code"] for p in plist]

    submitted = False
    cancel_site = False
    with st.form("modal_form_site", clear_on_submit=False):
        st.markdown('<p class="rnk-modal-section">Site</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2, gap="medium")
        with s1:
            sc = st.text_input("Site code *", placeholder="S-01", key="ms_code")
        with s2:
            sn = st.text_input("Site name *", placeholder="Batching plant / site office", key="ms_name")
        loc = st.text_input("Location", placeholder="District, landmark…", key="ms_loc")

        st.markdown('<p class="rnk-modal-section">Project</p>', unsafe_allow_html=True)
        pc = st.selectbox("Project *", pcs, key="ms_proj")

        st.divider()
        _s1, _s2, _s3 = st.columns([3, 1, 1], gap="small")
        with _s2:
            cancel_site = st.form_submit_button("Cancel", use_container_width=True)
        with _s3:
            submitted = st.form_submit_button("Create", type="primary", use_container_width=True)

    if cancel_site:
        st.session_state[_SS_SITE] = False
        st.rerun()

    if submitted:
        sc_t = (sc or "").strip()
        sn_t = (sn or "").strip()
        if not sc_t or not sn_t:
            st.error("Please enter site code and site name.")
            return
        pid = next((x for x in plist if x["project_code"] == pc), None)
        try:
            civil_store.site_add(
                _cid(),
                {
                    "site_code": sc_t,
                    "name": sn_t,
                    "location": (loc or "").strip(),
                    "active": True,
                    "project_code": pc,
                    "project_id": str(pid["_id"]) if pid else "",
                },
            )
            st.session_state[_SS_SITE] = False
            st.success("Site created.")
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


def page_projects(u: dict) -> None:
    """Projects register only — sites have their own page."""
    col_title, col_add = st.columns([6, 1])
    with col_title:
        page_header("Projects", "All jobs in your company — codes, clients, and status.", eyebrow="Field")
    with col_add:
        st.markdown('<div style="min-height:2.6rem;"></div>', unsafe_allow_html=True)
        if st.button("Add", type="primary", key="open_modal_project", help="Create a new project"):
            st.session_state[_SS_PROJ] = True
            st.session_state.pop("mp_team", None)
            st.session_state.pop(_MP_TEAM_ORDER, None)
            st.session_state.pop("mp_pm", None)
    if st.session_state.get(_SS_PROJ):
        _modal_add_project()

    plist = civil_store.projects_list(_cid())
    df_p = pd.DataFrame(plist)
    if df_p.empty:
        empty_state("No projects yet", "Use **Add** above to create your first project.")
    else:
        _proj_col_order = [
            "project_code",
            "name",
            "client_name",
            "status",
            "priority",
            "budget",
            "project_manager_user_id",
            "team_user_ids",
            "linked_employee_ids",
            "description",
        ]
        ordered = [c for c in _proj_col_order if c in df_p.columns]
        rest = [c for c in df_p.columns if c not in ordered]
        st.dataframe(df_p[ordered + rest], use_container_width=True, hide_index=True)


def page_sites(u: dict) -> None:
    """Sites linked to projects — attendance and costs use site codes."""
    col_title, col_add = st.columns([6, 1])
    with col_title:
        page_header("Sites", "Physical locations tied to a project — plants, camps, stretches.", eyebrow="Field")
    with col_add:
        st.markdown('<div style="min-height:2.6rem;"></div>', unsafe_allow_html=True)
        if st.button("Add", type="primary", key="open_modal_site", help="Add a new site"):
            st.session_state[_SS_SITE] = True
    if st.session_state.get(_SS_SITE):
        _modal_add_site()

    slist = civil_store.sites_list(_cid())
    df_s = pd.DataFrame(slist)
    if df_s.empty:
        empty_state("No sites yet", "Create a project first, then use **Add** to register a site.")
    else:
        st.dataframe(df_s, use_container_width=True, hide_index=True)


def page_workers(u: dict) -> None:
    wlist = civil_store.workers_list(_cid())
    df_w = pd.DataFrame(wlist)
    if df_w.empty:
        empty_state("No workers", "Register site labour — used for attendance and payroll.")
    else:
        st.dataframe(df_w, use_container_width=True, hide_index=True)
    rules = [r["rule_id"] for r in civil_store.ot_rules_list(_cid())]
    with st.form("wk"):
        w1, w2 = st.columns(2, gap="medium")
        with w1:
            wid = st.text_input("Worker ID", value="W-")
        with w2:
            fn = st.text_input("Full name")
        w3, w4 = st.columns(2, gap="medium")
        with w3:
            pt = st.selectbox("Pay type", ["Daily", "Monthly"])
        with w4:
            otr = st.selectbox("OT rule", rules or ["OT-STD"])
        w5, w6 = st.columns(2, gap="medium")
        with w5:
            dr = st.number_input("Daily rate", value=0.0)
        with w6:
            mg = st.number_input("Monthly gross", value=0.0)
        if st.form_submit_button("Save worker", type="primary", use_container_width=True):
            civil_store.worker_add(
                _cid(),
                {
                    "worker_id": wid,
                    "full_name": fn,
                    "pay_type": pt,
                    "daily_rate": dr if pt == "Daily" else None,
                    "monthly_gross": mg if pt == "Monthly" else None,
                    "ot_rule_id": otr,
                    "active": True,
                },
            )
            st.rerun()
