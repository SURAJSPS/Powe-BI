"""
RNK Civil — local web app (Streamlit + SQLite).
Run:  cd python_app && streamlit run app.py
Or from repo root:  PYTHONPATH=python_app streamlit run python_app/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
if str(_APP_DIR) not in sys.path:
    sys.path.insert(0, str(_APP_DIR))

from datetime import date, datetime

import pandas as pd
import streamlit as st
from sqlalchemy import func, select

from database import DATA_PATH, get_session, init_db, seed_if_empty
from models import Attendance, Expense, Invoice, OTRule, PayrollLine, PayrollRun, Project, Site, Worker

st.set_page_config(page_title="RNK Civil Operations", layout="wide")


@st.cache_resource
def _setup():
    init_db()
    seed_if_empty()
    return True


_setup()


def df_projects(s: Session) -> pd.DataFrame:
    rows = s.scalars(select(Project).order_by(Project.project_code)).all()
    return pd.DataFrame(
        [
            {
                "id": r.id,
                "project_code": r.project_code,
                "name": r.name,
                "client": r.client_name,
                "status": r.status,
                "budget": r.budget,
            }
            for r in rows
        ]
    )


def df_workers(s: Session) -> pd.DataFrame:
    rows = s.scalars(select(Worker).order_by(Worker.worker_id)).all()
    return pd.DataFrame(
        [
            {
                "id": r.id,
                "worker_id": r.worker_id,
                "full_name": r.full_name,
                "pay_type": r.pay_type,
                "daily_rate": r.daily_rate,
                "monthly_gross": r.monthly_gross,
                "active": r.active,
            }
            for r in rows
        ]
    )


def page_home():
    st.title("RNK Civil Operations")
    st.caption("Python + SQLite + Streamlit — local use. DB file: `" + str(DATA_PATH) + "`")
    st.markdown(
        """
- **Master data:** OT rules, projects, sites, workers  
- **Operations:** attendance, expenses  
- **Payroll / billing:** payroll runs & lines, invoices (simplified)  
- **Dashboard:** counts and period totals  

