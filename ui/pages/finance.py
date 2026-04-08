"""Payroll, invoices, and executive dashboard."""
from __future__ import annotations
from datetime import date, datetime

import streamlit as st
import pandas as pd

from services import auth_service, civil_store
from services.entry_policy import assert_entry_date_allowed, clamp_entry_day, entry_date_window
from ui.pages.common import _cid, dataframe_for_records
from ui.pages.form_ui import required_label, required_legend
from ui.theme import empty_state

def page_payroll_est(u: dict) -> None:
    c1, c2, c3 = st.columns([1, 1, 1])
    ps = c1.date_input("Start", value=date(2026, 4, 1), key="pes")
    pe = c2.date_input("End", value=date(2026, 4, 30), key="pee")
    if c3.button("Refresh table", type="secondary", use_container_width=True, help="Recompute from current data"):
        st.rerun()
    df = civil_store.payroll_estimate_df(_cid(), ps, pe)
    if df.empty:
        empty_state("Nothing to estimate", "Ensure workers, OT rules, and attendance exist for this range.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def page_payroll_runs(u: dict) -> None:
    runs_rows = civil_store.payroll_runs_list(_cid())
    lines_rows = civil_store.payroll_lines_list(_cid())
    wmap = {w["worker_id"]: (w.get("full_name") or "").strip() for w in civil_store.workers_list(_cid())}
    lines_enriched: list[dict] = []
    for row in lines_rows:
        r = dict(row)
        wid = r.get("worker_id")
        if wid and wmap.get(wid):
            r["worker_name"] = wmap[wid]
        lines_enriched.append(r)
    df_r = dataframe_for_records(runs_rows)
    df_l = dataframe_for_records(lines_enriched)
    st.subheader("Runs")
    if df_r.empty:
        empty_state("No payroll runs", "Create a run for a pay period, then add lines.")
    else:
        st.dataframe(df_r, use_container_width=True, hide_index=True)
    st.subheader("Lines")
    if df_l.empty:
        empty_state("No lines", "Attach amounts per worker to a run.")
    else:
        st.dataframe(df_l, use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.form("pr"):
            required_legend()
            pr1, pr2 = st.columns(2, gap="medium")
            with pr1:
                required_label("Run ID")
                rid = st.text_input("Run ID", value=f"RUN-{datetime.now().strftime('%Y%m')}", label_visibility="collapsed")
            with pr2:
                required_label("Label")
                pl = st.text_input("Label", value="Apr-2026", label_visibility="collapsed")
            pr3, pr4 = st.columns(2, gap="medium")
            with pr3:
                a = st.date_input("Start", value=date(2026, 4, 1))
            with pr4:
                b = st.date_input("End", value=date(2026, 4, 30))
            if st.form_submit_button("Save run", type="primary", use_container_width=True):
                civil_store.payroll_run_add(_cid(), {"run_id": rid, "period_label": pl, "period_start": a, "period_end": b, "status": "Draft"})
                st.rerun()
    with c2:
        runs = [r["run_id"] for r in civil_store.payroll_runs_list(_cid())]
        wids = [w["worker_id"] for w in civil_store.workers_list(_cid())]
        with st.form("pl"):
            required_legend()
            pl1, pl2 = st.columns(2, gap="medium")
            with pl1:
                required_label("Run")
                rr = st.selectbox("Run", runs or ["—"], label_visibility="collapsed")
            with pl2:
                required_label("Worker")
                ww = st.selectbox("Worker", wids or ["—"], label_visibility="collapsed")
            pl3, pl4 = st.columns(2, gap="medium")
            with pl3:
                required_label("Component")
                comp = st.text_input("Component", value="Gross_Est", label_visibility="collapsed")
            with pl4:
                amt = st.number_input("Amount", value=0.0)
            if st.form_submit_button("Add line", type="primary", use_container_width=True) and runs and wids:
                civil_store.payroll_line_add(_cid(), {"run_id": rr, "worker_id": ww, "component": comp, "amount": float(amt), "statutory_tag": "Earning"})
                st.rerun()


def page_invoices(u: dict) -> None:
    inv = civil_store.invoices_list(_cid())
    df_i = dataframe_for_records(inv)
    if df_i.empty:
        empty_state("No invoices", "Raise your first invoice when a milestone is ready.")
    else:
        st.dataframe(df_i, use_container_width=True, hide_index=True)
    co_inv = auth_service.get_company(_cid())
    role_inv = u.get("role", "viewer")
    min_d_i, max_d_i = entry_date_window(co_inv or {}, role_inv) if co_inv else (None, None)
    default_inv = clamp_entry_day(date.today(), min_d_i, max_d_i)
    with st.form("inv"):
        required_legend()
        i1, i2 = st.columns(2, gap="medium")
        with i1:
            required_label("Invoice no")
            no = st.text_input("Invoice no", value="INV-2026-001", label_visibility="collapsed")
        with i2:
            dt_kw: dict = {"label": "Date", "value": default_inv}
            if min_d_i is not None:
                dt_kw["min_value"] = min_d_i
            if max_d_i is not None:
                dt_kw["max_value"] = max_d_i
            dt = st.date_input(**dt_kw)
        i3, i4 = st.columns(2, gap="medium")
        with i3:
            required_label("Project code")
            pc = st.text_input("Project code", value="PRJ-001", label_visibility="collapsed")
        with i4:
            required_label("Client name")
            cl = st.text_input("Client name", label_visibility="collapsed")
        t1, t2, t3 = st.columns(3, gap="medium")
        with t1:
            sub = st.number_input("Subtotal", value=100000.0)
        with t2:
            cgst = st.number_input("CGST", value=9000.0)
        with t3:
            sgst = st.number_input("SGST", value=9000.0)
        t4, t5 = st.columns(2, gap="medium")
        with t4:
            igst = st.number_input("IGST", value=0.0)
        with t5:
            tot = st.number_input("Total", value=118000.0)
        if st.form_submit_button("Save invoice", type="primary", use_container_width=True):
            try:
                assert_entry_date_allowed(_cid(), dt, role_inv)
                civil_store.invoice_add(
                    _cid(),
                    {
                        "invoice_no": no,
                        "invoice_date": dt,
                        "project_code": pc,
                        "client_name": cl,
                        "sub_total": float(sub),
                        "cgst": float(cgst),
                        "sgst": float(sgst),
                        "igst": float(igst),
                        "total": float(tot),
                        "status": "Draft",
                    },
                )
                st.rerun()
            except ValueError as ex:
                st.error(str(ex))


def page_dashboard(u: dict) -> None:
    c1, c2, c3 = st.columns([1, 1, 1])
    ps = c1.date_input("Period start", value=date(2026, 4, 1), key="ds")
    pe = c2.date_input("Period end", value=date(2026, 4, 30), key="de")
    if c3.button("Refresh metrics", type="secondary", use_container_width=True, help="Reload numbers from the database"):
        st.rerun()
    s = civil_store.dashboard_stats(_cid(), ps, pe)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projects (total)", s["projects_total"])
    m2.metric("Active projects", s["projects_active"])
    m3.metric("Active workers", s["workers_active"])
    m4.metric("Present rows (period)", s["attendance_present_rows"])
    st.metric("Approved expenses (period)", f"₹ {s['approved_expenses_sum']:,.2f}")
