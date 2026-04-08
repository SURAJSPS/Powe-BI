"""Projects, sites, workers, and creation modals."""
from __future__ import annotations

import re

import streamlit as st
import pandas as pd

from core.roles import ROLE_LABELS
from services import auth_service, civil_store
from ui.pages.common import (
    dataframe_for_records,
    RNK_PENDING_DELETE,
    _cid,
    _fmt_datetime,
    confirm_delete_dialog,
    queue_delete_confirmation,
)
from ui.pages.form_ui import required_label, required_legend
from ui.pages.quick_add_dialog import QADD_RETURN, open_quick_add_modal, restore_project_after_quick_add
from ui.pages.registry_forms import render_quick_app_user_form
from ui.theme import empty_state, page_header

_SS_PROJ = "_rnk_open_modal_project"
_SS_SITE = "_rnk_open_modal_site"
_SS_WORKER = "_rnk_open_modal_worker"
_MP_TEAM_ORDER = "_mp_proj_team_order"
_MP_VIEW = "_mp_proj_subview"  # "project" while Create project modal is open
_MP_CLIENT_PRESELECT = "_mp_client_preselect"
_MP_TEAM_PRESELECT = "_mp_team_preselect"
_MP_EDIT_SUBVIEW = "_mp_edit_subview"  # "project" while Edit project modal is open
_MP_EDIT_CLIENT_PRE = "_mp_edit_client_preselect"  # tuple[str, str]: (safe, name)
_MP_EDIT_TEAM_PRE = "_mp_edit_team_preselect"  # tuple[str, str]: (safe, label)
_SS_EDIT_PROJ = "rnk_edit_project_code"
_SS_PROJ_INVITE_USER = "_rnk_proj_invite_user"  # Add app user from Create/Edit project (not Quick add)
# Strip ＋ Add app user… from multiselect on the *next* run (cannot set widget key after widget exists).
_MP_TEAM_PENDING_CLEAN = "_mp_team_pending_clean"
_MP_EDIT_TEAM_PENDING_CLEAN = "_mp_edit_team_pending_clean"  # tuple[str, list[str]]: (safe, labels)

# Dropdown tokens: pick these to open add sub-views inside the same dialog (no extra buttons).
PLACEHOLDER_CLIENT = "— Select a client —"
PLACEHOLDER_CLIENT_EMPTY = "— Select or add —"
ADD_CLIENT_TOKEN = "＋ Add new client…"
ADD_USER_TOKEN = "＋ Add app user…"


def _safe_key_fragment(s: str) -> str:
    return re.sub(r"\W+", "_", (s or ""))[:48] or "x"


def _request_edit_project(pc: str) -> None:
    st.session_state[_SS_EDIT_PROJ] = pc
    st.session_state[_MP_EDIT_SUBVIEW] = "project"


def _request_delete_project(pc: str) -> None:
    queue_delete_confirmation(
        kind="project",
        message=(
            f'Are you sure you want to delete project **{pc}**? '
            "Sites linked to this project will be removed. This cannot be undone."
        ),
        success_msg="Project deleted.",
        code=pc,
    )


def _edit_team_order_key(safe: str) -> str:
    return f"_rnk_edit_mp_team_order_{safe}"


def _sync_edit_project_team_order(raw: list[str], safe: str) -> None:
    k = _edit_team_order_key(safe)
    raw_set = set(raw)
    order = [x for x in st.session_state.get(k, []) if x in raw_set]
    seen = set(order)
    for x in raw:
        if x not in seen:
            order.append(x)
            seen.add(x)
    st.session_state[k] = order


def _sync_project_team_order(raw: list[str]) -> None:
    """Keep selection order: first in list = project manager.

    Must use the multiselect *return value* — inside ``st.form``, ``session_state["mp_team"]``
    is not always updated until after the widget returns, so reading it in sync was wrong.
    """
    raw_set = set(raw)
    order = [x for x in st.session_state.get(_MP_TEAM_ORDER, []) if x in raw_set]
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


