_Status: Reference • Last-verified: 2025-06-22 • Owner: @ux_designer_

# Brand Health Command Center - Redesign Specification

## Executive Summary

This document outlines the complete redesign of the Brand Audit Dashboard into a sophisticated **Brand Health Command Center** - a strategic marketing decision engine that transforms raw audit data into actionable business intelligence.

### Current State Assessment

- **Technical Issues**: TypeError sorting mixed data types, missing file references
- **User Experience Problems**: "Rich data but impenetrable", no insights or story
- **Architecture Issues**: Monolithic 2000+ line dashboard file
- **Missing Strategic Value**: No commercial impact storytelling or recommendations

### Target State Vision

A modern, executive-ready dashboard that answers three critical questions:

1. **Are we distinct?** - Differentiation analysis across personas and content
2. **Are we resonating?** - Sentiment and engagement measurement
3. **Are we converting?** - Conversion readiness and commercial impact

---

## 1. Global Framework & Architecture

### 1.1 Technical Architecture

```
Brand Health Command Center/
├── main_dashboard.py (Entry point)
├── components/
│   ├── data_loader.py (Enhanced CSV processing)
│   ├── metrics_calculator.py (Derived metrics engine)
│   ├── ai_insights.py (GPT-4 integration)
│   ├── audit_runner.py (Integrated audit execution)
│   └── export_manager.py (Multi-format exports)
├── pages/
│   ├── 1_executive_dashboard.py
│   ├── 2_persona_insights.py
│   ├── 3_content_matrix.py
│   ├── 4_opportunity_impact.py
│   ├── 5_success_library.py
│   ├── 6_run_audit.py
│   └── 7_reports_export.py
└── assets/
    ├── styles.css
    └── brand_colors.py
```

### 1.2 UI Framework Specifications

- **Layout**: 2-column shell → Left Nav 72px, Main Canvas (flex)
- **Inspector Drawer**: 320px slides in on drill-downs
- **Color Palette**: Deep Navy #0D1B2A, Snow White #FFFFFF, Status colors (Green #34C759, Yellow #FFB800, Red #FF3B30)
- **Typography**: Inter (Google Fonts) — 16px body, 24px headers
- **Charts**: Recharts integration (area, bar, heatmap, waterfall, scatter)
- **Performance**: P95 tab-switch < 3s, lazy-load tables > 500 rows

### 1.3 Data Pipeline Enhancement

```python
# Enhanced data structure mapping
CURRENT_FILES = {
    'pages.csv': ['page_id', 'url', 'slug', 'persona', 'tier', 'final_score', 'audited_ts'],
    'criteria_scores.csv': ['page_id', 'criterion_code', 'criterion_name', 'score', 'evidence', 'weight_pct', 'tier', 'descriptor'],
    'recommendations.csv': ['page_id', 'recommendation', 'strategic_impact', 'complexity', 'urgency', 'resources'],
    'experience.csv': ['page_id', 'persona_id', 'first_impression', 'sentiment', 'engagement', 'conversion_likelihood'],
    'scorecard_data.csv': ['page', 'url', 'tier', 'final_score']  # Legacy compatibility
}

# New derived metrics calculations
DERIVED_METRICS = {
    'criterion_gap': '10 - score',
    'pillar_score': 'weighted_avg(criteria_by_pillar)',
    'brand_score': 'avg(all_pillar_scores)',
    'effort_level': 'evidence_length_heuristic',
    'potential_impact': 'gap_score × weight_pct × 0.1',
    'quick_win': 'impact ≥ 1.5 AND effort = Low',
    'critical_issue': 'descriptor = CONCERN',
    'conversion_readiness': 'avg(cta_effectiveness, trust_signals)',
    'sentiment_index': '+1=Positive, 0=Neutral, -1=Negative',
    'success_page': 'brand_score ≥ 8 AND zero_warnings'
}
```

---

## 2. Seven-Tab Navigation Architecture

### Tab 1: Executive Dashboard

**Question**: "How healthy is the brand right now?"

#### Key Components:

- **Brand Health Score Tile**: Large metric (0-10) with mini sparkline trend
- **Critical Issues Alert**: Red banner if any pages score < 4.0
- **Sentiment Overview**: Net sentiment with percentage breakdown
- **Conversion Readiness**: Proxy metric with traffic-light status
- **Quick Wins Counter**: Immediate opportunities (high impact, low effort)
- **Tier Performance Grid**: Segmented analysis with experience data augmentation

#### Implementation Priority: Week 1

