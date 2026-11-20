"""Import document and compliance checklist."""

from __future__ import annotations

from dataclasses import dataclass

from navira import rates
from navira.models import Shipment

EU_COUNTRIES = frozenset({"DE", "FR", "NL", "IT", "ES", "BE", "IE", "PL", "SE", "AT"})


@dataclass(frozen=True)
class ChecklistItem:
    id: str
    label: str
    required: bool
    category: str
    note: str = ""


def build_checklist(shipment: Shipment) -> list[ChecklistItem]:
    """Return the documents and steps needed to import ``shipment``, required items first."""
    shipment.ensure_valid()
    items: list[ChecklistItem] = [
        ChecklistItem("commercial_invoice", "Commercial invoice", True, "Documents",
                      "Must show seller, buyer, Incoterm, currency and value per line."),
        ChecklistItem("packing_list", "Packing list", True, "Documents",
                      "Package count, gross/net weight and dimensions."),
    ]

    transport_doc = {
        "sea": ("bill_of_lading", "Bill of lading (B/L)"),
        "air": ("air_waybill", "Air waybill (AWB)"),
        "road": ("cmr", "Road consignment note (CMR)"),
    }[shipment.transport_mode]
    items.append(ChecklistItem(transport_doc[0], transport_doc[1], True, "Documents", "Issued by the carrier."))

    items.append(ChecklistItem("hs_classification", f"Confirm HS classification ({shipment.hs_code})", True,
                               "Compliance", "Duty depends on the correct code; confirm with your broker."))

    if shipment.preferential_origin:
        items.append(ChecklistItem("certificate_of_origin", "Certificate / statement of origin", True, "Compliance",
                                   "Needed to claim the preferential (reduced) duty rate."))
    else:
        items.append(ChecklistItem("certificate_of_origin", "Certificate of origin", False, "Compliance",
                                   "Sometimes requested by customs or banks."))

    if shipment.hs_chapter in rates.LICENSED_CHAPTERS:
        items.append(ChecklistItem("import_licence", "Import licence / permit", True, "Compliance",
                                   f"HS chapter {shipment.hs_chapter} is commonly controlled."))

    dest = shipment.destination_country
    if dest == "US":
        items.append(ChecklistItem("isf", "Importer Security Filing (ISF 10+2)", shipment.transport_mode == "sea",
                                   "Registration", "Required 24h before loading for ocean shipments."))
        items.append(ChecklistItem("customs_bond", "Customs bond", True, "Registration", "Continuous or single-entry bond."))
    elif dest in EU_COUNTRIES:
        items.append(ChecklistItem("eori", "EORI number", True, "Registration", "Needed for any EU customs declaration."))
    elif dest == "GB":
        items.append(ChecklistItem("eori", "GB EORI number", True, "Registration", "Needed for UK customs declarations."))
    else:
        items.append(ChecklistItem("importer_registration", "Importer registration / tax ID", True, "Registration",
                                   "Check the destination's importer registration rules."))

    items.append(ChecklistItem("insurance_certificate", "Cargo insurance certificate",
                               shipment.incoterm in {"CIF", "CIP"}, "Documents",
                               "Seller provides under CIF/CIP; otherwise recommended."))
    items.append(ChecklistItem("broker_poa", "Power of attorney for customs broker", False, "Registration",
                               "Lets your broker file the entry on your behalf."))

    return sorted(items, key=lambda item: not item.required)
