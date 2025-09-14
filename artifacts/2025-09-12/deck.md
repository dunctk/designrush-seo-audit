# DesignRush SEO Audit – Deck Outline

## Scope & Approach (Task 1)
- Section audited: Agency Directory (primary traffic and value driver).
- Source data: SEMrush Organic Positions (US) export + repo transformations.
- Method: classify ranking URLs by `url_category` and `service`; aggregate traffic/value, positions, intent, and SERP features; surface quick‑wins (positions 4–10).
- Why Agency Directory: it captures the majority of traffic and aligns directly to marketplace goals.

## Executive Summary
- 10,000 tracked keywords; avg position 5.18.
- Est. monthly traffic ≈ 80,031; value ≈ $755,278.
- Top page: https://www.designrush.com/agency/website-design-development → 8,824 visits (avg pos 3.94)
- Top page: https://www.designrush.com/agency/web-development-companies → 7,010 visits (avg pos 2.69)
- Top page: https://www.designrush.com/agency/profile/digitad → 2,228 visits (avg pos 2.50)
- Top page: https://www.designrush.com/agency/digital-marketing → 2,146 visits (avg pos 6.27)
- Top page: https://www.designrush.com/agency/search-engine-optimization → 1,535 visits (avg pos 9.08)
- Traffic concentration: top 10 pages ≈ 32.5% of total; top 20 ≈ 38.5%.

## Rankings Overview
- Distribution by position bucket:



- Commentary: ~49.7% of keywords already sit in top‑3, and ~38.7% are in 4–10 → strong quick‑win runway to push into top‑3.

## Intent Mix

- Traffic share: commercial ~58%, informational ~36%, transactional ~4%, navigational ~2%.
- Opportunity: grow transactional share with geo/near‑me, pricing/cost, and comparison queries into hubs.

- Why included: calibrates our content/keyword balance.
- Story: strong commercial coverage but thin transactional demand → add bottom‑funnel angles (near‑me, cost, compare) to convert.

## Categories & Services
- Coarse categories by traffic:


- agency: 63,849 • trends: 3,583 • geo: 2,641 • other: 9,958.

- Services by traffic (top 12):


- Top 4 services ≈ 67% of service traffic.
- Commentary: performance concentrates in a handful of service hubs → protect these pages and lift mid‑tier hubs with internal links and FAQs.

## SERP Features
- Sitelinks: 7549 keywords; 66,345 traffic; top‑3 share 49%.
- Video: 5325 keywords; 51,698 traffic; top‑3 share 47%.
- Local pack: 5145 keywords; 38,886 traffic; top‑3 share 52%.
- Image pack: 3622 keywords; 32,397 traffic; top‑3 share 49%.
- AI overview: 4158 keywords; 31,923 traffic; top‑3 share 60%.
- Takeaway: double down on PAA/FAQ modules, local signals, and short video snippets; prepare for AI Overview with tight entity/Q&A coverage.
- Why included: identifies SERP surfaces we can actively target (PAA, Local Pack, Video, AIO).
- Story: we already appear across these surfaces — adding FAQs, schema, and short videos lifts visibility and CTR.

## Keywords We Target (Task 1)
- app (pos 4, vol 301,000) → https://www.designrush.com/agency/mobile-app-design-development/trends/mobile-app-development-software
- app (pos 4, vol 301,000) → https://www.designrush.com/agency/mobile-app-design-development/trends/mobile-application-development-platform
- seo agency near me (pos 7, vol 12,100) → https://www.designrush.com/agency/search-engine-optimization
- logo (pos 6, vol 135,000) → https://www.designrush.com/agency/logo-design/trends/what-is-logo-design
- web development company (pos 7, vol 12,100) → https://www.designrush.com/agency/web-development-companies
- Full lists in this folder: top_keywords_by_traffic.csv and services/top_keywords_*.csv.

- Why included: ground the scope with concrete, high‑intent examples.
- Story: agency directory pages already rank — we refine on‑page and internal links to capture top‑3 and convert.