```python
# Executive metrics calculations
brand_health_score = df.groupby('persona')['final_score'].mean()
critical_issues = df[df['final_score'] < 4.0]['page_id'].count()
sentiment_breakdown = df['sentiment'].value_counts(normalize=True)
conversion_readiness = df[['cta_effectiveness', 'trust_signals']].mean().mean()
```

### Tab 2: Persona Insights

**Question**: "How do our priority personas feel and act?"

#### Key Components:

- **Persona Cards**: Individual persona performance with sentiment, engagement bars
- **Radar Chart**: Pillar scores vs benchmark comparison
- **Quote Carousel**: Rotating first_impression excerpts
- **Engagement Heatmap**: Page-level engagement by persona
- **Conversion Likelihood Distribution**: Statistical analysis

#### Implementation Priority: Week 2

### Tab 3: Content Matrix

**Question**: "Where do we pass/fail across pillars & page types?"

#### Key Components:

- **Interactive Heatmap**: Page Tier × Pillar performance matrix
- **Drill-down Drawer**: Click cell → detailed page list, sortable by score
- **Performance Filters**: By tier, pillar, score range
- **Export Functionality**: CSV export of filtered results

#### Implementation Priority: Week 2

### Tab 4: Opportunity & Impact

**Question**: "Which gaps matter most, what should we do, and how much will it earn?"

#### Key Components:

- **Prioritized Gap List**: Criterion gaps with effort badges and impact estimates
- **AI Action Drawer**: GPT-4 generated H1, CTA, meta recommendations
- **Impact Waterfall**: Visual representation of cumulative improvement potential
- **Bubble Plot**: Gap vs traffic (using page_score as proxy)
- **ROI Calculator**: Business impact estimates (gap × weight × €10,000)

#### Implementation Priority: Week 3

### Tab 5: Success Library

**Question**: "What already works that we can emulate?"

#### Key Components:

- **Success Cards**: Pages scoring ≥ 8.0 with screenshot placeholders
- **Pattern Analysis**: Top-3 evidence snippets auto-extracted
- **Apply Pattern**: One-click copy to clipboard functionality
- **Success Metrics**: What made these pages successful
- **Replication Guide**: Step-by-step improvement recommendations

#### Implementation Priority: Week 4

### Tab 6: Run Audit

**Question**: "How do I create new brand audits and monitor progress?"

#### Key Components:

- **Persona Upload**: Drag-and-drop interface for persona markdown files
- **URL Management**: Bulk URL upload with validation and categorization
- **Audit Configuration**: Select audit methodology, criteria weights, and output preferences
- **Progress Monitoring**: Real-time audit progress with live log streaming
- **Results Integration**: Automatic CSV generation and dashboard data refresh
- **Audit History**: Track previous audits with comparison capabilities

#### Implementation Priority: Week 1 (Integrated with existing audit runner)

### Tab 7: Reports & Export

**Question**: "How do I share or deep-dive the data?"

#### Key Components:

- **One-click Exports**: PPT (exec summary), PDF (full report), CSV (raw data)
- **Custom Report Builder**: Select metrics, personas, date ranges
- **API Keys**: Stubbed REST/GraphQL endpoints for future integration
- **Scheduled Reports**: Email automation setup (future)

#### Implementation Priority: Week 4

---

## 3. AI Integration Strategy

### 3.1 GPT-4 Services

```python
AI_SERVICES = {
    'copy_refiner': {
        'purpose': 'Rewrite H1, CTA, meta descriptions',
        'input': 'evidence_snippet + persona_context',
        'output': 'optimized_copy_variants'
    },
    'strategic_insights': {
        'purpose': 'Generate executive summary insights',
        'input': 'performance_patterns + gap_analysis',
        'output': 'strategic_recommendations'
    },
    'keyword_extractor': {
        'purpose': 'Suggest content tags and themes',
        'input': 'evidence_text',
        'output': 'relevant_keywords'
    }
}
```

### 3.2 Privacy & Security

- Strip organization names in GPT prompts (except "Sopra Steria")
- No client-sensitive PII sent to external APIs
- Local processing for sensitive calculations

---

## 4. Data Structure Enhancements

### 4.1 Current Data Issues Fixed

