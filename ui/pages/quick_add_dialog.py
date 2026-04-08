"""Shared @st.dialog for adding clients or employees (role-gated).

App users are **not** created here — use **Team → Invite** or **Add app user** from the
Create/Edit project flow (``field_ops`` invite dialog), which uses ``registry_forms.render_quick_app_user_form``."""
from __future__ import annotations

import streamlit as st

from core.roles import can_access
from services import civil_store
from ui.pages.common import INDIAN_STATES_UT, _cid
from ui.pages.form_ui import required_label, required_legend

_SS_QUICK_ADD = "_rnk_quick_add_modal_open"
_QUICK_ADD_PRESET = "_rnk_quick_add_preset"  # "client" | "employee"

# Return-to-project payload when opening Quick add from Create/Edit project (must match field_ops keys).
QADD_RETURN = "_rnk_qadd_return"
_SS_PROJ = "_rnk_open_modal_project"
_MP_VIEW = "_mp_proj_subview"
_MP_CLIENT_PRESELECT = "_mp_client_preselect"
_MP_TEAM_PRESELECT = "_mp_team_preselect"
_SS_EDIT_PROJ = "rnk_edit_project_code"
_MP_EDIT_SUBVIEW = "_mp_edit_subview"
_MP_EDIT_CLIENT_PRE = "_mp_edit_client_preselect"
_MP_EDIT_TEAM_PRE = "_mp_edit_team_preselect"


def _restore_project_after_qadd() -> None:
    """Re-open Create or Edit project after Quick add was opened from that flow (cancel/dismiss)."""
    ret = st.session_state.pop(QADD_RETURN, None)
    if not ret:
        return
    if ret.get("kind") == "create_project":
        st.session_state[_SS_PROJ] = True
        st.session_state[_MP_VIEW] = "project"
    elif ret.get("kind") == "edit_project":
        st.session_state[_SS_EDIT_PROJ] = ret["code"]
        st.session_state[_MP_EDIT_SUBVIEW] = "project"


def restore_project_after_quick_add() -> None:
    """Public: same as internal restore — used when cancelling invite-from-project (``field_ops``)."""
    _restore_project_after_qadd()


def _on_quick_add_dialog_dismiss() -> None:
    """Clear open flag when the user closes via X, ESC, or click-outside (not only Cancel)."""
    st.session_state[_SS_QUICK_ADD] = False
    st.session_state.pop(_QUICK_ADD_PRESET, None)
    _restore_project_after_qadd()


def open_quick_add_modal(preset: str | None = None) -> None:
    """Open the quick-add dialog.

    Pass ``preset`` to lock the dialog to one record type (no mode switcher):

    - ``"client"`` — client form only
    - ``"employee"`` — employee form only

    Omit ``preset`` only if you need both client and employee in one dialog (rare); prefer passing ``\"client\"`` or ``\"employee\"``.
    """
    st.session_state[_SS_QUICK_ADD] = True
    if preset in ("client", "employee"):
        st.session_state[_QUICK_ADD_PRESET] = preset
    else:
        st.session_state.pop(_QUICK_ADD_PRESET, None)


def _modes_for_preset(preset: str | None, role: str) -> list[tuple[str, str]]:
    """Modes to show: single type when ``preset`` is set; else client + employee when ``preset`` is None."""
    if preset == "client":
        if not can_access(role, "clients"):
            return []
        return [("client", "Client")]
    if preset == "employee":
        if not can_access(role, "team"):
            return []
        return [("employee", "Employee")]
    if preset is None:
        return _quick_add_modes(role)
    return []


def _quick_add_modes(role: str) -> list[tuple[str, str]]:
    """(mode_key, label) in display order."""
    out: list[tuple[str, str]] = []
    if can_access(role, "clients"):
        out.append(("client", "Client"))
    if can_access(role, "team"):
        out.append(("employee", "Employee"))
    return out


def render_quick_add_modal_if_open() -> None:
    """Call once per run from ``app.py`` after auth; shows the dialog when open."""
    if st.session_state.get(_SS_QUICK_ADD):
        _quick_add_modal()


@st.dialog("Create record", width="large", on_dismiss=_on_quick_add_dialog_dismiss)
def _quick_add_modal() -> None:
    u = st.session_state.get("user") or {}
    role = u.get("role", "viewer")
    cid = _cid()

    preset = st.session_state.get(_QUICK_ADD_PRESET)
    modes = _modes_for_preset(preset, role)

    if not modes:
        st.warning("You do not have permission to create clients or employees here.")
        if st.button("Close", key="qadd_close_noperm", use_container_width=True):
            st.session_state[_SS_QUICK_ADD] = False
            st.session_state.pop(_QUICK_ADD_PRESET, None)
            _restore_project_after_qadd()
            st.rerun()
        return

    idx_default = 0

    codes = [m[0] for m in modes]

    def _fmt(c: str) -> str:
        return next(lab for k, lab in modes if k == c)

    if len(modes) == 1:
        mode = modes[0][0]
        st.caption(_fmt(mode))
    else:
        mode = st.radio(
            "Record type",
            codes,
            index=idx_default,
            format_func=_fmt,
            horizontal=True,
            key="qadd_mode_radio",
        )

    st.divider()

    if mode == "client":
        _form_client(cid)
    else:
        _form_employee(cid)


def _close_quick_add_modal() -> None:
    st.session_state[_SS_QUICK_ADD] = False
    st.session_state.pop(_QUICK_ADD_PRESET, None)


