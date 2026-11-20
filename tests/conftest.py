import pytest

from navira.models import Shipment


@pytest.fixture
def air_shipment() -> Shipment:
    return Shipment(
        reference="T-1", description="Laptops", hs_code="8471.30", origin_country="CN",
        destination_country="US", incoterm="FOB", transport_mode="air",
        goods_value=48000, weight_kg=320, volume_cbm=1.8,
    )
