"""Clients master (directory, add, edit)."""
from __future__ import annotations

import html

import pandas as pd
import streamlit as st

from services import civil_store
from ui.pages.common import (
    INDIAN_STATES_UT,
    _cid,
    _client_directory_records,
    _client_pick_label,
)
from ui.theme import empty_state

def page_clients(u: dict) -> None:
    cid = _cid()
    rows = civil_store.clients_list(cid)
    summ = civil_store.clients_summary(cid)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Clients", summ["total"])
    m2.metric("With GSTIN", summ["with_gstin"])
    m3.metric("Projects linked", summ["projects_linked"], help="Projects whose client name matches a client here.")
    m4.metric("All projects", summ["projects_total"])

    tab_dir, tab_add, tab_edit = st.tabs(["Directory", "Add client", "View / edit"])

    with tab_dir:
        q = st.text_input("Search", placeholder="Name, code, city, GSTIN, phone, email…", key="cl_search")
        recs = _client_directory_records(rows, q)
        if not recs:
            empty_state(
                "No matching clients" if rows else "No clients yet",
                "Adjust search or add a client in the next tab.",
            )
        else:
            st.dataframe(pd.DataFrame(recs), use_container_width=True, hide_index=True)
        st.caption(
            "Tip: when you create a **Project**, use the same spelling as **Display name** here so «Projects linked» stays accurate."
        )

    with tab_add:
        with st.form("cl_new"):
            st.markdown("**Identity**")
            c1, c2 = st.columns(2)
            with c1:
                code = st.text_input("Client code (optional)", placeholder="e.g. CLT-NHAI", key="cln_code")
                name = st.text_input("Display name *", placeholder="Shown on invoices & projects", key="cln_name")
            with c2:
                legal = st.text_input("Legal / registered name", key="cln_legal")
                pan = st.text_input("PAN (TDS / records)", placeholder="AAAAA0000A", key="cln_pan")

            st.markdown("**Contact**")
            c3, c4 = st.columns(2)
            with c3:
                cp = st.text_input("Contact person", key="cln_cp")
                ph = st.text_input("Phone", key="cln_ph")
                ph2 = st.text_input("Alternate phone", key="cln_ph2")
            with c4:
                em = st.text_input("Email", key="cln_em")
                bem = st.text_input("Billing email (if different)", key="cln_bem")
                web = st.text_input("Website", placeholder="https://", key="cln_web")

            st.markdown("**Location**")
            st.caption("Use the same structure as GST / letterhead: street lines, then city · state · PIN.")
            a1, a2 = st.columns(2, gap="medium")
            with a1:
                addr = st.text_input(
                    "Address line 1",
                    placeholder="Building, street, door number",
                    key="cln_addr",
                )
            with a2:
                addr2 = st.text_input(
                    "Address line 2 (optional)",
                    placeholder="Area, landmark, district",
                    key="cln_addr2",
                )
            c5, c6, c7 = st.columns(3)
            with c5:
                city = st.text_input("City / town", key="cln_city")
            with c6:
                st_sel = st.selectbox("State / UT", INDIAN_STATES_UT, key="cln_state_sel")
                st_free = st.text_input("State (free text if not listed)", key="cln_state_txt")
            with c7:
                pin = st.text_input("PIN code", key="cln_pin")
            country = st.text_input("Country", value="India", key="cln_country")

            st.markdown("**Commercial**")
            c8, c9 = st.columns(2)
            with c8:
                gst = st.text_input("GSTIN", placeholder="15 characters", key="cln_gst")
            with c9:
                ptd = st.number_input("Payment terms (days)", min_value=0, max_value=365, value=30, step=1, key="cln_ptd")
            notes = st.text_area("Internal notes", placeholder="Credit limit, portal login, escalation…", height=100, key="cln_notes")

            if st.form_submit_button("Save client", type="primary", use_container_width=True):
                if not (name or "").strip():
                    st.error("Display name is required.")
                else:
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
                            alternate_phone=ph2 or None,
                            email=em or None,
                            billing_email=bem or None,
                            website=web or None,
                            address=addr or None,
                            address_line2=addr2 or None,
                            city=city or None,
                            state=state_val,
                            pincode=pin or None,
                            country=country or None,
                            gstin=gst or None,
                            payment_terms_days=int(ptd),
                            notes=notes or None,
                        )
                        st.success("Client saved.")
                        st.rerun()
                    except ValueError as ex:
                        st.error(str(ex))

    with tab_edit:
        if not rows:
            empty_state("No clients to edit", "Add a client first.")
        else:
            labels = [_client_pick_label(r) for r in rows]
            pick = st.selectbox("Choose client", labels, key="cl_edit_pick")
            rec = next(r for r in rows if _client_pick_label(r) == pick)
            oid = str(rec["_id"])
            fresh = civil_store.client_get(cid, oid) or rec

            pay_days = fresh.get("payment_terms_days")
            if pay_days is None:
                pay_days = 30
            try:
                pay_days = int(pay_days)
            except (TypeError, ValueError):
                pay_days = 30

            st_cur = (fresh.get("state") or "").strip()
            if st_cur in INDIAN_STATES_UT:
                st_idx = INDIAN_STATES_UT.index(st_cur)
                st_free_val = ""
            else:
                st_idx = 0
                st_free_val = st_cur

            addr_html = (fresh.get("address") or "").strip() or "—"
            addr2_html = (fresh.get("address_line2") or "").strip()
            notes_html = (fresh.get("notes") or "").strip() or "—"
            addr_block = html.escape(addr_html[:280]) + ("…" if len(addr_html) > 280 else "")
            if addr2_html:
                addr_block += f"<br/><span style='color:#a1a1aa;font-size:0.85rem;'>Line 2</span> {html.escape(addr2_html[:200])}"
                if len(addr2_html) > 200:
                    addr_block += "…"
            st.markdown(
                f'<div class="rnk-card" style="margin-bottom:1rem;">'
                f"<strong>Snapshot</strong><br/>"
                f"<span style='color:#a1a1aa;font-size:0.85rem;'>GSTIN</span> {html.escape(str(fresh.get('gstin') or '—'))} · "
                f"<span style='color:#a1a1aa;font-size:0.85rem;'>PAN</span> {html.escape(str(fresh.get('pan') or '—'))}<br/>"
                f"<span style='color:#a1a1aa;font-size:0.85rem;'>Location</span> "
                f"{html.escape(str(fresh.get('city') or '—'))}, {html.escape(str(fresh.get('state') or '—'))} "
                f"{html.escape(str(fresh.get('pincode') or ''))}<br/>"
                f"<span style='color:#a1a1aa;font-size:0.85rem;'>Address line 1</span> {addr_block}<br/>"
                f"<span style='color:#a1a1aa;font-size:0.85rem;'>Notes</span> {html.escape(notes_html[:200])}"
                f"{'…' if len(notes_html) > 200 else ''}"
                f"</div>",
                unsafe_allow_html=True,
            )

            with st.form("cl_edit"):
                st.markdown("**Identity**")
                e1, e2 = st.columns(2)
                with e1:
                    e_code = st.text_input(
                        "Client code",
                        value=fresh.get("client_code") or "",
                        key=f"cle_code_{oid}",
                    )
                    e_name = st.text_input(
                        "Display name *",
                        value=fresh.get("name") or "",
                        key=f"cle_name_{oid}",
                    )
                with e2:
                    e_legal = st.text_input(
                        "Legal / registered name",
                        value=fresh.get("legal_name") or "",
                        key=f"cle_legal_{oid}",
                    )
                    e_pan = st.text_input("PAN", value=fresh.get("pan") or "", key=f"cle_pan_{oid}")

                st.markdown("**Contact**")
                e3, e4 = st.columns(2)
                with e3:
                    e_cp = st.text_input("Contact person", value=fresh.get("contact_person") or "", key=f"cle_cp_{oid}")
                    e_ph = st.text_input("Phone", value=fresh.get("phone") or "", key=f"cle_ph_{oid}")
                    e_ph2 = st.text_input("Alternate phone", value=fresh.get("alternate_phone") or "", key=f"cle_ph2_{oid}")
                with e4:
                    e_em = st.text_input("Email", value=fresh.get("email") or "", key=f"cle_em_{oid}")
                    e_bem = st.text_input("Billing email", value=fresh.get("billing_email") or "", key=f"cle_bem_{oid}")
                    e_web = st.text_input("Website", value=fresh.get("website") or "", key=f"cle_web_{oid}")

                st.markdown("**Location**")
                ea1, ea2 = st.columns(2, gap="medium")
                with ea1:
                    e_addr = st.text_input(
                        "Address line 1",
                        value=fresh.get("address") or "",
                        placeholder="Building, street, door number",
                        key=f"cle_addr_{oid}",
                    )
                with ea2:
                    e_addr2 = st.text_input(
                        "Address line 2 (optional)",
                        value=fresh.get("address_line2") or "",
                        placeholder="Area, landmark, district",
                        key=f"cle_addr2_{oid}",
                    )
                e5, e6, e7 = st.columns(3)
                with e5:
                    e_city = st.text_input("City / town", value=fresh.get("city") or "", key=f"cle_city_{oid}")
                with e6:
                    e_st_sel = st.selectbox(
                        "State / UT",
                        INDIAN_STATES_UT,
                        index=st_idx,
                        key=f"cle_state_sel_{oid}",
                    )
                    e_st_txt = st.text_input(
                        "State (free text if not listed)",
                        value=st_free_val,
                        key=f"cle_state_txt_{oid}",
                    )
                with e7:
                    e_pin = st.text_input("PIN code", value=fresh.get("pincode") or "", key=f"cle_pin_{oid}")
                e_country = st.text_input(
                    "Country",
                    value=fresh.get("country") or "India",
                    key=f"cle_country_{oid}",
                )

                st.markdown("**Commercial**")
                e8, e9 = st.columns(2)
                with e8:
                    e_gst = st.text_input("GSTIN", value=fresh.get("gstin") or "", key=f"cle_gst_{oid}")
                with e9:
                    e_ptd = st.number_input(
                        "Payment terms (days)",
                        min_value=0,
                        max_value=365,
                        value=pay_days,
                        step=1,
                        key=f"cle_ptd_{oid}",
                    )
                e_notes = st.text_area(
                    "Internal notes",
                    value=fresh.get("notes") or "",
                    height=100,
                    key=f"cle_notes_{oid}",
                )

                if st.form_submit_button("Save changes", type="primary", use_container_width=True):
                    if not (e_name or "").strip():
                        st.error("Display name is required.")
                    else:
                        e_state_val = (e_st_txt or "").strip() or (e_st_sel or "").strip() or None
                        try:
                            civil_store.client_update(
                                cid,
                                oid,
                                client_code=e_code or None,
                                name=e_name.strip(),
                                legal_name=e_legal or None,
                                pan=e_pan or None,
                                contact_person=e_cp or None,
                                phone=e_ph or None,
                                alternate_phone=e_ph2 or None,
                                email=e_em or None,
                                billing_email=e_bem or None,
                                website=e_web or None,
                                address=e_addr or None,
                                address_line2=e_addr2 or None,
                                city=e_city or None,
                                state=e_state_val,
                                pincode=e_pin or None,
                                country=e_country or None,
                                gstin=e_gst or None,
                                payment_terms_days=int(e_ptd),
                                notes=e_notes or None,
                            )
                            st.success("Client updated.")
                            st.rerun()
                        except ValueError as ex:
                            st.error(str(ex))

