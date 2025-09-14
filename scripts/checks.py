"""Lightweight checks for the SEO audit dataset.

Run with:
    uv run python scripts/checks.py
"""
from __future__ import annotations

from pathlib import Path

import polars as pl

from designrush_seo_audit.analysis import (
    REQUIRED_COLUMNS,
    load_positions,
)


def main() -> None:
    # Find the CSV
    matches = list(Path("data").glob("www.designrush.com_*organic.Positions-*.csv"))
    assert matches, "No SEMrush organic positions CSV found in data/"
    csv_path = matches[0]
    df = load_positions(csv_path)

    # Basic sanity checks
    assert df.height > 0, "CSV is empty"
    for c in REQUIRED_COLUMNS:
        assert c in df.columns, f"Missing column: {c}"

    # Check duplicates by keyword+url
    dupes = (
        df.group_by(["Keyword", "URL"]).len().filter(pl.col("len") > 1)
    )
    assert dupes.height == 0, f"Duplicate keyword+url rows detected: {dupes.height}"

    # Spot check top rows have numeric positions
    assert df.select(pl.all().exclude("Position")).height >= 0  # structural
    assert df["Position"].cast(pl.Int64, strict=False).null_count() == 0

    print("Checks passed:")
    print(f"- Rows: {df.height}")
    print(f"- Columns: {len(df.columns)}")


if __name__ == "__main__":
    main()

