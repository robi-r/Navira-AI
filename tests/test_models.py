import pytest

from navira.models import Shipment, ShipmentValidationError


def test_valid_shipment_has_no_errors(air_shipment):
    assert air_shipment.validate() == []
    assert air_shipment.hs_chapter == "84"


def test_from_dict_normalises_case():
    s = Shipment.from_dict({"reference": "R", "description": "d", "hs_code": "8471", "origin_country": "cn",
                            "destination_country": "us", "incoterm": "fob", "transport_mode": "AIR",
                            "goods_value": "10", "weight_kg": 1, "volume_cbm": 0.1})
    assert (s.origin_country, s.incoterm, s.transport_mode, s.goods_value) == ("CN", "FOB", "air", 10.0)


def test_from_dict_rejects_non_numeric():
    with pytest.raises(ShipmentValidationError):
        Shipment.from_dict({"goods_value": "lots"})


@pytest.mark.parametrize("field,value,fragment", [
    ("hs_code", "12", "HS code"),
    ("origin_country", "China", "Origin"),
    ("destination_country", "CN", "different"),
    ("incoterm", "XYZ", "Incoterm"),
    ("transport_mode", "rail", "Transport mode"),
    ("goods_value", 0, "Goods value"),
    ("weight_kg", -1, "Weight"),
    ("currency", "EUR", "USD"),
])
def test_validation_errors(air_shipment, field, value, fragment):
    bad = Shipment(**{**air_shipment.to_dict(), field: value})
    errors = bad.validate()
    assert any(fragment in e for e in errors), errors
    with pytest.raises(ShipmentValidationError):
        bad.ensure_valid()
