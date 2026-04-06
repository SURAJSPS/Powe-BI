"""Application pages (Mongo-backed)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Callable

import pandas as pd
import streamlit as st

from core.roles import ROLE_LABELS, ROLES, can_access
from services import auth_service, civil_store
from ui.theme import hero


def _user() -> dict:
    return st.session_state["user"]


def _cid() -> str:
    return _user()["company_id"]


def page_home(u: dict) -> None:
    hero("RNK Civil Operations", "Company workspace — projects, site labour, attendance, payroll & billing.")
    c1, c2, c3 = st.columns(3)
    c1.markdown('<div class="rnk-card"><strong>Company</strong><br/>' + u.get("company_name", "") + "</div>", unsafe_allow_html=True)
    c2.markdown('<div class="rnk-card"><strong>Your role</strong><br/>' + ROLE_LABELS.get(u.get("role", ""), u.get("role", "")) + "</div>", unsafe_allow_html=True)
    c3.markdown('<div class="rnk-card"><strong>Signed in as</strong><br/>' + u.get("email", "") + "</div>", unsafe_allow_html=True)
    st.info("Use the sidebar to open modules. Access depends on your role.")


def page_company(u: dict) -> None:
    st.subheader("Company profile")
    c = auth_service.get_company(_cid())
    if not c:
        st.error("Company not found.")
        return
    with st.form("co"):
        name = st.text_input("Display name", value=c.get("name", ""))
        legal = st.text_input("Legal name", value=c.get("legal_name", ""))
        gstin = st.text_input("GSTIN (optional)", value=c.get("gstin") or "")
        addr = st.text_area("Address (optional)", value=c.get("address") or "")
        if st.form_submit_button("Save"):
            auth_service.update_company(_cid(), name=name, legal_name=legal, gstin=gstin or None, address=addr or None)
            st.success("Saved.")
            st.rerun()


def page_team(u: dict) -> None:
    st.subheader("Users & employees")
    t1, t2 = st.tabs(["App users (login)", "Employees (directory)"])
    with t1:
        users = auth_service.list_users(_cid())
        st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
        if u.get("role") == "company_admin":
            with st.expander("Invite app user"):
                with st.form("nu"):
                    em = st.text_input("Email")
                    fn = st.text_input("Full name")
                    pw = st.text_input("Temporary password", type="password")
                    role = st.selectbox("Role", ROLES, index=min(3, len(ROLES) - 1))
                    if st.form_submit_button("Create user"):
                        try:
                            auth_service.add_user(_cid(), em, pw, fn, role)
                            st.success("User created.")
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))
            st.caption("New users receive the role you assign. Ask them to change password after first login (future enhancement).")
    with t2:
        emps = civil_store.employees_list(_cid())
        st.dataframe(pd.DataFrame(emps) if emps else pd.DataFrame(), use_container_width=True, hide_index=True)
        with st.form("ne"):
            code = st.text_input("Employee code", value="EMP-")
            name = st.text_input("Full name")
            dept = st.text_input("Department")
            title = st.text_input("Job title")
            ph = st.text_input("Phone")
            if st.form_submit_button("Add employee"):
                civil_store.employee_add(_cid(), code, name, department=dept or None, role_title=title or None, phone=ph or None)
                st.rerun()


def page_clients(u: dict) -> None:
    st.subheader("Clients")
    rows = civil_store.clients_list(_cid())
    st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(), use_container_width=True, hide_index=True)
    with st.form("cl"):
        n = st.text_input("Client name")
        gst = st.text_input("GSTIN")
        cp = st.text_input("Contact person")
        ph = st.text_input("Phone")
        if st.form_submit_button("Add client"):
            civil_store.client_add(_cid(), n, gstin=gst or None, contact_person=cp or None, phone=ph or None)
            st.rerun()


def page_ot_rules(u: dict) -> None:
    st.subheader("OT rules")
    rows = civil_store.ot_rules_list(_cid())
    st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame(), use_container_width=True, hide_index=True)
    with st.form("ot"):
        rid = st.text_input("Rule ID", value="OT-STD")
        name = st.text_input("Name", value="Standard")
        mult = st.number_input("Multiplier", value=2.0)
        mx = st.number_input("Max OT hrs/day", value=4.0)
        notes = st.text_input("Notes", value="")
        if st.form_submit_button("Save rule"):
            civil_store.ot_rule_add(_cid(), rid, name, mult, mx, notes)
            st.rerun()


def page_projects_sites(u: dict) -> None:
    st.subheader("Projects & sites")
    a, b = st.tabs(["Projects", "Sites"])
    with a:
        st.dataframe(pd.DataFrame(civil_store.projects_list(_cid())), use_container_width=True, hide_index=True)
        with st.form("pj"):
            code = st.text_input("Project code", value="PRJ-")
            name = st.text_input("Name")
            client = st.text_input("Client name (text)")
            status = st.selectbox("Status", ["Planning", "Active", "On Hold", "Completed", "Archived"])
            budget = st.number_input("Budget", value=0.0)
            if st.form_submit_button("Save project"):
                civil_store.project_add(
                    _cid(),
                    {"project_code": code, "name": name, "client_name": client, "status": status, "budget": budget},
                )
                st.rerun()
    with b:
        st.dataframe(pd.DataFrame(civil_store.sites_list(_cid())), use_container_width=True, hide_index=True)
        with st.form("st"):
            sc = st.text_input("Site code", value="S-")
            sn = st.text_input("Site name")
            loc = st.text_input("Location")
            pcs = [p["project_code"] for p in civil_store.projects_list(_cid())]
            pc = st.selectbox("Project", pcs or ["—"])
            if st.form_submit_button("Save site") and pcs:
                # resolve project id
                plist = civil_store.projects_list(_cid())
                pid = next((x for x in plist if x["project_code"] == pc), None)
                civil_store.site_add(
                    _cid(),
                    {
                        "site_code": sc,
                        "name": sn,
                        "location": loc,
                        "active": True,
                        "project_code": pc,
                        "project_id": str(pid["_id"]) if pid else "",
                    },
                )
                st.rerun()


def page_workers(u: dict) -> None:
    st.subheader("Workers (site labour)")
    st.dataframe(pd.DataFrame(civil_store.workers_list(_cid())), use_container_width=True, hide_index=True)
    rules = [r["rule_id"] for r in civil_store.ot_rules_list(_cid())]
    with st.form("wk"):
        wid = st.text_input("Worker ID", value="W-")
        fn = st.text_input("Full name")
        pt = st.selectbox("Pay type", ["Daily", "Monthly"])
        dr = st.number_input("Daily rate", value=0.0)
        mg = st.number_input("Monthly gross", value=0.0)
        otr = st.selectbox("OT rule", rules or ["OT-STD"])
        if st.form_submit_button("Save worker"):
            civil_store.worker_add(
                _cid(),
                {
                    "worker_id": wid,
                    "full_name": fn,
                    "pay_type": pt,
                    "daily_rate": dr if pt == "Daily" else None,
                    "monthly_gross": mg if pt == "Monthly" else None,
                    "ot_rule_id": otr,
                    "active": True,
                },
            )
            st.rerun()


def page_attendance(u: dict) -> None:
    st.subheader("Attendance")
    st.dataframe(pd.DataFrame(civil_store.attendance_list(_cid())), use_container_width=True, hide_index=True)
    wids = [w["worker_id"] for w in civil_store.workers_list(_cid())]
    pids = [p["project_code"] for p in civil_store.projects_list(_cid())]
    sids = [s["site_code"] for s in civil_store.sites_list(_cid())]
    with st.form("at"):
        d = st.date_input("Date", value=date.today())
        w = st.selectbox("Worker", wids or ["—"])
        p = st.selectbox("Project", pids or ["—"])
        s = st.selectbox("Site", sids or ["—"])
        stt = st.selectbox("Status", ["Present", "Absent", "Leave", "Holiday", "Half-day"])
        nh = st.number_input("Normal hrs", value=8.0)
        oh = st.number_input("OT hrs", value=0.0)
        if st.form_submit_button("Add row") and wids:
            civil_store.attendance_add(
                _cid(),
                {"work_date": d, "worker_id": w, "project_code": p, "site_code": s, "status": stt, "normal_hrs": nh, "ot_hrs": oh},
            )
            st.rerun()


def page_expenses(u: dict) -> None:
    st.subheader("Expenses")
    st.dataframe(pd.DataFrame(civil_store.expenses_list(_cid())), use_container_width=True, hide_index=True)
    pids = [p["project_code"] for p in civil_store.projects_list(_cid())]
    with st.form("ex"):
        ed = st.date_input("Date", value=date.today())
        pc = st.selectbox("Project", pids or ["—"])
        cat = st.text_input("Category", value="Petty cash")
        amt = st.number_input("Amount", value=0.0)
        gst = st.number_input("GST", value=0.0)
        ven = st.text_input("Vendor")
        ap = st.checkbox("Approved", value=False)
        if st.form_submit_button("Add") and pids:
            civil_store.expense_add(
                _cid(),
                {"expense_date": ed, "project_code": pc, "category": cat, "amount": float(amt), "gst_amount": float(gst), "vendor": ven, "approved": ap},
            )
            st.rerun()


def page_payroll_est(u: dict) -> None:
    st.subheader("Payroll estimate")
    c1, c2 = st.columns(2)
    ps = c1.date_input("Start", value=date(2026, 4, 1), key="pes")
    pe = c2.date_input("End", value=date(2026, 4, 30), key="pee")
    df = civil_store.payroll_estimate_df(_cid(), ps, pe)
    st.dataframe(df, use_container_width=True, hide_index=True)


def page_payroll_runs(u: dict) -> None:
    st.subheader("Payroll runs & lines")
    st.dataframe(pd.DataFrame(civil_store.payroll_runs_list(_cid())), use_container_width=True, hide_index=True)
    st.dataframe(pd.DataFrame(civil_store.payroll_lines_list(_cid())), use_container_width=True, hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        with st.form("pr"):
            rid = st.text_input("Run ID", value=f"RUN-{datetime.now().strftime('%Y%m')}")
            pl = st.text_input("Label", value="Apr-2026")
            a = st.date_input("Start", value=date(2026, 4, 1))
            b = st.date_input("End", value=date(2026, 4, 30))
            if st.form_submit_button("Save run"):
                civil_store.payroll_run_add(_cid(), {"run_id": rid, "period_label": pl, "period_start": a, "period_end": b, "status": "Draft"})
                st.rerun()
    with c2:
        runs = [r["run_id"] for r in civil_store.payroll_runs_list(_cid())]
        wids = [w["worker_id"] for w in civil_store.workers_list(_cid())]
        with st.form("pl"):
            rr = st.selectbox("Run", runs or ["—"])
            ww = st.selectbox("Worker", wids or ["—"])
            comp = st.text_input("Component", value="Gross_Est")
            amt = st.number_input("Amount", value=0.0)
            if st.form_submit_button("Add line") and runs and wids:
                civil_store.payroll_line_add(_cid(), {"run_id": rr, "worker_id": ww, "component": comp, "amount": float(amt), "statutory_tag": "Earning"})
                st.rerun()


def page_invoices(u: dict) -> None:
    st.subheader("Invoices")
    st.dataframe(pd.DataFrame(civil_store.invoices_list(_cid())), use_container_width=True, hide_index=True)
    with st.form("inv"):
        no = st.text_input("Invoice no", value="INV-2026-001")
        dt = st.date_input("Date", value=date.today())
        pc = st.text_input("Project code", value="PRJ-001")
        cl = st.text_input("Client name")
        sub = st.number_input("Subtotal", value=100000.0)
        cgst = st.number_input("CGST", value=9000.0)
        sgst = st.number_input("SGST", value=9000.0)
        igst = st.number_input("IGST", value=0.0)
        tot = st.number_input("Total", value=118000.0)
        if st.form_submit_button("Save invoice"):
            civil_store.invoice_add(
                _cid(),
                {
                    "invoice_no": no,
                    "invoice_date": dt,
                    "project_code": pc,
                    "client_name": cl or "Client",
                    "sub_total": float(sub),
                    "cgst": float(cgst),
                    "sgst": float(sgst),
                    "igst": float(igst),
                    "total": float(tot),
                    "status": "Draft",
                },
            )
            st.rerun()


def page_dashboard(u: dict) -> None:
    st.subheader("Dashboard")
    c1, c2 = st.columns(2)
    ps = c1.date_input("Period start", value=date(2026, 4, 1), key="ds")
    pe = c2.date_input("Period end", value=date(2026, 4, 30), key="de")
    s = civil_store.dashboard_stats(_cid(), ps, pe)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Projects (total)", s["projects_total"])
    m2.metric("Active projects", s["projects_active"])
    m3.metric("Active workers", s["workers_active"])
    m4.metric("Present rows (period)", s["attendance_present_rows"])
    st.metric("Approved expenses (period)", f"₹ {s['approved_expenses_sum']:,.2f}")


# map page key -> (title, renderer)
PAGE_FUNCS: dict[str, tuple[str, Callable[..., None]]] = {
    "home": ("Home", page_home),
    "company": ("Company", page_company),
    "team": ("Team & employees", page_team),
    "clients": ("Clients", page_clients),
    "ot_rules": ("OT rules", page_ot_rules),
    "projects": ("Projects & sites", page_projects_sites),
    "workers": ("Workers", page_workers),
    "attendance": ("Attendance", page_attendance),
    "expenses": ("Expenses", page_expenses),
    "payroll_est": ("Payroll estimate", page_payroll_est),
    "payroll_runs": ("Payroll runs", page_payroll_runs),
    "invoices": ("Invoices", page_invoices),
    "dashboard": ("Dashboard", page_dashboard),
}


def sidebar_nav(role: str) -> str | None:
    keys = [k for k in PAGE_FUNCS if can_access(role, k)]
    if not keys:
        return None
    return st.sidebar.radio(
        "Navigate",
        keys,
        format_func=lambda k: PAGE_FUNCS[k][0],
        label_visibility="collapsed",
    )
