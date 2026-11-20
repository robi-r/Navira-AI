"""End-to-end tests of the Streamlit app using streamlit.testing (no browser needed)."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def _goto(at: AppTest, page: str) -> AppTest:
    at.sidebar.radio(key="nav").set_value(page).run()
    assert not at.exception, at.exception
    return at


def _text(at: AppTest) -> str:
    parts = [m.value for m in at.markdown] + [t.value for t in at.title] + [c.value for c in at.caption]
    parts += [m.label for m in at.metric] + [w.value for w in at.warning] + [s.value for s in at.success]
    return "\n".join(str(p) for p in parts)


@pytest.fixture
def at() -> AppTest:
    app = AppTest.from_file(APP, default_timeout=30).run()
    assert not app.exception, app.exception
    return app


def test_home_has_sample_banner_and_start_button(at):
    assert "Sample data" in _text(at)
    assert "Navira AI" in _text(at)
    at.button[0].click().run()  # "Start a shipment"
    assert at.session_state["nav"] == "new"
    assert at.text_input[0].value == "NAV-24001"


@pytest.mark.parametrize("page", ["home", "new", "cost", "checklist", "quote"])
def test_every_page_renders(at, page):
    _goto(at, page)
    assert not at.error


def test_form_prefilled_and_validation(at):
    _goto(at, "new")
    labels = {t.label: t for t in at.text_input}
    assert labels["Reference"].value == "NAV-24001"
    assert labels["HS code"].value == "8471.30"
    labels["HS code"].set_value("12")
    at.button[0].click().run()  # form submit
    assert at.error and "HS code" in at.error[0].value
    assert at.session_state["nav"] == "new"


def test_form_submit_updates_shipment_and_moves_to_cost(at):
    _goto(at, "new")
    at.selectbox(key="sample_pick").set_value(1).run()
    assert {t.label: t.value for t in at.text_input}["Reference"] == "NAV-24002"
    {t.label: t for t in at.text_input}["Reference"].set_value("MY-001")
    at.button[0].click().run()
    assert not at.exception
    assert at.session_state["nav"] == "cost"
    assert at.session_state["shipment"].reference == "MY-001"
    assert "Sample data" not in "\n".join(m.value for m in at.markdown)


def test_landed_cost_labels_estimates(at):
    _goto(at, "cost")
    text = _text(at)
    assert "Freight (estimate)" in text and "Duty (estimate)" in text
    df = at.dataframe[0].value
    assert "Freight (estimate)" in set(df["Item"]) and "Import duty (estimate)" in set(df["Item"])
    assert "Assumptions" in text


def test_checklist_ticks_persist_and_count_updates(at):
    _goto(at, "checklist")
    before = next(m for m in at.metric if m.label == "Missing required items").value
    at.checkbox[0].check().run()
    after = next(m for m in at.metric if m.label == "Missing required items").value
    assert int(after) == int(before) - 1
    _goto(at, "home")
    _goto(at, "checklist")
    assert at.checkbox[0].value is True
    assert next(m for m in at.metric if m.label == "Missing required items").value == after


def test_quote_has_download_and_estimates(at):
    _goto(at, "quote")
    assert "Freight (estimate)" in _text(at)
    assert "Download quote" in at.get("download_button")[0].proto.label
