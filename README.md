DesignRush SEO Audit
====================

Quick start
- Ensure dependencies installed: `uv sync`
- Run checks: `uv run python scripts/checks.py`
- Generate analysis artifacts: `uv run python scripts/analyze_positions.py --csv data/www.designrush.com_agency-organic.Positions-us-20250911-2025-09-12T16_10_02Z.csv`
 - (Optional) Capture screenshots for the deck: see "Screenshots" below

Outputs
- Artifacts are written under `artifacts/<date>/`:
  - `overview_buckets.csv` – position distribution
  - `top_keywords_by_traffic.csv` – top keywords
  - `top_pages_by_traffic.csv` – traffic by URL
  - `quick_wins.csv` – high-priority terms in positions 4–10
  - `movers_improvers.csv` / `movers_decliners.csv` – biggest changes
  - `intent_mix.csv` – intent distribution
  - `serp_features.csv` – SERP feature coverage
  - `categories.csv` – agency/trends/geo content mix
  - `services_summary.csv` – fine-grained service taxonomy metrics
  - `services/` – per-service `wins_*.csv`, `losses_*.csv`, `quick_wins_*.csv`
  - `charts/` – chart PNGs (basic renderer built-in); install Matplotlib for higher‑quality PNGs. Always includes `*.csv` chart data
  - `summary.md` – presentation-ready highlights
  - `deck.md` – slide-ready outline with embedded charts
  - `deck.html` – HTML presentation (dark/light theme, Inter). Shows one slide at a time with Prev/Next, arrow‑key navigation, a progress bar, and an optional theme toggle. Embeds PNG charts when available, otherwise loads Vega‑Lite charts. If `artifacts/<date>/screenshots/` contains images, a Screenshots section is auto‑added and groups desktop/mobile pairs on one slide.

Notes
- Source CSVs live in `data/` and are kept intact.
- Use `uv lock && uv sync` after adding dependencies.
- Optional: install Matplotlib for higher‑quality PNG charts: `uv add matplotlib` then re-run. Without it, a built‑in renderer still produces basic PNGs.
  - For the HTML deck: images are embedded; if some images are missing, the deck falls back to Vega/Vega‑Lite (CDN). Vega‑Lite JSON specs are saved under `charts/vega/`.

Screenshots
- Configure Spider Cloud API key in `.env` at repo root: `SPIDER_API_KEY=...`
- Define targets in `scripts/screenshots.yml` (edit to taste). Each item supports: `name`, `url`, `devices` (`desktop`/`mobile`), optional `delay_ms`, `full_page`.
- Capture screenshots (saved to `artifacts/<date>/screenshots/`):
  - `uv run python scripts/capture_screenshots.py --targets scripts/screenshots.yml`
  - Or choose an explicit directory: `uv run python scripts/capture_screenshots.py --out-dir artifacts/2025-09-13/screenshots`
- Regenerate the deck to include the screenshots:
  - Re-run analysis (same CSV as before): `uv run python scripts/analyze_positions.py --csv data/<your-semrush-export>.csv`
  - Open `artifacts/<date>/deck.html` and navigate to the Screenshots slides.

Tips
- Print/PDF export: append `?print=1` to the deck URL to show all slides stacked and hide controls (e.g., open `file:///.../deck.html?print=1` then print to PDF).
- Theme: toggle light/dark with the Theme button; preference persists per browser.
