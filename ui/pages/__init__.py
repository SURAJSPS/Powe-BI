"""Streamlit pages: split by domain; routing lives in `nav`."""
from __future__ import annotations

from ui.pages.nav import (
    PAGE_FUNCS,
    apply_nav_from_query_params,
    publish_nav_to_query_params,
    sidebar_nav,
)

__all__ = [
    "PAGE_FUNCS",
    "apply_nav_from_query_params",
    "publish_nav_to_query_params",
    "sidebar_nav",
]
