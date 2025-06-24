# Dashboard Improvement Plan

This document outlines a prioritized plan for redesigning the Brand Health Command Center pages based on a human-centered audit. Each page is assessed against a set of user stories, and a score is assigned to determine its priority in the redesign queue.

---

## 1. Methodology Page (`1_🔬_Methodology.py`)

**Priority:** 1 | **Redesign Score:** 2/10 (Critically Flawed)

### User Stories

1.  **As a** new user, I want to quickly understand the "why" behind the scores so I can trust the data.
2.  **As a** team member, I want to easily find a specific metric's definition so I can explain our performance.
3.  **As a** senior leader, I want a 30-second overview of the framework so I can confirm it's robust.

### Recommended Redesign

— Position the page as a **two-minute credibility check** for executives.

1.  **Headline Banner (30-sec read)**  
    • 3 bullet 'why trust this audit?' (methodology sources, sample size, AI safety).  
    • One KPI chip: _Pages analysed: 1 234_.
2.  **Key Highlights Strip**  
    Four metric cards: Criteria count • Tier model • Persona coverage • Date of last crawl. Each tells leaders "scope", not tech detail.
3.  **Expandable Detail Sections**  
    `Scoring Framework`, `Page Classification`, `AI Guard-rails`. Collapsed by default; each opens with a plain-English summary sentence before detail tables.
4.  **'What Good Looks Like' call-out**  
    One boxed paragraph explaining the target score (> 8 / 10) so non-technical readers see the bar.
5.  Remove tabs, custom HTML; use standard Streamlit layout to keep width fixed.

---

## 2. Persona Insights (`2_👥_Persona_Insights.py`)

**Priority:** 2 | **Redesign Score:** 4/10 (Significant Flaws)

### User Stories

1.  **As a** strategist, I want to quickly understand our key personas so I can validate our content strategy.
2.  **As a** content creator, I want to easily access verbatim feedback so I can write more resonant copy.
3.  **As a** senior leader, I want to see a high-level comparison of how we're serving each persona so I can allocate resources.

### Recommended Redesign

1.  **Persona Scoreboard (landing view)**  
    A 5-card row: persona photo, headline score, "Top Pain". No dropdown, no tabs.
2.  **Underserved Alert**  
    Any persona with score < 6 flagged in red beside card – exec sees gaps immediately.
3.  **Deep-Dive Modal**  
    Clicking a card opens a full-page overlay with sections: Profile • Journey hotspots • Voice quotes. Starts at the most recent pain-point so time isn't wasted.
4.  **Quote Copier**  
    Each quote block has "Copy" icon – content teams can lift wording for decks.
5.  Tone: plain English. Remove dev jargon; labels like "What they struggle with" instead of "Criteria delta".

---

## 3. Content Matrix (`3_📊_Content_Matrix.py`)

**Priority:** 3 | **Redesign Score:** 4/10 (Significant Flaws)

### User Stories

1.  **As a** content strategist, I want to see which content pillars are performing best and worst so I can adjust our editorial calendar.
2.  **As a** marketing manager, I want to identify high-performing content pieces so I can promote them as best-practice examples.
3.  **As a** senior leader, I want to see the overall content balance and quality at a glance so I can ensure we're not over-investing.

### Recommended Redesign

1.  **Content Health Overview**  
    Four KPI cards: Avg Score • Pages analysed • Excellent pages • Weak pages. Sets context before scrolling.
2.  **Insight Heat-map**  
    Matrix of _Content Pillar × Persona_ coloured by avg score. Single glance tells the room where gaps are. Click a cell → list of pages.
3.  **Best-in-Class Gallery**  
    A horizontal scroll of 6 thumbnails (title + score) – immediate examples to open in new tab. Pulled from pages scoring ≥ 9.
4.  **Focused Filters (optional)**  
    Compact dropdown in sidebar – only appears if user wants to dig deeper. Avoids "wall of filters".
5.  Language = "What this means" captions under every chart so senior client doesn't need an analyst beside them.

