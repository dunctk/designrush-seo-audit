from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

import polars as pl
import json


# Column names from the SEMrush export
COL_KEYWORD = "Keyword"
COL_POS = "Position"
COL_PREV_POS = "Previous position"
COL_VOLUME = "Search Volume"
COL_KD = "Keyword Difficulty"
COL_CPC = "CPC"
COL_URL = "URL"
COL_TRAFFIC = "Traffic"
COL_TRAFFIC_PCT = "Traffic (%)"
COL_TRAFFIC_COST = "Traffic Cost"
COL_COMPETITION = "Competition"
COL_RESULTS = "Number of Results"
COL_TRENDS = "Trends"
COL_TIMESTAMP = "Timestamp"
COL_SERP_FEATS = "SERP Features by Keyword"
COL_INTENTS = "Keyword Intents"
COL_POSITION_TYPE = "Position Type"


REQUIRED_COLUMNS: tuple[str, ...] = (
    COL_KEYWORD,
    COL_POS,
    COL_PREV_POS,
    COL_VOLUME,
    COL_KD,
    COL_CPC,
    COL_URL,
    COL_TRAFFIC,
    COL_TRAFFIC_PCT,
    COL_TRAFFIC_COST,
    COL_COMPETITION,
    COL_RESULTS,
    COL_TRENDS,
    COL_TIMESTAMP,
    COL_SERP_FEATS,
    COL_INTENTS,
    COL_POSITION_TYPE,
)


def load_positions(csv_path: str | Path) -> pl.DataFrame:
    """Load the SEMrush Organic Positions CSV using Polars.

    Ensures expected data types and trims whitespace.
    """
    df = pl.read_csv(
        csv_path,
        try_parse_dates=True,
        infer_schema_length=1000,
        ignore_errors=False,
    )

    # Verify required columns
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Normalize types and values
    df = df.with_columns(
        pl.col(COL_POS).cast(pl.Int64, strict=False),
        pl.col(COL_PREV_POS).cast(pl.Int64, strict=False),
        pl.col(COL_VOLUME).cast(pl.Int64, strict=False),
        pl.col(COL_KD).cast(pl.Float64, strict=False),
        pl.col(COL_CPC).cast(pl.Float64, strict=False),
        pl.col(COL_TRAFFIC).cast(pl.Float64, strict=False),
        pl.col(COL_TRAFFIC_PCT).cast(pl.Float64, strict=False),
        pl.col(COL_TRAFFIC_COST).cast(pl.Float64, strict=False),
        pl.col(COL_COMPETITION).cast(pl.Float64, strict=False),
        pl.col(COL_RESULTS).cast(pl.Float64, strict=False),
        # Parse Timestamp to date (robust to YYYY-MM-DD or other)
        pl.col(COL_TIMESTAMP).cast(pl.Utf8).str.to_date(strict=False).alias(COL_TIMESTAMP),
        # Strip strings
        pl.col(COL_KEYWORD).cast(pl.Utf8).str.strip_chars(),
        pl.col(COL_URL).cast(pl.Utf8).str.strip_chars(),
        pl.col(COL_INTENTS).cast(pl.Utf8).str.strip_chars(),
        pl.col(COL_SERP_FEATS).cast(pl.Utf8).str.strip_chars(),
        pl.col(COL_POSITION_TYPE).cast(pl.Utf8).str.strip_chars(),
    )

    # Add helpers
    df = df.with_columns(
        (pl.col(COL_PREV_POS) - pl.col(COL_POS)).alias("pos_change"),
        (pl.col(COL_POS) <= 3).alias("is_top3"),
        (pl.col(COL_POS) <= 10).alias("is_top10"),
        bucket_position(pl.col(COL_POS)).alias("pos_bucket"),
        url_category(pl.col(COL_URL)).alias("url_category"),
        url_service(pl.col(COL_URL)).alias("service"),
    )

    return df


def bucket_position(pos: pl.Expr) -> pl.Expr:
    """Return a position bucket label for the numeric position expression."""
    return (
        pl.when(pos <= 3)
        .then(pl.lit("01-03"))
        .when(pos <= 10)
        .then(pl.lit("04-10"))
        .when(pos <= 20)
        .then(pl.lit("11-20"))
        .when(pos <= 50)
        .then(pl.lit("21-50"))
        .otherwise(pl.lit("51+"))
    )


