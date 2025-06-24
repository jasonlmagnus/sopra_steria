# FUNCTIONAL SPECIFICATIONS - Brand Health Dashboard Pages

## Context

These specifications document the working functionality from `temp_committed_pages/` which had GREAT content and logic but terrible styling. Use this as a reference to fix the current broken pages that may have good styling but broken functionality.

## Page Index

0. 🎯 Brand Health Command Center - Executive dashboard and main entry point
1. 🔬 Methodology - Methodology documentation page
2. 👥 Persona Insights - Persona comparison and analysis
3. 📊 Content Matrix - Content performance analysis
4. 💡 Opportunity Impact - Improvement opportunities and roadmap
5. 🌟 Success Library - Success stories and patterns
6. 📋 Reports Export - Data exploration and export functionality
7. 🚀 Run Audit - Audit execution interface
8. 🔍 Social Media Analysis - Social media performance dashboard
9. 👤 Persona Viewer - Individual persona deep-dive analysis
10. 🎨 Visual Brand Hygiene - Visual brand compliance dashboard

---

## 0. 🎯 Brand Health Command Center

### Purpose

Executive dashboard providing 30-second strategic marketing decision engine for C-suite executives. Main entry point that loads all data and provides high-level overview with deep-dive navigation.

### Data Sources

- `BrandHealthDataLoader` - Unified data access layer
- `BrandHealthMetricsCalculator` - Executive metrics computation
- `master_df` - Unified audit data (stored in session state)
- `datasets` - All individual datasets (stored in session state)

### Page Structure

#### Header Section

- Title: "Brand Health Command Center"
- Description: "30-second strategic marketing decision engine for executives"

#### Executive Dashboard Layout

1. **Brand Health Overview** - Core performance metrics
2. **Strategic Focus** - Tier filtering controls
3. **Strategic Brand Assessment** - Key brand dimensions
4. **Top 3 Improvement Opportunities** - Quick wins identification
5. **Top 5 Success Stories** - Best performing content
6. **Strategic Recommendations** - AI-generated action priorities
7. **Deep-Dive Navigation** - Links to specialized analysis tabs

### Key Components

#### Brand Health Overview (4 metrics)

- **Overall Brand Health**: Weighted average score with status indicator
- **Critical Issues**: Count of pages scoring below threshold
- **Quick Wins**: Count of low-effort, high-impact opportunities
- **Success Stories**: Count of high-performing pages

#### Strategic Focus Controls

- **Tier Filter**: Dropdown for content tier filtering
  - All Tiers (default)
  - Tier 1 (Strategic)
  - Tier 2 (Tactical)
  - Tier 3 (Operational)
- **Filter Application**: Updates Strategic Brand Assessment metrics

#### Strategic Brand Assessment (3 dimensions)

- **Distinctiveness**: Brand differentiation score (0-10 scale)
  - Algorithm: `calculate_distinctiveness_score()`
  - Status: HIGH (≥7), MODERATE (4-6.9), LOW (<4)
- **Resonance**: Audience connection score (0-10 scale)
  - Algorithm: `calculate_resonance_score()` converted from percentage
  - Status: HIGH (≥7), MODERATE (4-6.9), LOW (<4)
- **Conversion**: Action-driving effectiveness (0-10 scale)
  - Algorithm: `calculate_conversion_score()`
  - Status: HIGH (≥7), MODERATE (4-6.9), LOW (<4)

#### Top 3 Improvement Opportunities

- **Data Source**: `get_top_opportunities(limit=3)`
- **Expandable Cards**: Page title with impact score
- **Metrics Display**: Current score, effort level, potential impact
- **Content**: Detailed recommendation, evidence, urgency
- **Navigation**: Link to Opportunity & Impact tab

#### Top 5 Success Stories

- **Data Source**: `calculate_success_stories(min_score=7.5)`
- **Expandable Cards**: Page title with performance score
- **Metrics Display**: Score, tier, key strengths
- **Content**: Evidence and success factors
- **Navigation**: Link to Success Library tab