## Quick Wins (4–10)
- app: vol 301,000, CPC $3.15, pos 4 → https://www.designrush.com/agency/mobile-app-design-development/trends/mobile-app-development-software
- app: vol 301,000, CPC $3.15, pos 4 → https://www.designrush.com/agency/mobile-app-design-development/trends/mobile-application-development-platform
- gg ads: vol 14,800, CPC $27.25, pos 6 → https://www.designrush.com/agency/paid-media-pay-per-click/google-adwords/trends/google-ads-costs
- seo agency near me: vol 12,100, CPC $19.76, pos 7 → https://www.designrush.com/agency/search-engine-optimization
- logo: vol 135,000, CPC $1.49, pos 6 → https://www.designrush.com/agency/logo-design/trends/what-is-logo-design
- web development company: vol 12,100, CPC $14.89, pos 7 → https://www.designrush.com/agency/web-development-companies
- ppc company: vol 5,400, CPC $32.98, pos 8 → https://www.designrush.com/agency/paid-media-pay-per-click
- web design agency: vol 18,100, CPC $9.43, pos 7 → https://www.designrush.com/agency/website-design-development
- social media marketing agency: vol 18,100, CPC $8.72, pos 8 → https://www.designrush.com/agency/social-media-marketing/trends/paid-social-media-advertising
- hr outsourcing: vol 5,400, CPC $29.10, pos 6 → https://www.designrush.com/agency/hr-outsourcing
- Commentary: 200 quick‑win keywords identified; priority sum ≈ 10,180,609. Top services to lift: mobile_app, ppc, seo.
- Playbook: service hubs → refresh H1/H2, add comparison/cost blocks, FAQs; trends → hub funnels with 4–6 contextual links; geo pages → local proof + LocalBusiness schema.

## Screenshots
![03-category-seo__desktop](artifacts/2025-09-12/screenshots/03-category-seo__desktop.png)

- Why included: show current UX templates that drive rankings (category, directory, geo).
- Story: ties on‑page recommendations (FAQs, CTAs, links) to real UI elements to ship.

## Methodology
- Source: SEMrush Organic Positions export (US).
- Processing: Polars-based cleansing; type normalization; date parsing.
- Enrichment: position buckets, service taxonomy mapping, intent explosion.
- Aggregations: top pages, quick wins (4–10) prioritized by volume×CPC, SERP features presence.
- Reproducibility: scripts/analyze_positions.py regenerates all artifacts.

## Process Details (Task 1)
- Map Agency Directory URLs (`/agency/...`) to services and intents.
- Filter ranking keywords; group by intent, volume, CPC, and current position; flag 4–10 as quick wins.
- Validate against top pages and SERP feature presence to attach on‑page tactics (FAQ/PAA, local pack, video, AIO coverage).

## Why These Keywords
- Align with high‑intent service hubs (e.g., web design, SEO, web dev).
- Strong demand × monetization signals (volume and CPC).
- Existing relevance (already ranking 4–10), indicating achievable uplift with on‑page/internal links.

## Recommendations
- On‑page: strengthen internal links from trends→service hubs; add FAQ/PAA blocks on category and geo pages; refine titles/meta for quick wins; ensure clean H1/H2 hierarchy.
- Off‑page: targeted digital PR to support slipping services; partner spotlights; leverage awards pages to attract authority links to hubs.
- Technical: canonicalize trends vs. listing overlaps; ensure ItemList/Service/FAQ schema; reduce crawl traps (filters/params); improve LCP/CLS on templates.
- SERP features: concise explainer videos, PAA‑friendly FAQs, LocalBusiness schema; prepare Q&A content to improve AI Overview inclusion.

## Title & Header A/B Testing (CTAs)

# A/B Testing Titles & Headers for Better CTAs

Use SEOTesting.com to run safer, controlled tests of Title/H1/H2 changes on “quick win” pages. Principle:
*   Title Tag = your ad on Google. Include the keyword, be compelling, earn the click.
*   H1 Tag = your on‑page welcome. Confirm the topic and user intent.
*   H2/H3 Tags = your outline. Structure related questions and variants logically.

---

## Example 1: SEO Agency Page
*   URL: `/agency/search-engine-optimization`
*   Target Quick Win Keyword: `seo agency near me` (Position 7)

### Current Tags
*   Title: Top SEO Agencies - Sep 2025 Rankings | DesignRush
*   H1: Top SEO Agencies

