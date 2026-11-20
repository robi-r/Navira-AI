"""Illustrative rate tables used for estimates.

These are NOT live tariff or carrier rates. They are round, illustrative numbers
so the estimator produces plausible ballpark figures. Replace with real data
sources before relying on any output.
"""

from __future__ import annotations

# Freight: USD per chargeable kg (air/road) or per m3 (sea), plus a minimum charge.
FREIGHT_RATES: dict[str, dict[str, float]] = {
    "air": {"per_unit": 4.50, "minimum": 150.0},
    "sea": {"per_unit": 85.0, "minimum": 250.0},
    "road": {"per_unit": 0.35, "minimum": 120.0},
}
AIR_VOLUMETRIC_DIVISOR_KG_PER_CBM = 167.0
ROAD_VOLUMETRIC_DIVISOR_KG_PER_CBM = 333.0

INSURANCE_RATE = 0.005  # 0.5% of goods + freight
CUSTOMS_BROKERAGE_FEE = 175.0
PORT_HANDLING_FEE = {"sea": 220.0, "air": 90.0, "road": 60.0}

# Illustrative MFN duty rate by HS chapter; anything else uses DEFAULT_DUTY_RATE.
DUTY_RATES_BY_CHAPTER: dict[str, float] = {
    "61": 0.12,  # knitted apparel
    "62": 0.12,  # woven apparel
    "64": 0.10,  # footwear
    "84": 0.02,  # machinery, computers
    "85": 0.025,  # electrical equipment
    "94": 0.04,  # furniture
    "95": 0.03,  # toys
    "09": 0.05,  # coffee, tea, spices
    "30": 0.0,  # pharmaceuticals
}
DEFAULT_DUTY_RATE = 0.05
PREFERENTIAL_DUTY_FACTOR = 0.0  # preferential origin assumed duty-free

# Illustrative import VAT / GST / sales tax by destination country.
IMPORT_TAX_RATES: dict[str, float] = {
    "US": 0.0,
    "GB": 0.20,
    "DE": 0.19,
    "FR": 0.20,
    "NL": 0.21,
    "AU": 0.10,
    "CA": 0.05,
    "BD": 0.15,
    "IN": 0.18,
    "JP": 0.10,
}
DEFAULT_IMPORT_TAX_RATE = 0.15

# Countries assumed to value goods FOB (freight excluded) for duty purposes.
FOB_VALUATION_COUNTRIES = frozenset({"US", "CA", "AU"})

# HS chapters that commonly require an import licence or permit.
LICENSED_CHAPTERS = frozenset({"30", "93", "28", "29", "01", "02", "03", "06"})