---

## 4. Opportunity & Impact (`4_💡_Opportunity_Impact.py`)

**Priority:** 4 | **Redesign Score:** 3/10 (Seriously Flawed)

### User Stories

1.  **As a** senior leader, I want to immediately see the top 3-5 quick wins and strategic projects so I can understand our biggest opportunities.
2.  **As a** marketing manager, I want to visualize the trade-offs between effort and impact so I can build a realistic roadmap.
3.  **As a** brand strategist, I want to identify all pages failing on a specific criterion so I can diagnose systemic issues.

### Recommended Redesign

1.  **Opportunity Radar Header**  
    Two big metric chips: _Quick Wins (low-effort / high-impact)_ and _Major Projects (high-effort / high-impact)_ – numbers update with filters so leadership sees the scale of work.
2.  **Impact-vs-Effort Matrix**  
    Simple 2 × 2 quadrants, colours: green = Quick Win, red = Major Project, yellow = Fill-in, grey = Re-evaluate; clicking a dot opens the page card.
3.  **Top-5 Lists**  
    Directly beneath the matrix: ranked lists for Quick Wins and Major Projects with one-line "why it matters". No scrolling through 40 cards.
4.  **Roadmap Explorer (optional)**  
    Collapsible section holding filters + full table for analysts; hidden by default so execs see clarity first.
5.  **Plain-English captions** under the matrix explaining how to read it – avoids tech talk about algorithms.

---

## 5. Success Library (`5_🌟_Success_Library.py`)

**Priority:** 5 | **Redesign Score:** 3/10 (Seriously Flawed)

### User Stories

1.  **As a** content creator, I want to quickly find "best of the best" examples so I can understand what "10/10" looks like.
2.  **As a** marketing manager, I want to see the common patterns in our successful pages so I can create a "Success Checklist" for my team.
3.  **As a** senior leader, I want a high-level view of our strengths so I can validate our strategic focus.

### Recommended Redesign

1.  **Hall-of-Fame Carousel**  
    Top 3 pages (thumbnail, headline score, 2-bullet why it works). Immediate inspiration for the client.
2.  **Success Checklist Generator**  
    Auto-build a 5-item checklist (e.g. "Clear value-prop in first 150 px") derived from criteria where _all_ hall-of-famers scored ≥ 9. Presented as a tick-list for teams.
3.  **Strengths Matrix**  
    Heat-map of Personas vs. Content Tiers showing count of pages scoring ≥ 8; instantly shows where the brand already wins.
4.  **Browse All Success Stories**  
    Collapsible table searchable by keyword, sorted by score; no clutter on first view.
5.  **Copy Buttons**  
    Each story card has "Copy headline" so marketers can reuse proven copy without digging.

---

## 6. Reports & Export (`6_📋_Reports_Export.py`)

**Priority:** 6 | **Redesign Score:** 5/10 (Functional but Confusing)

### User Stories

1.  **As an** analyst, I want to filter the complete dataset and export the result to CSV for deep-dive analysis.
2.  **As a** marketing manager, I want to generate a pre-formatted PowerPoint report for a persona with one click.
3.  **As a** data manager, I want a one-click option to download a complete backup of all data as a ZIP file.

### Recommended Redesign

1.  **Generate a Report**  
    Drop-down: choose report type (Executive Summary, Persona Deck, etc.) → click "Generate" → spinner → download PPTX/PDF. Default to Executive Summary so leadership gets value in one click.
2.  **Explore & Export Data**  
    Simple table with column picker + filters + "Export CSV" button. Hides charting; this is purely for taking data to Excel.
3.  **System Backups**  
    One big "Download Complete Archive" button (ZIP). Shows timestamp, size, and a tooltip explaining contents; reassures the client their data is portable.
4.  **Progress Messages**  
    While generating large files, show percentage and ETA so users don't assume the app froze.
5.  **No Tabs, No Tech Terms**  
    Section headers speak business: "Create a Board-Ready Report", not "Custom Reports Generator".

---

