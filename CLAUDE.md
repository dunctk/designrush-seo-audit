# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
- **First-time setup**: `uv sync` (installs dependencies and creates .venv)
- **Add dependencies**: `uv add <package>` (runtime) or `uv add --group dev <package>` (dev tools)
- **Update dependencies**: `uv lock && uv sync`

### Core Analysis Workflow
- **Run basic checks**: `uv run python scripts/checks.py`
- **Full SEO analysis**: `uv run python scripts/analyze_positions.py --csv data/www.designrush.com_agency-organic.Positions-us-*.csv`
- **Screenshot capture**: `uv run python scripts/capture_screenshots.py --targets scripts/screenshots.yml`

### Code Quality
- **Lint**: `uv run ruff .` or `uvx ruff .`
- **Format**: `uv run black .` or `uvx black .`
- Use `uv run` for all Python execution; avoid direct pip/virtualenv commands

## Project Architecture

This is an SEO audit analysis tool that processes SEMrush organic position exports and generates comprehensive reports and presentations.

### Core Data Flow
1. **Input**: SEMrush CSV exports in `data/` (e.g., `www.designrush.com_agency-organic.Positions-*.csv`)
2. **Processing**: Main analysis in `src/designrush_seo_audit/analysis.py` using Polars for data manipulation
3. **Output**: Timestamped artifacts in `artifacts/<date>/` including CSVs, charts, markdown summaries, and HTML presentations

### Key Modules
- **`analysis.py`**: Core data processing and SEO metrics calculation (position distribution, quick wins, movers, service taxonomy)
- **`charts.py`**: Chart generation (built-in renderer + optional Matplotlib for higher quality)
- **`deck.py`**: Markdown presentation generation  
- **`html_deck.py`**: Interactive HTML presentation with dark/light themes, navigation, and embedded charts

### Data Structure
The analysis expects SEMrush exports with specific columns (defined in `analysis.py`):
- Required: Keyword, Position, Previous position, Search Volume, URL, Traffic, SERP Features, Keyword Intents, etc.
- Processes 20+ service categories (SEO, web design, digital marketing, etc.)
- Generates per-service breakdowns (wins, losses, quick wins, SERP features)

### Output Artifacts
- **CSV files**: Overview buckets, top keywords/pages, quick wins, movers, service summaries
- **Charts**: PNG images (+ Vega-Lite JSON specs) for key metrics
- **Presentations**: `deck.md` (slide outline) and `deck.html` (interactive presentation)
- **Screenshots**: Optional Spider Cloud integration for visual captures

### Service Taxonomy
The codebase has built-in logic to categorize keywords/URLs into 20+ service types based on URL patterns and keyword analysis. This enables service-specific reporting and strategic recommendations.

## Important Notes
- Uses Python 3.13+ and Polars for fast data processing
- Screenshots require Spider API key in `.env`
- HTML presentations support print mode (`?print=1`) for PDF export
- All artifacts are timestamped to preserve historical analysis