### Video‑Enhanced Recommendations
*   Proposed Title:
    Find Vetted SEO Agencies Near You | 2025 Directory | DesignRush
    *   Why: matches “Near You” intent; “Vetted” is a strong trust signal for CTR.
*   Proposed H1:
    Top SEO Agencies
    *   Why: clear and strong; reinforce with H2s that capture local intent.
*   Proposed H2/H3 structure:
    *   How to Choose the Right SEO Agency for Your Business (H2)
    *   Top SEO Agencies by Location (H2)
        *   Top SEO Agencies in New York (H3)
        *   Top SEO Agencies in Los Angeles (H3)
        *   Top SEO Agencies in Chicago (H3)
    *   How Much Do SEO Agencies Cost in 2025? (H2)
    *   Frequently Asked Questions About SEO Services (H2)
        *   Are SEO agencies worth it? (H3)
        *   What KPIs should I track with an SEO agency? (H3)

---

## Example 2: Web Development Page
*   URL: `/agency/web-development-companies`
*   Target Quick Win Keyword: `web development company` (Position 7)

### Current Tags
*   Title: Top Web Development Companies - Sep 2025 Rankings | DesignRush
*   H1: Top Web Development Companies

### Video‑Enhanced Recommendations
*   Proposed Title:
    Top Web Development Companies for Custom Projects (2025) | DesignRush
    *   Why: “Custom Projects” appeals to higher‑intent users; more benefit‑driven.
*   Proposed H1:
    Find the Best Web Development Company for Your Needs
    *   Why: more user‑centric and action‑oriented; matches hiring intent.
*   Proposed H2/H3 structure:
    *   What Does a Web Development Company Do? (H2)
    *   Web Development Services by Specialty (H2)
        *   E‑commerce Development Companies (H3)
        *   Custom Software Development Firms (H3)
        *   B2B Web Development Specialists (H3)
    *   Average Web Development Costs (H2)
    *   Web Development Company FAQs (H2)

---

## Example 3: PPC Company Page
*   URL: `/agency/paid-media-pay-per-click`
*   Target Quick Win Keyword: `ppc company` (Position 8)

### Current Tags
*   Title: Top Pay Per Click (PPC) Agencies - Sep 2025 Rankings | DesignRush
*   H1: Top Pay Per Click (PPC) Agencies

### Video‑Enhanced Recommendations
*   Proposed Title:
    Top PPC Companies That Deliver ROI | Hire a PPC Expert | DesignRush
    *   Why: emphasizes commercial intent and outcomes (ROI); adds a strong CTA.
*   Proposed H1:
    Find a Top‑Rated PPC Management Company
    *   Why: includes “PPC Management” phrasing and trust signal “Top‑Rated”.
*   Proposed H2/H3 structure:
    *   What to Expect When Working With a PPC Company (H2)
    *   Compare PPC Management Pricing & Models (H2)
    *   Top PPC Companies by Platform (H2)
        *   Google Ads Management Agencies (H3)
        *   Social Media Advertising Companies (H3)
    *   Questions to Ask Before Hiring a PPC Company (H2)

---

## How to Test with SEOTesting.com
*   Choose 3–5 “quick win” pages per service (positions 4–10) and set up title experiments (A vs B) and H1/H2 content tests.
*   Run each test for at least 21–28 days (or 2× business cycles) with seasonality controls.
*   Measure: impressions, CTR, average position, clicks; annotate wins and promote winners site‑wide.
*   Safety: ship changes behind feature flags in the CMS; revert quickly if CTR/pos dip.

## Out‑of‑the‑Box Ideas
- Podcast Intelligence: founder interview mining → unique agency profiles; long‑tail brand/leader keywords; authoritative insights.
- AI Matching Widget: capture visitor intent and produce curated agency shortlists; boosts engagement, lead quality, and internal linking utilization.
- Awards Synergy: use awards pages as internal‑link engines to service/geo hubs; add Award schema to attract snippet/news coverage.


## Analyst Insights (One‑off Audit)