## 7. Run Audit (`7_🚀_Run_Audit.py`)

**Priority:** 7 | **Redesign Score:** 9/10 (Well-Designed)

### Assessment

This page is well-designed and meets its core user stories effectively. It correctly separates the "run" and "post-process" stages, provides excellent real-time feedback, and serves as a good model for a task-oriented page. No redesign is needed.

---

## 8. Social Media Analysis (`8_🔍_Social_Media_Analysis.py`)

**Priority:** 8 | **Redesign Score:** 4/10 (Significant Flaws)

### User Stories

1.  **As a** social media manager, I want to see a cross-channel comparison of KPIs to see which platforms perform best.
2.  **As a** brand manager, I want to understand our brand's tone and consistency across regions to spot inconsistencies.
3.  **As a** senior leader, I want to see the key, high-priority recommendations from the audit without reading the whole report.

### Recommended Redesign

1.  **Social Health Scorecard**  
    Four tiles up top: Total Followers • Avg Engagement • High-engagement Channels • Brand-Consistency Index. Lets the client gauge scale and quality immediately.
2.  **Engagement Heat-map**  
    Grid of _Platform × Region_ shaded by engagement category (High / Medium / Low). One glance → where to invest or fix.
3.  **Tone & Consistency Call-outs**  
    Beside the heat-map, a short bullet list auto-pulled from "Tone Analysis" table (e.g. "UK LinkedIn posts: formal tone, inconsistent visuals").
4.  **Top 3 Recommendations Banner**  
    Red, amber, green cards with headline action and 1-sentence "why it matters" – pulled from markdown "High" priority rows. Always visible above the fold.
5.  **Deep-Dive Filters (optional)**  
    Collapsible sidebar lets analysts pick platform / region; hidden by default so execs aren't overwhelmed.

---

## 9. Persona Viewer (`9_👤_Persona_Viewer.py`)

**Priority:** 9 | **Redesign Score:** 8/10 (Well-Designed)

### Assessment

This page is well-conceived and effectively uses tabs to manage a large amount of information about a single entity. It successfully meets user needs.

- **Refinements:** Format the "Profile" tab more cleanly with expanders; enhance the "Performance" tab with a summary chart of top/bottom pages for the persona.

---

## 10. Visual Brand Hygiene (`10_🎨_Visual_Brand_Hygiene.py`)

**Priority:** 10 | **Redesign Score:** 9/10 (Well-Designed)

### Assessment

This page is a strong example of the target design state, using modern styling and a clear, top-down information hierarchy. It meets all user stories.

- **Refinement:** The heatmap could be more actionable for designers by changing it from `Tier vs. Domain` to `Brand Criteria vs. Domain`.

---

## 11. Strategic Recommendations (`11_🎨_Strategic_Recommendations.py`)

**Priority:** 11 | **Redesign Score:** 1/10 (Critically Unusable)

### User Stories

1.  **As a** senior leader, I want to see a synthesized, high-level action plan, not a raw list of problems.
2.  **As a** marketing director, I want to see recommendations grouped by theme for clear ownership.
3.  **As a** strategist, I want to drill down from a recommendation to see the supporting evidence.

### Recommended Redesign

1.  **Three Theme Cards Front-and-Centre**  
    Brand & Messaging • Visual Identity • UX & Trust. Each card: 1-sentence headline, impact metric (pages affected), and "Next Step" button.
2.  **Priority Chips**  
    Every theme shows chips: Quick Wins (#) • Critical Issues (#) so leaders sense urgency without reading details.
3.  **Evidence Drawer**  
    Clicking "View Evidence" slides out a right-hand panel listing supporting pages & quotes (de-duplicated). No endless scroll.
4.  **90-Day Timeline Strip**  
    Under the cards, a simple bar (0-30, 30-60, 60-90) with icons indicating when each action starts – helps execs picture sequencing.
5.  **One-click PDF Export**  
    Button generates a 1-page PDF summary of the three themes – executive can forward without opening Streamlit.

---