def url_category(url: pl.Expr) -> pl.Expr:
    """Classify URL into a coarse content/category bucket.

    Heuristics:
    - agency listing pages
    - trends/educational content
    - city/state pages
    - other
    """
    return (
        pl.when(url.str.contains(r"/agency/(web|website|search|seo|ppc|branding|logo|app|mobile|ui|ux|ecommerce|shopify|magento|wordpress|drupal|joomla|content|social|pr|public-relations|software|it|outsourcing|blockchain|ai|data|analytics|video|production|animation|3d|game|ar|vr|big-data|business|consult|marketing|advert|media|influencer|email|lead|b2b|b2c|saas)"))
        .then(pl.lit("agency"))
        .when(url.str.contains(r"/agency/[^/]+/(alabama|alaska|arizona|arkansas|california|colorado|connecticut|delaware|florida|georgia|hawaii|idaho|illinois|indiana|iowa|kansas|kentucky|louisiana|maine|maryland|massachusetts|michigan|minnesota|mississippi|missouri|montana|nebraska|nevada|new-?hampshire|new-?jersey|new-?mexico|new-?york|north-?carolina|north-?dakota|ohio|oklahoma|oregon|pennsylvania|rhode-?island|south-?carolina|south-?dakota|tennessee|texas|utah|vermont|virginia|washington|west-?virginia|wisconsin|wyoming|chicago|new-york|los-angeles|san-?francisco|dallas|miami|seattle|austin|boston|denver|atlanta|houston)"))
        .then(pl.lit("geo"))
        .when(url.str.contains(r"/trends/"))
        .then(pl.lit("trends"))
        .otherwise(pl.lit("other"))
    )


def _default_service_patterns() -> list[tuple[str, str]]:
    return [
        (r"/agency/website-design-development", "web_design"),
        (r"/agency/web-development-companies", "web_dev"),
        (r"/agency/search-engine-optimization", "seo"),
        (r"/agency/paid-media-pay-per-click", "ppc"),
        (r"/agency/social-media-marketing", "social"),
        (r"/agency/branding", "branding"),
        (r"/agency/logo-design", "logo"),
        (r"/agency/mobile-app-design-development", "mobile_app"),
        (r"/agency/software-development", "software_dev"),
        (r"/agency/ecommerce", "ecommerce"),
        (r"/agency/video-(marketing|production)", "video"),
        (r"/agency/public-relations", "pr"),
        (r"/agency/it-services", "it_services"),
        (r"/agency/cybersecurity", "cybersecurity"),
        (r"/agency/hr-outsourcing", "hr_outsourcing"),
        (r"/agency/influencer-marketing", "influencer"),
        (r"/agency/content-marketing", "content"),
        (r"/agency/email-marketing", "email"),
        (r"/agency/lead-generation", "lead_gen"),
        (r"/agency/(ai|artificial-intelligence)", "ai"),
        (r"/agency/(data|analytics|big-data)", "data_analytics"),
        (r"/agency/(wordpress|shopify|magento|drupal|joomla)", "cms_platform"),
        (r"/agency/digital-marketing", "digital_marketing"),
        (r"/agency/ad-agencies", "advertising"),
    ]


def _load_service_patterns_from_config() -> list[tuple[str, str]] | None:
    cfg = Path("config/service_patterns.json")
    if not cfg.exists():
        return None
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        # expected: list of {"pattern": "regex", "label": "slug"}
        patterns = []
        for item in data:
            patterns.append((str(item["pattern"]), str(item["label"])) )
        return patterns
    except Exception:
        return None


def url_service(url: pl.Expr) -> pl.Expr:
    """Classify URL to a fine-grained agency service taxonomy.

    Returns a short slug such as 'seo', 'ppc', 'web_design', etc.
    Honors optional overrides in config/service_patterns.json when present.
    """
    patterns = _load_service_patterns_from_config() or _default_service_patterns()

    expr: pl.Expr = pl.lit("other")
    for pat, label in patterns:
        expr = pl.when(url.str.contains(pat)).then(pl.lit(label)).otherwise(expr)
    return expr


