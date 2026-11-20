from datetime import date

from navira.checklist import build_checklist
from navira.data import load_sample_shipments
from navira.landed_cost import estimate_landed_cost
from navira.models import Shipment
from navira.quote import build_quote_markdown


def test_samples_load_and_are_valid():
    samples = load_sample_shipments()
    assert len(samples) >= 3
    for s in samples:
        assert s.validate() == []
        estimate_landed_cost(s)
        build_checklist(s)


def test_checklist_required_first_and_mode_specific(air_shipment):
    items = build_checklist(air_shipment)
    ids = {i.id for i in items}
    assert "air_waybill" in ids and "bill_of_lading" not in ids
    assert "customs_bond" in ids
    flags = [i.required for i in items]
    assert flags == sorted(flags, reverse=True)
    assert len(ids) == len(items)


def test_checklist_preferential_and_licensed():
    s = Shipment(reference="R", description="Medicine", hs_code="3004.90", origin_country="IN",
                 destination_country="DE", incoterm="CIF", transport_mode="sea", goods_value=1000,
                 weight_kg=100, volume_cbm=1, preferential_origin=True)
    items = {i.id: i for i in build_checklist(s)}
    assert items["certificate_of_origin"].required
    assert items["import_licence"].required
    assert items["eori"].required
    assert items["insurance_certificate"].required


def test_quote_marks_estimates_and_missing_count(air_shipment):
    est = estimate_landed_cost(air_shipment)
    items = build_checklist(air_shipment)
    done = {items[0].id: True}
    md = build_quote_markdown(air_shipment, est, items, done, issued_on=date(2026, 1, 2))
    assert "Freight (estimate)" in md and "Import duty (estimate)" in md
    assert "Issued: 2026-01-02" in md
    required = sum(i.required for i in items)
    assert f"Missing required items: {required - 1}" in md
    assert "Goods value (invoice) (estimate)" not in md
