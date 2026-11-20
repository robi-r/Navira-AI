"""Landed-cost results page."""

import logging

import pandas as pd
import streamlit as st

from navira.landed_cost import estimate_landed_cost
from navira.models import ShipmentValidationError
from navira.ui import components, state
from navira.ui.view_models import breakdown_rows, format_money

logger = logging.getLogger(__name__)


def render() -> None:
    st.title("Landed cost")
    components.sample_data_banner()
    components.shipment_summary()
    shipment = state.shipment()

    try:
        estimate = estimate_landed_cost(shipment)
    except ShipmentValidationError as exc:
        st.error("This shipment can't be estimated:\n\n" + "\n".join(f"- {e}" for e in exc.errors))
        if st.button("Edit shipment"):
            state.go_to("new")
        return
    except Exception:  # noqa: BLE001 - show a friendly message, keep the trace in logs
        logger.exception("Landed-cost estimate failed for %s", shipment.reference)
        st.error("Something went wrong while estimating this shipment. The error has been logged.")
        return

    cur = estimate.currency
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total landed cost (estimate)", format_money(estimate.total, cur))
    m2.metric("Freight (estimate)", format_money(estimate.line("freight").amount, cur))
    m3.metric("Duty (estimate)", format_money(estimate.line("duty").amount, cur))
    m4.metric("Customs value (estimate)", format_money(estimate.customs_value, cur))

    st.markdown("#### Breakdown")
    st.dataframe(pd.DataFrame(breakdown_rows(estimate)), hide_index=True, width="stretch")
    components.estimate_note()

    for warning in estimate.warnings:
        st.warning(warning)

    st.markdown("#### Assumptions")
    st.markdown("\n".join(f"- {a}" for a in estimate.assumptions))

    c1, c2, _ = st.columns([1, 1, 2])
    if c1.button("Continue to checklist", type="primary", width="stretch"):
        state.go_to("checklist")
    if c2.button("Edit shipment", width="stretch"):
        state.go_to("new")
