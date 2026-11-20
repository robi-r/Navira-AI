"""Loading sample shipment data."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from navira.models import Shipment

logger = logging.getLogger(__name__)

DEFAULT_SAMPLE_PATH = Path(__file__).resolve().parents[2] / "data" / "sample_shipments.json"


def load_sample_shipments(path: Path | str = DEFAULT_SAMPLE_PATH) -> list[Shipment]:
    """Load sample shipments from a JSON file shaped as ``{"shipments": [...]}``."""
    path = Path(path)
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    records = payload["shipments"] if isinstance(payload, dict) else payload
    shipments = [Shipment.from_dict(record) for record in records]
    logger.debug("Loaded %d sample shipments from %s", len(shipments), path)
    return shipments
