"""Streamlit theme: light/dark workspace, purple sidebar (construction-admin style)."""
from __future__ import annotations

import streamlit as st


def _theme_root_block(theme: str) -> str:
    """Single :root token set — Streamlit strips <script> in markdown, so we cannot rely on data-theme."""
    if theme == "dark":
        return """
  :root {
    --rnk-bg-deep: #0a0f1a;
    --rnk-bg-main: #0f172a;
    --rnk-surface: #1e293b;
    --rnk-surface2: #334155;
    --rnk-border: rgba(148, 163, 184, 0.35);
    --rnk-border-strong: rgba(203, 213, 225, 0.48);
    --rnk-text: #f1f5f9;
    --rnk-text-muted: #94a3b8;
    --rnk-on-accent: #ffffff;
    --rnk-accent: #a78bfa;
    --rnk-accent-hover: #c4b5fd;
    --rnk-accent-dim: rgba(167, 139, 250, 0.22);
    --rnk-link: #c4b5fd;
    --rnk-link-hover: #e9d5ff;
    --rnk-input-bg: #1e293b;
    --rnk-input-border: rgba(203, 213, 225, 0.35);
    --rnk-input-text: #f1f5f9;
    --rnk-input-placeholder: #94a3b8;
    --rnk-select-bg: #1e293b;
    --rnk-select-border: rgba(203, 213, 225, 0.4);
    --rnk-focus-ring: rgba(167, 139, 250, 0.45);
    --rnk-focus-border: rgba(167, 139, 250, 0.75);
    --rnk-widget-label: #cbd5e1;
    --rnk-btn-primary-bg: linear-gradient(180deg, #9f87fa 0%, #7c5cf0 50%, #6d4ad6 100%);
    --rnk-btn-primary-shadow: 0 4px 16px rgba(124, 92, 240, 0.45);
    --rnk-btn-primary-shadow-hover: 0 8px 24px rgba(124, 92, 240, 0.55);
    --rnk-btn-secondary-hover-border: rgba(167, 139, 250, 0.55);
    --rnk-checkbox-border: rgba(203, 213, 225, 0.45);
    --rnk-df-header-bg: #273449;
    --rnk-df-border: rgba(148, 163, 184, 0.25);
    --rnk-code-bg: #0f172a;
    --rnk-code-border: rgba(148, 163, 184, 0.3);
    --rnk-header-bg: rgba(15, 23, 42, 0.96);
    --rnk-header-border: rgba(255, 255, 255, 0.22);
    --rnk-sidebar-gradient: linear-gradient(180deg, #020617 0%, #1e1b4b 52%, #0f172a 100%);
    --rnk-sidebar-shadow: 4px 0 48px rgba(0, 0, 0, 0.45);
    --rnk-sidebar-edge: rgba(255, 255, 255, 0.18);
    --rnk-main-bg:
      radial-gradient(ellipse 85% 55% at 100% 0%, rgba(167, 139, 250, 0.14), transparent 52%),
      linear-gradient(180deg, var(--rnk-bg-main) 0%, var(--rnk-bg-deep) 100%);
    --rnk-header-box-shadow: 0 1px 0 rgba(255, 255, 255, 0.06) inset, 0 8px 32px rgba(0, 0, 0, 0.38);
    --rnk-header-line-opacity: 0.58;
    --rnk-tab-selected-shadow: 0 2px 12px rgba(0, 0, 0, 0.35);
    --rnk-expander-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
    --rnk-metric-shadow: 0 2px 12px rgba(0, 0, 0, 0.25);
    --rnk-insight-shadow: 0 2px 14px rgba(0, 0, 0, 0.38);
    --rnk-dialog-shadow: 0 24px 64px rgba(0, 0, 0, 0.58);
    --rnk-metric-hover-border: rgba(167, 139, 250, 0.45);
    --rnk-metric-hover-shadow: 0 6px 22px rgba(0, 0, 0, 0.35);
    --rnk-df-row-hover: rgba(167, 139, 250, 0.1);
    --rnk-hero-inset: 0 1px 0 rgba(255, 255, 255, 0.1) inset;
    --rnk-stat-tile-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
    --rnk-stat-tile-hover-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
    --rnk-stat-tile-hover-border: rgba(167, 139, 250, 0.45);
    --rnk-hero-drop: 0 4px 24px rgba(0, 0, 0, 0.35);
    /* Streamlit native theme bridge (overrides .streamlit/config.toml when RNK dark is active) */
    --st-text-color: #f1f5f9;
    --st-background-color: #0f172a;
    --st-secondary-background-color: #1e293b;
    --st-primary-color: #a78bfa;
    --st-border-color: rgba(148, 163, 184, 0.45);
    --st-link-color: #c4b5fd;
    color-scheme: dark;
  }
"""
    return """
  :root {
    --rnk-bg-deep: #eef1f6;
    --rnk-bg-main: #f8fafc;
    --rnk-surface: #ffffff;
    --rnk-surface2: #f1f5f9;
    --rnk-border: rgba(15, 23, 42, 0.12);
    --rnk-border-strong: rgba(15, 23, 42, 0.22);
    --rnk-text: #18181b;
    --rnk-text-muted: #64748b;
    --rnk-on-accent: #ffffff;
    --rnk-accent: #7c3aed;
    --rnk-accent-hover: #6d28d9;
    --rnk-accent-dim: rgba(124, 58, 237, 0.12);
    --rnk-link: #6d28d9;
    --rnk-link-hover: #5b21b6;
    --rnk-input-bg: #ffffff;
    --rnk-input-border: rgba(15, 23, 42, 0.18);
    --rnk-input-text: #18181b;
    --rnk-input-placeholder: #94a3b8;
    --rnk-select-bg: #ffffff;
    --rnk-select-border: rgba(15, 23, 42, 0.2);
    --rnk-focus-ring: rgba(124, 58, 237, 0.28);
    --rnk-focus-border: rgba(124, 58, 237, 0.55);
    --rnk-widget-label: #3f3f46;
    --rnk-btn-primary-bg: linear-gradient(180deg, #8b5cf6 0%, #7c3aed 55%, #6d28d9 100%);
    --rnk-btn-primary-shadow: 0 4px 14px rgba(124, 58, 237, 0.35);
    --rnk-btn-primary-shadow-hover: 0 8px 22px rgba(124, 58, 237, 0.42);
    --rnk-btn-secondary-hover-border: rgba(124, 58, 237, 0.4);
    --rnk-checkbox-border: rgba(15, 23, 42, 0.28);
    --rnk-df-header-bg: #f8fafc;
    --rnk-df-border: rgba(15, 23, 42, 0.12);
    --rnk-code-bg: #f8fafc;
    --rnk-code-border: rgba(15, 23, 42, 0.12);
    --rnk-header-bg: rgba(255, 255, 255, 0.92);
    --rnk-header-border: rgba(15, 23, 42, 0.14);
    --rnk-sidebar-gradient: linear-gradient(180deg, #1e1b4b 0%, #312e81 48%, #1e1b4b 100%);
    --rnk-sidebar-shadow: 4px 0 40px rgba(30, 27, 75, 0.35);
    --rnk-sidebar-edge: rgba(255, 255, 255, 0.12);
    --rnk-main-bg:
      radial-gradient(ellipse 90% 60% at 100% 0%, rgba(124, 58, 237, 0.06), transparent 50%),
      linear-gradient(180deg, var(--rnk-bg-main) 0%, var(--rnk-bg-deep) 100%);
    --rnk-header-box-shadow: 0 1px 0 rgba(255, 255, 255, 0.06) inset, 0 4px 24px rgba(15, 23, 42, 0.08);
    --rnk-header-line-opacity: 0.45;
    --rnk-tab-selected-shadow: 0 1px 4px rgba(15, 23, 42, 0.1);
    --rnk-expander-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
    --rnk-metric-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
    --rnk-insight-shadow: 0 2px 14px rgba(15, 23, 42, 0.07);
    --rnk-dialog-shadow: 0 24px 64px rgba(15, 23, 42, 0.16);
    --rnk-metric-hover-border: rgba(124, 58, 237, 0.28);
    --rnk-metric-hover-shadow: 0 6px 20px rgba(15, 23, 42, 0.1);
    --rnk-df-row-hover: rgba(124, 58, 237, 0.06);
    --rnk-hero-inset: 0 1px 0 rgba(255, 255, 255, 0.9) inset;
    --rnk-stat-tile-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
    --rnk-stat-tile-hover-shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
    --rnk-stat-tile-hover-border: rgba(124, 58, 237, 0.22);
    --rnk-hero-drop: 0 4px 24px rgba(15, 23, 42, 0.06);
    --st-text-color: #18181b;
    --st-background-color: #f8fafc;
    --st-secondary-background-color: #ffffff;
    --st-primary-color: #7c3aed;
    --st-border-color: rgba(15, 23, 42, 0.2);
    --st-link-color: #6d28d9;
    color-scheme: light;
  }
"""


