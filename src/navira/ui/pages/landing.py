"""Landing / home page."""

import streamlit as st

from navira.ui import components, state

FEATURES = (
    ("Landed-cost estimates", "Freight, insurance, duty, import tax and fees in one breakdown, with every assumption listed."),
    ("Incoterm-aware", "Shows only the costs the importer pays under EXW, FOB, CIF, DDP and more."),
    ("Import checklist", "Documents and registrations by route, mode and HS chapter, with a count of what is still missing."),
    ("Shareable quote", "A clean quote preview you can download and send to your team or broker."),
)

STEPS = ("Enter or pick a shipment", "Review the estimated landed cost", "Tick off the checklist", "Download the quote")


def render() -> None:
    components.sample_data_banner(always=True)
    st.title("Navira AI")
    st.subheader("Know your landed cost before the goods ship.")
    st.write(
        "Navira estimates the full cost of importing a shipment (freight, insurance, duty, "
        "import VAT/GST and fees) and builds the document checklist you need to clear customs."
    )
    col_a, col_b, _ = st.columns([1, 1, 2])
    if col_a.button("Start a shipment", type="primary", width="stretch"):
        state.go_to("new")
    if col_b.button("See sample estimate", width="stretch"):
        state.go_to("cost")

    st.divider()
    st.markdown("### What it does")
    cols = st.columns(len(FEATURES))
    for col, (title, body) in zip(cols, FEATURES):
        with col.container(border=True):
            st.markdown(f"**{title}**")
            st.markdown(f'<span class="navira-muted">{body}</span>', unsafe_allow_html=True)

    st.markdown("### How it works")
    st.markdown("\n".join(f"{i}. {step}" for i, step in enumerate(STEPS, start=1)))

    st.divider()
    components.estimate_note()