#### Strategic Recommendations

- **Data Source**: `generate_executive_summary()['recommendations']`
- **AI-Generated**: Action priorities based on current brand health
- **Contextual Actions**: Smart navigation buttons based on recommendation type
  - Critical pages → Content Matrix (filtered)
  - Quick wins → Opportunity Impact (filtered)
  - Persona issues → Persona Insights (filtered)
  - General improvements → Opportunity Impact

### Navigation Integration

#### Deep-Dive Analysis Section

- **Content Cards**: Visual navigation to specialized tabs
- **Content Matrix**: Detailed page analysis and tier breakdown
- **Opportunity & Impact**: Action roadmap with effort/impact analysis
- **Success Library**: Learn from high-performing content patterns

#### Sidebar Essentials

- **Data Overview**: Total pages, records, average score
- **Data Quality**: Experience data and recommendations counts
- **Quick Actions**: Navigation shortcuts to key analysis pages

### Logic Flow

1. **Data Initialization**

   - Load all datasets via BrandHealthDataLoader
   - Store in session state for other pages
   - Initialize BrandHealthMetricsCalculator

2. **Executive Summary Generation**

   - Calculate brand health overview metrics
   - Generate strategic brand assessment scores
   - Identify top opportunities and success stories

3. **Interactive Filtering**

   - Apply tier filter to metrics calculator
   - Update Strategic Brand Assessment dynamically
   - Handle empty filtered datasets gracefully

4. **Contextual Navigation**

   - Parse recommendation text for smart filtering
   - Set appropriate session state filters
   - Navigate to relevant specialized pages

5. **Session State Management**
   - Cache all data for performance
   - Maintain filter states across pages
   - Provide data access for child pages

### Integration Points

#### Session State Variables

- `st.session_state['datasets']` - All loaded datasets
- `st.session_state['master_df']` - Unified audit data
- `st.session_state['summary']` - Executive summary stats
- Filter states for each specialized page

#### Navigation Targets

- `pages/2_👥_Persona_Insights.py` - Persona analysis
- `pages/3_📊_Content_Matrix.py` - Content performance
- `pages/4_💡_Opportunity_Impact.py` - Improvement roadmap
- `pages/5_🌟_Success_Library.py` - Success patterns

### Fix Checklist

- [ ] Data loader initialization working
- [ ] Session state caching functional
- [ ] Executive metrics calculating correctly
- [ ] Tier filtering updating assessments
- [ ] Opportunity identification working
- [ ] Success story calculation functional
- [ ] Contextual navigation buttons working
- [ ] Smart filter setting operational
- [ ] Page navigation preserving state
- [ ] Sidebar metrics displaying correctly

---

## 1. 🔬 Methodology

### Purpose

Display the complete audit methodology from `config/methodology.yaml` in an interactive, educational format.

### Data Sources

- `config/methodology.yaml` - Core methodology configuration
- Metadata, scoring, classification, criteria, messaging, and gating rules

### Page Structure

#### Header Section

- Page title: "🔬 Methodology"
- Description of the methodology framework

#### Tab Navigation (6 tabs)

1. **Overview** - High-level methodology summary
2. **Scoring Framework** - Detailed scoring system
3. **Page Classification** - Tier system explanation
4. **Tier Criteria** - Criteria by tier breakdown
5. **Brand Standards** - Messaging hierarchy and standards
6. **Quality Controls** - Gating rules and validation

### Key Components

#### Overview Tab

- **Brand Score Calculation**: Formula display with weights
- **Crisis Impact Multipliers**: How reputation issues affect scores
- **Process Overview**: 5-stage audit process explanation

#### Scoring Framework Tab

- **Score Scale**: 0-10 scoring with descriptors
- **Score Interpretation**: Color-coded performance levels
- **Evidence Requirements**: Mandatory evidence standards for high/low scores

#### Page Classification Tab

