"""Highly custom CSS motion: keyframes, staggered reveals, ambient layers, auth polish.

Streamlit re-renders on interaction; animations are CSS-only (no JS) and respect
``prefers-reduced-motion``.
"""
from __future__ import annotations

import streamlit as st


def inject_ui_animations(theme: str = "light") -> None:
    """Inject global animation stylesheet (call once per run after :func:`inject_theme`)."""
    _ = theme  # reserved for theme-specific tuning
    st.markdown(
        """
<style id="rnk-ui-animations">
  :root {
    --rnk-motion-ease-out: cubic-bezier(0.22, 1, 0.36, 1);
    --rnk-motion-ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
    --rnk-motion-stagger: 0.045s;
    --rnk-motion-page: 0.58s;
  }

  @media (prefers-reduced-motion: reduce) {
    .rnk-anim-hero,
    .rnk-anim-reveal,
    .rnk-auth-aside,
    .rnk-auth-aside__glow,
    .rnk-auth-aside::before,
    .rnk-auth-aside .rnk-mark--lg,
    [data-testid="stSidebar"] .rnk-sidebar-identity,
    [data-testid="stSidebar"] .rnk-sidebar-avatar,
    header[data-testid="stHeader"]::after,
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))::before,
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"],
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"],
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMetricContainer"],
    .rnk-stat-grid .rnk-stat-tile,
    .rnk-auth-aside__list li {
      animation: none !important;
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      .stButton
      > button[kind="primary"]::before {
      display: none !important;
    }
  }

  @media (prefers-reduced-motion: no-preference) {

    /* ---- Keyframes ---- */
    @keyframes rnk-reveal-up {
      from {
        opacity: 0;
        transform: translateY(16px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @keyframes rnk-reveal-soft {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes rnk-scale-in {
      from {
        opacity: 0;
        transform: scale(0.96);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    @keyframes rnk-slide-in-left {
      from {
        opacity: 0;
        transform: translateX(-14px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }

    @keyframes rnk-ambient-drift {
      0% {
        transform: translate(0%, 0%) rotate(0deg) scale(1);
        opacity: 0.55;
      }
      50% {
        transform: translate(-1.5%, 1%) rotate(1.5deg) scale(1.04);
        opacity: 0.72;
      }
      100% {
        transform: translate(0.5%, -0.5%) rotate(-1deg) scale(1);
        opacity: 0.6;
      }
    }

    @keyframes rnk-header-shimmer {
      0%,
      100% {
        opacity: 0.45;
        filter: hue-rotate(0deg) brightness(1);
      }
      50% {
        opacity: 0.85;
        filter: hue-rotate(18deg) brightness(1.08);
      }
    }

    @keyframes rnk-glow-pulse {
      0%,
      100% {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25), 0 0 0 0 rgba(196, 181, 253, 0.35);
      }
      50% {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.28), 0 0 24px 2px rgba(167, 139, 250, 0.22);
      }
    }

    @keyframes rnk-float-soft {
      0%,
      100% {
        transform: translateY(0);
      }
      50% {
        transform: translateY(-4px);
      }
    }

    @keyframes rnk-shimmer-sweep {
      0% {
        background-position: 200% 50%;
      }
      100% {
        background-position: -200% 50%;
      }
    }

    @keyframes rnk-auth-glow-breathe {
      0%,
      100% {
        opacity: 0.55;
        transform: scale(1);
      }
      50% {
        opacity: 0.9;
        transform: scale(1.08);
      }
    }

    @keyframes rnk-auth-mesh {
      0% {
        transform: translate(0, 0) rotate(0deg);
      }
      100% {
        transform: translate(-3%, 2%) rotate(4deg);
      }
    }

    @keyframes rnk-stat-pop {
      from {
        opacity: 0;
        transform: translateY(12px) scale(0.97);
      }
      to {
        opacity: 1;
        transform: translateY(0) scale(1);
      }
    }

    /* ---- Ambient mesh (workspace only) ---- */
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) {
      position: relative;
    }

    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))::before {
      content: "";
      position: absolute;
      inset: 0;
      z-index: 0;
      pointer-events: none;
      border-radius: 0;
      background:
        radial-gradient(ellipse 90% 55% at 95% 5%, rgba(124, 58, 237, 0.11), transparent 52%),
        radial-gradient(ellipse 70% 45% at 5% 95%, rgba(14, 165, 233, 0.07), transparent 48%),
        radial-gradient(ellipse 50% 35% at 50% 50%, rgba(167, 139, 250, 0.04), transparent 60%);
      animation: rnk-ambient-drift 22s ease-in-out infinite alternate;
      will-change: transform, opacity;
    }

    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .block-container {
      position: relative;
      z-index: 1;
    }

    /* ---- Header accent line ---- */
    header[data-testid="stHeader"]::after {
      animation: rnk-header-shimmer 5.5s ease-in-out infinite;
    }

    /* ---- Stagger Streamlit vertical blocks (main workspace) ---- */
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"] {
      animation: rnk-reveal-up var(--rnk-motion-page) var(--rnk-motion-ease-out) backwards;
    }

    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(1) {
      animation-delay: calc(var(--rnk-motion-stagger) * 0);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(2) {
      animation-delay: calc(var(--rnk-motion-stagger) * 1);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(3) {
      animation-delay: calc(var(--rnk-motion-stagger) * 2);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(4) {
      animation-delay: calc(var(--rnk-motion-stagger) * 3);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(5) {
      animation-delay: calc(var(--rnk-motion-stagger) * 4);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(6) {
      animation-delay: calc(var(--rnk-motion-stagger) * 5);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(7) {
      animation-delay: calc(var(--rnk-motion-stagger) * 6);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(8) {
      animation-delay: calc(var(--rnk-motion-stagger) * 7);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(9) {
      animation-delay: calc(var(--rnk-motion-stagger) * 8);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(10) {
      animation-delay: calc(var(--rnk-motion-stagger) * 9);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(11) {
      animation-delay: calc(var(--rnk-motion-stagger) * 10);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(12) {
      animation-delay: calc(var(--rnk-motion-stagger) * 11);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(13) {
      animation-delay: calc(var(--rnk-motion-stagger) * 12);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(14) {
      animation-delay: calc(var(--rnk-motion-stagger) * 13);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(15) {
      animation-delay: calc(var(--rnk-motion-stagger) * 14);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(16) {
      animation-delay: calc(var(--rnk-motion-stagger) * 15);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(17) {
      animation-delay: calc(var(--rnk-motion-stagger) * 16);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(18) {
      animation-delay: calc(var(--rnk-motion-stagger) * 17);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(19) {
      animation-delay: calc(var(--rnk-motion-stagger) * 18);
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      [data-testid="stVerticalBlock"]
      > div[data-testid="element-container"]:nth-child(20) {
      animation-delay: calc(var(--rnk-motion-stagger) * 19);
    }

    /* ---- Hero & branded components ---- */
    .rnk-anim-hero {
      animation: rnk-scale-in 0.65s var(--rnk-motion-ease-spring) 0.05s backwards;
    }

    .rnk-anim-reveal {
      animation: rnk-reveal-up 0.55s var(--rnk-motion-ease-out) backwards;
    }

    .rnk-stat-grid .rnk-stat-tile:nth-child(1) {
      animation: rnk-stat-pop 0.55s var(--rnk-motion-ease-out) 0.08s backwards;
    }
    .rnk-stat-grid .rnk-stat-tile:nth-child(2) {
      animation: rnk-stat-pop 0.55s var(--rnk-motion-ease-out) 0.16s backwards;
    }
    .rnk-stat-grid .rnk-stat-tile:nth-child(3) {
      animation: rnk-stat-pop 0.55s var(--rnk-motion-ease-out) 0.24s backwards;
    }
    .rnk-stat-grid .rnk-stat-tile:nth-child(4) {
      animation: rnk-stat-pop 0.55s var(--rnk-motion-ease-out) 0.32s backwards;
    }

    /* ---- Sidebar: identity card + avatar ---- */
    [data-testid="stSidebar"] .rnk-sidebar-identity {
      animation: rnk-slide-in-left 0.55s var(--rnk-motion-ease-out) backwards;
    }

    [data-testid="stSidebar"] .rnk-sidebar-avatar {
      position: relative;
      isolation: isolate;
      animation: rnk-glow-pulse 4.5s ease-in-out infinite;
    }

    /* ---- Primary buttons: shimmer accent on hover path ---- */
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
      .stButton
      > button[kind="primary"]::before {
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      background: linear-gradient(
        105deg,
        transparent 0%,
        rgba(255, 255, 255, 0.22) 45%,
        transparent 55%
      );
      background-size: 220% 100%;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) .stButton > button[kind="primary"] {
      position: relative;
      overflow: hidden;
    }
    @media (hover: hover) {
      :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root))
        .stButton
        > button[kind="primary"]:hover::before {
        opacity: 1;
        animation: rnk-shimmer-sweep 1.1s ease-out;
      }
    }

    /* ---- Auth: aside mesh + list stagger ---- */
    .rnk-auth-aside {
      animation: rnk-reveal-soft 0.7s ease backwards;
    }

    .rnk-auth-aside__glow {
      animation: rnk-auth-glow-breathe 7s ease-in-out infinite;
    }

    .rnk-auth-aside::before {
      content: "";
      position: absolute;
      inset: -20%;
      z-index: 0;
      background: radial-gradient(circle at 30% 30%, rgba(56, 189, 248, 0.2), transparent 55%),
        radial-gradient(circle at 70% 70%, rgba(124, 58, 237, 0.18), transparent 50%);
      pointer-events: none;
      animation: rnk-auth-mesh 28s ease-in-out infinite alternate;
    }

    .rnk-auth-aside .rnk-auth-aside__glow,
    .rnk-auth-aside .rnk-mark--lg,
    .rnk-auth-aside .rnk-auth-aside__title,
    .rnk-auth-aside .rnk-auth-aside__lead,
    .rnk-auth-aside .rnk-auth-aside__list {
      position: relative;
      z-index: 1;
    }

    .rnk-auth-aside__list li:nth-child(1) {
      animation: rnk-reveal-up 0.45s var(--rnk-motion-ease-out) 0.15s backwards;
    }
    .rnk-auth-aside__list li:nth-child(2) {
      animation: rnk-reveal-up 0.45s var(--rnk-motion-ease-out) 0.25s backwards;
    }
    .rnk-auth-aside__list li:nth-child(3) {
      animation: rnk-reveal-up 0.45s var(--rnk-motion-ease-out) 0.35s backwards;
    }
    .rnk-auth-aside__list li:nth-child(4) {
      animation: rnk-reveal-up 0.45s var(--rnk-motion-ease-out) 0.45s backwards;
    }
    .rnk-auth-aside__list li:nth-child(5) {
      animation: rnk-reveal-up 0.45s var(--rnk-motion-ease-out) 0.55s backwards;
    }

    .rnk-auth-aside .rnk-mark--lg {
      animation: rnk-float-soft 5s ease-in-out infinite;
    }

    /* ---- Dataframe / metrics subtle entrance ---- */
    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stDataFrame"] {
      animation: rnk-reveal-soft 0.5s var(--rnk-motion-ease-out) 0.12s backwards;
    }

    :is(section.main, [data-testid="stMain"]):not(:has(.rnk-auth-root)) [data-testid="stMetricContainer"] {
      animation: rnk-reveal-up 0.5s var(--rnk-motion-ease-out) backwards;
    }
  }
</style>
""",
        unsafe_allow_html=True,
    )
