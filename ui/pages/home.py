"""Home / landing page."""
from __future__ import annotations

import html

import streamlit as st

from core.roles import ROLE_LABELS, can_access
from ui.pages.common import HOME_QUICK_ACTIONS, _go_nav
from ui.theme import dashboard_callout, hero, styled_divider

def page_home(u: dict) -> None:
    hero("RNK Civil Operations")
    company = html.escape(u.get("company_name", "") or "—")
    role_l = html.escape(ROLE_LABELS.get(u.get("role", ""), u.get("role", "") or "—"))
    email = html.escape(u.get("email", "") or "—")
    st.markdown(
        f"""
<section class="rnk-stat-grid" aria-label="Workspace summary">
  <article class="rnk-stat-tile">
    <span class="rnk-stat-tile__icon" aria-hidden="true">🏢</span>
    <span class="rnk-stat-tile__label">Company</span>
    <span class="rnk-stat-tile__value">{company}</span>
  </article>
  <article class="rnk-stat-tile">
    <span class="rnk-stat-tile__icon" aria-hidden="true">🛡️</span>
    <span class="rnk-stat-tile__label">Your role</span>
    <span class="rnk-stat-tile__value">{role_l}</span>
  </article>
  <article class="rnk-stat-tile">
    <span class="rnk-stat-tile__icon" aria-hidden="true">✉️</span>
    <span class="rnk-stat-tile__label">Signed in as</span>
    <span class="rnk-stat-tile__value">{email}</span>
  </article>
</section>
""",
        unsafe_allow_html=True,
    )

    role = u.get("role", "viewer")
    quick = [(k, icon, label) for k, icon, label in HOME_QUICK_ACTIONS if can_access(role, k)]
    if quick:
        st.markdown('<p class="rnk-section-label">Jump to</p>', unsafe_allow_html=True)
        n = len(quick)
        cols = st.columns(min(n, 4))
        for i, (key, icon, label) in enumerate(quick):
            with cols[i % len(cols)]:
                if st.button(
                    f"{icon}  {label}",
                    key=f"home_qa_{key}",
                    use_container_width=True,
                    help=f"Open {label}",
                    type="secondary",
                ):
                    _go_nav(key)
        styled_divider()

    with st.expander("Tips for this workspace", expanded=False):
        st.markdown(
            """
- **Sidebar** lists every module your role can access — pick one to work there.
- **Jump to** buttons above match your permissions and switch pages instantly.
- Forms save on **Submit**; tables refresh after a successful save.
            """
        )

    dashboard_callout("Use the sidebar or Jump to for navigation. What you can see depends on your role.")

