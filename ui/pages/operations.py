"""Attendance and expenses."""
from __future__ import annotations
from datetime import date

import streamlit as st

from services import auth_service, civil_store
from services.entry_policy import assert_entry_date_allowed, clamp_entry_day, entry_date_window
from ui.pages.common import _cid, dataframe_for_records
from ui.pages.form_ui import required_label, required_legend
from ui.theme import empty_state

def page_attendance(u: dict) -> None:
    alist = civil_store.attendance_list(_cid())
    wmap = {w["worker_id"]: (w.get("full_name") or "").strip() for w in civil_store.workers_list(_cid())}
    enriched: list[dict] = []
    for row in alist:
        r = dict(row)
        wid = r.get("worker_id")
        if wid and wmap.get(wid):
            r["worker_name"] = wmap[wid]
        enriched.append(r)
    df_a = dataframe_for_records(enriched)
    if df_a.empty:
        empty_state("No attendance rows", "Log days once workers and sites exist.")
    else:
        st.dataframe(df_a, use_container_width=True, hide_index=True)
    wids = [w["worker_id"] for w in civil_store.workers_list(_cid())]
    pids = [p["project_code"] for p in civil_store.projects_list(_cid())]
    sids = [s["site_code"] for s in civil_store.sites_list(_cid())]
    co = auth_service.get_company(_cid())
    role = u.get("role", "viewer")
    min_d, max_d = entry_date_window(co or {}, role) if co else (None, None)
    default_d = clamp_entry_day(date.today(), min_d, max_d)
    with st.form("at"):
        required_legend()
        d_kw: dict = {"label": "Date", "value": default_d}
        if min_d is not None:
            d_kw["min_value"] = min_d
        if max_d is not None:
            d_kw["max_value"] = max_d
        d = st.date_input(**d_kw)
        w1, w2 = st.columns(2, gap="medium")
        with w1:
            required_label("Worker")
            w = st.selectbox("Worker", wids or ["—"], label_visibility="collapsed")
        with w2:
            required_label("Project")
            p = st.selectbox("Project", pids or ["—"], label_visibility="collapsed")
        s1, s2 = st.columns(2, gap="medium")
        with s1:
            required_label("Site")
            s = st.selectbox("Site", sids or ["—"], label_visibility="collapsed")
        with s2:
            stt = st.selectbox("Status", ["Present", "Absent", "Leave", "Holiday", "Half-day"])
        h1, h2 = st.columns(2, gap="medium")
        with h1:
            nh = st.number_input("Normal hrs", value=8.0)
        with h2:
            oh = st.number_input("OT hrs", value=0.0)
        if st.form_submit_button("Add row", type="primary", use_container_width=True) and wids:
            try:
                assert_entry_date_allowed(_cid(), d, role)
                civil_store.attendance_add(
                    _cid(),
                    {"work_date": d, "worker_id": w, "project_code": p, "site_code": s, "status": stt, "normal_hrs": nh, "ot_hrs": oh},
                )
                st.rerun()
            except ValueError as ex:
                st.error(str(ex))


def page_expenses(u: dict) -> None:
    elist = civil_store.expenses_list(_cid())
    df_e = dataframe_for_records(elist)
    if df_e.empty:
        empty_state("No expenses", "Record petty cash and job costs against a project.")
    else:
        st.dataframe(df_e, use_container_width=True, hide_index=True)
    pids = [p["project_code"] for p in civil_store.projects_list(_cid())]
    co = auth_service.get_company(_cid())
    role = u.get("role", "viewer")
    min_d, max_d = entry_date_window(co or {}, role) if co else (None, None)
    default_ed = clamp_entry_day(date.today(), min_d, max_d)
    with st.form("ex"):
        required_legend()
        ed_kw: dict = {"label": "Date", "value": default_ed}
        if min_d is not None:
            ed_kw["min_value"] = min_d
        if max_d is not None:
            ed_kw["max_value"] = max_d
        ed = st.date_input(**ed_kw)
        e1, e2 = st.columns(2, gap="medium")
        with e1:
            required_label("Project")
            pc = st.selectbox("Project", pids or ["—"], label_visibility="collapsed")
        with e2:
            required_label("Category")
            cat = st.text_input("Category", value="Petty cash", label_visibility="collapsed")
        e3, e4 = st.columns(2, gap="medium")
        with e3:
            amt = st.number_input("Amount", value=0.0)
        with e4:
            gst = st.number_input("GST", value=0.0)
        ven = st.text_input("Vendor")
        ap = st.checkbox("Approved", value=False)
        if st.form_submit_button("Add expense", type="primary", use_container_width=True) and pids:
            try:
                assert_entry_date_allowed(_cid(), ed, role)
                civil_store.expense_add(
                    _cid(),
                    {"expense_date": ed, "project_code": pc, "category": cat, "amount": float(amt), "gst_amount": float(gst), "vendor": ven, "approved": ap},
                )
                st.rerun()
            except ValueError as ex:
                st.error(str(ex))
