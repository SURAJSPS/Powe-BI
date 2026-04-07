"""Reusable Streamlit UI primitives (non-global CSS)."""
from __future__ import annotations

import html

import streamlit as st
from streamlit.delta_generator import DeltaGenerator


def pair_columns() -> tuple[DeltaGenerator, DeltaGenerator]:
    """Two equal columns for side-by-side inputs (gap matches global form-row CSS)."""
    a, b = st.columns(2, gap="medium")
    return (a, b)


def triple_columns() -> tuple[DeltaGenerator, DeltaGenerator, DeltaGenerator]:
    """Three equal columns for compact numeric / date rows."""
    a, b, c = st.columns(3, gap="medium")
    return (a, b, c)


def hero(title: str, subtitle: str | None = None) -> None:
    t = html.escape(title)
    sub = f"<p>{html.escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="rnk-hero rnk-hero--dashboard rnk-anim-hero"><div class="rnk-hero__inner"><h1>{t}</h1>{sub}</div></div>',
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str | None = None, eyebrow: str | None = None) -> None:
    """Section title for inner pages (uses existing theme classes)."""
    parts: list[str] = []
    if eyebrow:
        parts.append(f'<p class="rnk-section-label">{html.escape(eyebrow)}</p>')
    parts.append(
        f'<h2 style="margin:0 0 0.35rem 0;font-size:1.35rem;font-weight:600;letter-spacing:-0.02em;">'
        f"{html.escape(title)}</h2>"
    )
    if subtitle:
        parts.append(f'<p class="rnk-muted">{html.escape(subtitle)}</p>')
    st.markdown(
        f'<div class="rnk-page-head rnk-anim-reveal" style="margin-bottom:1rem;">{"".join(parts)}</div>',
        unsafe_allow_html=True,
    )


def sidebar_avatar_initials(u: dict) -> str:
    """Two-letter avatar text from full name or email (for sidebar circle)."""
    fn = (u.get("full_name") or "").strip()
    if fn:
        parts = fn.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[-1][0]).upper()
        w = parts[0]
        if len(w) >= 2:
            return w[:2].upper()
        return (w[0] + w[0]).upper()
    em = (u.get("email") or "").strip()
    if em:
        return em[:2].upper()
    return "RN"


def dashboard_callout(message: str) -> None:
    """Tip / hint below key content (light theme)."""
    st.markdown(
        f'<div class="rnk-callout"><span class="rnk-callout__icon" aria-hidden="true">⬡</span>'
        f"<p>{html.escape(message)}</p></div>",
        unsafe_allow_html=True,
    )


def styled_divider() -> None:
    st.markdown('<hr class="rnk-hr" />', unsafe_allow_html=True)


def empty_state(title: str, body: str) -> None:
    """Friendly placeholder when a table has no rows."""
    st.markdown(
        f'<div class="rnk-empty"><strong>{html.escape(title)}</strong>{html.escape(body)}</div>',
        unsafe_allow_html=True,
    )


def muted_hint(text: str) -> None:
    """Short grey helper line under headers or above forms."""
    st.markdown(f'<p class="rnk-muted">{html.escape(text)}</p>', unsafe_allow_html=True)


def insight_preview(title: str, rows: list[tuple[str, str]]) -> None:
    """Compact key–value summary (e.g. policy preview)."""
    body = "".join(
        f'<div class="rnk-insight__row"><span class="rnk-insight__k">{html.escape(k)}</span>'
        f'<span class="rnk-insight__v">{html.escape(v)}</span></div>'
        for k, v in rows
    )
    st.markdown(
        f'<div class="rnk-insight"><p class="rnk-insight__title">{html.escape(title)}</p>{body}</div>',
        unsafe_allow_html=True,
    )
