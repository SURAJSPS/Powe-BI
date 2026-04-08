"""Compact **client** form for project modals; **app user** form for Team → Invite and project **Add app user** (``field_ops``).

Quick add only offers client + employee — it does not use ``render_quick_app_user_form``."""
from __future__ import annotations

from typing import Callable

import streamlit as st

from core.roles import ROLE_LABELS, ROLES_INVITABLE
from services import auth_service, civil_store
from ui.pages.form_ui import required_label, required_legend


def _app_user_pick_label(*, full_name: str, email: str, role: str) -> str:
    fn = (full_name or "").strip() or "—"
    em = (email or "").strip()
    rl = ROLE_LABELS.get(role, role or "—")
    return f"{fn} — {rl} · {em}"


def render_quick_client_form(
    *,
    company_id: str,
    form_key: str,
    key_prefix: str,
    caption: str,
    on_back: Callable[[], None],
    on_saved: Callable[[str], None],
) -> None:
    """Compact new-client form for use inside the Project dialog sub-view."""
    st.markdown('<p class="rnk-modal-section">New client</p>', unsafe_allow_html=True)
    st.caption(caption)
    submitted = False
    back = False
    with st.form(f"{form_key}_client"):
        nm = st.text_input(
            "Display name *",
            placeholder="As on PO or agreement",
            key=f"{key_prefix}_c_nm",
        )
        lg = st.text_input("Legal name (optional)", key=f"{key_prefix}_c_lg")
        gst = st.text_input("GSTIN (optional)", key=f"{key_prefix}_c_gst")
        b1, b2 = st.columns(2, gap="small")
        with b1:
            back = st.form_submit_button("Back", use_container_width=True)
        with b2:
            submitted = st.form_submit_button("Save client", type="primary", use_container_width=True)
    if back:
        on_back()
        return
    if submitted:
        nt = (nm or "").strip()
        if not nt:
            st.error("Please enter a display name.")
            return
        try:
            civil_store.client_add(
                company_id,
                nt,
                legal_name=(lg or "").strip() or None,
                gstin=(gst or "").strip() or None,
            )
            on_saved(nt)
        except Exception as ex:
            st.error(str(ex))


def render_quick_app_user_form(
    *,
    company_id: str,
    form_key: str,
    key_prefix: str,
    caption: str,
    on_back: Callable[[], None],
    on_saved: Callable[[str], None],
) -> None:
    """Compact new app-user form for use inside the Project dialog sub-view or ``quick_add_dialog``."""
    st.markdown('<p class="rnk-modal-section">App user</p>', unsafe_allow_html=True)
    st.caption(caption)
    submitted = False
    back = False
    with st.form(f"{form_key}_user"):
        required_legend()
        u1, u2 = st.columns(2, gap="medium")
        with u1:
            required_label("Email")
            em = st.text_input("Email", label_visibility="collapsed", key=f"{key_prefix}_email")
        with u2:
            required_label("Full name")
            fn = st.text_input("Full name", label_visibility="collapsed", key=f"{key_prefix}_fn")
        u3, u4 = st.columns(2, gap="medium")
        with u3:
            required_label("Temporary password")
            pw = st.text_input(
                "Temporary password",
                type="password",
                label_visibility="collapsed",
                key=f"{key_prefix}_pw",
            )
        with u4:
            rl = st.selectbox(
                "Role",
                ROLES_INVITABLE,
                index=0,
                format_func=lambda r: ROLE_LABELS.get(r, r),
                key=f"{key_prefix}_role",
            )
        st.divider()
        b1, b2 = st.columns(2, gap="small")
        with b1:
            back = st.form_submit_button("Back", use_container_width=True)
        with b2:
            submitted = st.form_submit_button("Create user", type="primary", use_container_width=True)
    if back:
        on_back()
        return
    if submitted:
        try:
            auth_service.add_user(company_id, em or "", pw or "", fn or "", rl)
            label = _app_user_pick_label(full_name=fn or "", email=em or "", role=rl)
            on_saved(label)
        except Exception as ex:
            st.error(str(ex))
