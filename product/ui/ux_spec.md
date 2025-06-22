_Status: Active • Last-verified: 2025-06-22 • Owner: @ux_designer_

Below is the single, end-to-end MVP specification—nothing trimmed, every "good bit" kept intact—for the Brand Health Command Center.
This version assumes no third-party integrations yet (only the audit + persona CSVs you shared), but it preserves the richer UI/UX you want for launch-day demos.

1 Global Framework (UI Chrome & Perf)
Element Spec
Layout 2-column shell → Left Nav 72 px, Main Canvas (flex). Inspector Drawer 320 px slides in on drill-downs.
Top Utility Bar Global filters: Date-range · Persona selector · Locale · Search
Icon buttons: Dark/Light toggle · Export · Help
Colour Palette Deep Navy #0D1B2A, Snow White #FFFFFF, Status: Green #34C759, Yellow #FFB800, Red #FF3B30
Typography Inter (Google) — 16 px body, 24 px H-level
Charts & Tables Recharts (area, bar, heat-map, waterfall, scatter) + native HTML tables
Performance Budget P95 tab-switch < 3 s; lazy-load tables > 500 rows

2 Data Assumptions for MVP
Only two flat files available at build-time.

File Key Fields
audit.csv page_id, criterion_code, score, weight_pct, tier, descriptor, evidence
persona_feedback.csv page_id, persona_id, sentiment, engagement_level, first_impression, conversion_likelihood

No GA4, CRM, or CMS APIs yet.

3 Derived Metrics & Heuristics (Local Processing-Only)
Derivation Formula / Rule
3.1 Criterion Gap gap_score = 10 – score
3.2 Pillar Score Weighted AVG of criteria within same pillar
3.3 Brand Score AVG of all pillar scores
3.4 Effort Level Evidence length < 300 chars → Low;
300–800 → Medium;

> 800 OR descriptor contains "Press Release" → High
> 3.5 Potential Impact impact = gap_score × weight_pct × 0.1 (range 0-2.5)
> 3.6 Quick Win impact ≥ 1.5 AND effort = Low
> 3.7 Critical Issue Any criterion flagged CONCERN
> 3.8 Conversion Readiness Proxy AVG of calltoaction_effectiveness and trust_credibility_signals per page
> 3.9 Sentiment Index +1 = Positive, 0 = Neutral, –1 = Negative (blank → "—")
> 3.10 Success Page brand_score ≥ 8 AND zero WARN/CONCERN

4 Navigation & Tab Purposes (6 Tabs)

# Tab Answers the question … Key Artefacts

1 Executive Dashboard "How healthy is the brand _right now_?" KPI tiles · 6-month trend sparkline · Pillar alert strip
2 Persona Insights "How do our priority personas feel and act?" Persona cards · Radar vs benchmark · Quote carousel
3 Content Matrix "Where do we pass/fail across pillars & page types?" Interactive heat-map (Page Tier × Pillar) with drill-down drawer
4 Opportunity & Impact "Which gaps matter most, what should we do, and how much will it earn (proxy)?" Prioritised gap list · AI action sheet · Lift-style waterfall (using Potential Impact) · Gap-vs-traffic bubble plot (traffic placeholder dots equal page_score for now)
5 Success Library "What already works that we can emulate?" Cards (Score ≥ 8) · "What Worked" bullets · Apply Pattern button
6 Reports & Export "How do I share or deep-dive the data?" One-click PPT / PDF / CSV · REST/GraphQL keys (stubbed)

5 Per-Tab Detailed Widget Spec
5.1 Executive Dashboard
Widget Data / Logic
Brand Score Tile brand_score (0-10) + mini sparkline (last 6 runs)
Sentiment Tile AVG sentiment_index; red badge if < 0
Conversion Readiness Proxy Formula 3.8; yellow if < 6
Quick Wins Count of rule 3.6
Critical Issues Count of rule 3.7; click → drawer list

5.2 Persona Insights
Shows only personas present in CSV.

Component Notes
Persona Card Net Sentiment, Engagement (bar), Conversion Likelihood
Radar vs Benchmark Pillar scores for persona vs overall avg
Quote Carousel Cycles through first_impression excerpts

5.3 Content Matrix
Interactive heat-map

Interaction Result
Hover cell Tooltip: avg score, #pages
Click cell Drawer: table of pages, sortable by score, export CSV

5.4 Opportunity & Impact
Column Field
Gap List Title (criterion) · Gap Score · Effort Badge · Potential Impact € (impact × 10 000)
Right Drawer AI-generated H1, CTA, Meta; "Copy" buttons; Impact bars (heuristic)
Visuals Waterfall adds Impact for top N gaps · Bubble plot uses page_score as proxy for traffic size

5.5 Success Library
Card Face Details
Banner Screenshot (static placeholder)
Ribbon Brand Score
Body Top-3 evidence snippets auto-extracted
CTA Apply Pattern → exports copy to clipboard

5.6 Reports & Export
Export Content
CSV audit + derived fields
PPT Exec Dashboard slide, Top Opportunities, Success examples
PDF Full spec report inc. heat-map images

6 AI Services (Local + Cloud)
Service Purpose Source Data
GPT-4o Copy Refiner Rewrite H1, CTA, meta Evidence snippet + persona context
(Optional) Keyword Extractor Suggest tags Evidence text

Prompt engineering ensures no client-sensitive PII is sent.

7 Performance & Security
Area MVP Target
Tab switch (P95) < 3 s
LLM response < 5 s
Data refresh Manual re-upload or nightly batch
PII handling Strip org names in GPT prompt beyond "Sopra Steria"

8 MVP Delivery Roadmap (4 Weeks)
Week Build Focus
1 Data import + derivations 3.1-3.4 · Build Tabs 1-3 skeleton
2 Full Dashboard KPIs · Complete Persona & Matrix interactions
3 Opportunity list + AI drawer · Heuristic Impact calc · Waterfall
4 Success Library · Export module · QA & performance tuning

You Now Have — in one place — every MVP element
• All six tabs (with questions and widgets)
• Global framework, colours, typography
• Exact KPI formulas & heuristics
• AI drawer behaviour
• Security, performance, and 4-week sprint

Nothing is chopped; everything essential is locked in. Let's build.

**Note:** Detailed UX behaviours for dashboard. See high-level UX principles at [../ux.md](../ux.md).