**Note:** Not a substitute for statutory payroll software — validate with your CA.
        """
    )


def page_ot_rules():
    st.header("OT rules")
    with get_session() as s:
        rows = s.scalars(select(OTRule)).all()
        st.dataframe(
            pd.DataFrame([{c: getattr(r, c) for c in ("rule_id", "rule_name", "multiplier", "max_ot_hrs_per_day", "notes")} for r in rows]),
            use_container_width=True,
        )
    with st.form("add_ot"):
        rid = st.text_input("Rule ID", value="OT-NEW")
        name = st.text_input("Name")
        mult = st.number_input("Multiplier", value=2.0)
        max_ot = st.number_input("Max OT hrs/day", value=4.0)
        if st.form_submit_button("Add"):
            with get_session() as s:
                s.add(OTRule(rule_id=rid, rule_name=name, multiplier=float(mult), max_ot_hrs_per_day=float(max_ot)))
                s.commit()
            st.success("Saved.")
            st.rerun()


def page_projects_sites():
    st.header("Projects & sites")
    tab1, tab2 = st.tabs(["Projects", "Sites"])
    with tab1:
        with get_session() as s:
            st.dataframe(df_projects(s), use_container_width=True)
        with st.form("add_proj"):
            code = st.text_input("Project code", value="PRJ-")
            name = st.text_input("Project name")
            client = st.text_input("Client")
            status = st.selectbox("Status", ["Planning", "Active", "On Hold", "Completed", "Archived"])
            budget = st.number_input("Budget", value=0.0)
            if st.form_submit_button("Add project"):
                with get_session() as s:
                    s.add(Project(project_code=code, name=name, client_name=client or None, status=status, budget=budget or None))
                    s.commit()
                st.rerun()
    with tab2:
        with get_session() as s:
            projects = s.scalars(select(Project)).all()
            pmap = {p.name: p.id for p in projects}
            sites = s.scalars(select(Site)).all()
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "site_code": x.site_code,
                            "name": x.name,
                            "project_id": x.project_id,
                            "location": x.location,
                            "active": x.active,
                        }
                        for x in sites
                    ]
                ),
                use_container_width=True,
            )
            pname = st.selectbox("Project", list(pmap.keys()) or ["—"])
            with st.form("add_site"):
                sc = st.text_input("Site code", value="S-")
                sn = st.text_input("Site name")
                loc = st.text_input("Location")
                if st.form_submit_button("Add site") and pname != "—":
                    with get_session() as s2:
                        s2.add(Site(site_code=sc, project_id=pmap[pname], name=sn, location=loc or None, active=True))
                        s2.commit()
                    st.rerun()


def page_workers():
    st.header("Workers")
    with get_session() as s:
        st.dataframe(df_workers(s), use_container_width=True)
        rules = [r.rule_id for r in s.scalars(select(OTRule)).all()]
    with st.form("add_worker"):
        c1, c2 = st.columns(2)
        wid = c1.text_input("Worker ID", value="W-")
        fn = c2.text_input("Full name")
        pt = c1.selectbox("Pay type", ["Daily", "Monthly"])
        dr = c2.number_input("Daily rate", value=0.0)
        mg = c1.number_input("Monthly gross", value=0.0)
        otr = c2.selectbox("OT rule", rules or [None])
        if st.form_submit_button("Add worker"):
            with get_session() as s:
                s.add(
                    Worker(
                        worker_id=wid,
                        full_name=fn,
                        pay_type=pt,
                        daily_rate=dr if pt == "Daily" else None,
                        monthly_gross=mg if pt == "Monthly" else None,
                        ot_rule_id=otr,
                        active=True,
                    )
                )
                s.commit()
            st.rerun()


def page_attendance():
    st.header("Attendance")
    with get_session() as s:
        wids = [w.worker_id for w in s.scalars(select(Worker)).all()]
        pids = [p.project_code for p in s.scalars(select(Project)).all()]
        sids = [x.site_code for x in s.scalars(select(Site)).all()]
        rows = s.scalars(select(Attendance).order_by(Attendance.work_date.desc())).all()
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "id": r.id,
                        "work_date": r.work_date,
                        "worker_id": r.worker_id,
                        "project_code": r.project_code,
                        "site_code": r.site_code,
                        "status": r.status,
                        "normal_hrs": r.normal_hrs,
                        "ot_hrs": r.ot_hrs,
                    }
                    for r in rows[:200]
                ]
            ),
            use_container_width=True,
        )
    with st.form("add_att"):
        d = st.date_input("Date", value=date.today())
        w = st.selectbox("Worker", wids or ["—"])
        p = st.selectbox("Project", pids or ["—"])
        si = st.selectbox("Site", sids or ["—"])
        stt = st.selectbox("Status", ["Present", "Absent", "Leave", "Holiday", "Half-day"])
        nh = st.number_input("Normal hrs", value=8.0)
        oh = st.number_input("OT hrs", value=0.0)
        if st.form_submit_button("Add") and w != "—":
            with get_session() as s:
                s.add(
                    Attendance(
                        work_date=d,
                        worker_id=w,
                        project_code=p,
                        site_code=si,
                        status=stt,
                        normal_hrs=float(nh),
                        ot_hrs=float(oh),
                    )
                )
                s.commit()
            st.rerun()


def page_expenses():
    st.header("Expenses")
    with get_session() as s:
        pids = [p.project_code for p in s.scalars(select(Project)).all()]
        rows = s.scalars(select(Expense).order_by(Expense.expense_date.desc())).all()
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "id": r.id,
                        "expense_date": r.expense_date,
                        "project_code": r.project_code,
                        "category": r.category,
                        "amount": r.amount,
                        "gst_amount": r.gst_amount,
                        "vendor": r.vendor,
                        "approved": r.approved,
                    }
                    for r in rows
                ]
            ),
            use_container_width=True,
        )
    with st.form("add_ex"):
        ed = st.date_input("Expense date", value=date.today())
        pc = st.selectbox("Project", pids or ["—"])
        cat = st.text_input("Category", value="Petty cash")
        amt = st.number_input("Amount", value=0.0)
        gst = st.number_input("GST amount", value=0.0)
        ven = st.text_input("Vendor")
        ap = st.checkbox("Approved", value=False)
        if st.form_submit_button("Add") and pc != "—":
            with get_session() as s:
                s.add(
                    Expense(
                        expense_date=ed,
                        project_code=pc,
                        category=cat,
                        amount=float(amt),
                        gst_amount=float(gst),
                        vendor=ven or None,
                        approved=ap,
                    )
                )
                s.commit()
            st.rerun()


def page_payroll():
    st.header("Payroll runs & lines")
    c1, _ = st.columns(2)
    with c1:
        with st.form("add_run"):
            rid = st.text_input("Run ID", value=f"RUN-{datetime.now().strftime('%Y%m')}")
            plab = st.text_input("Period label", value="Apr-2026")
            ps = st.date_input("Period start", value=date(2026, 4, 1))
            pe = st.date_input("Period end", value=date(2026, 4, 30))
            if st.form_submit_button("Create run"):
                with get_session() as s:
                    s.add(PayrollRun(run_id=rid, period_label=plab, period_start=ps, period_end=pe, status="Draft"))
                    s.commit()
                st.rerun()
    with get_session() as s:
        st.subheader("Runs")
        st.dataframe(
            pd.DataFrame(
                [
                    {"run_id": r.run_id, "period": r.period_label, "start": r.period_start, "end": r.period_end, "status": r.status}
                    for r in s.scalars(select(PayrollRun)).all()
                ]
            ),
            use_container_width=True,
        )
        runs = [r.run_id for r in s.scalars(select(PayrollRun)).all()]
        wids = [w.worker_id for w in s.scalars(select(Worker)).all()]
        lines = s.scalars(select(PayrollLine)).all()
    st.dataframe(
        pd.DataFrame([{"run_id": r.run_id, "worker_id": r.worker_id, "component": r.component, "amount": r.amount} for r in lines]),
        use_container_width=True,
    )
    with st.form("add_line"):
        rr = st.selectbox("Run", runs or ["—"])
        ww = st.selectbox("Worker", wids or ["—"])
        comp = st.text_input("Component", value="Gross_Est")
        amt = st.number_input("Amount", value=0.0)
        tag = st.text_input("Statutory tag", value="Earning")
        if st.form_submit_button("Add line") and rr != "—" and ww != "—":
            with get_session() as s:
                s.add(PayrollLine(run_id=rr, worker_id=ww, component=comp, amount=float(amt), statutory_tag=tag))
                s.commit()
            st.rerun()


def page_invoices():
    st.header("Invoices & lines")
    with st.form("add_inv"):
        inv = st.text_input("Invoice no", value="INV-2026-001")
        idt = st.date_input("Date", value=date.today())
        pc = st.text_input("Project code", value="PRJ-001")
        cl = st.text_input("Client")
        sub = st.number_input("Subtotal", value=100000.0)
        cgst = st.number_input("CGST", value=9000.0)
        sgst = st.number_input("SGST", value=9000.0)
        igst = st.number_input("IGST", value=0.0)
        tot = st.number_input("Total", value=118000.0)
        if st.form_submit_button("Add invoice"):
            with get_session() as s:
                s.add(
                    Invoice(
                        invoice_no=inv,
                        invoice_date=idt,
                        project_code=pc,
                        client_name=cl or "Client",
                        sub_total=float(sub),
                        cgst=float(cgst),
                        sgst=float(sgst),
                        igst=float(igst),
                        total=float(tot),
                        status="Draft",
                    )
                )
                s.commit()
            st.rerun()
    with get_session() as s:
        st.dataframe(
            pd.DataFrame(
                [
                    {
                        "invoice_no": r.invoice_no,
                        "date": r.invoice_date,
                        "project": r.project_code,
                        "total": r.total,
                        "status": r.status,
                    }
                    for r in s.scalars(select(Invoice)).all()
                ]
            ),
            use_container_width=True,
        )


def page_dashboard():
    st.header("Dashboard")
    p_start = st.date_input("Period start", value=date(2026, 4, 1), key="d1")
    p_end = st.date_input("Period end", value=date(2026, 4, 30), key="d2")
    with get_session() as s:
        n_proj = s.scalar(select(func.count()).select_from(Project)) or 0
        n_act = s.scalar(select(func.count()).select_from(Project).where(Project.status == "Active")) or 0
        n_w = s.scalar(select(func.count()).select_from(Worker).where(Worker.active.is_(True))) or 0
        att = s.scalars(
            select(Attendance).where(Attendance.work_date >= p_start, Attendance.work_date <= p_end, Attendance.status == "Present")
        ).all()
        exp = s.scalars(
            select(Expense).where(Expense.expense_date >= p_start, Expense.expense_date <= p_end, Expense.approved.is_(True))
        ).all()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Projects (total)", n_proj or 0)
    c2.metric("Active projects", n_act or 0)
    c3.metric("Active workers", n_w or 0)
    c4.metric("Present attendance rows (period)", len(att))
    st.metric("Approved expenses (period)", sum(e.amount for e in exp))
    st.caption("Connect Power BI to SQLite later, or export CSV from each table.")


def page_payroll_estimate():
    st.header("Payroll estimate (from attendance)")
    st.caption("Simplified: Daily = paid days × rate + OT; Monthly = gross/26 × paid days + OT (adjust policy as needed).")
    p_start = st.date_input("Start", value=date(2026, 4, 1), key="pe1")
    p_end = st.date_input("End", value=date(2026, 4, 30), key="pe2")
    with get_session() as s:
        workers = {w.worker_id: w for w in s.scalars(select(Worker)).all()}
        rules = {r.rule_id: r for r in s.scalars(select(OTRule)).all()}
        att_rows = s.scalars(
            select(Attendance).where(Attendance.work_date >= p_start, Attendance.work_date <= p_end)
        ).all()
    paid = {}
    ot_h = {}
    for a in att_rows:
        if a.status != "Present":
            continue
        paid[a.worker_id] = paid.get(a.worker_id, 0) + 1
        ot_h[a.worker_id] = ot_h.get(a.worker_id, 0.0) + float(a.ot_hrs)
    out = []
    for wid, days in paid.items():
        w = workers.get(wid)
        if not w:
            continue
        mult = rules[w.ot_rule_id].multiplier if w.ot_rule_id and w.ot_rule_id in rules else 2.0
        dr = float(w.daily_rate or 0)
        mg = float(w.monthly_gross or 0)
        ot_pay = ot_h.get(wid, 0.0) * (dr / 8.0) * mult if w.pay_type == "Daily" else ot_h.get(wid, 0.0) * (mg / 26.0 / 8.0) * mult
        if w.pay_type == "Daily":
            base = days * dr
        else:
            base = mg / 26.0 * min(days, 26)
        out.append({"worker_id": wid, "paid_days": days, "ot_hrs": ot_h.get(wid, 0), "est_base": base, "est_ot": ot_pay, "est_gross": base + ot_pay})
    st.dataframe(pd.DataFrame(out), use_container_width=True)


# --- Router ---
PAGES = {
    "Home": page_home,
    "OT rules": page_ot_rules,
    "Projects & sites": page_projects_sites,
    "Workers": page_workers,
    "Attendance": page_attendance,
    "Expenses": page_expenses,
    "Payroll estimate": page_payroll_estimate,
    "Payroll runs": page_payroll,
    "Invoices": page_invoices,
    "Dashboard": page_dashboard,
}

choice = st.sidebar.radio("Navigate", list(PAGES.keys()))
PAGES[choice]()
