"""Session state and navigation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import streamlit as st

from navira.data import load_sample_shipments
from navira.models import Shipment

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PageInfo:
    key: str
    title: str


PAGES: tuple[PageInfo, ...] = (
    PageInfo("home", "Home"),
    PageInfo("new", "New shipment"),
    PageInfo("cost", "Landed cost"),
    PageInfo("checklist", "Checklist"),
    PageInfo("quote", "Quote"),
)
PAGE_TITLES = {p.key: p.title for p in PAGES}

NAV_KEY = "nav"
_PENDING_NAV = "_pending_nav"
_SHIPMENT = "shipment"
_IS_SAMPLE = "shipment_is_sample"
_CHECKLIST = "checklist_done"


@st.cache_data(show_spinner=False)
def samples() -> list[Shipment]:
    return load_sample_shipments()


def init() -> None:
    """Set defaults once per session and apply any navigation requested on the last run."""
    if _SHIPMENT not in st.session_state:
        st.session_state[_SHIPMENT] = samples()[0]
        st.session_state[_IS_SAMPLE] = True
        st.session_state[_CHECKLIST] = {}
    st.session_state.setdefault(NAV_KEY, "home")
    pending = st.session_state.pop(_PENDING_NAV, None)
    if pending in PAGE_TITLES:
        st.session_state[NAV_KEY] = pending


def go_to(page_key: str) -> None:
    """Switch page from inside a page body (after the sidebar widget was drawn)."""
    if page_key not in PAGE_TITLES:
        raise ValueError(f"Unknown page {page_key!r}")
    st.session_state[_PENDING_NAV] = page_key
    st.rerun()


def current_page() -> str:
    return st.session_state.get(NAV_KEY, "home")


def shipment() -> Shipment:
    return st.session_state[_SHIPMENT]


def is_sample() -> bool:
    return bool(st.session_state.get(_IS_SAMPLE, False))


def set_shipment(new: Shipment) -> None:
    old: Shipment = st.session_state.get(_SHIPMENT)
    st.session_state[_SHIPMENT] = new
    st.session_state[_IS_SAMPLE] = new in samples()
    if old is None or old.reference != new.reference:
        st.session_state[_CHECKLIST] = {}
    logger.info("Shipment set: %s (sample=%s)", new.reference, is_sample())


def checklist_done() -> dict[str, bool]:
    return st.session_state.setdefault(_CHECKLIST, {})
