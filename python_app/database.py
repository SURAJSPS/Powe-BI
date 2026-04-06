"""SQLite engine, session, init, optional seed."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from models import (
    Attendance,
    Base,
    Expense,
    Invoice,
    InvoiceLine,
    OTRule,
    PayrollLine,
    PayrollRun,
    Project,
    Site,
    Worker,
)

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "rnk_civil.db"
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

ENGINE = create_engine(
    f"sqlite:///{DATA_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)


def init_db() -> None:
    Base.metadata.create_all(bind=ENGINE)


def get_session() -> Session:
    return SessionLocal()


def seed_if_empty() -> None:
    """Load demo rows when DB is empty."""
    with get_session() as s:
        if s.scalars(select(OTRule).limit(1)).first() is not None:
            return
        s.add(
            OTRule(
                rule_id="OT-STD",
                rule_name="Standard double OT",
                multiplier=2.0,
                max_ot_hrs_per_day=4.0,
                notes="Demo",
            )
        )
        p = Project(
            project_code="PRJ-001",
            name="NH Road Package A",
            client_name="NHAI",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            status="Active",
            budget=5_000_000.0,
            description="Demo project",
        )
        s.add(p)
        s.flush()
        s.add(
            Site(
                site_code="S-001",
                project_id=p.id,
                name="Km 12–15 Site Office",
                location="NH-44",
                active=True,
            )
        )
        s.add(
            Worker(
                worker_id="W-001",
                full_name="Ramesh Kumar",
                phone="9876500001",
                pay_type="Daily",
                daily_rate=800.0,
                monthly_gross=None,
                ot_rule_id="OT-STD",
                skill="Mason",
                india_state="Maharashtra",
                active=True,
                primary_project_code="PRJ-001",
            )
        )
        s.add(
            Worker(
                worker_id="W-002",
                full_name="Suresh Patil",
                pay_type="Monthly",
                daily_rate=None,
                monthly_gross=22000.0,
                ot_rule_id="OT-STD",
                skill="Supervisor",
                india_state="Maharashtra",
                pan="ABCDE1234F",
                active=True,
                primary_project_code="PRJ-001",
            )
        )
        s.add(
            Attendance(
                work_date=date(2026, 4, 1),
                worker_id="W-001",
                project_code="PRJ-001",
                site_code="S-001",
                status="Present",
                normal_hrs=8.0,
                ot_hrs=2.0,
            )
        )
        s.add(
            Expense(
                expense_date=date(2026, 4, 3),
                project_code="PRJ-001",
                category="Petty cash",
                amount=3500.0,
                gst_amount=0.0,
                vendor="Local",
                approved=True,
            )
        )
        s.commit()
