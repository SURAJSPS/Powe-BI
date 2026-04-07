"""Global layout CSS + reusable UI primitives."""
from __future__ import annotations

from ui.theme.animations import inject_ui_animations
from ui.theme.components import (
    dashboard_callout,
    empty_state,
    hero,
    insight_preview,
    muted_hint,
    page_header,
    pair_columns,
    sidebar_avatar_initials,
    styled_divider,
    triple_columns,
)
from ui.theme.layout import inject_auth_layout, inject_theme

__all__ = [
    "inject_ui_animations",
    "dashboard_callout",
    "empty_state",
    "hero",
    "inject_auth_layout",
    "inject_theme",
    "insight_preview",
    "muted_hint",
    "page_header",
    "pair_columns",
    "sidebar_avatar_initials",
    "styled_divider",
    "triple_columns",
]
