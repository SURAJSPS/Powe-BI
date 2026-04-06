"""
RNK Civil — Streamlit app (MongoDB + role-based access).

Run from `python_app/`:  streamlit run app.py
Requires `.env` in the project root (MongoDB variables — see that file).
"""
from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

import streamlit as st

from config import get_mongo_uri
from db import mongo
from services import auth_service
from ui.pages_main import PAGE_FUNCS, sidebar_nav
from ui.theme import inject_theme

st.set_page_config(page_title="RNK Civil", layout="wide", initial_sidebar_state="expanded")


@st.cache_resource
def _ensure_indexes_cached(uri: str) -> None:
    """Run once per connection string after a successful ping."""
    if not uri:
        return
    mongo.ensure_indexes()


def _logout() -> None:
    for k in ("user",):
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def _auth_screen() -> None:
    st.markdown("### RNK Civil")
    tab1, tab2 = st.tabs(["Create company", "Sign in"])
    with tab1:
        with st.form("reg"):
            cname = st.text_input("Company name")
            legal = st.text_input("Legal name (optional)")
            gst = st.text_input("GSTIN (optional)")
            admin = st.text_input("Admin full name")
            email = st.text_input("Admin email")
            pw = st.text_input("Password", type="password")
            pw2 = st.text_input("Confirm password", type="password")
            ok = st.form_submit_button("Register")
        if ok:
            if not cname or not admin or not email or not pw:
                st.error("Fill company name, admin, email and password.")
            elif pw != pw2:
                st.error("Passwords do not match.")
            else:
                try:
                    auth_service.register_company(cname, admin, email, pw, legal_name=legal or None, gstin=gst or None)
                    st.success("Company created. Sign in on the next tab.")
                except Exception as e:
                    st.error(str(e))
    with tab2:
        with st.form("login"):
            em = st.text_input("Email", key="lem")
            pw = st.text_input("Password", type="password", key="lpw")
            go = st.form_submit_button("Sign in")
        if go:
            u = auth_service.login(em, pw)
            if not u:
                st.error("Invalid email or password.")
            else:
                st.session_state["user"] = u
                st.rerun()


def main() -> None:
    inject_theme()

    ok, detail = mongo.diagnose()
    if not ok:
        st.error("MongoDB is not configured or unreachable.")
        if detail:
            st.markdown(detail)
        st.markdown(
            """
**Checklist**

1. `.env` in the project root with `MONGO_USER`, `MONGO_PASSWORD`, `MONGO_HOST` (or `MONGO_URI`).
2. Password matches **Atlas → Database Access** for that user (reset there if unsure).
3. **Atlas → Network Access** allows your IP.
4. Restart Streamlit after changing `.env`.

Do not commit real credentials to Git.
            """
        )
        return

    _ensure_indexes_cached(get_mongo_uri() or "")

    if "user" not in st.session_state:
        _auth_screen()
        return

    u = st.session_state["user"]
    # refresh profile
    fresh = auth_service.get_user_by_id(u["user_id"])
    if fresh:
        st.session_state["user"] = fresh
        u = fresh

    st.sidebar.markdown(f"**{u.get('company_name', 'Company')}**")
    st.sidebar.caption(u.get("email", ""))
    st.sidebar.caption(f"Role: {u.get('role', '')}")
    if st.sidebar.button("Log out"):
        _logout()

    nav = sidebar_nav(u.get("role", "viewer"))
    if not nav:
        st.warning("No pages available for your role.")
        return

    _, render = PAGE_FUNCS[nav]
    render(u)


main()
