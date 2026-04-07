"""Team, app users, and employee directory."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from core.roles import ROLES
from services import auth_service, civil_store
from ui.pages.common import _cid
from ui.theme import empty_state

def page_team(u: dict) -> None:
    t1, t2 = st.tabs(["App users (login)", "Employees (directory)"])
    with t1:
        users = auth_service.list_users(_cid())
        df_u = pd.DataFrame(users)
        if df_u.empty:
            empty_state("No app users", "Create the first login-capable user below (company admin only).")
        else:
            st.dataframe(df_u, use_container_width=True, hide_index=True)
        if u.get("role") == "company_admin":
            with st.expander("Invite app user", expanded=False):
                with st.form("nu"):
                    u1, u2 = st.columns(2, gap="medium")
                    with u1:
                        em = st.text_input("Email")
                    with u2:
                        fn = st.text_input("Full name")
                    u3, u4 = st.columns(2, gap="medium")
                    with u3:
                        pw = st.text_input("Temporary password", type="password")
                    with u4:
                        role = st.selectbox("Role", ROLES, index=min(3, len(ROLES) - 1))
                    if st.form_submit_button("Create user", type="primary", use_container_width=True):
                        try:
                            auth_service.add_user(_cid(), em, pw, fn, role)
                            st.success("User created.")
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))
            st.caption("New users receive the role you assign. Ask them to change password after first login (future enhancement).")
    with t2:
        emps = civil_store.employees_list(_cid())
        df_e = pd.DataFrame(emps) if emps else pd.DataFrame()
        if df_e.empty:
            empty_state("No employees", "Add directory rows for HR — separate from login accounts.")
        else:
            st.dataframe(df_e, use_container_width=True, hide_index=True)
        with st.form("ne"):
            n1, n2 = st.columns(2, gap="medium")
            with n1:
                code = st.text_input("Employee code", value="EMP-")
            with n2:
                name = st.text_input("Full name")
            n3, n4 = st.columns(2, gap="medium")
            with n3:
                dept = st.text_input("Department")
            with n4:
                title = st.text_input("Job title")
            ph = st.text_input("Phone")
            if st.form_submit_button("Add employee", type="primary", use_container_width=True):
                civil_store.employee_add(_cid(), code, name, department=dept or None, role_title=title or None, phone=ph or None)
                st.rerun()

