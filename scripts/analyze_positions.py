"""Run the organic positions analysis and write artifacts.

Usage:
    uv run python scripts/analyze_positions.py \
        --csv data/www.designrush.com_agency-organic.Positions-us-20250911-2025-09-12T16_10_02Z.csv
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

from designrush_seo_audit.analysis import run_full_analysis


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze SEMrush Organic Positions export")
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("data").glob("www.designrush.com_*organic.Positions-*.csv"),
        help="Path to the SEMrush CSV (defaults to first matching in data/)",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (defaults to artifacts/<date>/)",
    )
    parser.add_argument(
        "--screenshots",
        action="store_true",
        help="Also capture screenshots (Spider) and rebuild the deck including them",
    )
    args = parser.parse_args()

    csv_path: Path
    if isinstance(args.csv, Path):
        csv_path = args.csv
    else:
        # If default glob iterator, pick the first match
        matches = list(args.csv)
        if not matches:
            raise SystemExit("No matching CSV found in data/")
        csv_path = matches[0]

    arts = run_full_analysis(csv_path, args.out_dir)
    print(f"Artifacts written to: {arts.base_dir}")
    print(f"- Summary: {arts.summary_md}")
    print(f"- Top keywords: {arts.top_keywords_csv}")
    print(f"- Quick wins: {arts.quick_wins_csv}")
    if arts.deck_md:
        print(f"- Deck: {arts.deck_md}")
    if arts.deck_html:
        print(f"- HTML deck: {arts.deck_html}")
    charts_dir = arts.base_dir / "charts"
    if charts_dir.exists():
        # Note: PNGs only if matplotlib available; CSVs always exist
        print(f"- Charts (PNGs or CSV data): {charts_dir}")

    # Optional: capture screenshots and rebuild deck to include them
    if args.screenshots:
        shots_dir = arts.base_dir / "screenshots"
        shots_dir.mkdir(parents=True, exist_ok=True)
        cmd = [
            sys.executable,
            str(Path("scripts") / "capture_screenshots.py"),
            "--targets",
            str(Path("scripts") / "screenshots.yml"),
            "--out-dir",
            str(shots_dir),
        ]
        print("Capturing screenshots via Spider…")
        try:
            subprocess.run(cmd, check=False)
        except Exception as e:
            print(f"Warning: screenshot capture failed: {e}")
        # Rebuild deck to pick up screenshots
        print("Rebuilding deck to include screenshots…")
        run_full_analysis(csv_path, arts.base_dir)
        print(f"Screenshots embedded. Open: {arts.base_dir / 'deck.html'}")


if __name__ == "__main__":
    main()
