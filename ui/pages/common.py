"""Shared session helpers and client-directory utilities for Streamlit pages.

**Dialogs (``@st.dialog``):** App-wide patterns live here — e.g. ``confirm_delete_dialog`` for any
destructive delete that uses ``queue_delete_confirmation`` / ``RNK_PENDING_DELETE``. Cross-page
**Quick add** (``quick_add_dialog.py``): opened from Clients / Team / project flows — **Create record** for client or employee. Create/Edit project can open the same dialog for **＋ Add new client** and returns with the new client selected.
Other feature-specific modals stay next to that page’s ``page_*`` when they are not shared.
"""
from __future__ import annotations

import html
from typing import Any

import pandas as pd
import streamlit as st
from bson import ObjectId

from core.roles import ROLE_LABELS
from services import civil_store

# Strip these from Mongo-backed tables so users see names and codes, not internal IDs.
_DISPLAY_DROP_KEYS: frozenset[str] = frozenset({"_id", "company_id"})

# Left-to-right column preference after stripping (remaining keys sort alphabetically after).
_DISPLAY_COL_PRIORITY: tuple[str, ...] = (
    "worker_name",
    "full_name",
    "name",
    "employee_code",
    "worker_id",
    "site_code",
    "project_code",
    "client_name",
    "email",
    "role",
    "invoice_no",
    "run_id",
    "period_label",
    "status",
    "work_date",
    "expense_date",
    "invoice_date",
    "active",
)


def _scalar_for_display(v: Any) -> Any:
    if isinstance(v, ObjectId):
        return str(v)
    return v


def _strip_internal_row(r: dict[str, Any], *, extra_drop: frozenset[str] | None = None) -> dict[str, Any]:
    drop = _DISPLAY_DROP_KEYS | (extra_drop or frozenset())
    out: dict[str, Any] = {}
    for k, v in r.items():
        if k in drop:
            continue
        out[k] = _scalar_for_display(v)
    return out


def dataframe_for_records(
    rows: list[dict[str, Any]],
    *,
    extra_drop: frozenset[str] | None = None,
    map_role_labels: bool = False,
) -> pd.DataFrame:
    """Build a DataFrame for UI tables: hide Mongo internals, put human-readable names first.

    If ``map_role_labels`` is True, the ``role`` column shows labels (e.g. *Company admin*)
    instead of internal keys (e.g. ``company_admin``).
    """
    if not rows:
        return pd.DataFrame()
    stripped = [_strip_internal_row(r, extra_drop=extra_drop) for r in rows]
    all_keys: set[str] = set()
    for r in stripped:
        all_keys.update(r.keys())
    ordered = [c for c in _DISPLAY_COL_PRIORITY if c in all_keys] + sorted(all_keys - set(_DISPLAY_COL_PRIORITY))
    cols = [c for c in ordered if any(c in r for r in stripped)]
    df = pd.DataFrame(stripped, columns=cols)
    if map_role_labels and "role" in df.columns:
        df = df.copy()
        df["role"] = df["role"].map(lambda r: ROLE_LABELS.get(str(r), r) if r is not None else r)
    return df


def _user() -> dict:
    return st.session_state["user"]


def _cid() -> str:
    return _user()["company_id"]


RNK_PENDING_DELETE = "rnk_pending_delete"


def queue_delete_confirmation(
    *,
    kind: str,
    message: str,
    success_msg: str = "Deleted.",
    **payload: Any,
) -> None:
    """Queue a destructive action; call ``confirm_delete_dialog()`` when ``RNK_PENDING_DELETE`` is set."""
    st.session_state[RNK_PENDING_DELETE] = {
        "kind": kind,
        "message": message,
        "success_msg": success_msg,
        **payload,
    }


@st.dialog("Confirm deletion")
def confirm_delete_dialog() -> None:
    """Show warning and run the pending delete handler. Reuse for any destructive delete in the app."""
    meta = st.session_state.get(RNK_PENDING_DELETE)
    if not meta:
        return
    st.warning(meta.get("message", "Are you sure you want to delete this item?"))
    c1, c2 = st.columns(2)
    if c1.button("Cancel", use_container_width=True):
        st.session_state.pop(RNK_PENDING_DELETE, None)
        st.rerun()
    if c2.button("Delete", type="primary", use_container_width=True):
        try:
            _execute_pending_delete(meta)
            st.session_state.pop(RNK_PENDING_DELETE, None)
            st.session_state["rnk_flash_success"] = meta.get("success_msg", "Deleted.")
            st.rerun()
        except Exception as ex:
            st.error(str(ex))


def _execute_pending_delete(meta: dict[str, Any]) -> None:
    kind = meta.get("kind")
    if kind == "project":
        civil_store.project_delete(_cid(), str(meta.get("code", "")))
        return
    raise ValueError(f"Unknown delete kind: {kind!r}")


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


def _fmt_datetime(v: Any) -> str:
    """Display Mongo ``datetime`` or ISO string for “last updated” style columns."""
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d %H:%M")
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

