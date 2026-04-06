"""Projects, sites, workers, and creation modals."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from services import civil_store
from ui.pages.common import _cid
from ui.theme import empty_state, page_header

_SS_PROJ = "_rnk_open_modal_project"
_SS_SITE = "_rnk_open_modal_site"


@st.dialog("New project", width="large")
def _modal_add_project() -> None:
    """Modal: create a project (unique code + name)."""
    st.markdown(
        """
<div class="rnk-modal-head">
  <h3 class="rnk-modal-head__title">Create a project</h3>
  <p class="rnk-modal-head__sub">Use a short unique code for reports and dropdowns. Client and budget are optional.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    clients = civil_store.clients_list(_cid())
    client_names = sorted(
        {(c.get("name") or "").strip() for c in clients if (c.get("name") or "").strip()}
    )
    manual_token = "— Type manually —"

    submitted = False
    cancel_in = False
    with st.form("modal_form_project", clear_on_submit=False):
        st.markdown('<p class="rnk-modal-section">Identification</p>', unsafe_allow_html=True)
        r1a, r1b = st.columns(2)
        with r1a:
            code = st.text_input(
                "Project code *",
                placeholder="PRJ-001",
                help="Unique within your company.",
                key="mp_code",
            )
        with r1b:
            name = st.text_input(
                "Project name *",
                placeholder="e.g. NH package / Block A",
                key="mp_name",
            )

        st.markdown('<p class="rnk-modal-section">Client</p>', unsafe_allow_html=True)
        if client_names:
            pick = st.selectbox(
                "Client",
                [manual_token] + client_names,
                key="mp_client_pick",
                help="Pick from Clients master or type a new name.",
            )
            if pick == manual_token:
                client = st.text_input(
                    "Client name",
                    placeholder="As on PO or agreement",
                    key="mp_client_free",
                )
            else:
                client = pick
        else:
            st.caption("No clients in master yet — enter a display name.")
            client = st.text_input("Client name", placeholder="As on PO or agreement", key="mp_client_only")

        st.markdown('<p class="rnk-modal-section">Planning</p>', unsafe_allow_html=True)
        r2a, r2b = st.columns(2)
        with r2a:
            status = st.selectbox(
                "Status",
                ["Planning", "Active", "On Hold", "Completed", "Archived"],
                key="mp_status",
            )
        with r2b:
            budget = st.number_input(
                "Budget (₹)",
                min_value=0.0,
                value=0.0,
                step=50_000.0,
                format="%.0f",
                help="Optional reference for dashboards.",
                key="mp_budget",
            )

        st.markdown("<br/>", unsafe_allow_html=True)
        btn_row = st.columns([1, 1, 1])
        with btn_row[0]:
            submitted = st.form_submit_button("Create project", type="primary", use_container_width=True)
        with btn_row[1]:
            cancel_in = st.form_submit_button("Cancel", use_container_width=True)

    if cancel_in:
        st.session_state[_SS_PROJ] = False
        st.rerun()

    if submitted:
        code_t = (code or "").strip()
        name_t = (name or "").strip()
        client_t = (client if isinstance(client, str) else "") or ""
        client_t = client_t.strip()
        if not code_t or not name_t:
            st.error("Please enter both project code and project name.")
            return
        try:
            civil_store.project_add(
                _cid(),
                {
                    "project_code": code_t,
                    "name": name_t,
                    "client_name": client_t,
                    "status": status,
                    "budget": float(budget),
                },
            )
            st.session_state[_SS_PROJ] = False
            st.success("Project created.")
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


@st.dialog("New site", width="large")
def _modal_add_site() -> None:
    """Modal: create a site linked to a project."""
    plist = civil_store.projects_list(_cid())
    if not plist:
        st.warning("Create at least one project before adding a site.")
        if st.button("Close", key="site_modal_close_empty", use_container_width=True):
            st.session_state[_SS_SITE] = False
            st.rerun()
        return

    st.markdown(
        """
<div class="rnk-modal-head">
  <h3 class="rnk-modal-head__title">Create a site</h3>
  <p class="rnk-modal-head__sub">Each site belongs to one project — used for attendance and cost tagging.</p>
</div>
""",
        unsafe_allow_html=True,
    )
    pcs = [p["project_code"] for p in plist]

    submitted = False
    cancel_site = False
    with st.form("modal_form_site", clear_on_submit=False):
        st.markdown('<p class="rnk-modal-section">Site</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)
        with s1:
            sc = st.text_input(
                "Site code *",
                placeholder="S-01",
                help="Unique within your company.",
                key="ms_code",
            )
        with s2:
            sn = st.text_input(
                "Site name *",
                placeholder="Batching plant / site office",
                key="ms_name",
            )
        loc = st.text_input(
            "Location",
            placeholder="District, landmark, or chainage",
            key="ms_loc",
        )

        st.markdown('<p class="rnk-modal-section">Link</p>', unsafe_allow_html=True)
        pc = st.selectbox("Project *", pcs, key="ms_proj")

        st.markdown("<br/>", unsafe_allow_html=True)
        br = st.columns([1, 1, 1])
        with br[0]:
            submitted = st.form_submit_button("Create site", type="primary", use_container_width=True)
        with br[1]:
            cancel_site = st.form_submit_button("Cancel", use_container_width=True)

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
    if st.session_state.get(_SS_PROJ):
        _modal_add_project()

    plist = civil_store.projects_list(_cid())
    df_p = pd.DataFrame(plist)
    if df_p.empty:
        empty_state("No projects yet", "Use **Add** above to create your first project.")
    else:
        st.dataframe(df_p, use_container_width=True, hide_index=True)


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
        wid = st.text_input("Worker ID", value="W-")
        fn = st.text_input("Full name")
        pt = st.selectbox("Pay type", ["Daily", "Monthly"])
        dr = st.number_input("Daily rate", value=0.0)
        mg = st.number_input("Monthly gross", value=0.0)
        otr = st.selectbox("OT rule", rules or ["OT-STD"])
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