```python
# Fix TypeError in sorting mixed data types
def safe_sort_unique(series):
    """Handle mixed float/string types in sorting"""
    return sorted(series.dropna().astype(str).unique())

# Enhanced data loading with proper type handling
def load_enhanced_data():
    """Load and merge all CSV files with proper data types"""
    pages_df = pd.read_csv('pages.csv')
    criteria_df = pd.read_csv('criteria_scores.csv')
    recommendations_df = pd.read_csv('recommendations.csv')
    experience_df = pd.read_csv('experience.csv')

    # Master dataset with 25+ columns
    master_df = pages_df.merge(criteria_df, on='page_id', how='left') \
                       .merge(recommendations_df, on='page_id', how='left') \
                       .merge(experience_df, on='page_id', how='left')

    return master_df
```

### 4.2 New Calculated Fields

```python
CALCULATED_FIELDS = [
    'criterion_gap',      # 10 - score
    'pillar_score',       # Weighted average by pillar
    'effort_level',       # Low/Medium/High based on evidence length
    'potential_impact',   # Gap × weight × 0.1
    'quick_win_flag',     # Boolean: high impact + low effort
    'critical_issue_flag', # Boolean: descriptor = CONCERN
    'success_page_flag',  # Boolean: score ≥ 8 + no warnings
    'sentiment_numeric',  # +1/0/-1 conversion
    'conversion_proxy',   # CTA + trust signals average
    'tier_performance',   # Tier-level aggregations
]
```

---

## 5. Visual Design System

### 5.1 Component Library

```css
/* Brand Health Command Center Styles */
:root {
  --navy-deep: #0d1b2a;
  --white-snow: #ffffff;
  --green-status: #34c759;
  --yellow-status: #ffb800;
  --red-status: #ff3b30;
  --font-primary: "Inter", sans-serif;
}

.dashboard-shell {
  display: flex;
  height: 100vh;
}

.left-nav {
  width: 72px;
  background: var(--navy-deep);
  display: flex;
  flex-direction: column;
}

.main-canvas {
  flex: 1;
  background: var(--white-snow);
  overflow-y: auto;
}

.inspector-drawer {
  width: 320px;
  background: var(--white-snow);
  border-left: 1px solid #e5e7eb;
  transform: translateX(100%);
  transition: transform 0.3s ease;
}

.inspector-drawer.open {
  transform: translateX(0);
}
```

### 5.2 Status Indicators

- **🟢 Excellent**: Score ≥ 8.0
- **🟡 Good**: Score 4.0-7.9
- **🔴 Critical**: Score < 4.0
- **⚡ Quick Win**: High impact + Low effort
- **🚨 Critical Issue**: Any CONCERN flags

---

## 6. Performance Optimization

### 6.1 Performance Targets

- **Tab Switch**: P95 < 3 seconds
- **LLM Response**: < 5 seconds
- **Data Refresh**: Manual upload or nightly batch
- **Large Tables**: Lazy loading for > 500 rows

### 6.2 Optimization Strategies

```python
# Lazy loading for large datasets
@st.cache_data
def load_paginated_data(page_num, page_size=100):
    start_idx = page_num * page_size
    end_idx = start_idx + page_size
    return master_df.iloc[start_idx:end_idx]

# Efficient filtering with indexes
@st.cache_data
def filter_data(persona=None, tier=None, score_range=None):
    filtered_df = master_df.copy()
    if persona:
        filtered_df = filtered_df[filtered_df['persona'] == persona]
    if tier:
        filtered_df = filtered_df[filtered_df['tier'] == tier]
    if score_range:
        filtered_df = filtered_df[
            (filtered_df['final_score'] >= score_range[0]) &
            (filtered_df['final_score'] <= score_range[1])
        ]
    return filtered_df
```

---

## 7. Implementation Roadmap

### Week 1: Foundation & Executive Dashboard

- [ ] Set up new architecture with component separation
- [ ] Fix current TypeError issues in data loading
- [ ] Implement enhanced data pipeline with derived metrics
- [ ] Build Executive Dashboard with key KPIs
- [ ] Create brand health scoring algorithm
- [ ] Add critical issues alerting system
- [ ] Integrate Run Audit tab with existing audit runner functionality

### Week 2: Persona & Content Analysis

- [ ] Build Persona Insights tab with cards and radar charts
- [ ] Implement Content Matrix with interactive heatmap
- [ ] Add drill-down drawer functionality
- [ ] Create persona comparison capabilities
- [ ] Integrate sentiment and engagement visualizations

### Week 3: Opportunity & AI Integration

- [ ] Build Opportunity & Impact analysis
- [ ] Integrate GPT-4 for strategic insights generation
- [ ] Implement impact waterfall visualizations
- [ ] Create ROI calculator with business impact estimates
- [ ] Add AI-powered copy recommendations

### Week 4: Success Library & Export

