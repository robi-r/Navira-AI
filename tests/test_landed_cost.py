import pytest

from navira.landed_cost import chargeable_weight, estimate_landed_cost
from navira.models import Shipment, ShipmentValidationError


def test_air_fob_to_us(air_shipment):
    est = estimate_landed_cost(air_shipment)
    assert est.line("freight").amount == 1440.00
    assert est.line("insurance").amount == 247.20
    assert est.customs_value == 48000.00  # US values FOB
    assert est.line("duty").amount == 960.00
    assert est.line("import_tax").amount == 0.00
    assert est.total == 50912.20


def test_freight_and_duty_lines_are_estimates(air_shipment):
    est = estimate_landed_cost(air_shipment)
    assert est.line("freight").is_estimate and est.line("duty").is_estimate
    assert not est.line("goods").is_estimate
    assert est.assumptions and "estimate" in est.assumptions[0].lower()


def test_volumetric_weight_used_for_air(air_shipment):
    bulky = Shipment(**{**air_shipment.to_dict(), "volume_cbm": 3.0})
    assert chargeable_weight(bulky) == pytest.approx(501.0)


def test_cif_seller_pays_freight_and_insurance(air_shipment):
    s = Shipment(**{**air_shipment.to_dict(), "incoterm": "CIF", "destination_country": "GB", "transport_mode": "sea"})
    est = estimate_landed_cost(s)
    assert est.line("freight").amount == 0 and est.line("insurance").amount == 0
    assert est.import_tax_rate == 0.20


def test_ddp_has_no_duty_or_tax(air_shipment):
    est = estimate_landed_cost(Shipment(**{**air_shipment.to_dict(), "incoterm": "DDP"}))
    assert est.line("duty").amount == 0 and est.line("import_tax").amount == 0


def test_preferential_origin_is_duty_free(air_shipment):
    est = estimate_landed_cost(Shipment(**{**air_shipment.to_dict(), "preferential_origin": True}))
    assert est.duty_rate == 0 and est.line("duty").amount == 0


def test_sea_minimum_charge(air_shipment):
    s = Shipment(**{**air_shipment.to_dict(), "transport_mode": "sea", "volume_cbm": 0.5, "weight_kg": 100})
    assert estimate_landed_cost(s).line("freight").amount == 250.00


def test_unknown_destination_warns(air_shipment):
    est = estimate_landed_cost(Shipment(**{**air_shipment.to_dict(), "destination_country": "ZZ"}))
    assert est.import_tax_rate == 0.15 and est.warnings


def test_invalid_shipment_raises(air_shipment):
    with pytest.raises(ShipmentValidationError):
        estimate_landed_cost(Shipment(**{**air_shipment.to_dict(), "goods_value": 0}))
