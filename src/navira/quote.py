"""Plain-text (Markdown) quote document."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from navira.checklist import ChecklistItem
from navira.landed_cost import LandedCostEstimate
from navira.models import Shipment

ESTIMATE_TAG = "(estimate)"


def build_quote_markdown(
    shipment: Shipment,
    estimate: LandedCostEstimate,
    checklist: list[ChecklistItem],
    completed: Mapping[str, bool] | None = None,
    issued_on: date | None = None,
) -> str:
    completed = completed or {}
    issued_on = issued_on or date.today()
    cur = estimate.currency
    out = [
        f"# Landed-cost quote: {shipment.reference}",
        "",
        f"Issued: {issued_on.isoformat()}  ",
        "Status: **ESTIMATE, not a binding offer**",
        "",
        "## Shipment",
        "",
        f"- Description: {shipment.description}",
        f"- HS code: {shipment.hs_code}",
        f"- Route: {shipment.origin_country} -> {shipment.destination_country} ({shipment.transport_mode})",
        f"- Incoterm: {shipment.incoterm}",
        f"- Weight / volume: {shipment.weight_kg:,.1f} kg / {shipment.volume_cbm:,.2f} m3",
        "",
        "## Cost breakdown",
        "",
        f"| Item | Amount ({cur}) | Basis |",
        "|---|---:|---|",
    ]
    for line in estimate.lines:
        label = f"{line.label} {ESTIMATE_TAG}" if line.is_estimate else line.label
        out.append(f"| {label} | {line.amount:,.2f} | {line.basis} |")
    out += [
        f"| **Total landed cost {ESTIMATE_TAG}** | **{estimate.total:,.2f}** | |",
        "",
        "## Assumptions",
        "",
        *[f"- {a}" for a in estimate.assumptions],
    ]
    if estimate.warnings:
        out += ["", "## Warnings", "", *[f"- {w}" for w in estimate.warnings]]
    out += ["", "## Document checklist", ""]
    for item in checklist:
        mark = "x" if completed.get(item.id) else " "
        req = "required" if item.required else "optional"
        out.append(f"- [{mark}] {item.label} ({req})")
    missing = sum(1 for i in checklist if i.required and not completed.get(i.id))
    out += [
        "",
        f"Missing required items: {missing}",
        "",
        "---",
        "Freight, duty, tax and fee figures are estimates from illustrative rates. "
        "Confirm with your carrier and customs broker before booking.",
        "",
    ]
    return "\n".join(out)
