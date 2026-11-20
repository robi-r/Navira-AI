# Navira AI

Estimate the landed cost of an import shipment, build the customs document checklist,
and produce a downloadable quote.

> **All freight, insurance, duty, tax and fee figures are estimates** from illustrative
> rate tables in `src/navira/rates.py`. They are not carrier quotes or tariff rulings.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
streamlit run app.py
```

Open http://localhost:8501. Run the tests with `pytest`.

## Streamlit app

| Page | What it does |
|---|---|
| Home | Product summary, features, "Start a shipment" button, **Sample data** banner |
| New shipment | Form pre-filled from `data/sample_shipments.json`, sample picker, input checks |
| Landed cost | Calls `estimate_landed_cost`; breakdown table (each estimated figure labelled), warnings, assumptions |
| Checklist | `build_checklist` with checkboxes that persist across pages and a missing-required count |
| Quote | Markdown quote preview with a download button |

Screenshots are in `docs/screenshots/`.

## Marketing landing page

A static, dependency-free landing page lives in `site/` (`index.html`, `styles.css`, `main.js`).
Open `site/index.html` in a browser, or serve it with any static host (GitHub Pages, Netlify).
Live app: https://navira-ai.streamlit.app · Landing page: https://robi-r.github.io/navira-ai/
(redeployed to the `gh-pages` branch automatically by `.github/workflows/pages.yml` when `site/` changes on `main`).

## Project layout

```
app.py                      Streamlit entry point (sidebar navigation, logging, error boundary)
src/navira/
  models.py                 Shipment dataclass + validation
  rates.py                  Illustrative rate tables (replace with real data sources)
  landed_cost.py            estimate_landed_cost()
  checklist.py              build_checklist()
  quote.py                  build_quote_markdown()
  data.py                   load_sample_shipments()
  ui/
    state.py                Session state + navigation
    components.py           Banner, estimate note, CSS
    view_models.py          Pure display helpers (unit-tested)
    pages/                  One module per page: landing, new_shipment, landed_cost, checklist, quote
data/sample_shipments.json  Sample shipments
tests/                      Logic tests + end-to-end app tests (streamlit.testing)
.streamlit/config.toml      Theme: white background, dark green accent
```

## Configuration

- `NAVIRA_LOG_LEVEL` sets the log level for the `navira` logger (default `INFO`).
- Only USD is supported. Countries use ISO-2 codes.

## Limitations

Rates, duty by HS chapter, VAT/GST and fees are hard-coded examples. Before production use,
connect real tariff data, carrier rates and FX, and have a licensed customs broker review the checklist rules.
