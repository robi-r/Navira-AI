"""Import checklist page. Ticks are kept in session state so they survive page changes."""

import logging
from itertools import groupby

import streamlit as st

from navira.checklist import build_checklist
from navira.models import ShipmentValidationError
from navira.ui import components, state
from navira.ui.view_models import missing_required

logger = logging.getLogger(__name__)


def _toggle(item_id: str, widget_key: str) -> None:
    state.checklist_done()[item_id] = bool(st.session_state[widget_key])


def render() -> None:
    st.title("Import checklist")
    components.sample_data_banner()
    components.shipment_summary()
    shipment = state.shipment()

    try:
        items = build_checklist(shipment)
    except ShipmentValidationError as exc:
        st.error("Fix the shipment first:\n\n" + "\n".join(f"- {e}" for e in exc.errors))
        return
    except Exception:  # noqa: BLE001
        logger.exception("Checklist failed for %s", shipment.reference)
        st.error("Something went wrong while building the checklist. The error has been logged.")
        return

    done = state.checklist_done()
    missing = missing_required(items, done)
    required_total = sum(i.required for i in items)

    c1, c2 = st.columns(2)
    c1.metric("Missing required items", len(missing))
    c2.metric("Required items complete", f"{required_total - len(missing)} / {required_total}")
    if missing:
        st.warning(f"{len(missing)} required item(s) still missing: " + ", ".join(i.label for i in missing))
    else:
        st.success("All required items are complete.")

    for category, group in groupby(sorted(items, key=lambda i: (i.category, not i.required)), key=lambda i: i.category):
        st.markdown(f"#### {category}")
        for item in group:
            key = f"chk_{shipment.reference}_{item.id}"
            label = f"{item.label} {'· **required**' if item.required else '· optional'}"
            st.checkbox(label, value=done.get(item.id, False), key=key, help=item.note or None,
                        on_change=_toggle, args=(item.id, key))

    if st.button("Preview quote", type="primary"):
        state.go_to("quote")
