"""
RNK Civil — Streamlit app (MongoDB + role-based access).

Run from the repository root:  streamlit run app.py
Requires `.env` in the project root (MongoDB variables — see that file).
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import streamlit as st

from config import get_app_session_secret, get_mongo_uri
from core.logging import setup_logging
from core.session_cookie import (
    get_cookie_token,
    inject_clear_cookie,
    inject_set_cookie,
    sign_session,
    verify_session,
)
from core.roles import ROLE_LABELS
from db import mongo
from services import auth_service
from ui.pages import (
    PAGE_FUNCS,
    apply_nav_from_query_params,
    publish_nav_to_query_params,
    sidebar_nav,
)
from ui.pages.field_ops import render_invite_user_modal_if_open
from ui.pages.quick_add_dialog import render_quick_add_modal_if_open
from ui.pages.form_ui import required_label, required_legend
from ui.theme import inject_auth_layout, inject_theme, inject_ui_animations, sidebar_avatar_initials

st.set_page_config(page_title="RNK Civil", layout="wide", initial_sidebar_state="expanded")


@st.cache_resource
def _ensure_indexes_cached(uri: str) -> None:
    """Run once per connection string after a successful ping."""
    if not uri:
        return
    mongo.ensure_indexes()


def _logout() -> None:
    for k in ("user", "rnk_nav", "rnk_nav_pending"):
        if k in st.session_state:
            del st.session_state[k]
    inject_clear_cookie()
    st.rerun()


def _try_restore_user_from_cookie() -> None:
    """Rehydrate session when Streamlit assigns a new session but the browser still has our cookie."""
    if "user" in st.session_state:
        return
    raw = get_cookie_token()
    if not raw:
        return
    secret = get_app_session_secret()
    uid = verify_session(raw, secret=secret)
    if not uid:
        return
    try:
        u = auth_service.get_user_by_id(uid)
    except Exception:
        return
    if u:
        st.session_state["user"] = u


def _auth_screen() -> None:
    inject_auth_layout()
    col_aside, col_main = st.columns([11, 13], gap="large")

    with col_aside:
        st.markdown(
            """
<aside class="rnk-auth-aside" aria-label="Product">
  <div class="rnk-auth-aside__glow" aria-hidden="true"></div>
  <div class="rnk-mark rnk-mark--lg">RNK</div>
  <h2 class="rnk-auth-aside__title">Civil operations, one place.</h2>
  <p class="rnk-auth-aside__lead">Projects, sites, labour, attendance and billing — built for field teams and office staff.</p>
  <ul class="rnk-auth-aside__list">
    <li><span class="rnk-auth-aside__icon">✓</span> Role-based access per company</li>
    <li><span class="rnk-auth-aside__icon">✓</span> Works in the browser — no install</li>
    <li><span class="rnk-auth-aside__icon">✓</span> Responsive on phone, tablet, desktop</li>
  </ul>
</aside>
""",
            unsafe_allow_html=True,
        )

    with col_main:
        st.markdown(
            '<div class="rnk-auth-root" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            """
<div class="rnk-auth-brand rnk-auth-brand--mobile">
  <div class="rnk-mark">RNK</div>
  <h1>RNK Civil Operations</h1>
  <p class="rnk-tagline">Projects, sites, attendance &amp; billing — sign in or register your company.</p>