def _explode_list_column_from_str(df: pl.DataFrame, column: str, sep: str = ",") -> pl.DataFrame:
    """Split a string column by commas and explode into rows, trimming spaces."""
    return (
        df.select(
            pl.all().exclude(column),
            pl.col(column).str.split(sep).list.eval(pl.element().str.strip_chars()).alias(column),
        )
        .explode(column)
        .filter(pl.col(column).is_not_null() & (pl.col(column) != ""))
    )


def overview(df: pl.DataFrame) -> dict:
    """Compute high-level overview metrics."""
    total_keywords = df.height
    totals = df.select(
        pl.sum(COL_TRAFFIC).alias("traffic"),
        pl.sum(COL_TRAFFIC_COST).alias("traffic_cost"),
        pl.mean(COL_POS).alias("avg_position"),
    ).row(0)

    by_bucket = (
        df.group_by("pos_bucket")
        .agg(
            pl.count().alias("keywords"),
            pl.sum(COL_TRAFFIC).alias("traffic"),
        )
        .with_columns((pl.col("keywords") / total_keywords).alias("share"))
        .sort("pos_bucket")
    )

    return {
        "total_keywords": int(total_keywords),
        "traffic": float(totals[0]),
        "traffic_cost": float(totals[1]),
        "avg_position": float(totals[2]) if totals[2] is not None else None,
        "by_bucket": by_bucket,
    }


def top_keywords_by_traffic(df: pl.DataFrame, n: int = 50) -> pl.DataFrame:
    return df.sort(COL_TRAFFIC, descending=True).head(n)


def top_keywords_by_volume(df: pl.DataFrame, n: int = 50) -> pl.DataFrame:
    return df.sort(COL_VOLUME, descending=True).head(n)


def top_pages_by_traffic(df: pl.DataFrame, n: int = 100) -> pl.DataFrame:
    return (
        df.group_by(COL_URL)
        .agg(
            pl.sum(COL_TRAFFIC).alias("traffic"),
            pl.sum(COL_TRAFFIC_COST).alias("traffic_cost"),
            pl.mean(COL_POS).alias("avg_position"),
            pl.count().alias("keywords"),
        )
        .sort(["traffic", "traffic_cost"], descending=[True, True])
        .head(n)
    )


def quick_wins(df: pl.DataFrame, n: int = 100) -> pl.DataFrame:
    """Keywords in positions 4–10 with high volume and CPC."""
    return (
        df.filter((pl.col(COL_POS) >= 4) & (pl.col(COL_POS) <= 10))
        .with_columns((pl.col(COL_VOLUME) * (pl.col(COL_CPC).fill_null(0.0))).alias("priority"))
        .sort(["priority", COL_VOLUME, COL_CPC], descending=[True, True, True])
        .head(n)
    )


