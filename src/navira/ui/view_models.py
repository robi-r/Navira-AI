"""Pure helpers that shape domain objects for display. No Streamlit imports, so they are easy to test."""

from __future__ import annotations

from collections.abc import Mapping

from navira.checklist import ChecklistItem
from navira.landed_cost import LandedCostEstimate

ESTIMATE = "Estimate"
INVOICE = "Invoice"


def format_money(amount: float, currency: str = "USD") -> str:
    return f"{currency} {amount:,.2f}"


def breakdown_rows(estimate: LandedCostEstimate) -> list[dict[str, str]]:
    """Rows for the breakdown table; every estimated figure is labelled as such."""
    rows = [
        {
            "Item": f"{line.label} (estimate)" if line.is_estimate else line.label,
            f"Amount ({estimate.currency})": f"{line.amount:,.2f}",
            "Type": ESTIMATE if line.is_estimate else INVOICE,
            "Basis": line.basis,
        }
        for line in estimate.lines
    ]
    rows.append({
        "Item": "Total landed cost (estimate)",
        f"Amount ({estimate.currency})": f"{estimate.total:,.2f}",
        "Type": ESTIMATE,
        "Basis": "Sum of all lines",
    })
    return rows


def missing_required(items: list[ChecklistItem], done: Mapping[str, bool]) -> list[ChecklistItem]:
    return [item for item in items if item.required and not done.get(item.id, False)]


def quote_filename(reference: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in reference) or "shipment"
    return f"navira-quote-{safe}.md"
