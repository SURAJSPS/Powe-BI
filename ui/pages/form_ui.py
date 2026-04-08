"""UI helpers for required-field indicators."""
from __future__ import annotations

import html

import streamlit as st


def required_label(label: str) -> None:
    safe = html.escape(label)
    st.markdown(
        f'<div style="margin-bottom:0.2rem;">{safe} <span style="color:#ef4444">*</span></div>',
        unsafe_allow_html=True,
    )


def required_legend() -> None:
    st.caption(":red[*] Required fields")
