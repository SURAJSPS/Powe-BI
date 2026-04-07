"""Company profile and OT rules (embedded)."""
from __future__ import annotations

import streamlit as st
import pandas as pd

from core.roles import ROLE_LABELS, can_manage_ot_rules
from services import auth_service, civil_store
from services.entry_policy import entry_date_window
from ui.pages.common import INDIAN_STATES_UT, _cid
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
        o1, o2 = st.columns(2, gap="medium")
        with o1:
            rid = st.text_input("Rule ID", value="OT-STD")
        with o2:
            name = st.text_input("Name", value="Standard")
        o3, o4 = st.columns(2, gap="medium")
        with o3:
            mult = st.number_input("Multiplier", value=2.0)
        with o4:
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
        st_cur = (c.get("state") or "").strip()
        if st_cur in INDIAN_STATES_UT:
            st_idx = INDIAN_STATES_UT.index(st_cur)
            st_free_val = ""
        else:
            st_idx = 0
            st_free_val = st_cur

        with st.form("co"):
            co1, co2 = st.columns(2, gap="medium")
            with co1:
                name = st.text_input("Display name", value=c.get("name", ""), help="Shown across the app and reports.")
            with co2:
                legal = st.text_input("Legal name", value=c.get("legal_name", ""))
            gstin = st.text_input("GSTIN (optional)", value=c.get("gstin") or "")

            st.markdown("**Registered address**")
            st.caption("Standard format: street first, then city / state / PIN — matches invoices and records.")
            ad1, ad2 = st.columns(2, gap="medium")
            with ad1:
                a1 = st.text_input(
                    "Address line 1",
                    value=c.get("address_line1") or "",
                    placeholder="Building, street, door number",
                )
            with ad2:
                a2 = st.text_input(
                    "Address line 2 (optional)",
                    value=c.get("address_line2") or "",
                    placeholder="Area, landmark, district",
                )
            r1, r2 = st.columns(2, gap="medium")
            with r1:
                city = st.text_input("City / town", value=c.get("city") or "")
            with r2:
                pin = st.text_input("PIN code", value=c.get("pincode") or "", max_chars=12)
            r3, r4 = st.columns(2, gap="medium")
            with r3:
                st_sel = st.selectbox("State / UT", INDIAN_STATES_UT, index=st_idx)
                st_txt = st.text_input("State (if not listed above)", value=st_free_val)
            with r4:
                country = st.text_input("Country", value=c.get("country") or "India")

            if st.form_submit_button("Save organisation", type="primary", use_container_width=True):
                state_val = (st_txt or "").strip() or (st_sel or "").strip() or None
                auth_service.update_company(
                    _cid(),
                    name=name,
                    legal_name=legal,
                    gstin=gstin or None,
                    address=None,
                    address_line1=a1.strip() or None,
                    address_line2=a2.strip() or None,
                    city=city.strip() or None,
                    state=state_val,
                    pincode=pin.strip() or None,
                    country=country.strip() or None,
                )
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

