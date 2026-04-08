"""Team, app users, and employee directory."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from services import auth_service, civil_store
from ui.pages.common import _cid, dataframe_for_records
from ui.pages.quick_add_dialog import open_quick_add_modal
from ui.pages.registry_forms import render_quick_app_user_form
from ui.theme import empty_state

_SS_TEAM_INVITE = "_rnk_team_invite_modal_open"


def _on_team_invite_dismiss() -> None:
    st.session_state[_SS_TEAM_INVITE] = False


@st.dialog("Add app user", width="large", on_dismiss=_on_team_invite_dismiss)
def _team_invite_dialog() -> None:
    cid = _cid()

    def _back() -> None:
        st.session_state[_SS_TEAM_INVITE] = False
        st.rerun()

    def _saved(_label: str) -> None:
        st.session_state[_SS_TEAM_INVITE] = False
        st.session_state["rnk_flash_success"] = "User created."
        st.rerun()

    render_quick_app_user_form(
        company_id=cid,
        form_key="team_invite",
        key_prefix="team_inv",
        caption="Creates a login for this company. Share the email and temporary password securely.",
        on_back=_back,
        on_saved=_saved,
    )


def page_team(u: dict) -> None:
    t1, t2 = st.tabs(["App users (login)", "Employees (directory)"])
    with t1:
        _, c_add = st.columns([4, 1])
        with c_add:
            st.markdown('<div style="min-height:2.6rem;"></div>', unsafe_allow_html=True)
            if u.get("role") == "company_admin" and st.button(
                "Invite",
                type="primary",
                key="team_btn_invite",
                help="Add a new app user (login)",
            ):
                st.session_state[_SS_TEAM_INVITE] = True
                st.rerun()
        users = auth_service.list_users(_cid())
        df_u = dataframe_for_records(
            users,
            extra_drop=frozenset({"user_id"}),
            map_role_labels=True,
        )
        if df_u.empty:
            empty_state(
                "No app users",
                "Use **Invite** (company admin) to create the first login-capable user.",
            )
        else:
            st.dataframe(df_u, use_container_width=True, hide_index=True)
        if u.get("role") == "company_admin":
            st.caption(
                "New users receive the role you assign. Ask them to change password after first login (future enhancement)."
            )
    with t2:
        _, c_add2 = st.columns([4, 1])
        with c_add2:
            st.markdown('<div style="min-height:2.6rem;"></div>', unsafe_allow_html=True)
            if st.button("Add", type="primary", key="team_btn_employee", help="Add an employee record"):
                open_quick_add_modal("employee")
                st.rerun()
        emps = civil_store.employees_list(_cid())
        df_e = dataframe_for_records(emps) if emps else pd.DataFrame()
        if df_e.empty:
            empty_state(
                "No employees",
                "Use **Add** to register directory rows for HR — separate from login accounts.",
            )
        else:
            st.dataframe(df_e, use_container_width=True, hide_index=True)

    if st.session_state.get(_SS_TEAM_INVITE):
        _team_invite_dialog()
