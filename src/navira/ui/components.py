"""Small shared UI pieces."""

from __future__ import annotations

import streamlit as st

from navira.ui import state

ACCENT = "#1B5E20"

_CSS = f"""
<style>
.navira-badge {{display:inline-block;padding:1px 8px;border-radius:10px;font-size:0.75rem;
  font-weight:600;border:1px solid {ACCENT};color:{ACCENT};background:#fff;}}
.navira-sample {{border-left:4px solid {ACCENT};background:#F3F6F3;padding:10px 14px;margin:4px 0 16px 0;}}
.navira-muted {{color:#5A635A;font-size:0.9rem;}}
h1, h2, h3 {{color:#14361A;}}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def sample_data_banner(always: bool = False) -> None:
    """Shown on the home page always, elsewhere only while a sample shipment is loaded."""
    if always or state.is_sample():
        st.markdown(
            '<div class="navira-sample"><span class="navira-badge">Sample data</span>&nbsp; '
            "You are viewing sample shipments from <code>data/sample_shipments.json</code>. "
            "Figures are illustrative.</div>",
            unsafe_allow_html=True,
        )


def estimate_note() -> None:
    st.caption(
        "Freight, duty, tax and fee figures are **estimates** from illustrative rate tables, "
        "not carrier quotes or tariff rulings."
    )


def shipment_summary() -> None:
    s = state.shipment()
    st.markdown(
        f"**{s.reference}** · {s.description} · HS {s.hs_code} · "
        f"{s.origin_country} → {s.destination_country} · {s.transport_mode} · {s.incoterm}"
    )