- **Three-Tier System**: Tier 1 (Brand), Tier 2 (Value Prop), Tier 3 (Functional)
- **Classification Triggers**: What determines each tier
- **Offsite Channel Classification**: Social media and third-party platforms

### Logic Flow

1. Load methodology.yaml configuration
2. Parse and structure data into display format
3. Create interactive tabs with expandable sections
4. Format and display comprehensive methodology documentation

### Fix Checklist

- [ ] YAML file loading and parsing working
- [ ] All 6 tabs displaying correctly
- [ ] Crisis multipliers calculation display
- [ ] Evidence requirements properly formatted
- [ ] Brand messaging hierarchy showing
- [ ] Expandable criteria sections functional
- [ ] Gating rules properly categorized

---

## 2. 👥 Persona Insights

### Purpose

Comprehensive persona analysis combining comparison view and individual deep-dive functionality.

### Data Sources

- `master_df` - Unified audit data
- `BrandHealthDataLoader` - Data access layer
- `BrandHealthMetricsCalculator` - Metrics computation

### Page Structure

#### Header Section

- Title: "👥 Persona Insights"
- Description: "Understand how different personas experience your brand"

#### Persona Selector

- Dropdown: 'All' (comparison mode) or individual persona
- Mode indicator: Comparison vs Deep Dive

### Two Analysis Modes

#### Comparison Mode ('All' selected)

- **Persona Performance Cards**: Grid of persona summary cards
- **Performance Metrics**: Overall score, page count, status indicator
- **Comparison Charts**: Bar charts and pie charts comparing personas
- **Ranking Insights**: Top/bottom performing personas with recommendations

#### Deep Dive Mode (Individual persona)

- **Overview Metrics**: Score, page count, tier distribution, critical issues
- **Page Performance**: Top/bottom performing pages for this persona
- **First Impressions**: Qualitative feedback and persona quotes

### Logic Flow

1. Load unified data via BrandHealthDataLoader
2. Initialize metrics calculator
3. Display persona selector with mode detection
4. Branch to comparison or individual analysis
5. Generate persona-level aggregations
6. Display visualizations and insights

### Fix Checklist

- [ ] Data loader initialization working
- [ ] Persona selector with 'All' option functional
- [ ] Comparison mode showing all personas
- [ ] Individual mode filtering correctly
- [ ] Persona performance cards displaying
- [ ] Charts rendering with proper data

---

## 3. 📊 Content Matrix

### Purpose

Comprehensive content analysis by tier, criteria, and performance with interactive filtering.

### Data Sources

- `master_df` - Unified audit data
- `TierAnalyzer` - Tier-specific analysis
- `BrandHealthMetricsCalculator` - Performance metrics

### Page Structure

#### Header Section

- Title: "📊 Content Matrix"
- Description: "Where do we pass/fail across content types?"

#### Content Filters (4 columns)

- **Persona**: All + individual personas
- **Content Tier**: All + specific tiers
- **Min Score**: Slider 0-10
- **Performance Level**: Excellent/Good/Fair/Poor

### Main Analysis Sections

#### Performance Overview

- **Business Impact Context**: Status message based on performance
- **Key Metrics**: Average score, total pages, performance distribution
- **Performance Cards**: Excellent (≥8), Good (6-8), Needs Work (<6)
- **Distribution Chart**: Bar chart of performance levels

#### Tier Performance Analysis

- **Tier Summary Table**: Performance metrics by content tier
- **Tier Comparison Chart**: Average scores by tier with color coding
- **Tier Insights**: Best/worst performing tiers with recommendations

#### Content Performance Heatmap

- **Interactive Heatmap**: Tier × Criteria performance matrix
- **Hotspots/Coldspots**: Top 3 best and worst performing areas
- **Color-coded visualization**: Red/Yellow/Green performance scale

### Logic Flow

1. Load and validate master dataset
2. Initialize tier analyzer and metrics calculator
3. Display filtering controls with validation
4. Apply filters and update all visualizations
5. Calculate tier-level aggregations
6. Generate heatmap data (tier × criteria)
7. Compute criteria performance rankings

