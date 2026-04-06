"""Central logging setup for the Streamlit app."""
from __future__ import annotations

import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure root logging once (idempotent)."""
    root = logging.getLogger()
    if root.handlers:
        return
    lvl = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=lvl,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stderr,
        force=False,
    )
    # Quiet noisy third-party loggers if needed
    logging.getLogger("pymongo").setLevel(logging.WARNING)
