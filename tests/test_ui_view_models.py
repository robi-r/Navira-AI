from navira.checklist import build_checklist
from navira.landed_cost import estimate_landed_cost
from navira.ui.view_models import breakdown_rows, format_money, missing_required, quote_filename


def test_breakdown_rows_label_estimates(air_shipment):
    rows = breakdown_rows(estimate_landed_cost(air_shipment))
    by_item = {r["Item"]: r for r in rows}
    assert by_item["Freight (estimate)"]["Type"] == "Estimate"
    assert by_item["Import duty (estimate)"]["Type"] == "Estimate"
    assert by_item["Goods value (invoice)"]["Type"] == "Invoice"
    assert rows[-1]["Item"] == "Total landed cost (estimate)"
    assert rows[-1]["Amount (USD)"] == "50,912.20"


def test_missing_required(air_shipment):
    items = build_checklist(air_shipment)
    required = [i for i in items if i.required]
    assert len(missing_required(items, {})) == len(required)
    assert len(missing_required(items, {required[0].id: True})) == len(required) - 1
    optional = next(i for i in items if not i.required)
    assert len(missing_required(items, {optional.id: True})) == len(required)


def test_format_and_filename():
    assert format_money(1234.5) == "USD 1,234.50"
    assert quote_filename("NAV/24 001") == "navira-quote-NAV_24_001.md"
    assert quote_filename("") == "navira-quote-shipment.md"