def inject_theme(theme: str = "light") -> None:
    """Apply global CSS. Pass ``theme`` as ``\"light\"`` or ``\"dark\"`` (from ``app.py`` session state)."""
    t = "dark" if theme == "dark" else "light"
    st.markdown(
        "<style>\n  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');\n"
        + _theme_root_block(t)
        + """

  html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
  }

  [data-testid="stAppViewContainer"] {
    background: var(--rnk-bg-deep);
  }

  header[data-testid="stHeader"] {
    position: relative;
    background: var(--rnk-header-bg) !important;
    backdrop-filter: blur(14px) saturate(1.2);
    -webkit-backdrop-filter: blur(14px) saturate(1.2);
    border-bottom: 1px solid var(--rnk-header-border) !important;
    box-shadow: var(--rnk-header-box-shadow);
    min-height: 3.25rem;
  }

  header[data-testid="stHeader"]::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent 0%, var(--rnk-accent) 35%, var(--rnk-accent-hover) 50%, var(--rnk-accent) 65%, transparent 100%);
    opacity: var(--rnk-header-line-opacity);
    pointer-events: none;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) {
    background: var(--rnk-main-bg) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 2.5rem !important;
    max-width: 1200px !important;
  }

  /* Sidebar — layout: fixed column height, scrollable nav, footer logout */
  [data-testid="stSidebar"] {
    background: var(--rnk-sidebar-gradient) !important;
    border-right: 1px solid var(--rnk-sidebar-edge) !important;
    box-shadow: var(--rnk-sidebar-shadow);
    min-height: 100vh;
    /* Force light text on purple chrome — overrides global --st-text-color from config.toml */
    --st-text-color: #f1f5f9;
    --st-link-color: #e9d5ff;
    --st-primary-color: #c4b5fd;
    --st-secondary-background-color: rgba(0, 0, 0, 0.22);
    --st-background-color: transparent;
    --st-border-color: rgba(255, 255, 255, 0.28);
  }

  [data-testid="stSidebar"] > div:first-child,
  [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    min-height: 100vh !important;
  }

  [data-testid="stSidebar"] .block-container {
    padding: 0.85rem 0.75rem 1rem !important;
    min-height: calc(100vh - 8px);
    display: flex !important;
    flex-direction: column !important;
    gap: 0 !important;
    box-sizing: border-box !important;
  }

  [data-testid="stSidebar"] .rnk-sidebar-shell {
    flex-shrink: 0;
  }

  [data-testid="stSidebar"] .rnk-sidebar-section-label {
    margin: 0 0 0.45rem 0.15rem;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: rgba(196, 181, 253, 0.75) !important;
    line-height: 1.2 !important;
  }

  [data-testid="stSidebar"] .rnk-sidebar-section-label--nav {
    margin-top: 0.15rem;
  }

  /* One block: app name + org + user (no duplicate logo row) */
  [data-testid="stSidebar"] .rnk-sidebar-identity {
    display: flex;
    align-items: flex-start;
    gap: 0.65rem;
    padding: 0.7rem 0.65rem;
    margin-bottom: 0.65rem;
    border-radius: 12px;
    background: rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
  }
  [data-testid="stSidebar"] .rnk-sidebar-avatar {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: #fff !important;
    background: linear-gradient(145deg, #7c3aed 0%, #5b21b6 100%);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
  }
  [data-testid="stSidebar"] .rnk-sidebar-identity__main {
    min-width: 0;
    flex: 1;
  }
  [data-testid="stSidebar"] .rnk-sidebar-identity__app {
    margin: 0 0 0.28rem 0 !important;
    font-size: 0.62rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #c4b5fd !important;
    line-height: 1.2 !important;
  }
  [data-testid="stSidebar"] .rnk-sidebar-identity__company {
    margin: 0 0 0.3rem 0 !important;
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
    color: #fafafa !important;
    word-break: break-word;
  }
  [data-testid="stSidebar"] .rnk-sidebar-identity__email {
    margin: 0 0 0.4rem 0 !important;
    font-family: 'JetBrains Mono', ui-monospace, monospace !important;
    font-size: 0.68rem !important;
    line-height: 1.35 !important;
    color: rgba(233, 213, 255, 0.88) !important;
    word-break: break-all;
  }
  [data-testid="stSidebar"] .rnk-sidebar-role-chip {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 0.2rem 0.45rem;
    border-radius: 6px;
    background: rgba(196, 181, 253, 0.15);
    color: #e9d5ff !important;
    border: 1px solid rgba(196, 181, 253, 0.25);
  }

  [data-testid="stSidebar"] .rnk-sidebar-nav-divider {
    height: 1px;
    margin: 0.15rem 0 0.65rem 0;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.14), transparent);
    border: none;
  }

  /* Nav stack (icon buttons) — grows and scrolls; second-to-last block = nav container, last = Log out */
  [data-testid="stSidebar"] .block-container > [data-testid="element-container"]:nth-last-child(2) {
    flex: 1 1 auto !important;
    min-height: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    overflow: hidden !important;
  }

  [data-testid="stSidebar"] .block-container > [data-testid="element-container"]:nth-last-child(2) [data-testid="stVerticalBlock"] {
    gap: 0.28rem !important;
    flex: 1 1 auto !important;
    min-height: 0 !important;
    max-height: calc(100vh - 240px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    padding: 0.1rem 0 0.25rem 0 !important;
    -webkit-overflow-scrolling: touch;
  }

  [data-testid="stSidebar"] .block-container > [data-testid="element-container"]:nth-last-child(2) [data-testid="stVerticalBlock"]::-webkit-scrollbar {
    width: 5px;
  }
  [data-testid="stSidebar"] .block-container > [data-testid="element-container"]:nth-last-child(2) [data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.22);
    border-radius: 99px;
  }

  [data-testid="stSidebar"] .block-container > [data-testid="element-container"]:last-child {
    flex-shrink: 0 !important;
    margin-top: auto !important;
    padding-top: 0.35rem !important;
  }

  /* Sidebar buttons: icon nav (primary = selected, secondary = idle) + Log out */
  [data-testid="stSidebar"] .stButton > button {
    width: 100%;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.8125rem !important;
    padding: 0.55rem 0.75rem !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease !important;
  }

  [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-secondary"] {
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: rgba(0, 0, 0, 0.2) !important;
    color: #e9d5ff !important;
    -webkit-text-fill-color: #e9d5ff !important;
    box-shadow: none !important;
  }
  [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-secondary"]:hover {
    background: rgba(255, 255, 255, 0.1) !important;
    border-color: rgba(255, 255, 255, 0.22) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
  }

  [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"] {
    border: 1px solid rgba(196, 181, 253, 0.45) !important;
    background: rgba(255, 255, 255, 0.14) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    box-shadow: inset 3px 0 0 0 #c4b5fd !important;
  }
  [data-testid="stSidebar"] .stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: rgba(255, 255, 255, 0.2) !important;
    border-color: rgba(196, 181, 253, 0.6) !important;
    color: #ffffff !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) h1,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) h2,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) h3 {
    color: var(--rnk-text) !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stMarkdown,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) p {
    color: var(--rnk-text-muted);
  }

  /* Hero — light card + purple accent */
  .rnk-hero--dashboard {
    position: relative;
    overflow: hidden;
    background: var(--rnk-surface);
    color: var(--rnk-text);
    padding: clamp(1.15rem, 2.5vw, 1.5rem) clamp(1.25rem, 2.5vw, 1.75rem);
    border-radius: 14px;
    margin-bottom: clamp(0.85rem, 2vw, 1.25rem);
    border: 1px solid var(--rnk-border-strong);
    box-shadow: var(--rnk-hero-drop), var(--rnk-hero-inset);
  }
  .rnk-hero--dashboard::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    border-radius: 14px 0 0 14px;
    background: linear-gradient(180deg, #7c3aed 0%, #6d28d9 100%);
  }
  .rnk-hero--dashboard::after {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 100% 0%, rgba(124, 58, 237, 0.06), transparent 45%);
    pointer-events: none;
  }
  .rnk-hero--dashboard .rnk-hero__inner {
    position: relative;
    z-index: 1;
    padding-left: 0.35rem;
  }
  .rnk-hero--dashboard h1 {
    margin: 0;
    font-size: clamp(1.25rem, 2.5vw, 1.55rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.2;
    color: var(--rnk-text) !important;
  }
  .rnk-hero--dashboard p {
    margin: 0.45rem 0 0;
    font-size: clamp(0.86rem, 1.8vw, 0.95rem);
    line-height: 1.55;
    max-width: 56ch;
    color: var(--rnk-text-muted) !important;
  }

  .rnk-hero:not(.rnk-hero--dashboard) {
    background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
    color: white;
    padding: 1.25rem 1.5rem;
    border-radius: 14px;
    margin-bottom: 1rem;
    box-shadow: 0 10px 30px rgba(124, 58, 237, 0.25);
  }
  .rnk-hero:not(.rnk-hero--dashboard) h1 { margin: 0; font-size: 1.45rem; font-weight: 600; }
  .rnk-hero:not(.rnk-hero--dashboard) p { margin: 0.35rem 0 0; opacity: 0.95; font-size: 0.95rem; }

  .rnk-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: clamp(0.65rem, 1.8vw, 1rem);
    margin-bottom: 1rem;
  }
  @media (max-width: 900px) {
    .rnk-stat-grid { grid-template-columns: 1fr; }
  }
  @media (min-width: 901px) and (max-width: 1100px) {
    .rnk-stat-grid { grid-template-columns: repeat(2, 1fr); }
    .rnk-stat-grid .rnk-stat-tile:last-child { grid-column: 1 / -1; }
  }

  .rnk-stat-tile {
    position: relative;
    background: var(--rnk-surface);
    border: 1px solid var(--rnk-border-strong);
    border-radius: 12px;
    padding: 1rem 1rem 1rem 1.1rem;
    min-height: 5.25rem;
    box-shadow: var(--rnk-stat-tile-shadow);
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  }
  @media (hover: hover) {
    .rnk-stat-tile:hover {
      transform: translateY(-2px);
      border-color: var(--rnk-stat-tile-hover-border);
      box-shadow: var(--rnk-stat-tile-hover-shadow);
    }
  }

  .rnk-stat-tile__icon {
    position: absolute;
    top: 0.85rem;
    right: 0.85rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 2.25rem;
    height: 2.25rem;
    border-radius: 10px;
    background: linear-gradient(145deg, rgba(124, 58, 237, 0.1), rgba(124, 58, 237, 0.04));
    font-size: 1.05rem;
  }

  .rnk-stat-tile__label {
    display: block;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--rnk-text-muted);
    margin-bottom: 0.4rem;
    padding-right: 2.5rem;
  }

  .rnk-stat-tile__value {
    display: block;
    font-size: clamp(0.92rem, 1.8vw, 1.02rem);
    font-weight: 600;
    color: var(--rnk-text);
    line-height: 1.35;
    word-break: break-word;
  }

  .rnk-callout {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
    padding: 0.9rem 1rem;
    border-radius: 12px;
    background: rgba(124, 58, 237, 0.06);
    border: 1px solid rgba(124, 58, 237, 0.18);
    margin-top: 0.15rem;
  }
  .rnk-callout__icon {
    flex-shrink: 0;
    width: 1.6rem;
    height: 1.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    background: rgba(124, 58, 237, 0.15);
    color: var(--rnk-accent);
    font-size: 0.9rem;
  }
  .rnk-callout p {
    margin: 0 !important;
    font-size: 0.88rem !important;
    line-height: 1.5 !important;
    color: var(--rnk-text-muted) !important;
  }

  .rnk-card {
    border: 1px solid var(--rnk-border-strong);
    border-radius: 12px;
    padding: 1rem 1.15rem;
    background: var(--rnk-surface);
    color: var(--rnk-text);
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  }
  .rnk-card strong { color: var(--rnk-text-muted); font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) div[data-testid="stAlert"] {
    border-radius: 12px !important;
    border: 1px solid var(--rnk-border-strong) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden;
    border: 1px solid var(--rnk-border-strong) !important;
    box-shadow: 0 2px 12px rgba(15, 23, 42, 0.04);
  }

  div[data-testid="stMetricValue"] {
    font-variant-numeric: tabular-nums;
    color: var(--rnk-text) !important;
  }

  @media (prefers-reduced-motion: reduce) {
    .rnk-stat-tile, .rnk-stat-tile:hover { transition: none !important; transform: none !important; }
  }

  .rnk-section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--rnk-text-muted);
    margin: 0 0 0.6rem 0;
  }

  .rnk-hr {
    border: none;
    height: 1px;
    margin: 1.15rem 0;
    background: linear-gradient(90deg, transparent, var(--rnk-border-strong), transparent);
  }

  .rnk-empty {
    text-align: center;
    padding: 1.75rem 1.15rem;
    border-radius: 12px;
    border: 1px dashed var(--rnk-border-strong);
    background: var(--rnk-surface2);
    color: var(--rnk-text-muted);
    font-size: 0.9rem;
    line-height: 1.5;
    margin-bottom: 1rem;
  }
  .rnk-empty strong {
    display: block;
    color: var(--rnk-text);
    font-size: 0.98rem;
    margin-bottom: 0.3rem;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stForm"] {
    background: var(--rnk-surface);
    border: 1px solid var(--rnk-border-strong);
    border-radius: 14px;
    padding: 1.1rem 1.2rem 1.2rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 2px 16px rgba(15, 23, 42, 0.04), 0 0 0 1px var(--rnk-border);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stForm"]:focus-within {
    border-color: rgba(124, 58, 237, 0.25);
    box-shadow: 0 4px 24px rgba(124, 58, 237, 0.08);
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="tab-list"] {
    gap: 0.3rem !important;
    background: var(--rnk-surface2) !important;
    padding: 0.35rem !important;
    border-radius: 12px !important;
    border-bottom: none !important;
    border: 1px solid var(--rnk-border-strong) !important;
    box-shadow: 0 0 0 1px var(--rnk-border) !important;
    margin-bottom: 0.65rem !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.86rem !important;
    padding: 0.45rem 0.85rem !important;
    color: var(--rnk-text-muted) !important;
    border: none !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="tab"]:hover {
    background: var(--rnk-surface) !important;
    color: var(--rnk-text) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="tab-panel"] {
    padding-top: 0.65rem;
    padding-left: 0.1rem;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [aria-selected="true"] {
    background: var(--rnk-surface) !important;
    color: var(--rnk-accent) !important;
    box-shadow: var(--rnk-tab-selected-shadow) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stExpander"] {
    border: 1px solid var(--rnk-border-strong) !important;
    border-radius: 12px !important;
    background: var(--rnk-surface) !important;
    overflow: hidden;
    box-shadow: var(--rnk-expander-shadow);
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stExpander"] summary,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stExpander"] [data-testid="stExpanderToggleIcon"] {
    color: var(--rnk-text) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="input"]:focus-within,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="textarea"]:focus-within,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="select"]:focus-within {
    box-shadow: 0 0 0 2px var(--rnk-focus-ring) !important;
    border-color: var(--rnk-focus-border) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: transform 0.15s ease, box-shadow 0.2s ease !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stButton > button[kind="secondary"] {
    background: var(--rnk-surface) !important;
    border: 1px solid var(--rnk-border-strong) !important;
    color: var(--rnk-text) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stButton > button[kind="secondary"]:hover {
    border-color: var(--rnk-btn-secondary-hover-border) !important;
    color: var(--rnk-accent) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stButton > button[kind="primary"] {
    background: var(--rnk-btn-primary-bg) !important;
    border: none !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
    box-shadow: var(--rnk-btn-primary-shadow) !important;
  }
  @media (hover: hover) {
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stButton > button[kind="primary"]:hover {
      transform: translateY(-1px);
      box-shadow: var(--rnk-btn-primary-shadow-hover) !important;
      color: #ffffff !important;
    }
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMetricContainer"] {
    background: var(--rnk-surface);
    border: 1px solid var(--rnk-border-strong);
    border-radius: 12px;
    padding: 0.6rem 0.8rem !important;
    box-shadow: var(--rnk-metric-shadow);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
  }
  @media (hover: hover) {
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMetricContainer"]:hover {
      border-color: var(--rnk-metric-hover-border);
      box-shadow: var(--rnk-metric-hover-shadow);
    }
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] [role="row"]:hover {
    background: var(--rnk-df-row-hover) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) h3 {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.02rem !important;
    padding-left: 0.6rem;
    border-left: 3px solid var(--rnk-accent);
    margin-top: 1.1rem;
    color: var(--rnk-text) !important;
  }

  /* Modal dialogs (st.dialog) — centered overlay + ~70% panel */
  div[data-testid="stDialog"] {
    position: fixed !important;
    inset: 0 !important;
    z-index: 100002 !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: center !important;
    padding: clamp(0.5rem, 2vw, 1.25rem) !important;
    box-sizing: border-box !important;
    margin: 0 !important;
    width: 100vw !important;
    max-width: 100vw !important;
    min-height: 100vh !important;
    min-height: 100dvh !important;
  }
  div[data-testid="stDialog"] > div,
  div[data-testid="stDialog"] > [role="dialog"] {
    width: min(70vw, calc(100vw - 1.5rem)) !important;
    max-width: min(70vw, calc(100vw - 1.5rem)) !important;
    min-height: 0 !important;
    max-height: min(88vh, 960px) !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    -webkit-overflow-scrolling: touch;
    border-radius: 16px !important;
    border: 1px solid var(--rnk-border-strong) !important;
    box-shadow: var(--rnk-dialog-shadow) !important;
    padding: 1rem 1.2rem 1.15rem !important;
    box-sizing: border-box !important;
    margin: 0 auto !important;
    flex-shrink: 0 !important;
    align-self: center !important;
  }
  div[data-testid="stDialog"] .block-container {
    padding-left: 0 !important;
    padding-right: 0 !important;
    max-width: 100% !important;
  }
  div[data-testid="stDialog"] .rnk-modal-head {
    margin: 0 0 0.75rem 0 !important;
    padding-bottom: 0.6rem !important;
  }
  div[data-testid="stDialog"] .rnk-modal-section {
    margin: 0.85rem 0 0.4rem 0 !important;
  }
  div[data-testid="stDialog"] hr {
    margin: 0.85rem 0 0.65rem 0 !important;
  }
  .rnk-modal-grid2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem 1rem;
    align-items: start;
  }
  @media (max-width: 700px) {
    .rnk-modal-grid2 {
      grid-template-columns: 1fr;
    }
  }
  .rnk-modal-callout {
    margin: 0.5rem 0 0.75rem 0;
    padding: 0.65rem 0.85rem;
    border-radius: 10px;
    border: 1px solid var(--rnk-border-strong);
    background: var(--rnk-surface2);
    font-size: 0.82rem;
    line-height: 1.5;
    color: var(--rnk-text-muted);
  }
  .rnk-modal-hint {
    font-size: 0.88rem;
    color: var(--rnk-text-muted);
    line-height: 1.5;
    margin: 0 0 1rem 0;
  }
  .rnk-modal-section {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--rnk-text-muted);
    margin: 0.75rem 0 0.5rem;
  }

  .rnk-modal-head {
    margin: -0.25rem 0 1rem 0;
    padding-bottom: 0.85rem;
    border-bottom: 1px solid var(--rnk-border-strong);
  }
  .rnk-modal-head__title {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--rnk-text);
  }
  .rnk-modal-head__sub {
    margin: 0.35rem 0 0;
    font-size: 0.86rem;
    line-height: 1.45;
    color: var(--rnk-text-muted);
  }

  .rnk-page-toolbar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
  }
  .rnk-page-toolbar .rnk-page-header {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
    flex: 1;
    min-width: 200px;
  }
  .rnk-page-toolbar__btn {
    flex-shrink: 0;
    padding-top: 0.35rem;
  }

  .rnk-muted {
    font-size: 0.88rem;
    line-height: 1.55;
    color: var(--rnk-text-muted);
    margin: 0 0 1rem 0;
    max-width: 68ch;
  }

  .rnk-insight {
    margin-top: 1rem;
    padding: 0.95rem 1.1rem;
    border-radius: 12px;
    border: 1px solid var(--rnk-border-strong);
    background: linear-gradient(165deg, var(--rnk-surface) 0%, var(--rnk-surface2) 100%);
    box-shadow: var(--rnk-insight-shadow);
  }
  .rnk-insight__title {
    margin: 0 0 0.6rem 0;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    color: var(--rnk-text-muted);
  }
  .rnk-insight__row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 1.25rem;
    padding: 0.4rem 0;
    border-bottom: 1px solid var(--rnk-border);
    font-size: 0.9rem;
    line-height: 1.4;
  }
  .rnk-insight__row:last-child {
    border-bottom: none;
    padding-bottom: 0;
  }
  .rnk-insight__k {
    color: var(--rnk-text-muted);
    flex-shrink: 0;
  }
  .rnk-insight__v {
    font-weight: 600;
    color: var(--rnk-text);
    text-align: right;
    word-break: break-word;
    font-variant-numeric: tabular-nums;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stCaption"] {
    color: var(--rnk-text-muted) !important;
    font-size: 0.82rem !important;
    line-height: 1.45 !important;
  }

  /* Form rows: side-by-side fields — column gap + no overflow */
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stHorizontalBlock"] {
    gap: 0.65rem 1rem !important;
    align-items: flex-start !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="column"] {
    min-width: 0 !important;
  }
  /* Slightly richer field chrome inside forms (matches card radius) */
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stForm"] [data-baseweb="input"],
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stForm"] [data-baseweb="textarea"] > div {
    border-radius: 10px !important;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05) !important;
  }

  @media (max-width: 640px) {
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
      flex-direction: column !important;
    }
  }

  /* --- Main: labels, inputs, selects, checkboxes, links, code, tables (light/dark via :root) --- */
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) label[data-testid="stWidgetLabel"],
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stWidgetLabel"] {
    color: var(--rnk-widget-label) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMetricLabel"] {
    color: var(--rnk-text-muted) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="input"],
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="textarea"],
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stTextInput"] [data-baseweb="input"],
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stTextInput"] [data-baseweb="input"] > div,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stTextArea"] [data-baseweb="textarea"] > div {
    background-color: var(--rnk-input-bg) !important;
    border-color: var(--rnk-input-border) !important;
    color: var(--rnk-input-text) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="input"] input,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="textarea"] textarea {
    color: var(--rnk-input-text) !important;
    -webkit-text-fill-color: var(--rnk-input-text) !important;
    caret-color: var(--rnk-accent) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="input"] input::placeholder,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="textarea"] textarea::placeholder {
    color: var(--rnk-input-placeholder) !important;
    opacity: 1 !important;
    -webkit-text-fill-color: var(--rnk-input-placeholder) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="select"] {
    color: var(--rnk-input-text) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="select"] > div {
    background-color: var(--rnk-select-bg) !important;
    border-color: var(--rnk-select-border) !important;
    color: var(--rnk-input-text) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="checkbox"] {
    border-color: var(--rnk-checkbox-border) !important;
    background: var(--rnk-input-bg) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="checkbox"][aria-checked="true"] {
    background: var(--rnk-accent) !important;
    border-color: var(--rnk-accent) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stRadio"] [data-baseweb="radio"] input[type="radio"] {
    accent-color: var(--rnk-accent);
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMarkdown"] a {
    color: var(--rnk-link) !important;
    text-decoration-color: var(--rnk-accent-dim);
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMarkdown"] a:hover {
    color: var(--rnk-link-hover) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stCode"] {
    background: var(--rnk-code-bg) !important;
    border: 1px solid var(--rnk-code-border) !important;
    border-radius: 10px !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stCode"] pre,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stCode"] code {
    color: var(--rnk-text) !important;
    background: transparent !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] [role="grid"],
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] [role="row"] {
    border-color: var(--rnk-df-border) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] [role="columnheader"] {
    background: var(--rnk-df-header-bg) !important;
    color: var(--rnk-text) !important;
    border-color: var(--rnk-df-border) !important;
  }
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] [role="gridcell"] {
    color: var(--rnk-text) !important;
    border-color: var(--rnk-df-border) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDownloadButton"] button {
    background: var(--rnk-btn-primary-bg) !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
    border: none !important;
    box-shadow: var(--rnk-btn-primary-shadow) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stFileUploader"] section,
  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    background: var(--rnk-input-bg) !important;
    border-color: var(--rnk-input-border) !important;
    color: var(--rnk-text) !important;
  }

  :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-baseweb="slider"] [role="slider"] {
    background: var(--rnk-accent) !important;
  }

  /* Select / date dropdowns render in a portal — inherit :root tokens */
  [data-baseweb="popover"] [role="listbox"],
  [data-baseweb="popover"] ul {
    background-color: var(--rnk-surface) !important;
    border: 1px solid var(--rnk-border-strong) !important;
    color: var(--rnk-text) !important;
  }
  [data-baseweb="popover"] [role="option"] {
    background-color: var(--rnk-surface) !important;
    color: var(--rnk-text) !important;
  }
  [data-baseweb="popover"] [role="option"]:hover {
    background: var(--rnk-surface2) !important;
  }
  [data-baseweb="popover"] [role="option"][aria-selected="true"] {
    background: var(--rnk-surface2) !important;
  }

  /* Sidebar — Dark mode toggle (Streamlit switch / checkbox) */
  [data-testid="stSidebar"] [data-baseweb="checkbox"] {
    border-color: rgba(196, 181, 253, 0.45) !important;
  }
  [data-testid="stSidebar"] [data-baseweb="checkbox"][aria-checked="true"] {
    background: linear-gradient(145deg, #a78bfa 0%, #7c3aed 100%) !important;
    border-color: transparent !important;
  }
  [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: rgba(233, 213, 255, 0.95) !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
  }

  /* Streamlit top-right toolbar (Deploy / menu) */
  [data-testid="stHeader"] [data-testid="stToolbar"] button {
    color: var(--rnk-text) !important;
  }

</style>
""",
        unsafe_allow_html=True,
    )


