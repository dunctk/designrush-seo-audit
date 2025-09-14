#!/usr/bin/env python
"""
Quick analysis for Semrush keyword CSVs using Polars.

Inputs
- A Semrush export CSV for the /agency section.

Outputs (written to artifacts/YYYY-MM-DD/)
- ranking_distribution.csv
- top_keywords.csv
- underperforming_opportunities.csv
- intent_breakdown.csv
- serp_features_counts.csv (optional, if present)

Run
  uv run python scripts/analyze_agency.py \
    --input data/www.designrush.com_agency-organic.Positions-us-20250911-2025-09-12T16_10_02Z.csv
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from typing import List

import polars as pl


NUMERIC_COLS: List[str] = [
    "Position",
    "Previous position",
    "Search Volume",
    "Keyword Difficulty",
    "CPC",
    "Traffic",
    "Traffic (%)",
    "Traffic Cost",
    "Competition",
    "Number of Results",
]


def load_csv(path: str) -> pl.DataFrame:
    df = pl.read_csv(path)
    # Cast common numeric columns; tolerate bad values as nulls
    cast_exprs = []
    for c in NUMERIC_COLS:
        if c in df.columns:
            cast_exprs.append(pl.col(c).cast(pl.Float64, strict=False))
    if cast_exprs:
        df = df.with_columns(cast_exprs)
    return df


def add_position_bucket(df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.when(pl.col("Position") <= 3)
        .then(pl.lit("1-3"))
        .when((pl.col("Position") >= 4) & (pl.col("Position") <= 10))
        .then(pl.lit("4-10"))
        .when((pl.col("Position") >= 11) & (pl.col("Position") <= 50))
        .then(pl.lit("11-50"))
        .otherwise(pl.lit("50+"))
        .alias("pos_bucket")
    )


def write_ranking_distribution(df: pl.DataFrame, out_dir: str) -> None:
    dist = (
        df.drop_nulls(subset=["Position"]).pipe(add_position_bucket)
        .groupby("pos_bucket")
        .agg(pl.len().alias("count"))
        .with_columns((pl.col("count") / pl.sum("count")).alias("share"))
        .sort("pos_bucket")
    )
    dist.write_csv(os.path.join(out_dir, "ranking_distribution.csv"))


def write_top_keywords(df: pl.DataFrame, out_dir: str, n: int = 200) -> None:
    cols = [c for c in ["Keyword", "Position", "Search Volume", "Traffic", "URL"] if c in df.columns]
    top = (
        df.drop_nulls(subset=["Keyword"]).sort(
            by=[pl.col("Traffic").fill_null(0), pl.col("Search Volume").fill_null(0)],
            descending=True,
        )
    )
    top.select(cols).head(n).write_csv(os.path.join(out_dir, "top_keywords.csv"))


def write_underperformers(df: pl.DataFrame, out_dir: str, n: int = 300) -> None:
    required = ["Position", "Search Volume"]
    filt = (
        df.drop_nulls(subset=required)
        .filter((pl.col("Position") >= 11) & (pl.col("Position") <= 50) & (pl.col("Search Volume") >= 500))
        .sort(by=[pl.col("Search Volume"), pl.col("Keyword Difficulty").fill_null(9999)], descending=[True, False])
    )
    cols = [
        c
        for c in [
            "Keyword",
            "Position",
            "Search Volume",
            "Keyword Difficulty",
            "URL",
        ]
        if c in df.columns
    ]
    filt.select(cols).head(n).write_csv(os.path.join(out_dir, "underperforming_opportunities.csv"))


def write_intent_breakdown(df: pl.DataFrame, out_dir: str) -> None:
    col = "Keyword Intents"
    if col not in df.columns:
        return
    intents = (
        df.with_columns(pl.col(col).fill_null("Unknown").alias(col))
        .groupby(col)
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
    )
    intents.write_csv(os.path.join(out_dir, "intent_breakdown.csv"))


def write_serp_features_counts(df: pl.DataFrame, out_dir: str) -> None:
    col = "SERP Features by Keyword"
    if col not in df.columns:
        return
    # Split comma-separated features, explode and count
    feats = (
        df.select(
            pl.col(col)
            .cast(pl.Utf8)
            .fill_null("")
            .str.split(", ")
            .alias("features")
        )
        .explode("features")
        .filter(pl.col("features") != "")
        .groupby("features")
        .agg(pl.len().alias("count"))
        .sort("count", descending=True)
    )
    feats.write_csv(os.path.join(out_dir, "serp_features_counts.csv"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Analyze Semrush /agency keywords (Polars)")
    ap.add_argument(
        "--input",
        default="data/www.designrush.com_agency-organic.Positions-us-20250911-2025-09-12T16_10_02Z.csv",
        help="Path to Semrush CSV export",
    )
    ap.add_argument("--out", default=None, help="Output directory (default artifacts/YYYY-MM-DD)")
    args = ap.parse_args(argv)

    out_dir = args.out or os.path.join("artifacts", dt.date.today().isoformat())
    os.makedirs(out_dir, exist_ok=True)

    df = load_csv(args.input)

    write_ranking_distribution(df, out_dir)
    write_top_keywords(df, out_dir)
    write_underperformers(df, out_dir)
    write_intent_breakdown(df, out_dir)
    write_serp_features_counts(df, out_dir)

    print(f"Wrote outputs to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