def _form_client(cid: str) -> None:
    st.markdown('<p class="rnk-modal-section">Client</p>', unsafe_allow_html=True)
    st.caption("Directory record for billing and projects — same data as Clients → Add client (compact).")
    submitted = False
    cancel = False
    with st.form("qadd_form_client"):
        required_legend()
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            code = st.text_input("Client code (optional)", placeholder="e.g. CLT-NHAI", key="qadd_c_code")
            required_label("Display name")
            name = st.text_input(
                "Display name *",
                placeholder="Shown on invoices & projects",
                label_visibility="collapsed",
                key="qadd_c_name",
            )
        with c2:
            legal = st.text_input("Legal / registered name", key="qadd_c_legal")
            pan = st.text_input("PAN", placeholder="AAAAA0000A", key="qadd_c_pan")

        c3, c4 = st.columns(2, gap="medium")
        with c3:
            cp = st.text_input("Contact person", key="qadd_c_cp")
            ph = st.text_input("Phone", key="qadd_c_ph")
        with c4:
            em = st.text_input("Email", key="qadd_c_em")
            gst = st.text_input("GSTIN", key="qadd_c_gst")

        st.markdown('<p class="rnk-modal-section">Location</p>', unsafe_allow_html=True)
        a1, a2 = st.columns(2, gap="medium")
        with a1:
            addr = st.text_input("Address line 1", key="qadd_c_addr")
        with a2:
            addr2 = st.text_input("Address line 2 (optional)", key="qadd_c_addr2")
        c5, c6, c7 = st.columns(3)
        with c5:
            city = st.text_input("City / town", key="qadd_c_city")
        with c6:
            st_sel = st.selectbox("State / UT", INDIAN_STATES_UT, key="qadd_c_state_sel")
            st_free = st.text_input("State (free text if not listed)", key="qadd_c_state_txt")
        with c7:
            pin = st.text_input("PIN code", key="qadd_c_pin")
        country = st.text_input("Country", value="India", key="qadd_c_country")
        ptd = st.number_input("Payment terms (days)", min_value=0, max_value=365, value=30, key="qadd_c_ptd")
        notes = st.text_area("Internal notes", height=72, key="qadd_c_notes")

        st.divider()
        _a, _b, _c = st.columns([3, 1, 1], gap="small")
        with _b:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        with _c:
            submitted = st.form_submit_button("Save client", type="primary", use_container_width=True)

    if cancel:
        _restore_project_after_qadd()
        _close_quick_add_modal()
        st.rerun()
    if submitted:
        if not (name or "").strip():
            st.error("Display name is required.")
            return
        state_val = (st_free or "").strip() or (st_sel or "").strip() or None
        try:
            civil_store.client_add(
                cid,
                name.strip(),
                client_code=code or None,
                legal_name=legal or None,
                pan=pan or None,
                contact_person=cp or None,
                phone=ph or None,
                email=em or None,
                gstin=gst or None,
                address=addr or None,
                address_line2=addr2 or None,
                city=city or None,
                state=state_val,
                pincode=pin or None,
                country=country or None,
                payment_terms_days=int(ptd),
                notes=notes or None,
            )
            ret = st.session_state.pop(QADD_RETURN, None)
            _close_quick_add_modal()
            if ret and ret.get("kind") == "create_project" and ret.get("target") == "client":
                st.session_state[_SS_PROJ] = True
                st.session_state[_MP_VIEW] = "project"
                st.session_state[_MP_CLIENT_PRESELECT] = name.strip()
                st.toast("Client saved.")
            elif ret and ret.get("kind") == "edit_project" and ret.get("target") == "client":
                st.session_state[_SS_EDIT_PROJ] = ret["code"]
                st.session_state[_MP_EDIT_SUBVIEW] = "project"
                st.session_state[_MP_EDIT_CLIENT_PRE] = (ret["safe"], name.strip())
                st.toast("Client saved.")
            else:
                st.session_state["rnk_flash_success"] = "Client saved."
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


def _form_employee(cid: str) -> None:
    st.markdown('<p class="rnk-modal-section">Employee</p>', unsafe_allow_html=True)
    st.caption("Directory only — no login until you invite an app user with the same email (optional).")
    submitted = False
    cancel = False
    with st.form("qadd_form_employee"):
        required_legend()
        n1, n2 = st.columns(2, gap="medium")
        with n1:
            required_label("Employee code")
            code = st.text_input("Employee code", value="EMP-", label_visibility="collapsed", key="qadd_e_code")
        with n2:
            required_label("Full name")
            name = st.text_input("Full name", label_visibility="collapsed", key="qadd_e_name")
        n3, n4 = st.columns(2, gap="medium")
        with n3:
            dept = st.text_input("Department", key="qadd_e_dept")
        with n4:
            title = st.text_input("Job title", key="qadd_e_title")
        ph = st.text_input("Phone", key="qadd_e_phone")
        em = st.text_input("Email (optional)", key="qadd_e_email")
        st.divider()
        _a, _b, _c = st.columns([3, 1, 1], gap="small")
        with _b:
            cancel = st.form_submit_button("Cancel", use_container_width=True)
        with _c:
            submitted = st.form_submit_button("Add employee", type="primary", use_container_width=True)

    if cancel:
        _restore_project_after_qadd()
        _close_quick_add_modal()
        st.rerun()
    if submitted:
        try:
            civil_store.employee_add(
                cid,
                code or "",
                name or "",
                department=dept or None,
                role_title=title or None,
                phone=ph or None,
                email=em or None,
            )
            st.session_state.pop(QADD_RETURN, None)
            _close_quick_add_modal()
            st.session_state["rnk_flash_success"] = "Employee added."
            st.rerun()
        except Exception as ex:
            st.error(str(ex))
