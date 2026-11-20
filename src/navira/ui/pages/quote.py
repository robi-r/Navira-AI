"""Quote preview and download."""

import logging

import streamlit as st

from navira.checklist import build_checklist
from navira.landed_cost import estimate_landed_cost
from navira.models import ShipmentValidationError
from navira.quote import build_quote_markdown
from navira.ui import components, state
from navira.ui.view_models import quote_filename

logger = logging.getLogger(__name__)


def render() -> None:
    st.title("Quote preview")
    components.sample_data_banner()
    shipment = state.shipment()

    try:
        estimate = estimate_landed_cost(shipment)
        items = build_checklist(shipment)
        markdown = build_quote_markdown(shipment, estimate, items, state.checklist_done())
    except ShipmentValidationError as exc:
        st.error("Fix the shipment first:\n\n" + "\n".join(f"- {e}" for e in exc.errors))
        return
    except Exception:  # noqa: BLE001
        logger.exception("Quote build failed for %s", shipment.reference)
        st.error("Something went wrong while building the quote. The error has been logged.")
        return

    st.download_button(
        "Download quote (.md)",
        data=markdown.encode("utf-8"),
        file_name=quote_filename(shipment.reference),
        mime="text/markdown",
        type="primary",
    )
    with st.container(border=True):
        st.markdown(markdown)