# Narrative Summary
- Agency Directory is the growth engine: agency pages account for ~80% of tracked traffic, and the top 10 pages drive ≈32.5% of total organic volume. Lift mid‑tier service hubs and geo pages to reduce concentration risk while protecting top hubs.
- Commercial intent dominates but transactional is thin: commercial ~58% vs. transactional ~4–5%. The highest upside is in “company/agency near me” and high‑CPC service terms (e.g., PPC, SEO, web dev). Prioritize quick wins in 4–10 to reach top‑3.
- SERP features are leverage: heavy presence of PAA and Local Pack; AI Overview and Video also appear frequently. Add PAA‑oriented FAQs, LocalBusiness schema on geo pages, and short explainer videos on top hubs to capture these surfaces.

## Handpicked Quick‑Win Shortlist (Impact‑First)
- seo agency near me — pos 7, vol 12,100, CPC $19.76 → /agency/search-engine-optimization
- web development company — pos 7, vol 12,100, CPC $14.89 → /agency/web-development-companies
- ppc company — pos 8, vol 5,400, CPC $32.98 → /agency/paid-media-pay-per-click
- google ads agencies — pos 10, vol 390, CPC $33.78 → /agency/paid-media-pay-per-click/google-adwords
- web design agency — pos 7, vol 18,100, CPC $9.43 → /agency/website-design-development
- Optional (non‑core but high CPC): hr outsourcing — pos 6, vol 5,400, CPC $29.10 → /agency/hr-outsourcing

## Template‑Level Actions to Ship
- Service hubs: align Title/H1 with primary query + variants; add comparison (“agency vs freelancer”), price ranges, top FAQs; surface top agencies with exact/partial‑match anchors.
- Trends → hub funnels: for trends pages ranking in 4–5 (e.g., “app” queries), add above‑the‑fold CTA and 4–6 contextual internal links to the related service hub and key geos.
- Geo pages: add local proof points (clients, awards, testimonials), city‑specific FAQs, LocalBusiness schema; cross‑link up/down the geo hierarchy.

## Hypotheses & Tests
- PAA expansion lifts CTR: adding 3–5 Q&As to top hubs increases PAA presence and CTR on keywords already showing PAA. Measure top‑3 share and CTR on PAA‑bearing terms.
- Trend→Hub internal links move 1–2 positions: adding 4–6 contextual links from related trends pages to their service hubs improves “company” queries (4–10 → 1–3). Track rank deltas on the linked cluster.
- Short videos earn carousel/AI inclusion: 60–90s “what/why/cost” clips on top hubs increase Video carousel visibility and help AI Overview quoting. Track video presence and CTR deltas.

## Risks & Mitigations
- Decliners to triage: video (avg pos ~7.6) and mobile_app have notable declines; schedule content refreshes and add FAQs/videos. Maintain weekly watchlist for services with >5 declining keywords.
- Concentration risk: protect the biggest hubs (web_design, web_dev) with frequent refreshes and internal link maintenance; diversify wins via mid‑tier services and geo expansion.

## 3‑Week Sprint (One‑off Delivery)
- Week 1: implement FAQ blocks + titles/H1 refresh on top 10 hubs; add 4–6 contextual links from 10 related trends pages; ship LocalBusiness schema on 10 highest‑value city pages.
- Week 2: publish 8–10 short explainer videos on top hubs; targeted PR for 2 weak services; fix canonicals on overlapping trends/listings.
- Week 3: review gains; expand to next 10 quick wins; document playbooks and handoff.

## Internal Linking — Contextual vs. Navigational

### Navigational Links (What They Have) vs. Contextual Links (What’s Missing)
- Navigational Links (Good): the list at the bottom of a page acts like a mini‑sitemap. It tells Google, “from this SEO page, you can also get to these other pages.” This is good for crawlability.
- Contextual, In‑Body Links (Better & Missing Opportunity): a contextual link is placed within a descriptive paragraph, where the surrounding text (the context) gives a strong signal about the relevance of the linked page. This is what the spiderweb concept is truly about — creating a rich, interconnected narrative.
- Why this matters: Google places significantly more weight on a link that is editorially placed within a sentence than on one that appears in a simple list at the end of an article.

### Revised, More Precise Examples of What Is Missing
#### Main SEO Agency Hub Page (/agency/search-engine-optimization)
1) Linking to Related Service Hubs
- What they have: a link to “Content Marketing Companies” in a list at the bottom.
- What’s missing (the contextual link): in the paragraph that reads, “These agencies are adept at creating compelling, valuable content that resonates with your target audience…”, the phrase “compelling, valuable content” is the perfect place to embed a link directly to the /agency/content-marketing page.
- Why it’s critical: this contextual, editorial link tells Google that the concept of “compelling content” is directly related to the “Content Marketing” hub page — a much stronger endorsement than a list item.