def movers(df: pl.DataFrame, n: int = 50) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Top improvers and decliners by change in position (previous vs current)."""
    has_prev = df.filter(pl.col(COL_PREV_POS) > 0)
    improvers = has_prev.sort("pos_change", descending=True).head(n)
    decliners = has_prev.sort("pos_change", descending=False).head(n)
    return improvers, decliners


def intent_mix(df: pl.DataFrame) -> pl.DataFrame:
    exploded = _explode_list_column_from_str(df, COL_INTENTS)
    return (
        exploded.group_by(COL_INTENTS)
        .agg(
            pl.count().alias("keywords"),
            pl.sum(COL_TRAFFIC).alias("traffic"),
        )
        .with_columns((pl.col("keywords") / df.height).alias("share"))
        .sort("traffic", descending=True)
    )


def serp_features_presence(df: pl.DataFrame, features: Iterable[str] | None = None) -> pl.DataFrame:
    feats = list(
        features
        or [
            "People also ask",
            "Local pack",
            "Sitelinks",
            "Video",
            "Image pack",
            "Ads top",
            "Ads bottom",
            "AI overview",
        ]
    )
    result = []
    for f in feats:
        mask = df[COL_SERP_FEATS].str.contains(pl.lit(f))
        sub = df.filter(mask)
        result.append(
            {
                "feature": f,
                "keywords": sub.height,
                "traffic": float(sub.select(pl.sum(COL_TRAFFIC)).item() or 0.0),
                "top3_share": float(sub.select(pl.mean("is_top3")).item() or 0.0),
            }
        )
    return pl.DataFrame(result).sort("traffic", descending=True)


def serp_features_presence_for_df(df: pl.DataFrame) -> pl.DataFrame:
    """Convenience wrapper to compute SERP features presence for a given subset."""
    return serp_features_presence(df)


def categories_breakdown(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("url_category")
        .agg(
            pl.count().alias("keywords"),
            pl.sum(COL_TRAFFIC).alias("traffic"),
            pl.sum(COL_TRAFFIC_COST).alias("traffic_cost"),
            pl.mean(COL_POS).alias("avg_position"),
        )
        .sort("traffic", descending=True)
    )


def services_breakdown(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("service")
        .agg(
            pl.count().alias("keywords"),
            pl.sum(COL_TRAFFIC).alias("traffic"),
            pl.sum(COL_TRAFFIC_COST).alias("traffic_cost"),
            pl.mean(COL_POS).alias("avg_position"),
            (pl.when(pl.col("pos_change") > 0).then(1).otherwise(0)).sum().alias("improving"),
            (pl.when(pl.col("pos_change") < 0).then(1).otherwise(0)).sum().alias("declining"),
        )
        .sort("traffic", descending=True)
    )


# --- Forecasting helpers ---

def position_ctr(pos: int) -> float:
    """Simple CTR model by position.

    Approximates desktop blended CTR; intentionally conservative.
    """
    if pos <= 1:
        return 0.28
    if pos == 2:
        return 0.15
    if pos == 3:
        return 0.11
    if pos == 4:
        return 0.08
    if pos == 5:
        return 0.07
    if pos == 6:
        return 0.06
    if pos == 7:
        return 0.05
    if pos == 8:
        return 0.04
    if pos == 9:
        return 0.035
    if pos == 10:
        return 0.03
    if pos <= 20:
        return 0.015
    return 0.005


def forecast_quick_wins_uplift(
    df: pl.DataFrame, target_pos: int = 3, n: int = 200
) -> tuple[dict, pl.DataFrame, pl.DataFrame]:
    """Estimate uplift moving quick wins to a target position.

    Returns (summary_dict, details_df, by_service_df)
    """
    # Build quick wins set (reuse same priority logic)
    q = (
        df.filter((pl.col(COL_POS) >= 4) & (pl.col(COL_POS) <= 10))
        .with_columns((pl.col(COL_VOLUME) * (pl.col(COL_CPC).fill_null(0.0))).alias("priority"))
        .sort(["priority", COL_VOLUME, COL_CPC], descending=[True, True, True])
        .head(n)
    )

    # Compute CTRs and uplifts
    def _ctr_expr_for(col: str) -> pl.Expr:
        return (
            pl.when(pl.col(col) <= 1)
            .then(0.28)
            .when(pl.col(col) == 2)
            .then(0.15)
            .when(pl.col(col) == 3)
            .then(0.11)
            .when(pl.col(col) == 4)
            .then(0.08)
            .when(pl.col(col) == 5)
            .then(0.07)
            .when(pl.col(col) == 6)
            .then(0.06)
            .when(pl.col(col) == 7)
            .then(0.05)
            .when(pl.col(col) == 8)
            .then(0.04)
            .when(pl.col(col) == 9)
            .then(0.035)
            .when(pl.col(col) == 10)
            .then(0.03)
            .when(pl.col(col) <= 20)
            .then(0.015)
            .otherwise(0.005)
        )

    details = q.with_columns(
        _ctr_expr_for(COL_POS).alias("ctr_current"),
        pl.lit(position_ctr(target_pos)).alias("ctr_target"),
    ).with_columns(
        (pl.col(COL_VOLUME) * pl.col("ctr_current")).alias("clicks_current"),
        (pl.col(COL_VOLUME) * pl.col("ctr_target")).alias("clicks_target"),
    ).with_columns(
        (pl.col("clicks_target") - pl.col("clicks_current")).alias("uplift_clicks"),
        (
            (pl.col("clicks_target") - pl.col("clicks_current"))
            * (pl.col(COL_CPC).fill_null(0.0))
        ).alias("uplift_value"),
    )

    summary_row = details.select(
        pl.sum("uplift_clicks").alias("uplift_clicks"),
        pl.sum("uplift_value").alias("uplift_value"),
        pl.count().alias("keywords"),
    ).row(0)
    summary = {
        "target_pos": target_pos,
        "considered_keywords": int(summary_row[2] or 0),
        "uplift_clicks": float(summary_row[0] or 0.0),
        "uplift_value": float(summary_row[1] or 0.0),
    }

    by_service = (
        details.group_by("service")
        .agg(
            pl.count().alias("keywords"),
            pl.sum("uplift_clicks").alias("uplift_clicks"),
            pl.sum("uplift_value").alias("uplift_value"),
        )
        .sort("uplift_value", descending=True)
    )

    return summary, details, by_service


def top_keywords_by_traffic_for_service(df: pl.DataFrame, service: str, n: int = 50) -> pl.DataFrame:
    return df.filter(pl.col("service") == service).sort(COL_TRAFFIC, descending=True).head(n)


def internal_targets_for_service(df: pl.DataFrame, service: str, n: int = 20) -> pl.DataFrame:
    """Select internal link targets: top URLs within the service by traffic.

    If the detected service hub exists (matches category URL), it will appear naturally.
    """
    return (
        df.filter(pl.col("service") == service)
        .group_by(COL_URL)
        .agg(pl.sum(COL_TRAFFIC).alias("traffic"), pl.mean(COL_POS).alias("avg_position"), pl.count().alias("keywords"))
        .sort("traffic", descending=True)
        .head(n)
    )


def _is_geo_url(url: pl.Expr) -> pl.Expr:
    return url.str.contains(r"/agency/[^/]+/([a-z-]+)(/[a-z-]+)?$")


def geo_reports(df: pl.DataFrame) -> dict[str, pl.DataFrame]:
    geo_df = df.filter(pl.col("url_category") == "geo")
    top_pages = (
        geo_df.group_by(COL_URL)
        .agg(
            pl.sum(COL_TRAFFIC).alias("traffic"),
            pl.mean(COL_POS).alias("avg_position"),
            pl.count().alias("keywords"),
        )
        .sort("traffic", descending=True)
    )
    wins = geo_df.filter(pl.col("pos_change") > 0).sort("pos_change", descending=True).head(200)
    losses = geo_df.filter(pl.col("pos_change") < 0).sort("pos_change", descending=False).head(200)
    qw = (
        geo_df.filter((pl.col(COL_POS) >= 4) & (pl.col(COL_POS) <= 10))
        .with_columns((pl.col(COL_VOLUME) * (pl.col(COL_CPC).fill_null(0.0))).alias("priority"))
        .sort(["priority", COL_VOLUME, COL_CPC], descending=[True, True, True])
        .head(200)
    )
    # Try to extract last 1-2 path segments as location key
    # Example: /agency/website-design-development/texas/houston -> texas/houston
    parts = (
        geo_df.select(
            pl.col(COL_URL),
            pl.col(COL_URL)
            .str.extract(r"/agency/[^/]+/(.+)$", 1)
            .str.replace_all(r"[^a-z0-9-/]", "")
            .alias("loc_path"),
            pl.col(COL_TRAFFIC),
        )
        .with_columns(
            pl.col("loc_path").str.split("/").list.tail(2).list.join("/").alias("location"),
        )
    )
    by_location = (
        parts.group_by("location")
        .agg(pl.count().alias("pages"), pl.sum(COL_TRAFFIC).alias("traffic"))
        .sort("traffic", descending=True)
    )
    return {
        "geo_top_pages": top_pages,
        "geo_wins": wins,
        "geo_losses": losses,
        "geo_quick_wins": qw,
        "geo_locations": by_location,
    }


def save_df(df: pl.DataFrame, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(path)


@dataclass
class AnalysisArtifacts:
    base_dir: Path
    overview_csv: Path
    top_keywords_csv: Path
    top_pages_csv: Path
    quick_wins_csv: Path
    improvers_csv: Path
    decliners_csv: Path
    intent_mix_csv: Path
    serp_features_csv: Path
    categories_csv: Path
    services_csv: Path
    summary_md: Path
    deck_md: Path | None = None
    charts: dict[str, Path] | None = None
    deck_html: Path | None = None
    vega_specs: dict[str, Path] | None = None
    forecast_by_service_csv: Path | None = None


def run_full_analysis(
    csv_path: str | Path,
    out_dir: str | Path | None = None,
    generate_charts: bool = True,
    generate_deck: bool = True,
) -> AnalysisArtifacts:
    df = load_positions(csv_path)
    # Target dir based on most recent timestamp found or today
    ts = df.select(pl.max(COL_TIMESTAMP)).to_series().item()
    if isinstance(ts, (datetime, date)):
        stamp = ts.strftime("%Y-%m-%d")
    else:
        stamp = date.today().strftime("%Y-%m-%d")

    base_dir = Path(out_dir) if out_dir else Path("artifacts") / stamp
    base_dir.mkdir(parents=True, exist_ok=True)

    ov = overview(df)
    top_kw = top_keywords_by_traffic(df, 100)
    top_pg = top_pages_by_traffic(df, 100)
    qw = quick_wins(df, 200)
    imp, dec = movers(df, 100)
    intents = intent_mix(df)
    serp = serp_features_presence(df)
    cats = categories_breakdown(df)
    svcs = services_breakdown(df)

    overview_csv = base_dir / "overview_buckets.csv"
    save_df(ov["by_bucket"], overview_csv)
    save_df(top_kw, base_dir / "top_keywords_by_traffic.csv")
    save_df(top_pg, base_dir / "top_pages_by_traffic.csv")
    save_df(qw, base_dir / "quick_wins.csv")
    save_df(imp, base_dir / "movers_improvers.csv")
    save_df(dec, base_dir / "movers_decliners.csv")
    save_df(intents, base_dir / "intent_mix.csv")
    save_df(serp, base_dir / "serp_features.csv")
    save_df(cats, base_dir / "categories.csv")
    save_df(svcs, base_dir / "services_summary.csv")

    # Per-service win/loss/quick-win tables
    services_dir = base_dir / "services"
    services_dir.mkdir(parents=True, exist_ok=True)
    svc_list = svcs.select("service").to_series().to_list()
    for svc in svc_list:
        sub = df.filter(pl.col("service") == svc)
        # Threshold: skip tiny services (< 20 keywords)
        if sub.height < 20:
            continue
        wins = sub.filter(pl.col("pos_change") > 0).sort("pos_change", descending=True).head(50)
        losses = sub.filter(pl.col("pos_change") < 0).sort("pos_change", descending=False).head(50)
        qw_svc = (
            sub.filter((pl.col(COL_POS) >= 4) & (pl.col(COL_POS) <= 10))
            .with_columns((pl.col(COL_VOLUME) * (pl.col(COL_CPC).fill_null(0.0))).alias("priority"))
            .sort(["priority", COL_VOLUME, COL_CPC], descending=[True, True, True])
            .head(50)
        )
        top_kw_svc = top_keywords_by_traffic_for_service(df, svc, 50)
        serp_svc = serp_features_presence_for_df(sub)
        internal_targets = internal_targets_for_service(df, svc, 20)
        # Save
        save_df(wins, services_dir / f"wins_{svc}.csv")
        save_df(losses, services_dir / f"losses_{svc}.csv")
        save_df(qw_svc, services_dir / f"quick_wins_{svc}.csv")
        save_df(top_kw_svc, services_dir / f"top_keywords_{svc}.csv")
        save_df(serp_svc, services_dir / f"serp_features_{svc}.csv")
        save_df(internal_targets, services_dir / f"internal_targets_{svc}.csv")

    # Geo reports
    geo = geo_reports(df)
    for name, gdf in geo.items():
        save_df(gdf, base_dir / f"{name}.csv")

    # Write summary markdown
    summary_md = base_dir / "summary.md"
    total_kw = ov["total_keywords"]
    total_traffic = ov["traffic"]
    total_cost = ov["traffic_cost"]
    avg_pos = ov["avg_position"]
    by_b = ov["by_bucket"].to_dict(as_series=False)
    with summary_md.open("w", encoding="utf-8") as f:
        f.write("# Organic Positions Summary\n\n")
        f.write(f"- Total keywords: {total_kw}\n")
        f.write(f"- Est. traffic: {total_traffic:,.0f}\n")
        f.write(f"- Est. traffic cost: ${total_cost:,.0f}\n")
        f.write(f"- Average position: {avg_pos:.2f}\n")
        f.write("- Position buckets: ")
        b_items = [
            f"{b} {k}/{total_kw} ({s:.1%})"
            for b, k, s in zip(by_b["pos_bucket"], by_b["keywords"], by_b["share"])
        ]
        f.write(", ".join(b_items) + "\n\n")

        # Quick takeaways
        top_kw_row = top_kw.select([COL_KEYWORD, COL_TRAFFIC, COL_POS, COL_URL]).head(5)
        f.write("## Highlights\n")
        for r in top_kw_row.iter_rows():
            kw, tr, pos, url = r
            f.write(f"- Top keyword: '{kw}' pos {pos}, traffic {tr:,.0f} → {url}\n")

        f.write("\n## Quick wins (pos 4–10)\n")
        for r in qw.select([COL_KEYWORD, COL_VOLUME, COL_CPC, COL_POS, COL_URL]).head(10).iter_rows():
            kw, vol, cpc, pos, url = r
            f.write(f"- {kw} (vol {vol:,}, CPC ${cpc:,.2f}) at pos {pos} → {url}\n")

    charts: dict[str, Path] | None = None
    deck_md: Path | None = None
    deck_html: Path | None = None
    vega_specs: dict[str, Path] | None = None

    if generate_charts:
        try:
            from .charts import generate_all_charts, generate_vega_specs

            charts = generate_all_charts(
                base_dir=base_dir,
                by_bucket=ov["by_bucket"],
                intent=intents,
                categories=cats,
                services=svcs,
            )
            # Also write Vega-Lite specs for portability
            vega_specs = generate_vega_specs(
                base_dir=base_dir,
                by_bucket=ov["by_bucket"],
                intent=intents,
                categories=cats,
                services=svcs,
            )
        except Exception:
            charts = None
            vega_specs = None

    # Forecast uplift for quick wins
    forecast_summary = None
    forecast_by_service = None
    try:
        forecast_summary, _forecast_details, forecast_by_service = forecast_quick_wins_uplift(df, target_pos=3, n=200)
        save_df(forecast_by_service, base_dir / "forecast_by_service.csv")
    except Exception:
        pass

    if generate_deck:
        try:
            from .deck import write_deck
            from .html_deck import write_html_deck

            # Geo reports
            geo = geo_reports(df)

            deck_md = write_deck(
                base_dir=base_dir,
                overview=ov,
                charts=charts or {},
                top_pages=top_pg,
                quick_wins=qw,
                intents=intents,
                serp=serp,
                categories=cats,
                services=svcs,
                geo=geo,
                forecast_summary=forecast_summary,
                forecast_by_service=forecast_by_service,
            )
            deck_html = write_html_deck(
                base_dir=base_dir,
                overview=ov,
                charts=charts or {},
                vega_specs=vega_specs or {},
                top_keywords=top_kw,
                top_pages=top_pg,
                quick_wins=qw,
                intents=intents,
                serp=serp,
                categories=cats,
                services=svcs,
                geo=geo,
                forecast_summary=forecast_summary,
                forecast_by_service=forecast_by_service,
            )
        except Exception:
            deck_md = None
            deck_html = None

    return AnalysisArtifacts(
        base_dir=base_dir,
        overview_csv=overview_csv,
        top_keywords_csv=base_dir / "top_keywords_by_traffic.csv",
        top_pages_csv=base_dir / "top_pages_by_traffic.csv",
        quick_wins_csv=base_dir / "quick_wins.csv",
        improvers_csv=base_dir / "movers_improvers.csv",
        decliners_csv=base_dir / "movers_decliners.csv",
        intent_mix_csv=base_dir / "intent_mix.csv",
        serp_features_csv=base_dir / "serp_features.csv",
        categories_csv=base_dir / "categories.csv",
        services_csv=base_dir / "services_summary.csv",
        summary_md=summary_md,
        deck_md=deck_md,
        charts=charts,
        deck_html=deck_html,
        vega_specs=vega_specs,
        forecast_by_service_csv=(base_dir / "forecast_by_service.csv") if forecast_by_service is not None else None,
    )
