"""Navira AI Streamlit app. Run with: streamlit run app.py"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

# Allow `streamlit run app.py` from a fresh checkout without `pip install -e .`.
_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st  # noqa: E402

from navira.ui import components, state  # noqa: E402
from navira.ui.pages import checklist, landed_cost, landing, new_shipment, quote  # noqa: E402

RENDERERS = {
    "home": landing.render,
    "new": new_shipment.render,
    "cost": landed_cost.render,
    "checklist": checklist.render,
    "quote": quote.render,
}


def _configure_logging() -> None:
    root = logging.getLogger()
    if not any(getattr(h, "_navira", False) for h in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        handler._navira = True  # type: ignore[attr-defined]
        root.addHandler(handler)
    logging.getLogger("navira").setLevel(os.environ.get("NAVIRA_LOG_LEVEL", "INFO").upper())


def main() -> None:
    _configure_logging()
    st.set_page_config(page_title="Navira AI", page_icon="🚢", layout="wide")
    components.inject_css()

    try:
        state.init()
    except Exception:  # noqa: BLE001
        logging.getLogger("navira").exception("Failed to load sample data")
        st.error("Could not load sample data from data/sample_shipments.json.")
        st.stop()

    with st.sidebar:
        st.markdown("## Navira AI")
        st.radio("Navigate", list(RENDERERS), key=state.NAV_KEY, format_func=state.PAGE_TITLES.get,
                 label_visibility="collapsed")
        st.divider()
        st.caption(f"Current shipment: **{state.shipment().reference}**")
        if state.is_sample():
            st.caption("Sample data")

    RENDERERS[state.current_page()]()


main()