@st.dialog("Project", width="large")
def _modal_add_project() -> None:
    """Modal: create a project with optional PM, team, and office staff links."""
    cid = _cid()
    user = st.session_state.get("user") or {}
    is_admin = user.get("role") == "company_admin"

    users = auth_service.list_users(cid)
    emps = civil_store.employees_list(cid)
    user_map = {_user_pick_label(u): u["user_id"] for u in users}
    user_labels = sorted(user_map.keys(), key=str.lower)

    emp_map = {_employee_pick_label(e): str(e["_id"]) for e in emps}
    emp_labels = sorted(emp_map.keys(), key=str.lower)

    clients = civil_store.clients_list(cid)
    client_names = sorted(
        {(c.get("name") or "").strip() for c in clients if (c.get("name") or "").strip()}
    )

    # Not using st.form: widgets inside a form do not update session_state until submit,
    # so "＋ Add new client…" would never open the sub-view until Create.
    
    st.markdown('<p class="rnk-modal-section">Identification</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        required_label("Project code")
        code = st.text_input("Project code *", placeholder="PRJ-001", key="mp_code", label_visibility="collapsed")
    with c2:
        required_label("Project name")
        name = st.text_input("Project name *", placeholder="e.g. NH package / Block A", key="mp_name", label_visibility="collapsed")

    st.markdown('<p class="rnk-modal-section">Client</p>', unsafe_allow_html=True)
    pre = st.session_state.pop(_MP_CLIENT_PRESELECT, None)
    if client_names:
        client_opts = [PLACEHOLDER_CLIENT] + client_names + [ADD_CLIENT_TOKEN]
        if pre and pre in client_names:
            st.session_state["mp_client_sel"] = pre
        elif "mp_client_sel" not in st.session_state:
            st.session_state["mp_client_sel"] = PLACEHOLDER_CLIENT
        required_label("Client")
        st.selectbox(
            "Client *",
            client_opts,
            key="mp_client_sel",
            label_visibility="collapsed",
        )
    else:
        client_opts = [PLACEHOLDER_CLIENT_EMPTY, ADD_CLIENT_TOKEN]
        if "mp_client_sel" not in st.session_state:
            st.session_state["mp_client_sel"] = PLACEHOLDER_CLIENT_EMPTY
        required_label("Client")
        st.selectbox(
            "Client *",
            client_opts,
            key="mp_client_sel",
            label_visibility="collapsed",
        )
    st.caption(
        "Pick **＋ Add new client** to open **Create record** (full client form); you return here with that client selected."
    )
    if st.session_state.get("mp_client_sel") == ADD_CLIENT_TOKEN:
        st.session_state.pop("mp_client_sel", None)
        st.session_state[QADD_RETURN] = {"kind": "create_project", "target": "client"}
        st.session_state[_SS_PROJ] = False
        st.session_state.pop(_MP_VIEW, None)
        open_quick_add_modal("client")
        st.rerun()

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
    _pending_clean = st.session_state.pop(_MP_TEAM_PENDING_CLEAN, None)
    if isinstance(_pending_clean, list):
        st.session_state["mp_team"] = list(_pending_clean)
        _sync_project_team_order(list(_pending_clean))
    team_pre = st.session_state.pop(_MP_TEAM_PRESELECT, None)
    if team_pre and team_pre in user_labels:
        cur = list(st.session_state.get("mp_team") or [])
        if team_pre not in cur:
            cur.append(team_pre)
        st.session_state["mp_team"] = cur
        _sync_project_team_order(cur)

    team_pick: list[str] = []
    if user_labels or is_admin:
        team_options = list(user_labels)
        if is_admin:
            team_options = team_options + [ADD_USER_TOKEN]
        team_pick = st.multiselect(
            "Team members",
            options=team_options,
            key="mp_team",
        )
        cleaned = [x for x in team_pick if x != ADD_USER_TOKEN]
        _sync_project_team_order(cleaned)
        if is_admin and ADD_USER_TOKEN in team_pick:
            st.session_state[_MP_TEAM_PENDING_CLEAN] = cleaned
            st.session_state[QADD_RETURN] = {"kind": "create_project", "target": "team_user"}
            st.session_state[_SS_PROJ] = False
            st.session_state.pop(_MP_VIEW, None)
            st.session_state[_SS_PROJ_INVITE_USER] = True
            st.rerun()
    else:
        st.caption("No users in this company yet.")
    st.caption(
        "First selected member is the project manager."
        + (
            f" Company admins: pick **{ADD_USER_TOKEN}** to open **Add app user** and add a login; you return here with them selected."
            if is_admin
            else ""
        )
    )

    emp_pick = st.multiselect("Employees", options=emp_labels, key="mp_emps") if emp_labels else []

    st.divider()
    _sp, _ca, _cr = st.columns([3, 1, 1], gap="small")
    with _ca:
        cancel_in = st.button("Cancel", use_container_width=True, key="mp_btn_cancel")
    with _cr:
        submitted = st.button("Create", type="primary", use_container_width=True, key="mp_btn_create")

    if cancel_in:
        st.session_state[_SS_PROJ] = False
        st.session_state.pop(_MP_VIEW, None)
        st.session_state.pop("mp_team", None)
        st.session_state.pop(_MP_TEAM_ORDER, None)
        st.session_state.pop(_MP_TEAM_PENDING_CLEAN, None)
        st.rerun()

    if submitted:
        code_t = (code or "").strip()
        name_t = (name or "").strip()
        client_t = (st.session_state.get("mp_client_sel") or "").strip()
        _bad_client = (
            "",
            PLACEHOLDER_CLIENT,
            PLACEHOLDER_CLIENT_EMPTY,
            ADD_CLIENT_TOKEN,
        )
        if not code_t or not name_t:
            st.error("Please enter both project code and project name.")
            return
        if client_t in _bad_client:
            st.error(
                "Choose a client from the list, or select **＋ Add new client** to register one first."
            )
            return
        team_pick = [
            x for x in (st.session_state.get("mp_team") or []) if x != ADD_USER_TOKEN
        ]
        _sync_project_team_order(list(team_pick))
        order = list(st.session_state.get(_MP_TEAM_ORDER) or [])
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
            st.session_state.pop(_MP_VIEW, None)
            st.session_state.pop("mp_team", None)
            st.session_state.pop(_MP_TEAM_ORDER, None)
            st.session_state.pop(_MP_TEAM_PENDING_CLEAN, None)
            st.success("Project created.")
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


@st.dialog("Project", width="large")
def _modal_edit_project() -> None:
    """Modal: update an existing project (code is fixed)."""
    code = st.session_state.get(_SS_EDIT_PROJ)
    if not code:
        return
    cid = _cid()
    proj = civil_store.project_get(cid, code)
    safe = _safe_key_fragment(code)

    if st.session_state.get("_rnk_edit_last_code") != code:
        st.session_state["_rnk_edit_last_code"] = code
        st.session_state[_MP_EDIT_SUBVIEW] = "project"
        for k in list(st.session_state.keys()):
            if isinstance(k, str) and k.startswith("edit_mp") and k.endswith(f"_{safe}"):
                st.session_state.pop(k, None)
        st.session_state.pop(_edit_team_order_key(safe), None)

    if not proj:
        st.error("Project not found.")
        if st.button("Close", key=f"edit_proj_nf_{safe}", use_container_width=True):
            st.session_state.pop(_SS_EDIT_PROJ, None)
            st.rerun()
        return

    user = st.session_state.get("user") or {}
    is_admin = user.get("role") == "company_admin"
    users = auth_service.list_users(cid)
    emps = civil_store.employees_list(cid)
    user_map = {_user_pick_label(u): u["user_id"] for u in users}
    user_labels = sorted(user_map.keys(), key=str.lower)
    user_map_rev = {u["user_id"]: _user_pick_label(u) for u in users}

    emp_map = {_employee_pick_label(e): str(e["_id"]) for e in emps}
    emp_labels = sorted(emp_map.keys(), key=str.lower)

    clients = civil_store.clients_list(cid)
    client_names = sorted(
        {(c.get("name") or "").strip() for c in clients if (c.get("name") or "").strip()}
    )
    cn = (proj.get("client_name") or "").strip()
    if cn and cn not in client_names:
        client_names = sorted(set(client_names) | {cn})

    team_ids = list(proj.get("team_user_ids") or [])
    pm_uid = proj.get("project_manager_user_id")
    order_ids: list[str] = []
    if pm_uid and pm_uid in team_ids:
        order_ids.append(pm_uid)
    for uid in team_ids:
        if uid not in order_ids:
            order_ids.append(uid)
    default_team_labels = [user_map_rev[uid] for uid in order_ids if uid in user_map_rev]

    emp_ids_stored = list(proj.get("linked_employee_ids") or [])
    default_emp_labels = [lb for lb, eid in emp_map.items() if eid in emp_ids_stored]

    # Not using st.form so client/team "＋ Add …" picks update session_state immediately (see create modal).
    st.caption(f"Project code: `{code}`")
    st.subheader("Edit project")
    st.markdown('<p class="rnk-modal-section">Identification</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        name = st.text_input(
            "Project name *",
            value=(proj.get("name") or "").strip(),
            placeholder="e.g. NH package / Block A",
            key=f"edit_mp_name_{safe}",
        )
    with c2:
        pass

    st.markdown('<p class="rnk-modal-section">Client</p>', unsafe_allow_html=True)
    pre = st.session_state.pop(_MP_EDIT_CLIENT_PRE, None)
    _ek = f"edit_mp_client_sel_{safe}"
    if (
        isinstance(pre, tuple)
        and len(pre) == 2
        and pre[0] == safe
        and pre[1] in client_names
    ):
        st.session_state[_ek] = pre[1]
    elif _ek not in st.session_state and cn in client_names:
        st.session_state[_ek] = cn
    if client_names:
        client_opts = [PLACEHOLDER_CLIENT] + client_names + [ADD_CLIENT_TOKEN]
        if _ek not in st.session_state:
            st.session_state[_ek] = cn if cn in client_names else PLACEHOLDER_CLIENT
        required_label("Client")
        st.selectbox("Client *", client_opts, key=_ek, label_visibility="collapsed")
    else:
        client_opts = [PLACEHOLDER_CLIENT_EMPTY, ADD_CLIENT_TOKEN]
        if _ek not in st.session_state:
            st.session_state[_ek] = PLACEHOLDER_CLIENT_EMPTY
        required_label("Client")
        st.selectbox("Client *", client_opts, key=_ek, label_visibility="collapsed")
    st.caption(
        "Pick **＋ Add new client** to open **Create record** (full client form); you return here with that client selected."
    )
    if st.session_state.get(_ek) == ADD_CLIENT_TOKEN:
        st.session_state.pop(_ek, None)
        st.session_state[QADD_RETURN] = {
            "kind": "edit_project",
            "code": code,
            "safe": safe,
            "target": "client",
        }
        st.session_state.pop(_SS_EDIT_PROJ, None)
        open_quick_add_modal("client")
        st.rerun()

    st.markdown('<p class="rnk-modal-section">Planning</p>', unsafe_allow_html=True)
    r2a, r2b, r2c = st.columns(3, gap="medium")
    statuses = ["Planning", "Active", "On Hold", "Completed", "Archived"]
    st_i = statuses.index(proj.get("status")) if proj.get("status") in statuses else 0
    prs = ["Normal", "High", "Critical"]
    pr_i = prs.index(proj.get("priority")) if proj.get("priority") in prs else 0
    with r2a:
        status = st.selectbox("Status", statuses, index=st_i, key=f"edit_mp_status_{safe}")
    with r2b:
        priority = st.selectbox("Priority", prs, index=pr_i, key=f"edit_mp_priority_{safe}")
    with r2c:
        budget = st.number_input(
            "Budget (₹)",
            min_value=0.0,
            value=float(proj.get("budget") or 0.0),
            step=50_000.0,
            format="%.0f",
            key=f"edit_mp_budget_{safe}",
        )
    desc = st.text_area(
        "Description (optional)",
        value=(proj.get("description") or "").strip(),
        placeholder="Scope, notes…",
        height=88,
        key=f"edit_mp_desc_{safe}",
    )

    st.markdown('<p class="rnk-modal-section">Team</p>', unsafe_allow_html=True)
    team_key = f"edit_mp_team_{safe}"
    _ed_pending = st.session_state.pop(_MP_EDIT_TEAM_PENDING_CLEAN, None)
    if (
        isinstance(_ed_pending, tuple)
        and len(_ed_pending) == 2
        and _ed_pending[0] == safe
        and isinstance(_ed_pending[1], list)
    ):
        st.session_state[team_key] = list(_ed_pending[1])
        _sync_edit_project_team_order(list(_ed_pending[1]), safe)
    team_pre = st.session_state.pop(_MP_EDIT_TEAM_PRE, None)
    if (
        isinstance(team_pre, tuple)
        and len(team_pre) == 2
        and team_pre[0] == safe
        and team_pre[1] in user_labels
    ):
        cur = list(st.session_state.get(team_key) or [])
        if team_pre[1] not in cur:
            cur.append(team_pre[1])
        st.session_state[team_key] = cur
        _sync_edit_project_team_order(cur, safe)

    team_pick: list[str] = []
    if user_labels or is_admin:
        if team_key not in st.session_state:
            st.session_state[team_key] = default_team_labels
        team_options = list(user_labels)
        if is_admin:
            team_options = team_options + [ADD_USER_TOKEN]
        team_pick = st.multiselect(
            "Team members",
            options=team_options,
            key=team_key,
        )
        cleaned = [x for x in team_pick if x != ADD_USER_TOKEN]
        _sync_edit_project_team_order(cleaned, safe)
        if is_admin and ADD_USER_TOKEN in team_pick:
            st.session_state[_MP_EDIT_TEAM_PENDING_CLEAN] = (safe, cleaned)
            st.session_state[QADD_RETURN] = {
                "kind": "edit_project",
                "code": code,
                "safe": safe,
                "target": "team_user",
            }
            st.session_state.pop(_SS_EDIT_PROJ, None)
            st.session_state[_SS_PROJ_INVITE_USER] = True
            st.rerun()
    else:
        st.caption("No users in this company yet.")
    

    emp_key = f"edit_mp_emps_{safe}"
    if emp_key not in st.session_state:
        st.session_state[emp_key] = default_emp_labels
    emp_pick = st.multiselect("Employees", options=emp_labels, key=emp_key) if emp_labels else []

    st.divider()
    st.markdown('<p class="rnk-modal-section">Danger zone</p>', unsafe_allow_html=True)
    if st.button(
        "Delete project",
        type="tertiary",
        key=f"edit_mp_delete_{safe}",
        help="Remove this project and its sites (confirmation required)",
    ):
        st.session_state.pop(_SS_EDIT_PROJ, None)
        st.session_state.pop(_MP_EDIT_SUBVIEW, None)
        _request_delete_project(code)
        st.rerun()

    st.divider()
    _sp, _ca, _cr = st.columns([3, 1, 1], gap="small")
    with _ca:
        cancel_edit = st.button("Cancel", use_container_width=True, key=f"edit_mp_cancel_{safe}")
    with _cr:
        submitted = st.button("Save changes", type="primary", use_container_width=True, key=f"edit_mp_save_{safe}")

    if cancel_edit:
        st.session_state.pop(_SS_EDIT_PROJ, None)
        st.session_state.pop(_MP_EDIT_SUBVIEW, None)
        st.session_state.pop(_MP_EDIT_TEAM_PENDING_CLEAN, None)
        st.rerun()

    if submitted:
        name_t = (name or "").strip()
        client_t = (st.session_state.get(f"edit_mp_client_sel_{safe}") or "").strip()
        _bad_client = (
            "",
            PLACEHOLDER_CLIENT,
            PLACEHOLDER_CLIENT_EMPTY,
            ADD_CLIENT_TOKEN,
        )
        if not name_t:
            st.error("Please enter the project name.")
            return
        if client_t in _bad_client:
            st.error(
                "Choose a client from the list, or select **＋ Add new client** to register one first."
            )
            return
        team_pick = [
            x
            for x in (st.session_state.get(f"edit_mp_team_{safe}") or [])
            if x != ADD_USER_TOKEN
        ]
        _sync_edit_project_team_order(list(team_pick), safe)
        order = list(st.session_state.get(_edit_team_order_key(safe)) or [])
        if not order and team_pick:
            order = list(team_pick)
        team_ids_new = [user_map[lb] for lb in order if lb in user_map]
        pm_uid_new: str | None = user_map.get(order[0]) if order else None

        emp_ids: list[str] = []
        for lb in emp_pick:
            eid = emp_map.get(lb)
            if eid and eid not in emp_ids:
                emp_ids.append(eid)

        desc_t = (desc or "").strip() or None
        try:
            civil_store.project_update(
                cid,
                code,
                {
                    "name": name_t,
                    "client_name": client_t,
                    "status": status,
                    "budget": float(budget),
                    "priority": priority,
                    "description": desc_t,
                    "project_manager_user_id": pm_uid_new,
                    "team_user_ids": team_ids_new,
                    "linked_employee_ids": emp_ids,
                },
            )
            st.session_state.pop(_SS_EDIT_PROJ, None)
            st.session_state.pop(_MP_EDIT_SUBVIEW, None)
            st.session_state["rnk_flash_success"] = "Project updated."
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


@st.dialog("Create Site", width="large")
def _modal_add_site() -> None:
    """Modal: create a site linked to a project."""
    plist = civil_store.projects_list(_cid())
    if not plist:
        st.warning("Add a project first.")
        if st.button("Close", key="site_modal_close_empty", use_container_width=True):
            st.session_state[_SS_SITE] = False
            st.rerun()
        return

    pcs = [p["project_code"] for p in plist]

    submitted = False
    cancel_site = False
    with st.form("modal_form_site", clear_on_submit=False):
        required_legend()
        st.markdown('<p class="rnk-modal-section">Site</p>', unsafe_allow_html=True)
        s1, s2 = st.columns(2, gap="medium")
        with s1:
            required_label("Site code")
            sc = st.text_input("Site code *", placeholder="S-01", key="ms_code", label_visibility="collapsed")
        with s2:
            required_label("Site name")
            sn = st.text_input("Site name *", placeholder="Batching plant / site office", key="ms_name", label_visibility="collapsed")
        loc = st.text_input("Location", placeholder="District, landmark…", key="ms_loc")

        st.markdown('<p class="rnk-modal-section">Project</p>', unsafe_allow_html=True)
        required_label("Project")
        pc = st.selectbox("Project *", pcs, key="ms_proj", label_visibility="collapsed")

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


def _on_proj_invite_user_dismiss() -> None:
    st.session_state[_SS_PROJ_INVITE_USER] = False
    restore_project_after_quick_add()


@st.dialog("Add app user", width="large", on_dismiss=_on_proj_invite_user_dismiss)
def _modal_invite_user_for_project() -> None:
    """Invite login user from Create/Edit project — uses ``registry_forms.render_quick_app_user_form`` (not Quick add)."""
    cid = _cid()

    def _back() -> None:
        st.session_state[_SS_PROJ_INVITE_USER] = False
        restore_project_after_quick_add()
        st.rerun()

    def _saved(label: str) -> None:
        ret = st.session_state.pop(QADD_RETURN, None)
        st.session_state[_SS_PROJ_INVITE_USER] = False
        if ret and ret.get("kind") == "create_project" and ret.get("target") == "team_user":
            st.session_state[_SS_PROJ] = True
            st.session_state[_MP_VIEW] = "project"
            # Pending clean was applied on reopen; keep pre-tick selections, then add new user.
            st.session_state[_MP_TEAM_PRESELECT] = label
            st.toast("User added.")
        elif ret and ret.get("kind") == "edit_project" and ret.get("target") == "team_user":
            st.session_state[_SS_EDIT_PROJ] = ret["code"]
            st.session_state[_MP_EDIT_SUBVIEW] = "project"
            st.session_state[_MP_EDIT_TEAM_PRE] = (ret["safe"], label)
            st.toast("User added.")
        else:
            st.session_state["rnk_flash_success"] = "User created."
        st.rerun()

    render_quick_app_user_form(
        company_id=cid,
        form_key="proj_invite_user",
        key_prefix="piu",
        caption="Creates a login for this company. Share the email and temporary password securely.",
        on_back=_back,
        on_saved=_saved,
    )


def render_invite_user_modal_if_open() -> None:
    """Call from ``app.py`` after auth; shows invite dialog when opened from project create/edit."""
    if st.session_state.get(_SS_PROJ_INVITE_USER):
        _modal_invite_user_for_project()


def page_projects(u: dict) -> None:
    """Projects register only — sites have their own page."""
    col_title, col_add = st.columns([6, 1])
    with col_title:
        page_header("Projects")
    with col_add:
        st.markdown('<div style="min-height:2.6rem;"></div>', unsafe_allow_html=True)
        if st.button("Add", type="primary", key="open_modal_project", help="Create a new project"):
            st.session_state[_SS_PROJ] = True
            st.session_state[_MP_VIEW] = "project"
            st.session_state.pop("mp_client_sel", None)
            st.session_state.pop("mp_team", None)
            st.session_state.pop(_MP_TEAM_ORDER, None)
            st.session_state.pop(_MP_TEAM_PENDING_CLEAN, None)
            st.session_state.pop("mp_pm", None)
    if st.session_state.get(_SS_PROJ):
        _modal_add_project()
    if st.session_state.get(_SS_EDIT_PROJ):
        _modal_edit_project()
    if st.session_state.get(RNK_PENDING_DELETE):
        confirm_delete_dialog()

    plist = civil_store.projects_list(_cid())
    if not plist:
        empty_state("No projects yet", "")
    else:
        _proj_extra_drop = frozenset(
            {
                "project_manager_user_id",
                "team_user_ids",
                "linked_employee_ids",
                "description",
            }
        )
        df = dataframe_for_records(plist, extra_drop=_proj_extra_drop)
        if not df.empty:
            if "updated_at" in df.columns:
                df = df.copy()
                df["updated_at"] = df["updated_at"].apply(
                    lambda x: _fmt_datetime(x) if pd.notna(x) and x is not None else "—"
                )
            if "created_at" in df.columns:
                df = df.drop(columns=["created_at"])
            _pref = [
                "name",
                "project_code",
                "client_name",
                "status",
                "priority",
                "budget",
                "updated_at",
            ]
            _cols = [c for c in _pref if c in df.columns] + [c for c in df.columns if c not in _pref]
            df = df[_cols]
            _rn = {
                "name": "Project",
                "project_code": "Code",
                "client_name": "Client",
                "status": "Status",
                "priority": "Priority",
                "budget": "Budget (₹)",
                "updated_at": "Last updated",
            }
            df = df.rename(columns={k: v for k, v in _rn.items() if k in df.columns})

        _cc: dict = {}
        if "Budget (₹)" in df.columns:
            _cc["Budget (₹)"] = st.column_config.NumberColumn(
                "Budget (₹)",
                format="₹%d",
                min_value=0,
            )
        if "Status" in df.columns:
            _cc["Status"] = st.column_config.TextColumn("Status")
        if "Priority" in df.columns:
            _cc["Priority"] = st.column_config.TextColumn("Priority")

        _n = len(df)
        _h = min(520, 48 + _n * 36) if _n else 120
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=_h,
            column_config=_cc or None,
        )

        _codes = [(p.get("project_code") or "").strip() for p in plist if (p.get("project_code") or "").strip()]
        if _codes:

            def _proj_pick_label(c: str) -> str:
                row = next((x for x in plist if (x.get("project_code") or "").strip() == c), None)
                if not row:
                    return c
                nm = (row.get("name") or "").strip() or "—"
                return f"{nm} · {c}"

            _e1, _e2 = st.columns([5, 1], gap="small")
            with _e1:
                st.selectbox(
                    "Project",
                    options=_codes,
                    format_func=_proj_pick_label,
                    key="proj_page_edit_pick",
                    label_visibility="collapsed",
                )
            with _e2:
                if st.button("Edit", type="primary", key="proj_page_edit_btn", use_container_width=True):
                    _request_edit_project(st.session_state["proj_page_edit_pick"])


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
    df_s = dataframe_for_records(slist, extra_drop=frozenset({"project_id"}))
    if df_s.empty:
        empty_state("No sites yet", "Create a project first, then use **Add** to register a site.")
    else:
        st.dataframe(df_s, use_container_width=True, hide_index=True)