2) Linking to Geo‑Specific Pages
- What they have: a link to “SEO in Madrid” at the very bottom.
- What’s missing (the contextual link): a dedicated paragraph within the main body that provides context for local search, for example:
  - Finding the Best Local SEO Partner
    “For businesses that rely on foot traffic, working with a local SEO company is essential. These firms specialize in Google Business Profile optimization and location‑specific keyword strategies. Whether you need an SEO agency in New York to dominate the city’s competitive market or a firm in Chicago with deep local knowledge, finding an expert in your area is key.”
- Why it’s critical: this weaves links into a user‑helpful narrative and provides rich context for search engines. It answers “near me” intent far more effectively than a single footer link.


## Internal Linking — Contextual vs. Navigational


### Navigational Links (What They Have) vs. Contextual Links (What’s Missing)
- Navigational Links (Good): the list at the bottom of a page acts like a mini‑sitemap. It tells Google, “from this SEO page, you can also get to these other pages.” This is good for crawlability.
- Contextual, In‑Body Links (Better & Missing Opportunity): a contextual link is placed within a descriptive paragraph, where the surrounding text (the context) gives a strong signal about the relevance of the linked page. This is what the spiderweb concept is truly about — creating a rich, interconnected narrative.
- Why this matters: Google places significantly more weight on a link that is editorially placed within a sentence than on one that appears in a simple list at the end of an article.

### Revised, More Precise Examples of What Is Missing
#### Main SEO Agency Hub Page (/agency/search-engine-optimization)
1) Linking to Related Service Hubs
- What they have: a link to “Content Marketing Companies” in a list at the bottom.
- What’s missing (the contextual link): in the paragraph that reads, “These agencies are adept at creating compelling, valuable content that resonates with your target audience…”, the phrase “compelling, valuable content” is the perfect place to embed a link directly to the /agency/content-marketing page.
- Why it’s critical: this contextual, editorial link tells Google that the concept of “compelling content” is directly related to the “Content Marketing” hub page — a much stronger endorsement than a list item.

2) Linking to Geo‑Specific Pages
- What they have: a link to “SEO in Madrid” at the very bottom.
- What’s missing (the contextual link): a dedicated paragraph within the main body that provides context for local search, for example:
  - Finding the Best Local SEO Partner
    “For businesses that rely on foot traffic, working with a local SEO company is essential. These firms specialize in Google Business Profile optimization and location‑specific keyword strategies. Whether you need an SEO agency in New York to dominate the city’s competitive market or a firm in Chicago with deep local knowledge, finding an expert in your area is key.”
- Why it’s critical: this weaves links into a user‑helpful narrative and provides rich context for search engines. It answers “near me” intent far more effectively than a single footer link.


## Internal Linking — Contextual vs. Navigational

### Navigational Links (What They Have) vs. Contextual Links (What’s Missing)
- Navigational Links (Good): the list at the bottom of a page acts like a mini‑sitemap. It tells Google, “from this SEO page, you can also get to these other pages.” This is good for crawlability.
- Contextual, In‑Body Links (Better & Missing Opportunity): a contextual link is placed within a descriptive paragraph, where the surrounding text (the context) gives a strong signal about the relevance of the linked page. This is what the spiderweb concept is truly about — creating a rich, interconnected narrative.
- Why this matters: Google places significantly more weight on a link that is editorially placed within a sentence than on one that appears in a simple list at the end of an article.

### Revised, More Precise Examples of What Is Missing
#### Main SEO Agency Hub Page (/agency/search-engine-optimization)
1) Linking to Related Service Hubs
- What they have: a link to “Content Marketing Companies” in a list at the bottom.
- What’s missing (the contextual link): in the paragraph that reads, “These agencies are adept at creating compelling, valuable content that resonates with your target audience…”, the phrase “compelling, valuable content” is the perfect place to embed a link directly to the /agency/content-marketing page.
- Why it’s critical: this contextual, editorial link tells Google that the concept of “compelling content” is directly related to the “Content Marketing” hub page — a much stronger endorsement than a list item.

