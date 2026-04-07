"""Shared session helpers and client-directory utilities for Streamlit pages."""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

def _user() -> dict:
    return st.session_state["user"]


def _cid() -> str:
    return _user()["company_id"]


# India — states & union territories (optional dropdown on Clients page)
INDIAN_STATES_UT: tuple[str, ...] = (
    "",
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
)


def _client_pick_label(c: dict[str, Any]) -> str:
    name = (c.get("name") or "?").strip()
    code = (c.get("client_code") or "").strip()
    tail = str(c.get("_id", ""))[-6:]
    return f"{name} · {code}" if code else f"{name} · …{tail}"


def _fmt_ts(v: Any) -> str:
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    return str(v or "—")


def _client_directory_records(rows: list[dict[str, Any]], search: str) -> list[dict[str, Any]]:
    q = (search or "").strip().lower()
    out: list[dict[str, Any]] = []
    for c in rows:
        if q:
            blob = " ".join(
                str(c.get(k) or "")
                for k in (
                    "name",
                    "legal_name",
                    "client_code",
                    "address",
                    "address_line2",
                    "city",
                    "state",
                    "pincode",
                    "gstin",
                    "contact_person",
                    "email",
                    "phone",
                    "pan",
                )
            ).lower()
            if q not in blob:
                continue
        out.append(
            {
                "Code": (c.get("client_code") or "").strip() or "—",
                "Name": (c.get("name") or "").strip() or "—",
                "Legal name": (c.get("legal_name") or "").strip() or "—",
                "City": (c.get("city") or "").strip() or "—",
                "State": (c.get("state") or "").strip() or "—",
                "GSTIN": (c.get("gstin") or "").strip() or "—",
                "PAN": (c.get("pan") or "").strip() or "—",
                "Contact": (c.get("contact_person") or "").strip() or "—",
                "Phone": (c.get("phone") or "").strip() or "—",
                "Email": (c.get("email") or "").strip() or "—",
                "Added": _fmt_ts(c.get("created_at")),
            }
        )
    return out


def _go_nav(page_key: str) -> None:
    # Session state for rnk_nav is applied in sidebar_nav before nav buttons render — use pending + apply there.
    st.session_state["rnk_nav_pending"] = page_key
    st.rerun()


HOME_QUICK_ACTIONS: tuple[tuple[str, str, str], ...] = (
    ("dashboard", "📈", "Dashboard"),
    ("projects", "🏗", "Projects"),
    ("sites", "📍", "Sites"),
    ("workers", "👷", "Workers"),
    ("attendance", "📅", "Attendance"),
    ("expenses", "💰", "Expenses"),
    ("team", "👥", "Team & employees"),
    ("invoices", "🧾", "Invoices"),
    ("company", "◆", "Company profile"),
)