- [ ] Build Success Library with pattern analysis
- [ ] Implement multi-format export system (PPT/PDF/CSV)
- [ ] Add custom report builder
- [ ] Performance optimization and QA testing
- [ ] User acceptance testing and refinements

### Phase 0: Quick Wins _(Immediate – 1-2 days)_

| Task     | Description                                                                                                                                  | Success Metric                                                                         |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **P0-1** | **Unified Persona Selector** – replace ad-hoc tag list with a Multiselect containing an **☑️ All Personas** option and dynamic count display | All pages reflect identical persona filter; 'Current Selection' shows _x / n personas_ |
| **P0-2** | Persist filter choices in `st.session_state` and apply inside `data_loader` so that every page and KPI tile respects the global filter       | Switching tabs does **not** reset persona or tier selection                            |
| **P0-3** | Harmonise score column naming: create alias `raw_score → final_score` (or vice-versa) to stop `KeyError: 'final_score'` crashes              | Dashboard loads with zero missing-column errors                                        |
| **P0-4** | Add real-time counter tiles in Command Center: **Personas selected · Pages filtered · Evaluations**                                          | Counters update instantly when slider / multiselect changes                            |
| **P0-5** | Health-check endpoint (`/healthz`) + single launch command in README                                                                         | `curl /healthz` returns _ok_ while Streamlit is live                                   |

> **Outcome** : marketing stakeholders can slice the entire dashboard by persona (or "All") without losing context; technical team eliminates the most frequent runtime exceptions.

---

## 8. Success Metrics

### 8.1 Technical Success Criteria

- [ ] Zero TypeError exceptions in production
- [ ] All 7 tabs functional with full feature set
- [ ] P95 performance targets met
- [ ] Successful data processing for all personas
- [ ] Export functionality working across all formats
- [ ] Integrated audit runner with seamless data pipeline

### 8.2 User Experience Success Criteria

- [ ] Executive summary provides clear brand health status
- [ ] Strategic insights generate actionable recommendations
- [ ] Users can identify top 3 improvement opportunities within 30 seconds
- [ ] Commercial impact questions answered: distinct, resonating, converting
- [ ] Dashboard transforms from "impenetrable" to "strategic decision engine"

### 8.3 Business Impact Success Criteria

- [ ] CMO/Marketing Executive can present brand health to board
- [ ] Marketing teams can prioritize content improvements
- [ ] Clear ROI estimates for brand improvement investments
- [ ] Persona-specific optimization strategies identified
- [ ] Success patterns documented for replication

---

## 9. Risk Mitigation

### 9.1 Technical Risks

- **Data Quality Issues**: Implement robust data validation and error handling
- **Performance Degradation**: Use caching, pagination, and lazy loading
- **AI Integration Failures**: Fallback to heuristic-based insights
- **Export Failures**: Multiple format options with graceful degradation

### 9.2 User Adoption Risks

- **Complexity Overwhelm**: Progressive disclosure with guided tours
- **Lack of Insights**: AI-powered narrative generation for key findings
- **Poor Mobile Experience**: Responsive design considerations
- **Training Requirements**: Built-in help system and tooltips

---

## 10. Future Enhancements (Post-MVP)

### 10.1 Data Integration Expansions

- GA4 traffic data integration
- CRM conversion tracking
- CMS content performance metrics
- Social media engagement data
- Competitor benchmarking data

### 10.2 Advanced Analytics

- Predictive modeling for brand health trends
- A/B testing framework for content optimization
- Machine learning-based persona insights
- Natural language processing for content analysis
- Advanced statistical modeling for impact attribution

### 10.3 Collaboration Features

- Team collaboration on recommendations
- Approval workflows for content changes
- Integration with project management tools
- Automated reporting and alerting
- API ecosystem for third-party integrations

---

## Conclusion

This redesign transforms the Brand Audit Dashboard from a data dump into a strategic marketing command center. By focusing on the three core questions (distinct, resonating, converting) and providing clear actionable insights, we create a tool that serves both tactical optimization needs and strategic decision-making requirements.

The phased implementation approach ensures we can deliver value incrementally while building toward the full vision of an AI-powered brand intelligence platform.

**Next Steps**:

1. Review and approve this redesign plan
2. Begin Week 1 implementation with foundation architecture and Run Audit integration
3. Set up regular stakeholder reviews for each weekly milestone
4. Prepare user testing scenarios for validation
5. Consolidate existing audit runner functionality into unified dashboard experience

---

_Document Version: 1.0_  
_Last Updated: 2025-06-21_  
_Author: AI Assistant_  
_Stakeholders: Marketing Leadership, Development Team_
