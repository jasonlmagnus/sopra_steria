# Codex Implementation Prompts

_Run each prompt in isolation; supply the repo context so Codex can edit the right file._

---

## 1 · Methodology Page

```
OPEN   audit_tool/dashboard/pages/1_🔬_Methodology.py
TASK   Replace tab-based layout with single-scroll page.
       • Add headline banner with three bullet "why trust" list + KPI chip for pages analysed.
       • Insert four MetricCards (criteria_count, tier_model, persona_coverage, crawl_date).
       • Wrap each yaml-derived section in st.expander with a one-sentence plain-English summary.
       • Remove all custom HTML & tabs.
```

## 2 · Persona Insights

```
OPEN   audit_tool/dashboard/pages/2_👥_Persona_Insights.py
TASK   Make landing view a 5-card Persona Scoreboard (photo, score, top_pain).
       Add red 'underserved' label if score < 6.
       Clicking a card should call show_deep_dive(persona_id) which renders a modal with sections Profile | Journey | Voice.
       Remove dropdown "mode" selector.
```

## 3 · Content Matrix

```
OPEN   audit_tool/dashboard/pages/3_📊_Content_Matrix.py
TASK   Strip filter block; add KPI metric row (avg_score, page_count, excellent, weak).
       Build heat-map df.pivot_table(index='content_pillar',columns='persona_id',values='avg_score',aggfunc='mean').
       On click of a heat-map cell open st.dataframe of pages for that pillar/persona.
       Add horizontal Best-in-Class gallery showing top 6 pages (avg_score ≥ 9).
```

## 4 · Opportunity & Impact

```
OPEN   audit_tool/dashboard/pages/4_💡_Opportunity_Impact.py
TASK   Remove initial filters row; create top MetricChips: quick_win_count, major_project_count.
       Plot 2×2 matrix (impact vs effort) colour by quadrant.
       Under matrix, render two st.columns with Top-5 Quick Wins and Top-5 Major Projects (page_title & one-line reason).
       Move full filters + table into st.expander("Roadmap Explorer").
```

## 5 · Success Library

```
OPEN   audit_tool/dashboard/pages/5_🌟_Success_Library.py
TASK   First section = Hall-of-Fame carousel (top 3 pages by avg_score) with 2-bullet "why it works".
       Build success_checklist = intersect high-scoring criteria across those pages; render as tick-list.
       Show Strengths Matrix heat-map Personas × Tiers (count of pages avg_score ≥ 8).
       Collapse detailed story list in st.expander("Browse All Success Stories").
```

## 6 · Reports & Export

```
OPEN   audit_tool/dashboard/pages/6_📋_Reports_Export.py
TASK   Remove Streamlit tabs; split page into three st.header sections:
       1) "Create a Board-Ready Report" – dropdown report_type → button → generate_report(report_type).
       2) "Explore & Export Data" – filterable dataframe + Export CSV button.
       3) "Download Complete Archive" – single ZIP export button with size & timestamp.
       Show progress messages during long operations.
```

## 8 · Social Media Analysis

```
OPEN   audit_tool/dashboard/pages/8_🔍_Social_Media_Analysis.py
TASK   Add top KPI scorecard (total followers, avg engagement, high_eng_channels, consistency_index).
       Replace existing charts with engagement_heatmap (platform × region) and side bullet list from tone_analysis markdown.
       Insert banner with Top-3 high priority recommendations from recommendations df where Priority=='High'.
       Hide filters in sidebar expander by default.
```

## 11 · Strategic Recommendations

```
OPEN   audit_tool/dashboard/pages/11_🎨_Strategic_Recommendations.py
TASK   Build ThemeCard component (headline, impact_metric, next_step, chips).
       Run synthesis_engine to produce df with theme column.
       Display three ThemeCards for Brand & Messaging, Visual Identity, UX & Trust.
       Add sidebar PDF export button to generate 1-page summary.
       Implement evidence_drawer(page_level_df) that slides from right on ThemeCard click.
       Add 90-day timeline strip below cards.
```

---

**Note:** MetricCard, ThemeCard, etc. refer to helpers in `perfect_styling_method`; create new ones if missing.
