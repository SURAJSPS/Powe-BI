"""Company profile and OT rules (embedded)."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from core.roles import ROLE_LABELS, can_manage_ot_rules
from services import auth_service, civil_store
from services.entry_policy import entry_date_window
from ui.pages.common import _cid
from ui.theme import empty_state, insight_preview, muted_hint

def _render_ot_rules_section(u: dict) -> None:
    """OT multipliers — embedded in Company profile (sidebar no longer lists OT rules)."""
    muted_hint("Define rules (e.g. OT-STD) and assign them to workers on the Workers screen.")
    rows = civil_store.ot_rules_list(_cid())
    df = pd.DataFrame(rows) if rows else pd.DataFrame()
    if df.empty:
        empty_state("No OT rules", "Add at least one rule before assigning workers.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
    with st.form("co_ot_rules"):
        rid = st.text_input("Rule ID", value="OT-STD")
        name = st.text_input("Name", value="Standard")
        mult = st.number_input("Multiplier", value=2.0)
        mx = st.number_input("Max OT hrs/day", value=4.0)
        notes = st.text_input("Notes", value="")
        if st.form_submit_button("Save rule", type="primary", use_container_width=True):
            civil_store.ot_rule_add(_cid(), rid, name, mult, mx, notes)
            st.rerun()


def page_company(u: dict) -> None:
    c = auth_service.get_company(_cid())
    if not c:
        st.error("Company not found.")
        return

    role = u.get("role", "viewer")
    tab_labels = ["Organisation", "Bank", "Entry rules"]
    if can_manage_ot_rules(role):
        tab_labels.append("OT rules")
    ta = st.tabs(tab_labels)

    with ta[0]:
        with st.form("co"):
            name = st.text_input("Display name", value=c.get("name", ""), help="Shown across the app and reports.")
            legal = st.text_input("Legal name", value=c.get("legal_name", ""))
            gstin = st.text_input("GSTIN (optional)", value=c.get("gstin") or "")
            addr = st.text_area("Registered address (optional)", value=c.get("address") or "", height=100)
            if st.form_submit_button("Save organisation", type="primary", use_container_width=True):
                auth_service.update_company(_cid(), name=name, legal_name=legal, gstin=gstin or None, address=addr or None)
                st.success("Saved.")
                st.rerun()

    with ta[1]:
        with st.form("cobank"):
            a, b = st.columns(2)
            with a:
                bh = st.text_input("Account holder", value=c.get("bank_account_holder") or "")
            with b:
                bn = st.text_input("Bank name", value=c.get("bank_name") or "")
            c1, c2 = st.columns(2)
            with c1:
                br = st.text_input("Branch", value=c.get("bank_branch") or "")
            with c2:
                ac = st.text_input("Account number", value=c.get("bank_account_no") or "")
            ifsc = st.text_input("IFSC", value=c.get("bank_ifsc") or "", max_chars=11, placeholder="e.g. SBIN0001234")
            if st.form_submit_button("Save bank details", type="primary", use_container_width=True):
                auth_service.update_company(
                    _cid(),
                    bank_account_holder=bh.strip() or None,
                    bank_name=bn.strip() or None,
                    bank_branch=br.strip() or None,
                    bank_account_no=ac.strip() or None,
                    bank_ifsc=ifsc.strip().upper() or None,
                )
                st.success("Saved.")
                st.rerun()

    with ta[2]:
        limit_on = c.get("backdate_max_days") is not None
        with st.form("codates"):
            limit = st.checkbox("Limit back-dated entries (non-admin users)", value=limit_on)
            days = st.number_input(
                "Max days in the past (inclusive)",
                min_value=0,
                max_value=3650,
                value=int(c.get("backdate_max_days") or 30),
                help="Earliest allowed date = today minus this many days. 0 = today only.",
                disabled=not limit,
            )
            bypass = st.checkbox(
                "Company admins may bypass the past limit",
                value=bool(c.get("backdate_bypass_admin", True)),
            )
            future = st.checkbox(
                "Allow future-dated entries",
                value=bool(c.get("allow_future_dated_entries", False)),
                help="If off, transaction dates cannot be after today.",
            )
            if st.form_submit_button("Save entry rules", type="primary", use_container_width=True):
                auth_service.update_company(
                    _cid(),
                    backdate_max_days=(int(days) if limit else None),
                    backdate_bypass_admin=bypass,
                    allow_future_dated_entries=future,
                )
                st.success("Saved.")
                st.rerun()
        min_d, max_d = entry_date_window(c, u.get("role", "viewer"))
        role_l = ROLE_LABELS.get(u.get("role", ""), u.get("role", "") or "—")
        insight_preview(
            "Effective date range for your account",
            [
                ("Role", role_l),
                ("Earliest date", min_d.isoformat() if min_d else "No limit"),
                ("Latest date", max_d.isoformat() if max_d else "No limit"),
            ],
        )

    if can_manage_ot_rules(role):
        with ta[3]:
            _render_ot_rules_section(u)