@st.dialog("Add Worker", width="large")
def _modal_add_worker() -> None:
    rules = [r["rule_id"] for r in civil_store.ot_rules_list(_cid())]
    submitted = False
    cancel_w = False
    with st.form("modal_form_worker", clear_on_submit=False):
        required_legend()
        st.markdown('<p class="rnk-modal-section">Identification</p>', unsafe_allow_html=True)
        w1, w2 = st.columns(2, gap="medium")
        with w1:
            required_label("Worker ID")
            wid = st.text_input("Worker ID", value="W-", label_visibility="collapsed", key="mw_wid")
        with w2:
            required_label("Full name")
            fn = st.text_input("Full name", label_visibility="collapsed", key="mw_fn")
        st.markdown('<p class="rnk-modal-section">Pay and OT</p>', unsafe_allow_html=True)
        w3, w4 = st.columns(2, gap="medium")
        with w3:
            pt = st.selectbox("Pay type", ["Daily", "Monthly"], key="mw_pt")
        with w4:
            otr = st.selectbox("OT rule", rules or ["OT-STD"], key="mw_otr")
        w5, w6 = st.columns(2, gap="medium")
        with w5:
            dr = st.number_input("Daily rate", value=0.0, key="mw_dr")
        with w6:
            mg = st.number_input("Monthly gross", value=0.0, key="mw_mg")
        st.divider()
        _wa, _wb, _wc = st.columns([3, 1, 1], gap="small")
        with _wb:
            cancel_w = st.form_submit_button("Cancel", use_container_width=True)
        with _wc:
            submitted = st.form_submit_button("Save worker", type="primary", use_container_width=True)

    if cancel_w:
        st.session_state[_SS_WORKER] = False
        st.rerun()

    if submitted:
        wid_t = (wid or "").strip()
        fn_t = (fn or "").strip()
        if not wid_t or not fn_t:
            st.error("Please enter worker ID and full name.")
            return
        try:
            civil_store.worker_add(
                _cid(),
                {
                    "worker_id": wid_t,
                    "full_name": fn_t,
                    "pay_type": pt,
                    "daily_rate": dr if pt == "Daily" else None,
                    "monthly_gross": mg if pt == "Monthly" else None,
                    "ot_rule_id": otr,
                    "active": True,
                },
            )
            st.session_state[_SS_WORKER] = False
            st.session_state["rnk_flash_success"] = "Worker added."
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


def page_workers(u: dict) -> None:
    col_title, col_add = st.columns([6, 1])
    with col_title:
        page_header(
            "Workers",
            "Register site labour — used for attendance and payroll.",
            eyebrow="Field",
        )
    with col_add:
        st.markdown('<div style="min-height:2.6rem;"></div>', unsafe_allow_html=True)
        if st.button("Add", type="primary", key="open_modal_worker", help="Register a worker"):
            st.session_state[_SS_WORKER] = True
    if st.session_state.get(_SS_WORKER):
        _modal_add_worker()

    wlist = civil_store.workers_list(_cid())
    df_w = dataframe_for_records(wlist)
    if df_w.empty:
        empty_state("No workers", "Use **Add** above to register your first worker.")
    else:
        st.dataframe(df_w, use_container_width=True, hide_index=True)
