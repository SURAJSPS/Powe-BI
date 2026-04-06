"""Inject compact Streamlit theme (dark sidebar accent)."""
from __future__ import annotations

import streamlit as st


def inject_theme() -> None:
    st.markdown(
        """
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;1,9..40,400&display=swap');
  html, body, [class*="css"]  {
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    border-right: 1px solid #334155;
  }
  [data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
  }
  [data-testid="stSidebar"] .stRadio label {
    font-weight: 500;
  }
  .rnk-hero {
    background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%);
    color: white;
    padding: 1.25rem 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    box-shadow: 0 8px 24px rgba(3, 105, 161, 0.25);
  }
  .rnk-hero h1 { margin: 0; font-size: 1.5rem; font-weight: 600; }
  .rnk-hero p { margin: 0.35rem 0 0; opacity: 0.95; font-size: 0.95rem; }
  .rnk-card {
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    background: #f8fafc;
  }
  div[data-testid="stMetricValue"] { font-variant-numeric: tabular-nums; }
</style>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="rnk-hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )
