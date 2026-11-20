"""Shipment data model and validation."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any

TRANSPORT_MODES = ("sea", "air", "road")
INCOTERMS = ("EXW", "FCA", "FOB", "CFR", "CIF", "CPT", "CIP", "DAP", "DDP")
HS_CODE_PATTERN = re.compile(r"^\d{4}(\.?\d{2}){0,3}$")
COUNTRY_PATTERN = re.compile(r"^[A-Z]{2}$")


class ShipmentValidationError(ValueError):
    """Raised when a shipment has invalid or missing fields."""

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors))


@dataclass(frozen=True)
class Shipment:
    """A single import shipment. Money is in ``currency``; weight in kg; volume in m3."""

    reference: str
    description: str
    hs_code: str
    origin_country: str
    destination_country: str
    incoterm: str
    transport_mode: str
    goods_value: float
    weight_kg: float
    volume_cbm: float
    currency: str = "USD"
    preferential_origin: bool = False
    notes: str = field(default="", compare=False)

    @property
    def hs_chapter(self) -> str:
        """First two digits of the HS code."""
        return self.hs_code.replace(".", "")[:2]

    def validate(self) -> list[str]:
        """Return a list of human-readable problems; empty when the shipment is valid."""
        errors: list[str] = []
        if not self.reference.strip():
            errors.append("Reference is required.")
        if not self.description.strip():
            errors.append("Description is required.")
        if not HS_CODE_PATTERN.match(self.hs_code.strip()):
            errors.append("HS code must be 4-10 digits, e.g. 8471.30 or 847130.")
        for label, code in (("Origin", self.origin_country), ("Destination", self.destination_country)):
            if not COUNTRY_PATTERN.match(code):
                errors.append(f"{label} country must be a 2-letter ISO code, e.g. CN.")
        if self.origin_country and self.origin_country == self.destination_country:
            errors.append("Origin and destination must be different countries.")
        if self.incoterm not in INCOTERMS:
            errors.append(f"Incoterm must be one of {', '.join(INCOTERMS)}.")
        if self.transport_mode not in TRANSPORT_MODES:
            errors.append(f"Transport mode must be one of {', '.join(TRANSPORT_MODES)}.")
        if self.goods_value <= 0:
            errors.append("Goods value must be greater than 0.")
        if self.weight_kg <= 0:
            errors.append("Weight must be greater than 0 kg.")
        if self.volume_cbm <= 0:
            errors.append("Volume must be greater than 0 m3.")
        if self.currency != "USD":
            errors.append("Only USD is supported in this version.")
        return errors

    def ensure_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise ShipmentValidationError(errors)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Shipment":
        """Build a shipment from loosely-typed input (JSON, form values)."""
        try:
            return cls(
                reference=str(data.get("reference", "")).strip(),
                description=str(data.get("description", "")).strip(),
                hs_code=str(data.get("hs_code", "")).strip(),
                origin_country=str(data.get("origin_country", "")).strip().upper(),
                destination_country=str(data.get("destination_country", "")).strip().upper(),
                incoterm=str(data.get("incoterm", "")).strip().upper(),
                transport_mode=str(data.get("transport_mode", "")).strip().lower(),
                goods_value=float(data.get("goods_value", 0)),
                weight_kg=float(data.get("weight_kg", 0)),
                volume_cbm=float(data.get("volume_cbm", 0)),
                currency=str(data.get("currency", "USD")).strip().upper(),
                preferential_origin=bool(data.get("preferential_origin", False)),
                notes=str(data.get("notes", "")),
            )
        except (TypeError, ValueError) as exc:
            raise ShipmentValidationError([f"Invalid numeric value: {exc}"]) from exc

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