2) Linking to Geo‑Specific Pages
- What they have: a link to “SEO in Madrid” at the very bottom.
- What’s missing (the contextual link): a dedicated paragraph within the main body that provides context for local search, for example:
  - Finding the Best Local SEO Partner
    “For businesses that rely on foot traffic, working with a local SEO company is essential. These firms specialize in Google Business Profile optimization and location‑specific keyword strategies. Whether you need an SEO agency in New York to dominate the city’s competitive market or a firm in Chicago with deep local knowledge, finding an expert in your area is key.”
- Why it’s critical: this weaves links into a user‑helpful narrative and provides rich context for search engines. It answers “near me” intent far more effectively than a single footer link.

## Strategy & Forecast
- Move ~200 quick wins to top‑3: ≈ 52,867 extra clicks/mo (value ≈ $542,521).
- Top services by uplift value:
  - ppc: $98,731
  - mobile_app: $96,970
  - seo: $95,670
  - web_design: $54,938
  - digital_marketing: $41,286
- Geo quick‑wins backlog (vol×CPC priority sum): ≈ 259,320. Focus on tier‑1 cities first.

- Why included: quantify upside to prioritize effort.
- Story: moving positions 4–10 into top‑3 on high‑value services is the fastest lever for traffic and value.

## 3‑Month Roadmap
- Month 1: fix technical canonicals/schema, implement internal‑link hubs, add FAQs on top 20 categories, rescue decliners.
- Month 2: scale local SEO (geo internal links, local schema, city proof points), focused PR to 3 weak services, content refreshes.
- Month 3: launch AI matching MVP, pilot founder podcast profiles for 50 agencies, expand trends→hub funnels; iterate on gains.

## Measurement & KPIs (Task 3)
- Rank: number of quick‑wins moved to top‑3 by service/geo; top‑3 share on queries with PAA/Local/Video/AIO features.
- Traffic: incremental clicks/mo from quick‑wins; geo clicks by city; CTR on hubs post FAQ/video additions.
- Quality: leads per session on hubs; AI‑matching engagement; indexation/canonical coverage on listings and trends.
- Cadence: weekly keyword movement; bi‑weekly template health (CWV, schema); monthly geo/service expansion scorecard.

## Risks & Declines
- web_design: 17 declining keywords
- other: 12 declining keywords
- seo: 12 declining keywords
- digital_marketing: 11 declining keywords
- mobile_app: 10 declining keywords
- web_dev: 9 declining keywords
- it_services: 7 declining keywords
- video: 7 declining keywords
- Focus rescues: ai (avg pos 8.5), video (avg pos 7.6).

- Why included: protect the base to avoid negative drift that cancels gains.
- Story: triage weak services with refreshes and links while we push quick‑wins.

## Next Steps
- Prioritize high‑CPC quick wins via internal linking and on‑page tuning.
- Refresh declining service pages; add FAQs to capture PAA.
- Strengthen local signals for 'near me' and geo variants.
- Expand trends content with clear CTAs into listing pages.
- Add hreflang and localized proof to top country hubs; implement Award schema and cross‑linking; ship short explainer videos on top hubs.

## Geo Report
- texas/dallas: 26 pages; 319 traffic
- georgia/atlanta: 45 pages; 203 traffic
- florida: 27 pages; 134 traffic
- new-jersey: 30 pages; 125 traffic
- texas/houston: 16 pages; 112 traffic
- new-york: 24 pages; 102 traffic
- connecticut: 14 pages; 91 traffic
- california/los-angeles: 12 pages; 86 traffic
- utah: 19 pages; 84 traffic
- pennsylvania: 14 pages; 70 traffic
- Commentary: focus top cities → texas/dallas (319), georgia/atlanta (203), florida (134).
- Why included: local is the closest proxy for transactional intent (‘near me’, city modifiers).
- Story: prioritize top cities with local proof, schema, and internal links to lift conversions.

- See geo_top_pages.csv, geo_quick_wins.csv, geo_wins.csv, geo_losses.csv for details.

## Appendix: Charts
- Vega-Lite JSON specs are written to charts/vega/*.json — importable in the Vega Editor or Observable.