### Fix Checklist

- [ ] Filter controls working correctly
- [ ] Filter application updating all sections
- [ ] Performance overview calculating properly
- [ ] Tier analysis displaying correctly
- [ ] Heatmap rendering with proper data

---

## 4. 💡 Opportunity Impact

### Purpose

Prioritized improvement roadmap with impact scoring and strategic recommendations.

### Data Sources

- `master_df` - Unified audit data
- `BrandHealthMetricsCalculator` - Opportunity identification
- Impact calculation: `(10 - Current Score) × Tier Weight`

### Page Structure

#### Header Section

- Title: "💡 Opportunity & Impact"
- Description: "Which gaps matter most and what should we do?"
- **Impact Calculation Explanation**: Expandable formula documentation

#### Opportunity Controls (4 columns)

- **Min Impact Score**: Slider 0-10
- **Effort Level**: All/Low/Medium/High
- **Priority Level**: All/Urgent/High/Medium/Low
- **Content Tier**: All + specific tiers

### Main Analysis Sections

#### Impact Overview

- **Key Metrics**: Total opportunities, avg impact, high impact count, low effort count
- **Impact vs Effort Matrix**: Scatter plot with tier coloring
- **Tier Performance**: Opportunities grouped by content tier

#### Prioritized Opportunities

- **Filtered Opportunity List**: Based on selected criteria
- **Tier Grouping**: Opportunities organized by content tier
- **Opportunity Cards**: Expandable cards with detailed analysis

### Logic Flow

1. Load opportunity data and calculate impact scores
2. Apply filtering based on user selections
3. Sort opportunities by impact and priority
4. Group by tier for organized display
5. Generate detailed opportunity cards with evidence

### Fix Checklist

- [ ] Impact calculation formula working
- [ ] Opportunity controls filtering correctly
- [ ] Impact vs effort scatter plot rendering
- [ ] Opportunity cards expanding/collapsing
- [ ] Tier grouping logic functional

---

## 5. 🌟 Success Library

### Purpose

Comprehensive success analysis with replication templates and pattern identification.

### Data Sources

- `master_df` - Unified audit data
- `BrandHealthMetricsCalculator` - Success identification
- Success threshold filtering (default 7.5/10)

### Page Structure

#### Header Section

- Title: "🌟 Success Library"
- Description: "What already works that we can emulate?"

#### Success Controls (4 columns)

- **Success Threshold**: Slider 5.0-10.0 (default 7.5)
- **Persona Focus**: All + individual personas
- **Content Tier**: All + specific tiers
- **Max Success Stories**: Number input 5-50

### Main Analysis Sections

#### Success Overview

- **Key Metrics**: Total pages, success pages, success rate, avg success score
- **Success Distribution**: Excellent (≥9), Very Good (8-9), Good (7.5-8)
- **Success Charts**: Distribution histogram, success by tier pie chart

#### Detailed Success Stories

- **Page-Level Aggregation**: Grouped by page_id to avoid duplicates
- **Tier Organization**: Success stories grouped by content tier
- **Success Story Cards**: Expandable detailed analysis

### Logic Flow

1. Apply success threshold and filters
2. Aggregate to page level to avoid duplicates
3. Calculate success metrics and distributions
4. Group success stories by tier
5. Generate detailed success cards with evidence

### Fix Checklist

- [ ] Success threshold filtering working
- [ ] Page-level aggregation preventing duplicates
- [ ] Success metrics calculating correctly
- [ ] Success story cards expanding
- [ ] Pattern analysis generating insights

---

## 6. 📋 Reports Export

### Purpose

Comprehensive data exploration, custom report generation, and export functionality.

### Data Sources

- `master_df` - Unified audit data
- `datasets` - All individual datasets
- `BrandHealthDataLoader` - Data access layer

### Page Structure

#### Header Section

- Title: "📋 Reports & Export"
- Description: "How do I analyze data and run new audits?"

