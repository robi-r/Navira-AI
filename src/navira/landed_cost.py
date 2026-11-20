"""Landed-cost estimation.

Landed cost = goods value + freight + insurance + duty + import tax + fees, from
the importer's point of view. Which costs the importer pays depends on the
Incoterm. All figures except the invoiced goods value are estimates built from
the illustrative tables in :mod:`navira.rates`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from navira import rates
from navira.models import Shipment

logger = logging.getLogger(__name__)

# Incoterms under which the importer (buyer) pays main freight / insurance / duty+tax.
BUYER_PAYS_FREIGHT = frozenset({"EXW", "FCA", "FOB"})
BUYER_PAYS_INSURANCE = frozenset({"EXW", "FCA", "FOB", "CFR", "CPT"})
SELLER_PAYS_DUTY_AND_TAX = frozenset({"DDP"})


def _money(value: float) -> float:
    return round(value + 0.0, 2)


@dataclass(frozen=True)
class CostLine:
    """One row of the landed-cost breakdown."""

    key: str
    label: str
    amount: float
    is_estimate: bool
    basis: str


@dataclass(frozen=True)
class LandedCostEstimate:
    shipment_reference: str
    currency: str
    lines: list[CostLine]
    assumptions: list[str]
    chargeable_weight_kg: float
    customs_value: float
    duty_rate: float
    import_tax_rate: float
    warnings: list[str] = field(default_factory=list)

    @property
    def total(self) -> float:
        return _money(sum(line.amount for line in self.lines))

    @property
    def estimated_portion(self) -> float:
        return _money(sum(line.amount for line in self.lines if line.is_estimate))

    def line(self, key: str) -> CostLine:
        for item in self.lines:
            if item.key == key:
                return item
        raise KeyError(key)


def chargeable_weight(shipment: Shipment) -> float:
    """Greater of actual and volumetric weight (air and road)."""
    if shipment.transport_mode == "air":
        return max(shipment.weight_kg, shipment.volume_cbm * rates.AIR_VOLUMETRIC_DIVISOR_KG_PER_CBM)
    if shipment.transport_mode == "road":
        return max(shipment.weight_kg, shipment.volume_cbm * rates.ROAD_VOLUMETRIC_DIVISOR_KG_PER_CBM)
    return shipment.weight_kg


def _freight_cost(shipment: Shipment) -> tuple[float, str]:
    table = rates.FREIGHT_RATES[shipment.transport_mode]
    if shipment.transport_mode == "sea":
        # Sea LCL is charged per m3, with 1 m3 ~ 1000 kg weight/measure rule.
        units = max(shipment.volume_cbm, shipment.weight_kg / 1000.0)
        basis = f"{units:,.2f} m3 (W/M) x {table['per_unit']:,.2f}/m3, min {table['minimum']:,.0f}"
    else:
        units = chargeable_weight(shipment)
        basis = f"{units:,.1f} chargeable kg x {table['per_unit']:,.2f}/kg, min {table['minimum']:,.0f}"
    return max(units * table["per_unit"], table["minimum"]), basis


def duty_rate_for(shipment: Shipment) -> float:
    if shipment.preferential_origin:
        return rates.PREFERENTIAL_DUTY_FACTOR
    return rates.DUTY_RATES_BY_CHAPTER.get(shipment.hs_chapter, rates.DEFAULT_DUTY_RATE)


def estimate_landed_cost(shipment: Shipment) -> LandedCostEstimate:
    """Estimate the importer's landed cost for ``shipment``.

    Raises :class:`navira.models.ShipmentValidationError` if the shipment is invalid.
    """
    shipment.ensure_valid()
    incoterm = shipment.incoterm
    mode = shipment.transport_mode
    dest = shipment.destination_country

    freight_full, freight_basis = _freight_cost(shipment)
    buyer_freight = freight_full if incoterm in BUYER_PAYS_FREIGHT else 0.0
    if not buyer_freight:
        freight_basis = f"Paid by seller under {incoterm} (included in goods value)"

    insurance_full = (shipment.goods_value + freight_full) * rates.INSURANCE_RATE
    buyer_insurance = insurance_full if incoterm in BUYER_PAYS_INSURANCE else 0.0
    insurance_basis = (
        f"{rates.INSURANCE_RATE:.1%} of goods + freight"
        if buyer_insurance
        else f"Paid by seller under {incoterm}"
    )

    if dest in rates.FOB_VALUATION_COUNTRIES:
        customs_value = shipment.goods_value
        valuation = "FOB"
    else:
        customs_value = shipment.goods_value + buyer_freight + buyer_insurance
        valuation = "CIF"

    duty_rate = duty_rate_for(shipment)
    tax_rate = rates.IMPORT_TAX_RATES.get(dest, rates.DEFAULT_IMPORT_TAX_RATE)
    duty = customs_value * duty_rate
    import_tax = (customs_value + duty) * tax_rate
    if incoterm in SELLER_PAYS_DUTY_AND_TAX:
        duty_basis = tax_basis = "Paid by seller under DDP"
        duty = import_tax = 0.0
    else:
        duty_basis = f"{duty_rate:.1%} of {valuation} customs value {customs_value:,.2f}"
        tax_basis = f"{tax_rate:.1%} of customs value + duty"

    lines = [
        CostLine("goods", "Goods value (invoice)", _money(shipment.goods_value), False, f"Commercial invoice, {incoterm}"),
        CostLine("freight", "Freight", _money(buyer_freight), True, freight_basis),
        CostLine("insurance", "Cargo insurance", _money(buyer_insurance), True, insurance_basis),
        CostLine("duty", "Import duty", _money(duty), True, duty_basis),
        CostLine("import_tax", "Import VAT / GST", _money(import_tax), True, tax_basis),
        CostLine("brokerage", "Customs brokerage", _money(rates.CUSTOMS_BROKERAGE_FEE), True, "Flat illustrative fee"),
        CostLine("handling", "Port / terminal handling", _money(rates.PORT_HANDLING_FEE[mode]), True, f"Flat illustrative {mode} fee"),
    ]

    assumptions = [
        "All freight, insurance, duty, tax and fee figures are estimates from illustrative rate tables, not live quotes or tariff lookups.",
        f"Duty rate {duty_rate:.1%} is based on HS chapter {shipment.hs_chapter}"
        + (" with preferential origin assumed duty-free." if shipment.preferential_origin else " at an illustrative MFN rate."),
        f"Customs value uses {valuation} valuation for destination {dest}.",
        f"Import VAT/GST rate for {dest} assumed at {tax_rate:.1%}.",
        f"Incoterm {incoterm}: the importer's costs shown reflect who pays freight, insurance and duties under this term.",
        f"{mode.capitalize()} freight uses chargeable weight {chargeable_weight(shipment):,.1f} kg"
        + (" (W/M rule for sea)." if mode == "sea" else " (greater of actual and volumetric)."),
        "Amounts are in USD; no currency conversion, surcharges (fuel, peak season) or demurrage are included.",
    ]
    warnings: list[str] = []
    if dest not in rates.IMPORT_TAX_RATES:
        warnings.append(f"No tax rate on file for {dest}; a default of {rates.DEFAULT_IMPORT_TAX_RATE:.0%} was used.")
    if shipment.hs_chapter in rates.LICENSED_CHAPTERS:
        warnings.append(f"HS chapter {shipment.hs_chapter} often needs an import licence or permit.")

    estimate = LandedCostEstimate(
        shipment_reference=shipment.reference,
        currency=shipment.currency,
        lines=lines,
        assumptions=assumptions,
        chargeable_weight_kg=round(chargeable_weight(shipment), 2),
        customs_value=_money(customs_value),
        duty_rate=duty_rate,
        import_tax_rate=tax_rate,
        warnings=warnings,
    )
    logger.info("Estimated landed cost for %s: %.2f %s", shipment.reference, estimate.total, shipment.currency)
    return estimate