def inject_auth_layout() -> None:
    """Auth screen: responsive split / stacked layout, touch-friendly, motion-safe."""
    st.markdown(
        """
<style>
  /* --- Auth shell: hide chrome --- */
  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }
  section[data-testid="stSidebar"] ~ div { margin-left: 0 !important; max-width: 100% !important; }

  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) {
    min-height: 100dvh;
    min-height: 100vh;
    background-color: #e8edf3;
    background-image:
      radial-gradient(ellipse 120% 80% at 100% 0%, rgba(14, 165, 233, 0.14), transparent 50%),
      radial-gradient(ellipse 90% 60% at 0% 100%, rgba(59, 130, 246, 0.1), transparent 45%),
      linear-gradient(165deg, #f8fafc 0%, #e2e8f0 55%, #cbd5e1 100%);
    padding-left: env(safe-area-inset-left);
    padding-right: env(safe-area-inset-right);
    padding-bottom: env(safe-area-inset-bottom);
  }

  /* Main content: fluid width, breathing room on all breakpoints */
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .block-container {
    max-width: min(1120px, 100%) !important;
    margin-left: auto !important;
    margin-right: auto !important;
    margin-top: clamp(0.75rem, 3vw, 2rem) !important;
    margin-bottom: clamp(1rem, 4vw, 2.5rem) !important;
    padding: clamp(1rem, 3vw, 1.75rem) clamp(0.75rem, 3vw, 2rem) !important;
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.85);
    border-radius: clamp(14px, 2.5vw, 22px);
    box-shadow:
      0 1px 0 rgba(255, 255, 255, 0.9) inset,
      0 4px 24px rgba(15, 23, 42, 0.07),
      0 24px 64px rgba(15, 23, 42, 0.1);
  }

  @media (prefers-reduced-motion: no-preference) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .block-container {
      animation: rnk-auth-enter 0.55s cubic-bezier(0.22, 1, 0.36, 1) both;
    }
  }

  @keyframes rnk-auth-enter {
    from { opacity: 0; transform: translateY(16px) scale(0.99); }
    to { opacity: 1; transform: translateY(0) scale(1); }
  }

  /* --- Two-column row: responsive flex --- */
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    gap: clamp(1rem, 3vw, 2rem) !important;
    flex-wrap: nowrap !important;
  }

  /* Nested columns inside auth forms (register / sign-in field pairs) */
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
    gap: 0.65rem 1rem !important;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stForm"] [data-testid="column"] {
    min-width: 0 !important;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stForm"] [data-baseweb="input"] {
    border-radius: 10px !important;
  }

  @media (max-width: 520px) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stForm"] [data-testid="stHorizontalBlock"] {
      flex-direction: column !important;
    }
  }

  /* Phone / small tablet: stack — form column first (DOM order: swap visually) */
  @media (max-width: 900px) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stHorizontalBlock"] {
      flex-direction: column !important;
    }
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) {
      order: 2;
    }
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
      order: 1;
    }
  }

  /* --- Left marketing panel (desktop / large) --- */
  .rnk-auth-aside {
    position: relative;
    height: 100%;
    min-height: min(420px, 55vh);
    padding: clamp(1.25rem, 3vw, 2rem);
    border-radius: clamp(12px, 2vw, 18px);
    background: linear-gradient(145deg, #0f172a 0%, #1e3a5f 48%, #0c4a6e 100%);
    color: #e2e8f0;
    overflow: hidden;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
  }
  .rnk-auth-aside__glow {
    position: absolute;
    inset: -40% -20% auto -20%;
    height: 80%;
    background: radial-gradient(circle, rgba(14, 165, 233, 0.35) 0%, transparent 65%);
    pointer-events: none;
  }
  .rnk-auth-aside .rnk-mark--lg {
    position: relative;
    z-index: 1;
    width: clamp(52px, 12vw, 64px);
    height: clamp(52px, 12vw, 64px);
    font-size: clamp(1.1rem, 2.5vw, 1.35rem);
    margin-bottom: 1.25rem;
  }
  .rnk-auth-aside__title {
    position: relative;
    z-index: 1;
    margin: 0;
    font-size: clamp(1.35rem, 3.2vw, 1.85rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    line-height: 1.2;
    color: #fff;
  }
  .rnk-auth-aside__lead {
    position: relative;
    z-index: 1;
    margin: 0.65rem 0 1.25rem;
    font-size: clamp(0.88rem, 2vw, 1rem);
    line-height: 1.55;
    color: #94a3b8;
    max-width: 28ch;
  }
  .rnk-auth-aside__list {
    position: relative;
    z-index: 1;
    list-style: none;
    margin: 0;
    padding: 0;
    font-size: clamp(0.82rem, 1.8vw, 0.95rem);
    line-height: 1.65;
    color: #cbd5e1;
  }
  .rnk-auth-aside__list li {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    margin-bottom: 0.65rem;
  }
  .rnk-auth-aside__icon {
    flex-shrink: 0;
    width: 1.35rem;
    height: 1.35rem;
    margin-top: 0.1rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 6px;
    background: rgba(14, 165, 233, 0.2);
    color: #38bdf8;
    font-size: 0.75rem;
    font-weight: 700;
  }

  @media (max-width: 900px) {
    .rnk-auth-aside {
      min-height: auto;
      padding: clamp(1rem, 3vw, 1.25rem);
    }
    .rnk-auth-aside__title { font-size: clamp(1.15rem, 4vw, 1.35rem); }
    .rnk-auth-aside__lead { margin-bottom: 0.75rem; }
    .rnk-auth-aside__list li { margin-bottom: 0.45rem; }
  }

  /* Hide full aside on very small screens — brand block in form column covers it */
  @media (max-width: 520px) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) {
      display: none !important;
    }
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {
      order: 1 !important;
    }
  }

  /* --- Shared logo tile --- */
  .rnk-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border-radius: 14px;
    background: linear-gradient(145deg, #0ea5e9 0%, #0284c7 100%);
    color: #fff;
    font-weight: 700;
    font-size: 1.15rem;
    letter-spacing: -0.02em;
    box-shadow: 0 10px 28px rgba(2, 132, 199, 0.35);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
  }
  @media (hover: hover) and (prefers-reduced-motion: no-preference) {
    .rnk-auth-aside:hover .rnk-mark--lg,
    .rnk-auth-brand:hover .rnk-mark {
      transform: translateY(-2px) scale(1.02);
      box-shadow: 0 14px 36px rgba(2, 132, 199, 0.45);
    }
  }

  /* Mobile brand (hidden on wide where aside shows) */
  .rnk-auth-brand {
    text-align: center;
    margin-bottom: clamp(1rem, 3vw, 1.5rem);
  }
  .rnk-auth-brand h1 {
    margin: 0;
    font-size: clamp(1.35rem, 4vw, 1.65rem);
    font-weight: 700;
    color: #0f172a;
    letter-spacing: -0.03em;
  }
  .rnk-auth-brand .rnk-tagline {
    margin: 0.4rem 0 0;
    font-size: clamp(0.88rem, 2.2vw, 0.95rem);
    color: #64748b;
    line-height: 1.45;
    max-width: 36ch;
    margin-left: auto;
    margin-right: auto;
  }
  /* Brand strip: only when left panel is off (narrow phones) — tablets/desktop use aside or split */
  @media (min-width: 521px) {
    .rnk-auth-brand--mobile { display: none !important; }
  }
  @media (max-width: 520px) {
    .rnk-auth-brand--mobile { display: block !important; }
  }

  /* --- Form column polish --- */
  .rnk-auth-section-label {
    margin: 0.5rem 0 0.35rem;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #64748b;
  }

  .rnk-auth-hint {
    font-size: clamp(0.78rem, 2vw, 0.85rem);
    color: #64748b;
    margin: -0.2rem 0 0.9rem;
    line-height: 1.45;
  }

  /* Tabs: tactile pill control */
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="tab-list"] {
    gap: 0.4rem;
    background: #e2e8f0;
    padding: 0.4rem;
    border-radius: 14px;
    border-bottom: none !important;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="tab"] {
    border-radius: 11px !important;
    font-weight: 600 !important;
    font-size: clamp(0.82rem, 2vw, 0.92rem) !important;
    padding: 0.55rem 1rem !important;
    min-height: 44px;
    color: #64748b !important;
    border: none !important;
    transition: background 0.2s ease, color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="tab"]:hover {
    background: rgba(255, 255, 255, 0.92) !important;
    color: #334155 !important;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [aria-selected="true"] {
    background: #fff !important;
    color: #0f172a !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.1) !important;
  }
  @media (hover: hover) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="tab"]:active {
      transform: scale(0.98);
    }
  }

  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="tab-panel"] {
    padding-top: clamp(0.85rem, 2vw, 1.15rem);
  }

  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) label,
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-testid="stWidgetLabel"] {
    font-weight: 500 !important;
    font-size: clamp(0.82rem, 2vw, 0.88rem) !important;
    color: #334155 !important;
  }

  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="input"] {
    border-radius: 11px !important;
    min-height: 46px;
    transition: box-shadow 0.2s ease, border-color 0.2s ease, transform 0.15s ease;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="input"]:focus-within {
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.25) !important;
    border-color: #0ea5e9 !important;
  }

  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .stButton > button[kind="primary"] {
    width: 100%;
    min-height: 48px;
    border-radius: 12px;
    font-weight: 600;
    font-size: clamp(0.92rem, 2.2vw, 1rem);
    padding: 0.65rem 1rem;
    background: linear-gradient(180deg, #0ea5e9 0%, #0284c7 100%);
    border: none;
    box-shadow: 0 4px 16px rgba(2, 132, 199, 0.38);
    transition: transform 0.18s ease, box-shadow 0.22s ease, filter 0.15s ease;
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(2, 132, 199, 0.48);
    filter: brightness(1.02);
  }
  :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .stButton > button[kind="primary"]:active {
    transform: translateY(0);
  }

  @media (prefers-reduced-motion: reduce) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .block-container { animation: none !important; }
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) [data-baseweb="tab"],
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .stButton > button[kind="primary"] {
      transition: none !important;
    }
    .rnk-mark { transition: none !important; }
  }

  .rnk-auth-foot {
    text-align: center;
    margin-top: clamp(1.25rem, 3vw, 1.75rem);
    font-size: clamp(0.72rem, 1.8vw, 0.8rem);
    color: #94a3b8;
  }

  /* Large desktop: optional max width on form column content */
  @media (min-width: 1200px) {
    :is(section.main, [data-testid="stMain"]):has(.rnk-auth-root) .block-container {
      max-width: min(1180px, 94vw) !important;
    }
  }
</style>
""",
        unsafe_allow_html=True,
    )

