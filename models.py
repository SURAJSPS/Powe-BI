"""SQLAlchemy models — RNK Civil (all phases, simplified)."""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class OTRule(Base):
    __tablename__ = "ot_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rule_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    rule_name: Mapped[str] = mapped_column(String(200))
    multiplier: Mapped[float] = mapped_column(Float, default=2.0)
    max_ot_hrs_per_day: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(300))
    client_name: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="Planning")
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    sites: Mapped[list["Site"]] = relationship(back_populates="project")


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    site_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String(300))
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped["Project"] = relationship(back_populates="sites")


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    worker_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(300))
    phone: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    pay_type: Mapped[str] = mapped_column(String(20))
    daily_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    monthly_gross: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ot_rule_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    skill: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    india_state: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    primary_project_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class Attendance(Base):
    __tablename__ = "attendance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    work_date: Mapped[date] = mapped_column(Date, index=True)
    worker_id: Mapped[str] = mapped_column(String(64), index=True)
    project_code: Mapped[str] = mapped_column(String(64))
    site_code: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(40), default="Present")
    normal_hrs: Mapped[float] = mapped_column(Float, default=8.0)
    ot_hrs: Mapped[float] = mapped_column(Float, default=0.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_utcnow)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    expense_date: Mapped[date] = mapped_column(Date, index=True)
    project_code: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(120))
    amount: Mapped[float] = mapped_column(Float)
    gst_amount: Mapped[float] = mapped_column(Float, default=0.0)
    vendor: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    bill_ref: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    period_label: Mapped[str] = mapped_column(String(80))
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(40), default="Draft")
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PayrollLine(Base):
    __tablename__ = "payroll_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(String(64), index=True)
    worker_id: Mapped[str] = mapped_column(String(64), index=True)
    component: Mapped[str] = mapped_column(String(80))
    amount: Mapped[float] = mapped_column(Float)
    statutory_tag: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_no: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    invoice_date: Mapped[date] = mapped_column(Date)
    project_code: Mapped[str] = mapped_column(String(64))
    client_name: Mapped[str] = mapped_column(String(300))
    client_gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    sub_total: Mapped[float] = mapped_column(Float)
    cgst: Mapped[float] = mapped_column(Float, default=0.0)
    sgst: Mapped[float] = mapped_column(Float, default=0.0)
    igst: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float)
    retention_pct: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="Draft")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_no: Mapped[str] = mapped_column(String(64), index=True)
    line_no: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(500))
    hsn_sac: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    taxable_amount: Mapped[float] = mapped_column(Float)
    gst_rate_pct: Mapped[float] = mapped_column(Float, default=18.0)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