#### Three Main Tabs

1. **📊 Data Explorer** - Interactive data exploration
2. **📈 Custom Reports** - Report generation
3. **📦 Export Center** - Data export functionality

### Tab 1: Data Explorer

#### Data Overview

- **Key Metrics**: Total records, unique pages, personas, data completeness
- **Dataset Breakdown**: Table showing all datasets with record counts

#### Interactive Filters (4 columns)

- **Persona**: All + individual personas
- **Tier**: All + specific tiers
- **Score Range**: Min/max slider
- **Columns**: Multi-select column chooser

### Logic Flow

1. Load all datasets and master dataframe
2. Calculate data overview metrics
3. Apply interactive filters to data
4. Display filtered results in chosen format

### Fix Checklist

- [ ] Data loading and overview working
- [ ] Interactive filters applying correctly
- [ ] Table view pagination functional
- [ ] Export functionality operational

---

## 7. 🚀 Run Audit

### Purpose

Integrated audit execution interface with real-time monitoring and post-processing.

### Data Sources

- File uploads (persona .md files, URL lists)
- Subprocess execution of audit_tool.main
- Generated audit outputs for processing

### Page Structure

#### Header Section

- Title: "🚀 Run Brand Audit"
- Description: Methodology and AI provider support information

#### Audit Configuration (2 columns)

#### Column 1: Persona & Model Selection

- **Step 1**: Persona file upload (.md files)
- **Step 1.5**: AI Model selection (OpenAI vs Anthropic)

#### Column 2: URL Configuration

- **Step 2**: URL input methods (paste or upload)

### Audit Execution

#### Run Button

- **Validation**: Require persona file + URLs
- **State Management**: Prevent multiple concurrent audits
- **Progress Tracking**: Real-time audit monitoring

### Logic Flow

1. Initialize audit state variables
2. Display configuration interface
3. Validate inputs and enable/disable controls
4. Execute audit subprocess with live monitoring
5. Handle completion and offer post-processing

### Fix Checklist

- [ ] File upload handling working
- [ ] Model selection persisting
- [ ] URL validation calculating correctly
- [ ] Subprocess execution working
- [ ] Live log streaming functional

---

## 8. 🔍 Social Media Analysis

### Purpose

Cross-platform social media brand presence and engagement analysis dashboard.

### Data Sources

- `audit_inputs/social_media/sm_dashboard_data.md` - Social media metrics
- Markdown table parsing for structured data

### Page Structure

#### Header Section

- Title: "🔍 Social Media Analysis"
- Description: "Cross-platform brand presence and engagement insights"

#### Analysis Filters (2 columns)

- **Platform**: Multi-select with all platforms
- **Region**: Multi-select with all regions

### Main Analysis Sections

#### Key Metrics Overview (4 cards)

- **Active Platforms**: Count of selected platforms
- **Regional Presences**: Count of regional implementations
- **High Engagement Channels**: Count of high-performing channels
- **Strong Brand Consistency**: Count of consistent implementations

### Logic Flow

1. Load and parse social media markdown data
2. Extract structured tables from markdown
3. Apply platform and region filters
4. Calculate and display key metrics

### Fix Checklist

- [ ] Markdown file loading working
- [ ] Table extraction parsing correctly
- [ ] Filter controls updating all sections
- [ ] Key metrics calculating correctly

---

## 9. 👤 Persona Viewer

### Purpose

Deep individual persona analysis combining profiles, journey maps, and performance data.

### Data Sources

- `audit_inputs/personas/[P1-P5].md` - Persona profile files
- `audit_inputs/persona_journeys/unified_journey_analysis.md` - Journey data
- `master_df` - Performance data by persona

### Page Structure

#### Header Section

- Title: "👤 Persona Viewer"
- Description: "Deep-dive analysis combining strategic context, journey experience, and performance data"

#### Persona Selection

- **Dropdown**: P1-P5 with friendly names mapping
- **Persona Overview**: 4-column metrics display

