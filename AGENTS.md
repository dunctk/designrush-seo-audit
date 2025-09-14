# Repository Guidelines

## Project Structure & Module Organization
- `hello.py` — simple entry script. Use this as a starting point for a CLI or quick experiments.
- `data/` — CSV exports and inputs for analysis (e.g., `data/www.designrush.com_*.csv`). Keep raw inputs; avoid committing large intermediates.
- `prd.md` — problem/requirements notes for the SEO audit work.
- `pyproject.toml` — project metadata (Python >= 3.13). Add dependencies here under `[project]`.
- `README.md` — overview and usage notes.
- When the code grows, place library code under `src/designrush_seo_audit/` and keep the CLI in `src/designrush_seo_audit/__main__.py`.

## Build, Test, and Development Commands (uv)
- First-time setup: `uv sync` (creates `.venv` and installs deps; no manual activation needed).
- Run locally: `uv run python hello.py`
- Add runtime deps: `uv add <package>` (writes to `pyproject.toml` and locks).
- Data analysis: prefer Polars. Install via `uv add polars` (if not already available) and run scripts with `uv run`.
- Dev tools (optional): `uv add --group dev ruff black`
- Lint/format: `uv run ruff .` and `uv run black .` (or `uvx ruff .`/`uvx black .`).
- One‑off scripts: `uv run python -c "print('rows:', sum(1 for _ in open('data/input.csv')))"`
- Lock/update: `uv lock` then `uv sync` to apply.

## Coding Style & Naming Conventions
- Follow PEP 8; 4‑space indentation; max ~88–100 columns.
- Names: snake_case for modules/functions/variables; PascalCase for classes; UPPER_CASE for constants.
- Prefer small, pure functions; add type hints for public interfaces.
- Include docstrings for modules, public functions, and classes.

## Validation & Accuracy (Fast)
- No complex test suite required. Prioritize accurate data and reproducible steps.
- Perform quick checks (with Polars): row counts, required columns present, duplicates by URL/domain, spot-check top N results.
- Save lightweight artifacts for the deck under `artifacts/` (e.g., `artifacts/2025-09-12/top_keywords.csv`).
- Optional: add a single `scripts/checks.py` with basic assertions and run via `uv run python scripts/checks.py`.

## Commit & Pull Request Guidelines
- Use Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`, etc. Example: `feat: add URL canonicalization utility`.
- Keep commits small and cohesive; write an imperative subject line (~50 chars) and a brief body when needed.
- PRs: include a clear description, scope of change, any linked issues, and sample inputs/outputs or screenshots for behavioral changes.

## Security & Data Tips
- Never commit secrets or API keys; use environment variables and keep `.env` files out of version control.
- CSV policy: do not sanitize or redact. Commit public CSVs exactly as obtained to preserve every field and value. Ignore only ephemeral caches and derived intermediates (consider Git LFS for very large files).

## UV Usage Policy
- Use uv for all workflow tasks; do not call `pip` or activate virtualenvs directly.
- Recommended: pin Python in `pyproject.toml` and, if needed, `[tool.uv]` configuration; manage all packages via `uv add`/`uv remove` and execute tools with `uv run`/`uvx`.
