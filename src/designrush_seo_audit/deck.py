from __future__ import annotations

from pathlib import Path
from typing import Dict

import polars as pl


def write_deck(
    base_dir: Path,
    overview: dict,
    charts: Dict[str, Path],
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
    deck_path = Path(base_dir) / "deck.md"

    total_kw = overview["total_keywords"]
    total_traffic = overview["traffic"]
    total_cost = overview["traffic_cost"]
    avg_pos = overview["avg_position"]

    def _img(name: str) -> str:
        p = charts.get(name)
        return f"![{name}]({p.name})" if p and p.exists() else ""

    with deck_path.open("w", encoding="utf-8") as f:
        # Title
        f.write("# DesignRush SEO Audit – Deck Outline\n\n")

        # Scope & Approach (Task 1)
        f.write("## Scope & Approach (Task 1)\n")
        f.write("- Section audited: Agency Directory (primary traffic and value driver).\n")
        f.write("- Source data: SEMrush Organic Positions (US) export + repo transformations.\n")
        f.write(
            "- Method: classify ranking URLs by `url_category` and `service`; aggregate traffic/value, positions, intent, and SERP features; surface quick‑wins (positions 4–10).\n"
        )
        f.write(
            "- Why Agency Directory: it captures the majority of traffic and aligns directly to marketplace goals.\n\n"
        )

        # Executive Summary
        f.write("## Executive Summary\n")
        f.write(f"- {total_kw:,} tracked keywords; avg position {avg_pos:.2f}.\n")
        f.write(f"- Est. monthly traffic ≈ {total_traffic:,.0f}; value ≈ ${total_cost:,.0f}.\n")
        # Top traffic URLs
        top_urls = top_pages.head(5).select(["URL", "traffic", "avg_position"]).iter_rows()
        for url, tr, ap in top_urls:
            f.write(f"- Top page: {url} → {tr:,.0f} visits (avg pos {ap:.2f})\n")
        # Traffic concentration (top 10/20 pages)
        try:
            t10 = float(top_pages.select(pl.col("traffic").head(10).sum()).item())
            t20 = float(top_pages.select(pl.col("traffic").head(20).sum()).item())
            share10 = t10 / total_traffic if total_traffic else 0.0
            share20 = t20 / total_traffic if total_traffic else 0.0
            f.write(
                f"- Traffic concentration: top 10 pages ≈ {share10:.1%} of total; top 20 ≈ {share20:.1%}.\n"
            )
        except Exception:
            pass
        f.write("\n")

        # Rankings Overview
        f.write("## Rankings Overview\n")
        f.write("- Distribution by position bucket:\n\n")
        f.write(_img("position_buckets") + "\n\n")
        # Narrative on buckets (data-derived)
        try:
            byb = overview.get("by_bucket")
            if isinstance(byb, pl.DataFrame):
                byb_d = byb.to_dict(as_series=False)
                share_map = {b: s for b, s in zip(byb_d["pos_bucket"], byb_d["share"])}
                top3 = share_map.get("01-03")
                win = share_map.get("04-10")
                if top3 is not None and win is not None:
                    f.write(
                        f"- Commentary: ~{top3:.1%} of keywords already sit in top‑3, and ~{win:.1%} are in 4–10 → strong quick‑win runway to push into top‑3.\n\n"
                    )
        except Exception:
            pass

        # Intent Mix
        f.write("## Intent Mix\n")
        f.write(_img("intent_mix") + "\n")
        try:
            # Compute traffic shares for key intents
            it = intents.select(["Keyword Intents", "traffic"]).to_dict(as_series=False)
            total_int_traffic = sum(float(x or 0.0) for x in it.get("traffic", [])) or 0.0
            if total_int_traffic > 0:
                shares = {
                    k: (float(t) / total_int_traffic)
                    for k, t in zip(it.get("Keyword Intents", []), it.get("traffic", []))
                }
                # Order for readability
                order = ["commercial", "informational", "transactional", "navigational"]
                vals = [f"{k} ~{shares.get(k, 0.0):.0%}" for k in order if k in shares]
                if vals:
                    f.write("- Traffic share: " + ", ".join(vals) + ".\n")
                f.write(
                    "- Opportunity: grow transactional share with geo/near‑me, pricing/cost, and comparison queries into hubs.\n\n"
                )
                f.write(
                    "- Why included: calibrates our content/keyword balance.\n"
                    "- Story: strong commercial coverage but thin transactional demand → add bottom‑funnel angles (near‑me, cost, compare) to convert.\n\n"
                )
        except Exception:
            f.write("\n")

        # Categories & Services
        f.write("## Categories & Services\n")
        f.write("- Coarse categories by traffic:\n\n")
        f.write(_img("categories") + "\n")
        try:
            cats = categories.select(["url_category", "traffic"]).to_dict(as_series=False)
            # Normalize to a consistent order if present
            cat_map = {k: float(v) for k, v in zip(cats["url_category"], cats["traffic"])}
            parts = []
            for k in ("agency", "trends", "geo", "other"):
                if k in cat_map:
                    parts.append(f"{k}: {cat_map[k]:,.0f}")
            if parts:
                f.write("- " + " • ".join(parts) + ".\n")
        except Exception:
            pass
        f.write("\n- Services by traffic (top 12):\n\n")
        f.write(_img("services") + "\n")
        try:
            sv = services.select(["service", "traffic"]).to_dict(as_series=False)
            traf = [float(x) for x in sv.get("traffic", [])]
            ttl = sum(traf) or 0.0
            if ttl > 0 and traf:
                # Share of top 4
                top4_share = sum(sorted(traf, reverse=True)[:4]) / ttl
                f.write(f"- Top 4 services ≈ {top4_share:.0%} of service traffic.\n")
                f.write(
                    "- Commentary: performance concentrates in a handful of service hubs → protect these pages and lift mid‑tier hubs with internal links and FAQs.\n\n"
                )
        except Exception:
            f.write("\n")

        # SERP Features
        f.write("## SERP Features\n")
        top_serp = serp.head(5).iter_rows()
        for feat, kws, tr, top3 in top_serp:
            f.write(f"- {feat}: {kws} keywords; {tr:,.0f} traffic; top‑3 share {top3:.0%}.\n")
        f.write("- Takeaway: double down on PAA/FAQ modules, local signals, and short video snippets; prepare for AI Overview with tight entity/Q&A coverage.\n")
        f.write(
            "- Why included: identifies SERP surfaces we can actively target (PAA, Local Pack, Video, AIO).\n"
            "- Story: we already appear across these surfaces — adding FAQs, schema, and short videos lifts visibility and CTR.\n\n"
        )

        # Keywords We Target (Task 1)
        f.write("## Keywords We Target (Task 1)\n")
        try:
            # Prefer agency directory quick wins as examples
            q_example = (
                quick_wins.filter(pl.col("url_category") == "agency")
                .select(["Keyword", "Position", "Search Volume", "URL"])
                .head(5)
            )
            for kw, pos, vol, url in q_example.iter_rows():
                f.write(f"- {kw} (pos {pos}, vol {vol:,}) → {url}\n")
        except Exception:
            pass
        f.write(
            "- Full lists in this folder: top_keywords_by_traffic.csv and services/top_keywords_*.csv.\n\n"
        )
        f.write(
            "- Why included: ground the scope with concrete, high‑intent examples.\n"
            "- Story: agency directory pages already rank — we refine on‑page and internal links to capture top‑3 and convert.\n\n"
        )

        # Quick Wins
        f.write("## Quick Wins (4–10)\n")
        for kw, vol, cpc, pos, url in quick_wins.select(["Keyword", "Search Volume", "CPC", "Position", "URL"]).head(10).iter_rows():
            f.write(f"- {kw}: vol {vol:,}, CPC ${cpc:,.2f}, pos {pos} → {url}\n")
        try:
            total_qw = int(quick_wins.height)
            total_pri = float(quick_wins.select(pl.sum("priority")).item() or 0.0) if "priority" in quick_wins.columns else 0.0
            # Top services by priority within quick wins
            if "service" in quick_wins.columns:
                svc_sum = (
                    quick_wins.group_by("service")
                    .agg(pl.sum("priority").alias("pri")).sort("pri", descending=True).head(3)
                )
                svc_list = ", ".join(f"{s}" for s, _ in svc_sum.iter_rows())
            else:
                svc_list = ""
            f.write(
                f"- Commentary: {total_qw} quick‑win keywords identified; priority sum ≈ {total_pri:,.0f}. Top services to lift: {svc_list}.\n"
            )
        except Exception:
            pass
        f.write(
            "- Playbook: service hubs → refresh H1/H2, add comparison/cost blocks, FAQs; trends → hub funnels with 4–6 contextual links; geo pages → local proof + LocalBusiness schema.\n\n"
        )

        # Screenshots (auto-include if available)
        shots_dir = Path(base_dir) / "screenshots"
        exts = {".png", ".jpg", ".jpeg", ".webp"}
        if shots_dir.exists():
            shots = sorted([p for p in shots_dir.iterdir() if p.suffix.lower() in exts])
            if shots:
                f.write("## Screenshots\n")
                for p in shots[:12]:
                    f.write(f"![{p.stem}]({p.as_posix()})\n\n")
                f.write(
                    "- Why included: show current UX templates that drive rankings (category, directory, geo).\n"
                    "- Story: ties on‑page recommendations (FAQs, CTAs, links) to real UI elements to ship.\n\n"
                )

        # Methodology
        f.write("## Methodology\n")
        f.write("- Source: SEMrush Organic Positions export (US).\n")
        f.write("- Processing: Polars-based cleansing; type normalization; date parsing.\n")
        f.write("- Enrichment: position buckets, service taxonomy mapping, intent explosion.\n")
        f.write("- Aggregations: top pages, quick wins (4–10) prioritized by volume×CPC, SERP features presence.\n")
        f.write("- Reproducibility: scripts/analyze_positions.py regenerates all artifacts.\n\n")

        # Process Details (Task 1)
        f.write("## Process Details (Task 1)\n")
        f.write("- Map Agency Directory URLs (`/agency/...`) to services and intents.\n")
        f.write(
            "- Filter ranking keywords; group by intent, volume, CPC, and current position; flag 4–10 as quick wins.\n"
        )
        f.write(
            "- Validate against top pages and SERP feature presence to attach on‑page tactics (FAQ/PAA, local pack, video, AIO coverage).\n\n"
        )

        # Why These Keywords
        f.write("## Why These Keywords\n")
        f.write("- Align with high‑intent service hubs (e.g., web design, SEO, web dev).\n")
        f.write("- Strong demand × monetization signals (volume and CPC).\n")
        f.write(
            "- Existing relevance (already ranking 4–10), indicating achievable uplift with on‑page/internal links.\n\n"
        )

        # Recommendations
        f.write("## Recommendations\n")
        f.write(
            "- On‑page: strengthen internal links from trends→service hubs; add FAQ/PAA blocks on category and geo pages; refine titles/meta for quick wins; ensure clean H1/H2 hierarchy.\n"
        )
        f.write(
            "- Off‑page: targeted digital PR to support slipping services; partner spotlights; leverage awards pages to attract authority links to hubs.\n"
        )
        f.write(
            "- Technical: canonicalize trends vs. listing overlaps; ensure ItemList/Service/FAQ schema; reduce crawl traps (filters/params); improve LCP/CLS on templates.\n"
        )
        f.write(
            "- SERP features: concise explainer videos, PAA‑friendly FAQs, LocalBusiness schema; prepare Q&A content to improve AI Overview inclusion.\n\n"
        )

        # Title & Header A/B testing (optional one-off notes)
        try:
            ab_path = Path(base_dir) / "ab_testing_titles_headers.md"
            if ab_path.exists():
                f.write("## Title & Header A/B Testing (CTAs)\n\n")
                f.write(ab_path.read_text(encoding="utf-8") + "\n")
        except Exception:
            pass

        # Out‑of‑the‑Box Ideas
        f.write("## Out‑of‑the‑Box Ideas\n")
        f.write(
            "- Podcast Intelligence: founder interview mining → unique agency profiles; long‑tail brand/leader keywords; authoritative insights.\n"
        )
        f.write(
            "- AI Matching Widget: capture visitor intent and produce curated agency shortlists; boosts engagement, lead quality, and internal linking utilization.\n"
        )
        f.write(
            "- Awards Synergy: use awards pages as internal‑link engines to service/geo hubs; add Award schema to attract snippet/news coverage.\n\n"
        )

        # Analyst Insights (optional one-off notes)
        insights_path = Path(base_dir) / "analyst_insights.md"
        if insights_path.exists():
            f.write("\n## Analyst Insights (One‑off Audit)\n\n")
            try:
                f.write(insights_path.read_text(encoding="utf-8") + "\n")
            except Exception:
                # Fail silent – keep deck generation resilient
                pass

        # Dedicated Internal Linking section if present in insights
        try:
            if insights_path.exists():
                raw = insights_path.read_text(encoding="utf-8")
                lines = raw.splitlines()
                target = "## Internal Linking — Contextual vs. Navigational"
                capture = False
                extracted: list[str] = []
                for ln in lines:
                    if ln.startswith("## "):
                        if capture:
                            break
                        if ln.strip() == target:
                            capture = True
                            continue
                    if capture:
                        extracted.append(ln)
                if extracted:
                    f.write("\n## Internal Linking — Contextual vs. Navigational\n\n")
                    f.write("\n".join(extracted) + "\n\n")
        except Exception:
            pass

        # Also include a separate internal_linking.md if provided
        try:
            il_path = Path(base_dir) / "internal_linking.md"
            if il_path.exists():
                f.write("\n## Internal Linking — Contextual vs. Navigational\n\n")
                f.write(il_path.read_text(encoding="utf-8") + "\n")
        except Exception:
            pass

        # Strategy & Forecast
        f.write("## Strategy & Forecast\n")
        if forecast_summary:
            up_c = forecast_summary.get("uplift_clicks", 0.0)
            up_v = forecast_summary.get("uplift_value", 0.0)
            kcnt = forecast_summary.get("considered_keywords", 0)
            tgt = forecast_summary.get("target_pos", 3)
            f.write(
                f"- Move ~{kcnt} quick wins to top‑{tgt}: ≈ {up_c:,.0f} extra clicks/mo (value ≈ ${up_v:,.0f}).\n"
            )
        else:
            f.write("- Forecast temporarily unavailable (insufficient data).\n")
        if forecast_by_service is not None:
            f.write("- Top services by uplift value:\n")
            for svc, val in forecast_by_service.select(["service", "uplift_value"]).head(5).iter_rows():
                f.write(f"  - {svc}: ${val:,.0f}\n")
        # Geo opportunity backlog
        try:
            geo_qw = geo.get("geo_quick_wins") if geo else None
            if geo_qw is not None and "priority" in geo_qw.columns:
                total_pri = float(geo_qw.select(pl.sum("priority")).item() or 0.0)
                f.write(
                    f"- Geo quick‑wins backlog (vol×CPC priority sum): ≈ {total_pri:,.0f}. Focus on tier‑1 cities first.\n"
                )
        except Exception:
            pass
        f.write("\n")
        f.write(
            "- Why included: quantify upside to prioritize effort.\n"
            "- Story: moving positions 4–10 into top‑3 on high‑value services is the fastest lever for traffic and value.\n\n"
        )

        # 3‑Month Plan
        f.write("## 3‑Month Roadmap\n")
        f.write(
            "- Month 1: fix technical canonicals/schema, implement internal‑link hubs, add FAQs on top 20 categories, rescue decliners.\n"
        )
        f.write(
            "- Month 2: scale local SEO (geo internal links, local schema, city proof points), focused PR to 3 weak services, content refreshes.\n"
        )
        f.write(
            "- Month 3: launch AI matching MVP, pilot founder podcast profiles for 50 agencies, expand trends→hub funnels; iterate on gains.\n"
        )

        # Measurement & KPIs (Task 3)
        f.write("\n## Measurement & KPIs (Task 3)\n")
        f.write(
            "- Rank: number of quick‑wins moved to top‑3 by service/geo; top‑3 share on queries with PAA/Local/Video/AIO features.\n"
        )
        f.write(
            "- Traffic: incremental clicks/mo from quick‑wins; geo clicks by city; CTR on hubs post FAQ/video additions.\n"
        )
        f.write(
            "- Quality: leads per session on hubs; AI‑matching engagement; indexation/canonical coverage on listings and trends.\n"
        )
        f.write(
            "- Cadence: weekly keyword movement; bi‑weekly template health (CWV, schema); monthly geo/service expansion scorecard.\n\n"
        )

        # Risks & Declines
        f.write("## Risks & Declines\n")
        # Services with most declining rows
        svc_risk = services.select(["service", "declining"]).sort("declining", descending=True).head(8)
        for svc, cnt in svc_risk.iter_rows():
            f.write(f"- {svc}: {cnt} declining keywords\n")
        # Highlight a couple of lowest‑performing services by avg position
        try:
            worst = services.select(["service", "avg_position"]).sort("avg_position", descending=True).head(2)
            names = [f"{s} (avg pos {ap:.1f})" for s, ap in worst.iter_rows()]
            if names:
                f.write("- Focus rescues: " + ", ".join(names) + ".\n")
        except Exception:
            pass
        f.write("\n")
        f.write(
            "- Why included: protect the base to avoid negative drift that cancels gains.\n"
            "- Story: triage weak services with refreshes and links while we push quick‑wins.\n\n"
        )

        # Next Steps
        f.write("## Next Steps\n")
        f.write("- Prioritize high‑CPC quick wins via internal linking and on‑page tuning.\n")
        f.write("- Refresh declining service pages; add FAQs to capture PAA.\n")
        f.write("- Strengthen local signals for 'near me' and geo variants.\n")
        f.write("- Expand trends content with clear CTAs into listing pages.\n")
        f.write(
            "- Add hreflang and localized proof to top country hubs; implement Award schema and cross‑linking; ship short explainer videos on top hubs.\n"
        )

        # Geo Report
        if geo:
            f.write("\n## Geo Report\n")
            locs = geo.get("geo_locations")
            if locs is not None:
                head = locs.head(10)
                for location, pages, tr in head.iter_rows():
                    f.write(f"- {location}: {pages} pages; {tr:,.0f} traffic\n")
                try:
                    top3 = [f"{loc} ({tr:,.0f})" for loc, _, tr in head.head(3).iter_rows()]
                    if top3:
                        f.write("- Commentary: focus top cities → " + ", ".join(top3) + ".\n")
                except Exception:
                    pass
                f.write(
                    "- Why included: local is the closest proxy for transactional intent (‘near me’, city modifiers).\n"
                    "- Story: prioritize top cities with local proof, schema, and internal links to lift conversions.\n"
                )
            f.write("\n- See geo_top_pages.csv, geo_quick_wins.csv, geo_wins.csv, geo_losses.csv for details.\n")

        # Appendix: How to use Vega-Lite specs
        f.write("\n## Appendix: Charts\n")
        f.write(
            "- Vega-Lite JSON specs are written to charts/vega/*.json — importable in the Vega Editor or Observable.\n"
        )

    return deck_path