### Four-Tab Interface

#### Tab 1: 📋 Profile

- **Content Source**: Load from `personas/[ID].md`
- **Section Parsing**: Extract numbered/headed sections
- **Expandable Display**: Collapsible sections with formatted content

#### Tab 2: 🗺️ Journey

- **Journey Data**: Load from unified_journey_analysis.md
- **5-Step Journey**: Homepage → Services → Proof → Thought Leadership → Contact
- **Gap Analysis**: Severity scoring 1-5 per step

#### Tab 3: 📊 Performance

- **Performance Data**: Filter master_df by persona
- **Page Performance**: Top/bottom performing pages
- **Metrics Display**: Scores, engagement, sentiment analysis

#### Tab 4: 🗣️ Voice

- **Voice Analysis**: Extract persona voice patterns
- **Quote Extraction**: First-person statements and feedback

### Logic Flow

1. Load available personas from directory
2. Display persona selector with friendly names
3. Load profile, journey, and performance data
4. Display comprehensive four-tab analysis

### Fix Checklist

- [ ] Persona file loading working
- [ ] Tab persistence across persona changes
- [ ] Profile section parsing correctly
- [ ] Journey visualization rendering

---

## 10. 🎨 Visual Brand Hygiene

### Purpose

Interactive visual brand compliance monitoring across digital properties.

### Data Sources

- `audit_inputs/visual_brand/brand_audit_scores.csv` - Visual brand audit data
- **Independent Dataset**: NOT part of unified audit data

### Page Structure

#### Header Section

- Title: "🎨 Visual Brand Hygiene"
- Description: "Interactive dashboard for monitoring visual brand consistency"

#### Executive Summary (4 cards)

- **Overall Brand Health**: Average final score across all pages
- **Critical Issues**: Count of pages scoring <7.0
- **Pages Audited**: Total page count
- **Compliance Rate**: Percentage scoring ≥8.0

### Five-Tab Interface

#### Tab 1: 📊 Criteria Performance

- **Radar Chart**: 6 criteria performance visualization
- **Detailed Table**: Sortable performance breakdown

#### Tab 2: 🏢 Tier Analysis

- **Tier Statistics**: Performance metrics by content tier
- **Tier Comparison Chart**: Average scores by tier

#### Tab 3: 🌍 Regional Consistency

- **Regional Analysis**: Performance by region
- **Regional Radar Chart**: Multi-region comparison

#### Tab 4: 🔧 Fix Prioritization

- **Priority Matrix**: Impact vs effort prioritization
- **Critical Issues**: Immediate attention items

#### Tab 5: 📖 Brand Standards

- **Brand Guidelines**: Reference documentation
- **Color Palette**: Official brand colors

### Logic Flow

1. Load brand audit CSV data
2. Process and enhance with derived fields
3. Calculate key performance metrics
4. Generate executive summary
5. Display five specialized analysis tabs

### Fix Checklist

- [ ] CSV data loading correctly
- [ ] Data enhancement fields calculating
- [ ] Executive summary metrics accurate
- [ ] All 5 tabs displaying properly
- [ ] Charts maintaining fixed sizes

---

## General Troubleshooting Checklist

### Data Loading Issues

- [ ] File paths correctly resolved from page locations
- [ ] Required data files exist in expected locations
- [ ] Data loading functions handling errors gracefully

### Component Integration

- [ ] Brand styling CSS applied consistently
- [ ] Data loader components imported correctly
- [ ] Metrics calculator functioning properly

### Interactive Elements

- [ ] Filters updating all dependent visualizations
- [ ] Tab navigation maintaining state
- [ ] Expandable sections working properly

### Error Handling

- [ ] Empty datasets handled gracefully
- [ ] Missing files showing appropriate warnings
- [ ] Invalid data displaying helpful error messages

---

**End of Functional Specifications**

Use this document as your reference when fixing broken pages that have good styling but broken functionality. Each section provides the complete logic flow and component structure needed to restore full functionality.