</div>
""",
            unsafe_allow_html=True,
        )

        tab_reg, tab_in = st.tabs(["Register company", "Sign in"])

        with tab_reg:
            st.markdown(
                '<p class="rnk-auth-hint">One organisation account — you become the company admin.</p>',
                unsafe_allow_html=True,
            )
            with st.form("reg"):
                required_legend()
                st.markdown('<p class="rnk-auth-section-label">Company</p>', unsafe_allow_html=True)
                c1, c2 = st.columns(2, gap="medium")
                with c1:
                    required_label("Display name")
                    cname = st.text_input("Display name", placeholder="e.g. RNK Infratech Pvt Ltd", label_visibility="collapsed")
                with c2:
                    legal = st.text_input("Legal name (optional)", placeholder="As on GST / incorporation")
                gst = st.text_input("GSTIN (optional)", placeholder="15 characters")
                st.markdown('<p class="rnk-auth-section-label">Administrator</p>', unsafe_allow_html=True)
                a1, a2 = st.columns(2, gap="medium")
                with a1:
                    required_label("Full name")
                    admin = st.text_input("Full name", placeholder="Primary contact person", label_visibility="collapsed")
                with a2:
                    required_label("Work email")
                    email = st.text_input("Work email", placeholder="name@company.com", label_visibility="collapsed")
                p1, p2 = st.columns(2, gap="medium")
                with p1:
                    required_label("Password")
                    pw = st.text_input("Password", type="password", label_visibility="collapsed")
                with p2:
                    required_label("Confirm password")
                    pw2 = st.text_input("Confirm password", type="password", label_visibility="collapsed")
                ok = st.form_submit_button("Create company account →", type="primary", use_container_width=True)
            if ok:
                if pw != pw2:
                    st.error("Passwords do not match.")
                else:
                    try:
                        auth_service.register_company(cname, admin, email, pw, legal_name=legal or None, gstin=gst or None)
                        st.success("Company created. Open **Sign in** and use your email and password.")
                    except Exception as e:
                        st.error(str(e))

        with tab_in:
            st.markdown(
                '<p class="rnk-auth-hint">Sign in with the email and password from your company registration.</p>',
                unsafe_allow_html=True,
            )
            with st.form("login"):
                required_legend()
                l1, l2 = st.columns(2, gap="medium")
                with l1:
                    required_label("Email")
                    em = st.text_input("Email", key="lem", placeholder="you@company.com", label_visibility="collapsed")
                with l2:
                    required_label("Password")
                    pw = st.text_input("Password", type="password", key="lpw", label_visibility="collapsed")
                go = st.form_submit_button("Sign in →", type="primary", use_container_width=True)
            if go:
                u = auth_service.login(em, pw)
                if not u:
                    st.error("Invalid email or password.")
                else:
                    st.session_state["user"] = u
                    inject_set_cookie(sign_session(u["user_id"], secret=get_app_session_secret()))
                    st.rerun()

        st.markdown(
            '<p class="rnk-auth-foot">RNK Infratech · Internal operations portal</p>',
            unsafe_allow_html=True,
        )


def main() -> None:
    setup_logging()
    if "rnk_dark_toggle" not in st.session_state:
        # Migrate legacy key if present; default light
        legacy = st.session_state.pop("rnk_theme", None)
        st.session_state["rnk_dark_toggle"] = legacy == "dark" if legacy is not None else False
    inject_theme("dark" if st.session_state["rnk_dark_toggle"] else "light")
    inject_ui_animations("dark" if st.session_state["rnk_dark_toggle"] else "light")

    ok, detail = mongo.diagnose()
    if not ok:
        st.error("MongoDB is not configured or unreachable.")
        if detail:
            st.markdown(detail)
        st.markdown(
            """
**Checklist**

1. Project root **`.env`** with **`MONGODB_USERNAME`**, **`MONGODB_PASSWORD`**, **`MONGODB_CLUSTER`**, **`MONGODB_DATABASE`** (and optional `MONGODB_APP_NAME`, `MONGODB_AUTH_SOURCE`) — or a single **`MONGODB_URI`** / **`MONGO_URI`**.
2. Username/password match **Atlas → Database Access** (reset password there if unsure).
3. **Atlas → Network Access** allows your IP.
4. Restart Streamlit after saving `.env`.

Do not commit `.env` to Git.
            """
        )
        return

    _ensure_indexes_cached(get_mongo_uri() or "")

    _try_restore_user_from_cookie()

    if "user" not in st.session_state:
        _auth_screen()
        return

    u = st.session_state["user"]
    # refresh profile (do not drop session on transient DB errors)
    try:
        fresh = auth_service.get_user_by_id(u["user_id"])
    except Exception:
        fresh = None
    if fresh:
        st.session_state["user"] = fresh
        u = fresh

    cname = html.escape(u.get("company_name", "Company") or "Company")
    em = html.escape(u.get("email", "") or "")
    fn = (u.get("full_name") or "").strip()
    name_html = (
        f'<p class="rnk-sidebar-identity__name">{html.escape(fn)}</p>'
        if fn
        else ""
    )
    role = html.escape(ROLE_LABELS.get(u.get("role", ""), str(u.get("role", "") or "")))
    av = sidebar_avatar_initials(u)
    av_e = html.escape(av)
    st.sidebar.markdown(
        f"""
<div class="rnk-sidebar-shell">
  <div class="rnk-sidebar-identity" role="group" aria-label="Signed in">
    <div class="rnk-sidebar-avatar" aria-hidden="true">{av_e}</div>
    <div class="rnk-sidebar-identity__main">
      <p class="rnk-sidebar-identity__app">RNK Civil</p>
      <p class="rnk-sidebar-identity__company">{cname}</p>
      {name_html}
      <p class="rnk-sidebar-identity__email">{em}</p>
      <span class="rnk-sidebar-role-chip">{role}</span>
    </div>
  </div>
  <div class="rnk-sidebar-nav-divider" role="separator" aria-hidden="true"></div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.sidebar.markdown(
        '<p class="rnk-sidebar-section-label">Appearance</p>',
        unsafe_allow_html=True,
    )
    st.sidebar.toggle("Dark mode", key="rnk_dark_toggle")

    st.sidebar.markdown(
        '<p class="rnk-sidebar-section-label rnk-sidebar-section-label--nav">Navigation</p>',
        unsafe_allow_html=True,
    )

    role = u.get("role", "viewer")
    apply_nav_from_query_params(role)
    nav = sidebar_nav(role)
    if st.sidebar.button("Log out", key="sidebar_logout", use_container_width=True):
        _logout()

    if not nav:
        st.warning("No pages available for your role.")
        return

    publish_nav_to_query_params(nav)

    render_quick_add_modal_if_open()
    render_invite_user_modal_if_open()
    flash = st.session_state.pop("rnk_flash_success", None)
    if flash:
        st.success(flash)

    _, render = PAGE_FUNCS[nav]
    render(u)


main()
