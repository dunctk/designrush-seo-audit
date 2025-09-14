from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple
import re
import base64

import polars as pl


def _table(df: pl.DataFrame, cols: list[str], max_rows: int = 10) -> str:
    df2 = df.select(cols).head(max_rows)
    # Escape HTML
    def esc(v: object) -> str:
        s = "" if v is None else str(v)
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    head = "".join(f"<th>{esc(c)}</th>" for c in df2.columns)
    rows = []
    for row in df2.iter_rows():
        rows.append("<tr>" + "".join(f"<td>{esc(v)}</td>" for v in row) + "</tr>")
    body = "".join(rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def write_html_deck(
    base_dir: Path,
    overview: dict,
    charts: Dict[str, Path],
    vega_specs: Dict[str, Path],
    top_keywords: pl.DataFrame,
    top_pages: pl.DataFrame,
    quick_wins: pl.DataFrame,
    intents: pl.DataFrame,
    serp: pl.DataFrame,
    categories: pl.DataFrame,
    services: pl.DataFrame,
    geo: Dict[str, pl.DataFrame] | None = None,
    forecast_summary: dict | None = None,
    forecast_by_service: pl.DataFrame | None = None,
) -> Path:
    out = Path(base_dir) / "deck.html"

    # Inline the Vega-Lite specs to avoid local file fetch/CORS issues
    specs_inline: Dict[str, dict] = {}
    for name, p in vega_specs.items():
        try:
            specs_inline[name] = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            specs_inline[name] = {}

    total_kw = overview.get("total_keywords")
    total_traffic = overview.get("traffic")
    total_cost = overview.get("traffic_cost")
    avg_pos = overview.get("avg_position")

    # Helper: inline PNG chart if present
    def inline_png(name: str) -> str | None:
        if not charts:
            return None
        p = charts.get(name)
        if not p:
            return None
        try:
            data = Path(p).read_bytes()
            b64 = base64.b64encode(data).decode("ascii")
            return f"<img alt=\"{name}\" src=\"data:image/png;base64,{b64}\" style=\"max-width:100%;height:auto\">"
        except Exception:
            return None

    # Build HTML
    html = []
    html.append("<!doctype html>")
    html.append("<html lang=\"en\">\n<head>")
    html.append("<meta charset=\"utf-8\">")
    html.append("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">")
    html.append("<title>DesignRush SEO Audit – v1</title>")
    # External resources
    html.append("<link rel=\"preconnect\" href=\"https://cdn.jsdelivr.net\">")
    html.append("<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">")
    html.append(
        "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>"
    )
    html.append(
        "<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap\" rel=\"stylesheet\">"
    )
    # Theming + refined layout
    html.append(
        "<style>"
        ":root{--bg:#0b1220;--panel:#0f172a;--border:#1f2937;--text:#e5e7eb;--muted:#9ca3af;--accent:#60a5fa;--accent2:#a5b4fc;--shadow:0 2px 16px rgba(0,0,0,.35)}"
        "body.light{--bg:#ffffff;--panel:#f8fafc;--border:#e5e7eb;--text:#111827;--muted:#6b7280;--accent:#2563eb;--accent2:#7c3aed;--shadow:0 2px 16px rgba(0,0,0,.08)}"
        "html,body{height:100%}"
        "body{background:var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;line-height:1.5;"
        "-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;transition:background .2s,color .2s}"
        ".deck{position:relative;min-height:100%;padding-bottom:64px}"
        ".slide{display:block;box-sizing:border-box;min-height:100dvh;padding:48px 56px;max-width:1200px;margin:0 auto}"
        ".js .slide{display:none}"
        ".js .slide.current{display:block}"
        "h1{font-size:40px;margin:0 0 8px 0;color:var(--text)}"
        "h2{font-size:28px;margin:0 0 16px 0;color:var(--text)}"
        "h3{font-size:20px;margin:16px 0 8px;color:var(--text)}"
        ".muted{color:var(--muted)}"
        ".metrics{margin-top:12px;margin-bottom:8px;display:flex;flex-wrap:wrap;gap:12px}"
        ".metric{display:flex;align-items:center;gap:8px;margin-top:8px;padding:10px 12px;background:var(--panel);border:1px solid var(--border);border-radius:10px;color:var(--text);box-shadow:var(--shadow)}"
        ".metric .ico{width:18px;height:18px;opacity:.9}"
        ".charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}"
        ".chart{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:12px;box-shadow:var(--shadow)}"
        ".chart-title{font:600 14px/1.2 Inter,system-ui;color:var(--text);margin:0 0 8px 0}"
        ".chart-caption{font:500 12px/1.4 Inter,system-ui;color:#94a3b8;margin-top:8px}"
        "table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px;background:var(--panel);border:1px solid var(--border);border-radius:10px;overflow:hidden}"
        "th,td{border-bottom:1px solid #243244;padding:10px 12px;text-align:left}"
        "th{background:#111827;color:var(--text)}"
        "tbody tr:nth-child(odd){background:rgba(255,255,255,0.02)}"
        "a{color:#93c5fd}"
        ".pill{display:inline-block;border-radius:9999px;border:1px solid var(--border);background:var(--panel);padding:6px 10px;color:var(--accent2);text-transform:uppercase;letter-spacing:.08em;font:700 11px/1 Inter,system-ui}"
        ".idea{display:block;margin-top:8px}"
        ".idea-card{background:linear-gradient(180deg,#0e1628,#0b1220);border:1px solid var(--border);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}"
        ".roadmap-card{background:linear-gradient(180deg,#0e1628,#0b1220);border:1px solid var(--border);border-radius:14px;padding:16px 18px;box-shadow:var(--shadow)}"
        ".shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin-top:8px}"
        ".shot-card{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:10px;box-shadow:var(--shadow)}"
        ".shot-card img{width:100%;height:auto;display:block;border-radius:8px;border:1px solid var(--border);cursor:zoom-in}"
        ".shot-cap{font:500 12px/1.4 Inter,system-ui;color:#94a3b8;margin-top:6px}"
        ".nav{position:fixed;left:0;right:0;bottom:12px;display:flex;gap:12px;align-items:center;justify-content:center;pointer-events:none}"
        ".nav-inner{display:flex;gap:8px;align-items:center;pointer-events:auto;background:var(--panel);border:1px solid var(--border);border-radius:9999px;padding:6px 10px;box-shadow:0 2px 10px rgba(0,0,0,.4)}"
        ".btn{appearance:none;border:1px solid #334155;background:#111827;color:#e5e7eb;border-radius:9999px;padding:8px 14px;font:600 14px/1 Inter,system-ui;cursor:pointer}"
        ".btn--ghost{background:transparent;border-color:var(--border);color:var(--text)}"
        ".btn:disabled{opacity:.5;cursor:not-allowed}"
        ".counter{color:var(--muted);font:500 12px/1 Inter,system-ui;padding:0 8px}"
        ".progress{position:fixed;left:0;right:0;bottom:0;height:3px;background:rgba(255,255,255,0.08)}"
        ".progress .bar{height:100%;width:0;background:linear-gradient(90deg,var(--accent),var(--accent2));transition:width .2s}"
        ".zoom{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:50}"
        ".zoom img{max-width:92vw;max-height:92vh;border-radius:12px;box-shadow:var(--shadow)}"
        "body.print .slide{display:block;page-break-after:always;min-height:auto;padding:28px 40px}"
        "body.print .nav,body.print .progress{display:none}"
        "@media (max-width:640px){.slide{padding:28px 20px}h1{font-size:30px}h2{font-size:22px}}"
        "</style>"
    )
    # Vega libraries
    html.append("<script src=\"https://cdn.jsdelivr.net/npm/vega@5\"></script>")
    html.append("<script src=\"https://cdn.jsdelivr.net/npm/vega-lite@5\"></script>")
    html.append("<script src=\"https://cdn.jsdelivr.net/npm/vega-embed@6\"></script>")
    html.append("</head><body>")
    html.append("<main class=\"deck\">")

    # Intro slide (title + key metrics)
    html.append("<section class=\"slide current\">")
    html.append("<h1>DesignRush SEO Audit – v1</h1>")
    html.append("<div class=\"metrics\">")
    html.append(
        f"<div class=\"metric\"><svg class=\"ico\" viewBox=\"0 0 24 24\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M12 3l4 4-9 9-4 1 1-4 9-9z\" stroke=\"currentColor\" stroke-width=\"2\"/></svg>Keywords: {total_kw:,}</div>"
        f"<div class=\"metric\"><svg class=\"ico\" viewBox=\"0 0 24 24\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M3 12h18M12 3v18\" stroke=\"currentColor\" stroke-width=\"2\"/></svg>Avg position: {avg_pos:.2f}</div>"
        f"<div class=\"metric\"><svg class=\"ico\" viewBox=\"0 0 24 24\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><path d=\"M3 17l6-6 4 4 7-7\" stroke=\"currentColor\" stroke-width=\"2\"/></svg>Traffic: {total_traffic:,.0f}</div>"
        f"<div class=\"metric\"><svg class=\"ico\" viewBox=\"0 0 24 24\" fill=\"none\" xmlns=\"http://www.w3.org/2000/svg\"><circle cx=\"12\" cy=\"12\" r=\"7\" stroke=\"currentColor\" stroke-width=\"2\"/></svg>Value: ${total_cost:,.0f}</div>"
    )
    html.append("</div>")
    
    # Add screenshot to first slide if available
    agency_screenshot = inline_png("04-directory-root__desktop") or inline_png("03-category-seo__desktop")
    if agency_screenshot:
        title = "Agency Directory Overview" if "04-directory-root" in str(agency_screenshot) else "SEO Category Page"
        html.append("<div style=\"margin-top: 20px; max-width: 600px;\">")
        html.append(f"<h3>{title}</h3>")
        html.append(agency_screenshot.replace('style="max-width:100%;height:auto"', 'style="max-width:100%;height:auto;border-radius:8px;"'))
        html.append("</div>")
    
    html.append("<p class=\"muted\">Use ←/→, Space, or the buttons to navigate.</p>")
    html.append("</section>")

    # Charts section
    html.append("<section class=\"slide\"><h2>Rankings Overview</h2>")
    html.append("<div class=\"charts\">")
    # For each chart, prefer PNG inline; otherwise, insert a div for Vega fallback
    # 1) Position buckets
    html.append("<figure class=\"chart\">")
    html.append("<div class=\"chart-title\">Keyword Distribution by Position</div>")
    png = inline_png("position_buckets")
    html.append(png or '<div id="chart_position_buckets" aria-label="Keyword distribution by position"></div>')
    html.append("<figcaption class=\"chart-caption\">Counts of ranking keywords in position ranges (01–03, 04–10, etc.). Goal: grow 01–03 for visibility and CTR.</figcaption>")
    html.append("</figure>")
    # 2) Intent mix
    html.append("<figure class=\"chart\">")
    html.append("<div class=\"chart-title\">Intent Mix (by keywords)</div>")
    png = inline_png("intent_mix")
    html.append(png or '<div id="chart_intent_mix" aria-label="Intent mix by keywords"></div>')
    html.append("<figcaption class=\"chart-caption\">Share of keywords by search intent. Guides content balance between informational and commercial terms.</figcaption>")
    html.append("</figure>")
    # 3) Categories
    html.append("<figure class=\"chart\">")
    html.append("<div class=\"chart-title\">Traffic by Category</div>")
    png = inline_png("categories")
    html.append(png or '<div id="chart_categories" aria-label="Traffic by category"></div>')
    html.append("<figcaption class=\"chart-caption\">Estimated organic traffic by content category (agency, trends, geo, other). Highlights where performance concentrates.</figcaption>")
    html.append("</figure>")
    # 4) Services
    html.append("<figure class=\"chart\">")
    html.append("<div class=\"chart-title\">Traffic by Service (Top 12)</div>")
    png = inline_png("services")
    html.append(png or '<div id="chart_services" aria-label="Traffic by service"></div>')
    html.append("<figcaption class=\"chart-caption\">Traffic contribution by service taxonomy. Helps prioritize which hubs to strengthen.</figcaption>")
    html.append("</figure>")
    html.append("</div>")
    # Narrative commentary for charts (data-derived)
    try:
        byb = overview.get("by_bucket")
        top3 = None; win = None
        if isinstance(byb, pl.DataFrame):
            d = byb.to_dict(as_series=False)
            share_map = {b: s for b, s in zip(d.get("pos_bucket", []), d.get("share", []))}
            top3 = share_map.get("01-03")
            win = share_map.get("04-10")
        cat_map = {}
        try:
            cd = categories.select(["url_category", "traffic"]).to_dict(as_series=False)
            cat_map = {k: float(v) for k, v in zip(cd.get("url_category", []), cd.get("traffic", []))}
        except Exception:
            pass
        sv_share = None
        try:
            sv = services.select(["service", "traffic"]).to_dict(as_series=False)
            traf = [float(x) for x in sv.get("traffic", [])]
            ttl = sum(traf) or 0.0
            if ttl > 0 and traf:
                sv_share = sum(sorted(traf, reverse=True)[:4]) / ttl
        except Exception:
            pass
        bullets = []
        if top3 is not None and win is not None:
            bullets.append(f"~{top3:.1%} of keywords in top‑3; ~{win:.1%} in 4–10 → strong quick‑win runway.")
        if cat_map:
            parts = []
            for k in ("agency", "trends", "geo", "other"):
                if k in cat_map:
                    parts.append(f"{k} {int(cat_map[k]):,}")
            if parts:
                bullets.append("Category mix → " + ", ".join(parts) + ".")
        if sv_share is not None:
            bullets.append(f"Top 4 services ≈ {sv_share:.0%} of service traffic → protect & lift hubs.")
        if bullets:
            html.append("<div class=\"muted\" style=\"margin-top:12px\"><ul>" + "".join(f"<li>{_esc(b)}</li>" for b in bullets) + "</ul></div>")
    except Exception:
        pass
    html.append("</section>")

    # Top Keywords (by traffic)
    if top_keywords is not None:
        html.append("<section class=\"slide\"><h2>Top Keywords (by Traffic)</h2>")
        html.append(_table(top_keywords, ["Keyword", "Traffic", "Position", "URL"], max_rows=15))
        html.append("<p class=\"muted\" style=\"margin-top:8px\">Why included: spot the highest-demand queries and confirm that directory pages map to them. Story: we already rank on many commercial queries — polishing titles/FAQs and adding contextual links drives top‑3 and better CTR.</p>")
        html.append("</section>")

    # Top pages
    html.append("<section class=\"slide\"><h2>Top Pages</h2>")
    html.append(_table(top_pages, ["URL", "traffic", "avg_position", "keywords"], max_rows=12))
    try:
        # Concentration commentary
        ts = [float(t) for t in top_pages.select("traffic").to_series().to_list() if t is not None]
        t10 = sum(ts[:10]) if ts else 0.0
        t20 = sum(ts[:20]) if ts else 0.0
        tot = float(overview.get("traffic") or 0.0)
        if tot > 0 and t10 > 0:
            html.append(
                f"<p class=\"muted\" style=\"margin-top:8px\">Top 10 pages ≈ {t10/tot:.1%} of total traffic; top 20 ≈ {t20/tot:.1%}. Diversify wins beyond a few hubs.</p>"
            )
    except Exception:
        pass
    html.append("</section>")

    # Quick wins
    html.append("<section class=\"slide\"><h2>Quick Wins (Positions 4–10)</h2>")
    html.append(_table(quick_wins, ["Keyword", "Search Volume", "CPC", "Position", "URL"], max_rows=15))
    try:
        total_qw = int(quick_wins.height)
        total_pri = float(quick_wins.select(pl.sum("priority")).item() or 0.0) if "priority" in quick_wins.columns else 0.0
        bullets = [f"{total_qw} quick‑win keywords; priority sum ≈ {total_pri:,.0f}."]
        if forecast_by_service is not None and "uplift_value" in forecast_by_service.columns:
            top3 = (
                forecast_by_service.select(["service", "uplift_value"]).sort("uplift_value", descending=True).head(3)
            )
            svcs = ", ".join(f"{s}" for s, _ in top3.iter_rows())
            if svcs:
                bullets.append("Top uplift services: " + svcs + ".")
        bullets.append("Why included: a prioritized backlog for immediate impact. Story: internal links + on‑page tuning can push 4–10 to top‑3 quickly.")
        html.append("<div class=\"muted\" style=\"margin-top:8px\"><ul>" + "".join(f"<li>{_esc(b)}</li>" for b in bullets) + "</ul></div>")
    except Exception:
        pass
    html.append("</section>")

    # SERP Features slide
    try:
        if serp is not None and serp.height > 0:
            html.append("<section class=\"slide\"><h2>SERP Features</h2>")
            html.append(_table(serp, ["feature", "keywords", "traffic", "top3_share"], max_rows=10))
            html.append("<p class=\"muted\" style=\"margin-top:8px\">Why included: shows the SERP surfaces we can win (PAA, Local Pack, Video, AI Overview). Story: add FAQs, LocalBusiness schema, and short videos to lift presence and CTR where these features exist.</p>")
            html.append("</section>")
    except Exception:
        pass

    # Geo locations + quick wins
    try:
        if geo is not None and isinstance(geo, dict):
            locs = geo.get("geo_locations")
            if locs is not None and locs.height > 0:
                html.append("<section class=\"slide\"><h2>Geo Locations & Local Quick Wins</h2>")
                html.append("<h3>Top Locations by Traffic</h3>")
                html.append(_table(locs, ["location", "pages", "traffic"], max_rows=10))
                qw_geo = geo.get("geo_quick_wins")
                if qw_geo is not None and qw_geo.height > 0:
                    html.append("<h3>Top Geo Quick Wins</h3>")
                    cols = ["Keyword", "Search Volume", "CPC", "Position", "URL"]
                    cols = [c for c in cols if c in qw_geo.columns]
                    html.append(_table(qw_geo, cols, max_rows=10))
                html.append("<p class=\"muted\" style=\"margin-top:8px\">Why included: local pages are the closest proxy for transactional intent (\"near me\"/city). Story: focus top cities first with local proof, schema, and internal links to lift conversions.</p>")
                html.append("</section>")
    except Exception:
        pass

    # Analyst Insights (optional one-off audit notes from artifacts/<date>/analyst_insights.md)
    try:
        insights_md_path = Path(base_dir) / "analyst_insights.md"
        if insights_md_path.exists():
            raw = insights_md_path.read_text(encoding="utf-8")

            def _esc2(s: str) -> str:
                return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')
            html.append("<section class=\"slide\"><h2>Analyst Insights</h2>")
            html.append("<div class=\"idea idea-card\">")
            for line in raw.splitlines():
                ls = line.rstrip()
                if ls.startswith("#### "):
                    html.append(f"<h4>{_esc2(ls[5:])}</h4>")
                    continue
                if ls.startswith("### "):
                    html.append(f"<h3>{_esc2(ls[4:])}</h3>")
                    continue
                if ls.startswith("## "):
                    html.append(f"<h2>{_esc2(ls[3:])}</h2>")
                    continue
                if ls.startswith("# "):
                    html.append(f"<h2>{_esc2(ls[2:])}</h2>")
                    continue
                m = re.match(r"^\s*([\-*•])\s+(.*)$", ls)
                if m:
                    html.append(f"<p>• {_esc2(m.group(2))}</p>")
                else:
                    html.append(f"<p>{_esc2(ls)}</p>")
            html.append("</div></section>")

            # (Internal Linking slide rendered separately below if provided as its own file)
    except Exception:
        pass

    # Internal Linking slide (from standalone file) placed after Analyst Insights
    il_path = Path(base_dir) / "internal_linking.md"
    if il_path.exists():
        raw_il = il_path.read_text(encoding="utf-8", errors="ignore")
        def _esc3(s: str) -> str:
            return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')
        html.append("<section class=\"slide\"><h2>Internal Linking</h2>")
        html.append("<div class=\"idea idea-card\">")
        for line in raw_il.splitlines():
            ls = line.rstrip()
            if ls.startswith("#### "):
                html.append(f"<h4>{_esc3(ls[5:])}</h4>")
                continue
            if ls.startswith("### "):
                html.append(f"<h3>{_esc3(ls[4:])}</h3>")
                continue
            if ls.startswith("## "):
                html.append(f"<h2>{_esc3(ls[3:])}</h2>")
                continue
            if ls.startswith("# "):
                html.append(f"<h2>{_esc3(ls[2:])}</h2>")
                continue
            m = re.match(r"^\s*([\-*•])\s+(.*)$", ls)
            if m:
                html.append(f"<p>• {_esc3(m.group(2))}</p>")
            else:
                html.append(f"<p>{_esc3(ls)}</p>")
        html.append("</div></section>")

    # Title & Header A/B Testing slide (optional)
    ab_path = Path(base_dir) / "ab_testing_titles_headers.md"
    if ab_path.exists():
        raw_ab = ab_path.read_text(encoding="utf-8", errors="ignore")
        def _esc4(s: str) -> str:
            return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"','&quot;')
        html.append("<section class=\"slide\"><h2>Title &amp; Header A/B Testing (CTAs)</h2>")
        html.append("<div class=\"idea idea-card\">")
        for line in raw_ab.splitlines():
            ls = line.rstrip()
            if ls.startswith("#### "):
                html.append(f"<h4>{_esc4(ls[5:])}</h4>")
                continue
            if ls.startswith("### "):
                html.append(f"<h3>{_esc4(ls[4:])}</h3>")
                continue
            if ls.startswith("## "):
                html.append(f"<h2>{_esc4(ls[3:])}</h2>")
                continue
            if ls.startswith("# "):
                html.append(f"<h2>{_esc4(ls[2:])}</h2>")
                continue
            m = re.match(r"^\s*([\-*•])\s+(.*)$", ls)
            if m:
                html.append(f"<p>• {_esc4(m.group(2))}</p>")
            else:
                html.append(f"<p>{_esc4(ls)}</p>")
        html.append("</div></section>")

    # Screenshots section (auto-embed if artifacts/<date>/screenshots has images)
    try:
        shots_dir = Path(base_dir) / "screenshots"
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        if shots_dir.exists():
            shots = sorted([p for p in shots_dir.iterdir() if p.suffix.lower() in exts])
        else:
            shots = []
    except Exception:
        shots = []

    def inline_img(path: Path) -> str | None:
        try:
            data = Path(path).read_bytes()
            b64 = base64.b64encode(data).decode("ascii")
            mime = "image/png"
            suf = path.suffix.lower()
            if suf in (".jpg", ".jpeg"):
                mime = "image/jpeg"
            elif suf == ".webp":
                mime = "image/webp"
            return f"<img alt=\"{path.name}\" src=\"data:{mime};base64,{b64}\" style=\"max-width:100%;height:auto;border:1px solid #1f2937;border-radius:10px\">"
        except Exception:
            return None

    def _group_key(path: Path) -> str:
        # Group name: before '__'
        stem = path.stem
        return stem.split("__", 1)[0]

    def _group_title(group_key: str) -> str:
        t = re.sub(r"^\d+[-_\s]*", "", group_key)
        return t.replace("-", " ").strip().title()

    def _variant_label(path: Path) -> str:
        stem = path.stem
        return stem.split("__", 1)[1] if "__" in stem else "view"

    def _esc(s: str) -> str:
        return (
            s.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    if shots:
        groups: Dict[str, List[Path]] = {}
        for pth in shots:
            groups.setdefault(_group_key(pth), []).append(pth)
        for gkey in sorted(groups.keys()):
            items = sorted(groups[gkey], key=lambda p: p.stem)
            title = _group_title(gkey)
            html.append(f'<section class="slide"><h2>Screenshots — {_esc(title)}</h2>')
            html.append("<div class=\"shots\">")
            for pth in items:
                img_tag = inline_img(pth)
                cap = _variant_label(pth)
                html.append("<figure class=\"shot-card\">")
                if img_tag:
                    html.append(img_tag)
                html.append(f'<figcaption class="shot-cap">{_esc(cap)}</figcaption>')
                html.append("</figure>")
            html.append("</div>")
            html.append("</section>")

    # Methodology
    html.append("<section class=\"slide\"><h2>Methodology</h2>")
    html.append("<ul>")
    html.append("<li>Source: SEMrush Organic Positions export (US).</li>")
    html.append("<li>Processing: Polars cleansing; type normalization; date parsing.</li>")
    html.append("<li>Enrichment: position buckets, service taxonomy, intent explosion.</li>")
    html.append("<li>Aggregations: top pages, quick wins (vol×CPC), SERP features.</li>")
    html.append("<li>Reproducibility: scripts/analyze_positions.py regenerates artifacts.</li>")
    html.append("</ul></section>")

    # Why These Keywords
    html.append("<section class=\"slide\"><h2>Why These Keywords</h2>")
    html.append("<ul>")
    html.append("<li>Aligned to high-intent service hubs (web design, SEO, web dev).</li>")
    html.append("<li>Strong demand and monetization signals (volume + CPC).</li>")
    html.append("<li>Already ranking 4–10 → achievable uplift via on-page and internal links.</li>")
    html.append("</ul></section>")

    # Recommendations
    html.append("<section class=\"slide\"><h2>Recommendations</h2>")
    html.append("<h3>On‑page</h3><ul>")
    html.append("<li>Internal link hubs from trends → service pages; FAQ/PAA blocks.</li>")
    html.append("<li>Title/meta rewrites for quick wins; clean H1/H2 hierarchy.</li>")
    html.append("</ul><h3>Off‑page</h3><ul>")
    html.append("<li>Digital PR to lift slipping categories; partner spotlights; awards→hubs.</li>")
    html.append("</ul><h3>Technical</h3><ul>")
    html.append("<li>Canonicalize trends vs. listings; schema (ItemList/Service/FAQ); reduce crawl traps; improve Core Web Vitals.</li>")
    html.append("</ul>")
    html.append("<h3>Out‑of‑the‑Box</h3><ul>")
    html.append("<li>Podcast Intelligence (PodScan.fm): founder interview mining → unique profiles; long‑tail brand/leader coverage.</li>")
    html.append("<li>AI Matching Widget: captures visitor intent; curated shortlists; boosts engagement and lead quality.</li>")
    html.append("</ul></section>")

    # Strategy & Forecast
    html.append("<section class=\"slide\"><h2>Strategy &amp; Forecast</h2>")
    if forecast_summary:
        up_c = int(forecast_summary.get("uplift_clicks", 0))
        up_v = float(forecast_summary.get("uplift_value", 0.0))
        kcnt = int(forecast_summary.get("considered_keywords", 0))
        tgt = int(forecast_summary.get("target_pos", 3))
        html.append(
            f"<p>Move ~{kcnt} quick wins to top‑{tgt}: ≈ {up_c:,} extra clicks/month (value ≈ ${up_v:,.0f}).</p>"
        )
    else:
        html.append("<p>Forecast temporarily unavailable.</p>")
    if forecast_by_service is not None:
        html.append(_table(forecast_by_service, ["service", "uplift_value", "keywords"], max_rows=8))
    html.append("</section>")

    # 3‑Month Plan
    # Build roadmap slide but append it as the final slide later
    roadmap_slide: List[str] = []
    roadmap_slide.append("<section class=\"slide\">")
    roadmap_slide.append("<div class=\"pill\">3‑Month Roadmap</div>")
    roadmap_slide.append("<h2>Execution Plan & KPIs</h2>")
    roadmap_slide.append("<div class=\"roadmap-card\">")
    roadmap_slide.append("<h3>Month 1 – Foundation &amp; Fixes</h3>")
    roadmap_slide.append("<ul>")
    roadmap_slide.append("<li>Canonicalization: consolidate trends vs. listings; fix duplicate titles/meta.</li>")
    roadmap_slide.append("<li>Schema: ItemList/Service/FAQ on priority hubs; validate with Rich Results Test.</li>")
    roadmap_slide.append("<li>Internal Links: build hubs from trends → services (3–5 links/page); add breadcrumbs.</li>")
    roadmap_slide.append("<li>Content Hygiene: rewrite titles/meta for top 50 pages; tighten H1/H2; prune thin pages.</li>")
    roadmap_slide.append("<li>Technical: Core Web Vitals quick wins (LCP/CLS), remove crawl traps; refresh XML sitemaps.</li>")
    roadmap_slide.append("<li>Analytics: dashboards for position buckets, quick wins, services; annotate releases.</li>")
    roadmap_slide.append("</ul>")
    roadmap_slide.append("<h3>Month 2 – Scale &amp; Authority</h3>")
    roadmap_slide.append("<ul>")
    roadmap_slide.append("<li>Local SEO: expand geo pages; interlink to hubs; add LocalBusiness schema where relevant.</li>")
    roadmap_slide.append("<li>Digital PR: pitches for weak services (3–5/wk); link reclamation; thought‑leadership posts.</li>")
    roadmap_slide.append("<li>Refreshes: update top 50 decliners; expand FAQ/PAA on top categories.</li>")
    roadmap_slide.append("<li>Links: systematic internal linking using related trends; add contextual CTAs.</li>")
    roadmap_slide.append("<li>Product: matching widget alpha; instrument events and funnel analytics.</li>")
    roadmap_slide.append("</ul>")
    roadmap_slide.append("<h3>Month 3 – Acceleration &amp; Productization</h3>")
    roadmap_slide.append("<ul>")
    roadmap_slide.append("<li>Launch AI matching MVP; A/B test entry points; promote across high‑traffic pages.</li>")
    roadmap_slide.append("<li>Podcast Intelligence MVP: publish 10 founder profile pages (PodScan.fm); add internal links.</li>")
    roadmap_slide.append("<li>Service Hubs: finalize 5 service clusters with supporting content and lists.</li>")
    roadmap_slide.append("<li>Programmatic SEO: pilot long‑tail use‑cases; templated pages with guardrails.</li>")
    roadmap_slide.append("<li>Advocacy: outreach for testimonials/case studies; add review snippets.</li>")
    roadmap_slide.append("</ul>")
    roadmap_slide.append("<h3>KPIs &amp; Targets</h3>")
    roadmap_slide.append("<ul>")
    roadmap_slide.append("<li>Move 150+ quick‑win keywords to top‑3; +20–30% non‑brand clicks.</li>")
    roadmap_slide.append("<li>+1.5 pp CTR on top pages via titles/meta; +15% sitewide organic sessions.</li>")
    roadmap_slide.append("<li>100+ qualified leads/month from matching widget within 6 weeks of launch.</li>")
    roadmap_slide.append("</ul>")
    roadmap_slide.append("</div>")
    roadmap_slide.append("</section>")
    # Services summary
    html.append("<section class=\"slide\"><h2>Services Summary</h2>")
    html.append(_table(services, ["service", "traffic", "avg_position", "keywords", "improving", "declining"], max_rows=20))
    html.append("</section>")

    # SERP features
    html.append("<section class=\"slide\"><h2>SERP Features</h2>")
    html.append(_table(serp, ["feature", "keywords", "traffic", "top3_share"], max_rows=10))
    html.append("</section>")

    # Geo
    if geo:
        locs = geo.get("geo_locations")
        if locs is not None and isinstance(locs, pl.DataFrame):
            html.append("<section class=\"slide\"><h2>Geo Locations</h2>")
            html.append(_table(locs, ["location", "pages", "traffic"], max_rows=15))
            html.append("</section>")

    # Embed specs and render for only charts that weren't inlined as PNG
    needs_vega = []
    for name in ("position_buckets", "intent_mix", "categories", "services"):
        if not charts or not charts.get(name) or not Path(charts[name]).exists():
            needs_vega.append(name)

    if needs_vega:
        html.append("<script>")
        html.append("const specs = {};")
        for name, spec in specs_inline.items():
            json_str = json.dumps(spec)
            html.append(f"specs['{name}'] = {json_str};")
        for name in needs_vega:
            html.append(
                "vegaEmbed('#chart_" + name + "', specs['" + name + "'], {actions:false});"
            )
        html.append("</script>")

    # Out-of-the-Box Ideas (one idea per slide, parsed from Markdown)
    def find_ideas_md() -> Path | None:
        candidates: List[Path] = []
        try:
            candidates.append(Path.cwd() / "out-of-the-box-ideas.md")
        except Exception:
            pass
        # Also try near repository roots relative to this file
        try:
            here = Path(__file__).resolve()
            for p in list(here.parents)[:5]:
                candidates.append(p / "out-of-the-box-ideas.md")
        except Exception:
            pass
        # Also try two levels above artifacts dir
        candidates.append(Path(base_dir).resolve().parents[1] / "out-of-the-box-ideas.md")
        for c in candidates:
            try:
                if c.exists():
                    return c
            except Exception:
                continue
        return None

    def md_to_blocks(md: str) -> List[str]:
        # Very small Markdown to HTML converter for headings, bold, lists, and paragraphs
        lines = md.splitlines()
        html_blocks: List[str] = []
        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            if not line:
                i += 1
                continue
            if line.startswith("### "):
                html_blocks.append(f"<h3>{_esc(line[4:])}</h3>")
                i += 1
                continue
            if line.startswith("- "):
                items = []
                while i < len(lines) and lines[i].startswith("- "):
                    items.append(lines[i][2:].rstrip())
                    i += 1
                items_html = "".join(f"<li>{inline_md(_esc(it))}</li>" for it in items)
                html_blocks.append(f"<ul>{items_html}</ul>")
                continue
            # Paragraph: gather until blank line or next list/heading
            para = [line]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if not nxt or nxt.startswith("- ") or nxt.startswith("## ") or nxt.startswith("### "):
                    break
                para.append(nxt.rstrip())
                i += 1
            html_blocks.append(f"<p>{inline_md(_esc(' '.join(para)))}</p>")
        return html_blocks

    def inline_md(text: str) -> str:
        # Bold **text**
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)

    ideas_md_path = find_ideas_md()
    if ideas_md_path is not None:
        try:
            md_text = ideas_md_path.read_text(encoding="utf-8")
            # Split into ideas on level-2 headings starting with '## '
            parts: List[Tuple[str, str]] = []  # (title, content)
            current_title: str | None = None
            current_lines: List[str] = []
            for raw_line in md_text.splitlines():
                if raw_line.startswith("## "):
                    # flush previous
                    if current_title is not None:
                        parts.append((current_title, "
".join(current_lines).strip()))
                    # normalize title (strip leading numbers like '1. ')
                    t = raw_line[3:].strip()
                    t = re.sub(r"^\d+\.\s*", "", t)
                    current_title = t
                    current_lines = []
                else:
                    if current_title is not None:
                        current_lines.append(raw_line)
            if current_title is not None:
                parts.append((current_title, "
".join(current_lines).strip()))

            # Render slides for each idea
            for (title, content) in parts:
                if not title.strip():
                    continue
                blocks = md_to_blocks(content)
                html.append("<section class=\"slide\">")
                html.append("<div class=\"pill\">Out‑of‑the‑Box Idea</div>")
                html.append(f"<h2>{_esc(title)}</h2>")
                html.append("<div class=\"idea idea-card\">")
                for b in blocks:
                    html.append(b)
                html.append("</div>")
                html.append("</section>")
        except Exception:
            # If parsing fails, silently skip rendering ideas
            pass

    # Finally, append the roadmap slide as the last slide
    if 'roadmap_slide' in locals() and roadmap_slide:
        html.extend(roadmap_slide)

    # Navigation controls + slide logic
    html.append(
        "<div class=\"nav\"><div class=\"nav-inner\">"
        "<button id=\"prevBtn\" class=\"btn\" aria-label=\"Previous\">Prev</button>"
        "<span class=\"counter\" id=\"counter\">1 / 1</span>"
        "<button id=\"nextBtn\" class=\"btn\" aria-label=\"Next\">Next</button>"
        "<button id=\"themeBtn\" class=\"btn btn--ghost\" aria-label=\"Toggle theme\">Theme</button>"
        "</div></div><div class=\"progress\"><div class=\"bar\" id=\"bar\"></div></div>"
    )
    html.append("</main>")
    html.append(
        "<script>"
        "(function(){
"
        "document.body.classList.add('js');const slides=[...document.querySelectorAll('.slide')];
"
        "let idx = 0;
"
        "const params=new URLSearchParams(location.search);
"
        "if(params.get('print')==='1'){document.body.classList.add('print')}
"
        "const THEME_KEY='deck.theme';
"
        "try{const saved=localStorage.getItem(THEME_KEY);if(saved==='light'){document.body.classList.add('light')}}catch(e){}
"
        "function parseHash(){const h=location.hash.replace('#','');if(!h) return 0;const n=parseInt(h.replace('slide-',''))||parseInt(h);return isNaN(n)?0:Math.max(0,Math.min(slides.length-1,(n-1)));}
"
        "function setHash(i){const h='#'+(i+1);if(location.hash!==h){history.replaceState(null,'',h)}}
"
        "const prev=document.getElementById('prevBtn');const next=document.getElementById('nextBtn');const counter=document.getElementById('counter');const bar=document.getElementById('bar');const themeBtn=document.getElementById('themeBtn');
"
        "function progress(i){if(!bar)return;const p=slides.length<=1?1:(i/(slides.length-1));bar.style.width=(p*100)+'%'}
"
        "function show(i){slides.forEach((s,j)=>{if(j===i){s.classList.add('current')}else{s.classList.remove('current')}});idx=i;setHash(i);prev.disabled = (i===0);next.disabled = (i===slides.length-1);counter.textContent=(i+1)+' / '+slides.length;progress(i)}
"
        "function go(delta){const n=Math.max(0,Math.min(slides.length-1,idx+delta));if(n!==idx) show(n);}
"
        "function onKey(e){const k=e.key;if(k==='ArrowRight'||k==='PageDown'||k===' '){go(1);e.preventDefault()}else if(k==='ArrowLeft'||k==='PageUp'){go(-1);e.preventDefault()}}
"
        "if(prev) prev.addEventListener('click',()=>go(-1)); if(next) next.addEventListener('click',()=>go(1)); window.addEventListener('keydown',onKey); window.addEventListener('hashchange',()=>{const n=parseHash();show(n)});
"
        "if(themeBtn){themeBtn.addEventListener('click',()=>{document.body.classList.toggle('light');try{localStorage.setItem(THEME_KEY,document.body.classList.contains('light')?'light':'dark')}catch(e){}})}
"
        "/* Zoom overlay for screenshots */
"
        "const zoom=document.createElement('div');zoom.className='zoom';zoom.innerHTML='<img alt=\\"zoom\\">';document.body.appendChild(zoom);zoom.addEventListener('click',()=>{zoom.style.display='none'});
"
        "document.addEventListener('click',e=>{const t=e.target;if(t && t.tagName==='IMG' && t.closest('.shot-card')){zoom.querySelector('img').src=t.src;zoom.style.display='flex'}});
"
        "show(parseHash());
"
        "})();
"
        "</script>"
    )

    html.append("</body></html>")
    out.write_text("
".join(html), encoding="utf-8")
    return out
