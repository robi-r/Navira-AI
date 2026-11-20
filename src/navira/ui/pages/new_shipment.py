"""New-shipment form, pre-filled from the sample data."""

import logging

import streamlit as st

from navira.models import INCOTERMS, TRANSPORT_MODES, Shipment, ShipmentValidationError
from navira.ui import components, state

logger = logging.getLogger(__name__)

_PICK_KEY = "sample_pick"


def _sample_label(s: Shipment) -> str:
    return f"{s.reference}: {s.description} ({s.origin_country} → {s.destination_country})"


def render() -> None:
    st.title("New shipment")
    components.sample_data_banner()
    samples = state.samples()
    current = state.shipment()

    # Offer the user's own (edited) shipment first, then the samples.
    choices: list[tuple[str, Shipment]] = []
    if current not in samples:
        choices.append((f"Current shipment: {current.reference}", current))
    choices += [(_sample_label(s), s) for s in samples]
    default_idx = 0 if current not in samples else samples.index(current)
    idx = st.selectbox(
        "Start from",
        options=range(len(choices)),
        index=default_idx,
        format_func=lambda i: choices[i][0],
        key=_PICK_KEY,
        help="Pick a sample to pre-fill the form, then edit any field.",
    )
    base = choices[idx][1]

    with st.form(key=f"shipment_form_{idx}"):
        c1, c2 = st.columns(2)
        reference = c1.text_input("Reference", base.reference, max_chars=40)
        description = c2.text_input("Goods description", base.description, max_chars=120)
        c1, c2, c3 = st.columns(3)
        hs_code = c1.text_input("HS code", base.hs_code, help="4-10 digits, e.g. 8471.30")
        origin = c2.text_input("Origin country (ISO-2)", base.origin_country, max_chars=2)
        destination = c3.text_input("Destination country (ISO-2)", base.destination_country, max_chars=2)
        c1, c2, c3 = st.columns(3)
        incoterm = c1.selectbox("Incoterm", INCOTERMS, index=INCOTERMS.index(base.incoterm))
        mode = c2.selectbox("Transport mode", TRANSPORT_MODES, index=TRANSPORT_MODES.index(base.transport_mode))
        c3.text_input("Currency", "USD", disabled=True, help="Only USD is supported in this version.")
        c1, c2, c3 = st.columns(3)
        goods_value = c1.number_input("Goods value (USD)", min_value=0.0, value=float(base.goods_value), step=100.0)
        weight = c2.number_input("Gross weight (kg)", min_value=0.0, value=float(base.weight_kg), step=10.0)
        volume = c3.number_input("Volume (m3)", min_value=0.0, value=float(base.volume_cbm), step=0.1, format="%.2f")
        preferential = st.checkbox("Claim preferential origin (reduced duty)", value=base.preferential_origin)
        submitted = st.form_submit_button("Save and estimate", type="primary")

    if not submitted:
        return

    try:
        shipment = Shipment.from_dict({
            "reference": reference, "description": description, "hs_code": hs_code,
            "origin_country": origin, "destination_country": destination, "incoterm": incoterm,
            "transport_mode": mode, "goods_value": goods_value, "weight_kg": weight,
            "volume_cbm": volume, "currency": "USD", "preferential_origin": preferential,
        })
        shipment.ensure_valid()
    except ShipmentValidationError as exc:
        logger.info("Shipment form rejected: %s", exc)
        st.error("Please fix the following before continuing:\n\n" + "\n".join(f"- {e}" for e in exc.errors))
        return

    state.set_shipment(shipment)
    state.go_to("cost")
