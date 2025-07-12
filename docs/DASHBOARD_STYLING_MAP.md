# Dashboard Styling Map
*Complete functional components and styling requirements for all 17 dashboard pages*

**Generated:** December 2024  
**Purpose:** Comprehensive styling reference for React dashboard pages

---

## Overview

This document maps the functional components and required CSS classes for all 17 dashboard pages. Each page section includes:
- **Functionality**: What the page does
- **Components**: Key functional areas
- **Required Classes**: Specific CSS classes needed
- **Priority**: Critical vs. optional styling

---

## Page-by-Page Analysis

### 1. AuditReports.tsx
**File Size:** 17KB, 493 lines  
**Functionality:** HTML report viewer with report selection and display capabilities

#### Components:
- **Report Selection Interface**
  - Dropdown for report selection
  - Auto-loading of default reports
  - Report metadata display

- **Report Display Area**
  - HTML content rendering
  - Iframe/content area for reports
  - Placeholder content for missing reports

- **Report Actions**
  - Regenerate reports functionality
  - Download individual reports
  - Download all reports

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page container */
.container--section         /* Section containers */
.container--feedback        /* Error/loading states */

/* Typography */
.heading--page             /* "📄 Audit Reports" */
.heading--section          /* Section headings */
.text--body               /* Descriptive text */

/* Interactive Elements */
.select--form             /* Report selection dropdown */
.button--action           /* Primary action buttons */
.button--secondary        /* Secondary actions */

/* State Indicators */
.loading--state           /* Loading spinner/text */
```

**Priority:** HIGH - Core functionality for report access

---

### 2. ContentMatrix.tsx
**File Size:** 33KB, 856 lines  
**Functionality:** Comprehensive content analysis with performance scoring and strategic insights

#### Components:
- **Content Analysis Filters**
  - Persona selection dropdown
  - Content tier filtering
  - Minimum score slider
  - Performance level selection

- **Performance Overview**
  - Key metrics cards
  - Total pages analyzed
  - Average scores by category
  - Performance distribution

- **Tier Performance Analysis**
  - Tier-specific metrics
  - Comparative performance charts
  - Tier weighting display

- **Content Performance Heatmap**
  - Visual performance matrix
  - Interactive heatmap charts
  - Score distribution visualization

- **Criteria Deep Dive**
  - Detailed criteria breakdowns
  - Evidence-based scoring
  - Performance insights

- **Page Drill Down**
  - Individual page analysis
  - Detailed performance metrics
  - Evidence display

- **Persona-Specific Evidence Context**
  - Persona reaction analysis
  - Context-specific insights
  - Evidence correlation

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Major sections */
.container--card           /* Content cards */
.container--feedback       /* No data states */
.container--grid           /* Grid layouts */

/* Typography */
.heading--page             /* "📊 Content Matrix" */
.heading--section          /* "🎛️ Content Analysis Filters" */
.heading--subsection       /* Sub-section headings */
.heading--card             /* Card titles */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized text */

/* Form Controls */
.select--form             /* Filter dropdowns */
.label--form              /* Form labels */
.input--form              /* Range sliders */

/* Data Display */
.metric--display          /* Performance metrics */
.badge--status            /* Status indicators */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** HIGH - Core analytics functionality

---

### 3. DatasetDetail.tsx
**File Size:** 1.3KB, 45 lines  
**Functionality:** Simple dataset viewer using URL parameters

#### Components:
- **Dataset Display**
  - Dynamic column generation
  - Data table rendering
  - Uses PageContainer component

#### Required Classes:
```css
/* Minimal - relies on PageContainer and DataTable components */
/* No custom page-specific classes needed */
```

**Priority:** LOW - Uses existing components

---

### 4. Methodology.tsx
**File Size:** 19KB, 496 lines  
**Functionality:** Tabbed methodology documentation viewer with comprehensive audit framework

#### Components:
- **Tab Navigation**
  - 6 tabs: Overview, Scoring, Classification, Criteria, Standards, Controls
  - Active tab highlighting
  - Tab content switching

- **Overview Section**
  - Brand health audit methodology
  - Brand score calculation formulas
  - Crisis impact multipliers
  - Audit process steps

- **Scoring Framework**
  - Scoring scale explanation
  - Score interpretation guides
  - Evidence requirements
  - Mandatory evidence standards

- **Classification System**
  - Three-tier classification
  - Tier weightings and criteria
  - Offsite channel classification
  - Trigger examples

- **Criteria Documentation**
  - Detailed criteria definitions
  - Scoring rubrics
  - Assessment guidelines

- **Brand Standards**
  - Brand compliance requirements
  - Visual identity guidelines
  - Messaging standards

- **Quality Controls**
  - Audit quality assurance
  - Validation processes
  - Review procedures

#### Required Classes:
```css
/* Layout Structure */
.container--content         /* Content containers */
.container--section         /* Section divisions */
.container--feedback        /* Highlighted content */
.container--grid           /* Grid layouts */

/* Typography */
.heading--section          /* "Brand Health Audit Methodology" */
.heading--card             /* Subsection headings */
.text--body               /* Body content */
.text--display            /* Metric displays */

/* Navigation */
.button--tab              /* Tab navigation buttons */

/* Utilities */
.spacing--sm              /* Small spacing */
```

**Priority:** MEDIUM - Documentation page

---

### 5. PersonaInsights.tsx
**File Size:** 16KB, 455 lines  
**Functionality:** Cross-persona performance analysis and strategic persona comparison

#### Components:
- **Persona Analysis Focus**
  - Persona selection dropdown
  - Analysis mode toggle (comparison vs individual)
  - Mode indicator display

- **Persona Comparison Analysis**
  - Performance comparison cards
  - Sorted persona rankings
  - Comparison charts and visualizations
  - Persona ranking insights

- **Individual Persona Analysis**
  - Deep dive into specific persona
  - Detailed page analysis
  - Performance metrics
  - Evidence display

- **Cross-Persona Insights**
  - Strategic insights across personas
  - Pattern identification
  - Recommendations

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Persona cards */
.container--feedback       /* Alert messages */

/* Typography */
.heading--page             /* "👥 Persona Insights" */
.heading--section          /* "🎯 Persona Analysis Focus" */
.heading--subsection       /* "📊 Persona Performance Comparison" */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized content */

/* Form Controls */
.select--form             /* Persona selection */
.label--form              /* Form labels */

/* Data Display */
.metric--display          /* Performance metrics */
.badge--status            /* Status indicators */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** HIGH - Core persona analysis

---

### 6. PersonaViewer.tsx
**File Size:** 61KB, 1393 lines  
**Functionality:** Comprehensive persona profile viewer with multi-tab interface

#### Components:
- **Persona Selection**
  - Persona dropdown selection
  - Persona metadata display
  - Loading states

- **Tab Navigation**
  - Profile, Journey, Performance, Voice Analysis tabs
  - Active tab management
  - Tab content switching

- **Profile Section**
  - Collapsible profile sections
  - Markdown content parsing
  - Section expansion/collapse
  - Formatted profile display

- **Journey Analysis**
  - Journey step visualization
  - Gap severity indicators
  - Quick fixes display
  - Journey flow charts

- **Performance Analysis**
  - Performance data filtering
  - Tier-based filtering
  - Score distribution
  - Performance metrics

- **Voice Analysis**
  - Voice statistics
  - Sentiment analysis
  - Theme identification
  - Quote categorization
  - Search functionality

- **Evidence Browser Integration**
  - Evidence display
  - Quote filtering
  - Evidence categorization

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Major sections */
.container--card           /* Content cards */
.container--feedback       /* Status messages */
.container--grid           /* Grid layouts */

/* Typography */
.heading--page             /* "👤 Persona Viewer" */
.heading--section          /* Section headings */
.heading--subsection       /* Subsection headings */
.heading--card             /* Card titles */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized text */

/* Navigation */
.button--tab              /* Tab navigation */
.button--action           /* Primary actions */
.button--secondary        /* Secondary actions */

/* Form Controls */
.select--form             /* Dropdowns */
.label--form              /* Form labels */
.input--form              /* Search inputs */

/* Data Display */
.metric--display          /* Performance metrics */
.badge--status            /* Status badges */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** HIGH - Core persona functionality

---

### 7. ReportsExport.tsx
**File Size:** 35KB, 855 lines  
**Functionality:** Multi-tab interface for data exploration, custom reports, and HTML generation

#### Components:
- **Tab Navigation**
  - Data Explorer, Custom Reports, HTML Generation tabs
  - Active tab management
  - Tab content switching

- **Data Explorer**
  - Dataset metadata display
  - Data filtering controls
  - Dataset viewing functionality
  - Data quality metrics

- **Filter Controls**
  - Persona filtering
  - Tier filtering
  - Score range sliders
  - Display mode selection

- **Data Overview**
  - Total records metrics
  - Data completeness indicators
  - Quality analysis
  - Dataset statistics

- **Custom Report Generation**
  - Report configuration options
  - Format selection
  - Generation controls
  - Download functionality

- **HTML Report Generation**
  - Generation mode selection
  - Report options configuration
  - Batch generation controls
  - Progress tracking

- **Export Functionality**
  - Multiple format support
  - Export configuration
  - Batch export options
  - Progress indicators

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */
.container--feedback       /* Status messages */

/* Typography */
.heading--page             /* "📊 Reports & Export" */
.heading--section          /* Section headings */
.heading--subsection       /* Subsection headings */
.text--body               /* Body text */
.text--display            /* Metric displays */

/* Navigation */
.button--tab              /* Tab navigation */
.button--action           /* Primary actions */
.button--secondary        /* Secondary actions */

/* Form Controls */
.select--form             /* Dropdowns */
.label--form              /* Form labels */
.input--form              /* Range inputs */

/* Data Display */
.metric--display          /* Data metrics */
.badge--status            /* Status indicators */

/* State Management */
.loading--state           /* Loading/generation states */
```

**Priority:** MEDIUM - Export functionality

---

### 8. RunAudit.tsx
**File Size:** 37KB, 956 lines  
**Functionality:** Audit execution interface with real-time monitoring

#### Components:
- **Persona Input Interface**
  - File upload for persona
  - Text paste interface
  - Tab switching (paste/upload)
  - Persona content validation

- **URL Input Interface**
  - URL text input
  - URL file upload
  - URL validation
  - Invalid URL feedback

- **Audit Configuration**
  - Model selection (OpenAI/Anthropic)
  - Configuration options
  - Validation checks

- **Audit Execution Controls**
  - Start audit button
  - Stop audit functionality
  - Reset audit state
  - Progress monitoring

- **Real-time Status Display**
  - Progress indicators
  - Status text updates
  - Log streaming
  - Processing state tracking

- **Results Display**
  - Completion notifications
  - Score cards
  - Result summaries
  - Next steps guidance

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */
.container--feedback       /* Status/error messages */

/* Typography */
.heading--page             /* "🚀 Run Audit" */
.heading--section          /* Section headings */
.text--body               /* Body text */
.text--display            /* Status displays */

/* Navigation */
.button--tab              /* Tab navigation */
.button--action           /* Primary actions */
.button--secondary        /* Secondary actions */

/* Form Controls */
.select--form             /* Model selection */
.label--form              /* Form labels */
.input--form              /* Text inputs */

/* State Management */
.loading--state           /* Loading indicators */
.status--*                /* Status indicators */

/* Data Display */
.metric--display          /* Progress displays */
```

**Priority:** HIGH - Core audit functionality

---

### 9. SocialMediaAnalysis.tsx
**File Size:** 42KB, 1112 lines  
**Functionality:** Social media platform analysis across personas with comprehensive insights

#### Components:
- **Executive Summary**
  - Overall health status
  - Critical alert banners
  - Key performance indicators
  - Health status cards

- **Platform Health Overview**
  - Individual platform cards
  - Health status indicators
  - Performance metrics
  - Critical issues highlighting

- **Platform Performance Analysis**
  - Detailed platform breakdowns
  - Performance comparisons
  - Trend analysis
  - Score distributions

- **Persona Analysis**
  - Persona-platform matrix
  - Cross-persona insights
  - Performance correlations
  - Persona-specific recommendations

- **Insights and Recommendations**
  - Strategic insights
  - Actionable recommendations
  - Priority categorization
  - Implementation timelines

- **Detailed Analysis Tabs**
  - Platform Deep Dive
  - Content Strategy Analysis
  - Performance Analytics
  - Quick Wins Analysis
  - Action Priority Matrix

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */
.container--feedback       /* Alert banners */

/* Typography */
.heading--page             /* "🔍 Social Media Analysis" */
.heading--section          /* "📊 Executive Summary" */
.heading--subsection       /* Subsection headings */
.heading--card             /* Card titles */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized content */

/* Navigation */
.button--tab              /* Tab navigation */
.button--action           /* Action buttons */

/* Form Controls */
.select--form             /* Filter controls */
.label--form              /* Form labels */

/* Data Display */
.metric--display          /* Performance metrics */
.badge--status            /* Status badges */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** HIGH - Social media insights

---

### 10. StrategicRecommendations.tsx
**File Size:** 23KB, 606 lines  
**Functionality:** Strategic intelligence with comprehensive recommendations and action plans

#### Components:
- **Strategic Intelligence Overview**
  - Executive summary metrics
  - High-impact opportunities
  - Quick win identification
  - Critical issues tracking

- **Strategic Themes**
  - Theme identification
  - Business impact analysis
  - Current vs target scores
  - Competitive risk assessment
  - Key insights display

- **Recommendations Engine**
  - Detailed recommendations
  - Implementation steps
  - Success metrics
  - Timeline planning
  - Effort assessment

- **Competitive Context**
  - Market positioning
  - Benchmark comparisons
  - Opportunity identification
  - Vulnerability assessment

- **Tier Analysis**
  - Tier-specific insights
  - Business context
  - Priority assessment
  - Performance analysis

- **Implementation Roadmap**
  - Phased approach
  - Focus areas
  - Expected impact
  - Resource planning

- **Business Impact Assessment**
  - Optimization potential
  - Improvement areas
  - Competitive advantages
  - Success stories

- **Fallback Recommendations**
  - Basic recommendations view
  - Simplified interface
  - Core functionality maintenance

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */
.container--feedback       /* Alert messages */

/* Typography */
.heading--page             /* "🎯 Strategic Intelligence" */
.heading--section          /* Section headings */
.heading--subsection       /* Subsection headings */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized content */

/* Form Controls */
.select--form             /* Filter controls */
.label--form              /* Form labels */

/* Interactive Elements */
.button--action           /* Primary actions */
.button--secondary        /* Secondary actions */

/* Data Display */
.metric--display          /* Performance metrics */
.badge--status            /* Status indicators */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** HIGH - Strategic planning

---

### 11. VisualBrandHygiene.tsx
**File Size:** 60KB, 1330 lines  
**Functionality:** Visual brand compliance analysis with comprehensive brand standards

#### Components:
- **Brand Standards Display**
  - Primary color palette
  - Secondary color palette
  - Color specifications (hex, CMYK)
  - Brand color descriptions

- **Overall Metrics**
  - Total pages analyzed
  - Average compliance scores
  - Top performers count
  - Compliance rate calculation

- **Criteria Analysis**
  - Logo compliance scoring
  - Color palette adherence
  - Typography compliance
  - Layout structure assessment
  - Image quality evaluation
  - Brand messaging consistency

- **Visualization Components**
  - Heatmap by tier/domain
  - Radar charts for criteria
  - Performance distribution
  - Tier analysis charts
  - Regional analysis

- **Priority Matrix**
  - Business impact scoring
  - Implementation effort assessment
  - ROI calculations
  - Priority quadrant mapping
  - Recommendation prioritization

- **Detailed Analysis**
  - Data table with compliance scores
  - Violation tracking
  - Page-level analysis
  - Filtering capabilities

- **Tabbed Interface**
  - Criteria overview
  - Brand standards
  - Priority matrix
  - Detailed analysis

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */
.container--feedback       /* Status messages */

/* Typography */
.heading--page             /* "🎨 Visual Brand Hygiene" */
.heading--section          /* Section headings */
.heading--subsection       /* Subsection headings */
.heading--card             /* Card titles */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized content */

/* Navigation */
.button--tab              /* Tab navigation */
.button--action           /* Action buttons */

/* Form Controls */
.select--form             /* Filter controls */
.label--form              /* Form labels */

/* Data Display */
.metric--display          /* Compliance metrics */
.badge--status            /* Status indicators */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** HIGH - Brand compliance

---

### 12. SuccessLibrary.tsx
**File Size:** 25KB, 647 lines  
**Functionality:** Success stories library with filtering and analysis capabilities

#### Components:
- **Success Library Controls**
  - Success threshold slider
  - Maximum stories limit
  - Evidence type filtering
  - Search functionality

- **Overview Metrics**
  - Total pages analyzed
  - Success pages count
  - Success rate calculation
  - Average score display
  - Excellence level distribution

- **Success Stories Display**
  - Story cards with scores
  - Excellence level indicators
  - Tier and persona information
  - Percentile rankings

- **Pattern Analysis**
  - Success patterns by tier
  - Pattern data visualization
  - Trend identification
  - Performance correlations

- **Evidence Integration**
  - Evidence items display
  - Evidence categorization
  - Quote integration
  - Supporting data

- **Replication Templates**
  - Template generation
  - Key elements identification
  - Replication guidelines
  - Implementation guidance

- **Visualization Components**
  - Score distribution charts
  - Tier success pie charts
  - Performance trends
  - Success metrics

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--content         /* Content containers */
.container--card           /* Success story cards */
.container--feedback       /* Status messages */

/* Typography */
.heading--page             /* "🌟 Success Library" */
.heading--section          /* Section headings */
.text--body               /* Body text */
.text--display            /* Metric displays */

/* Form Controls */
.select--form             /* Filter controls */
.label--form              /* Form labels */
.input--form              /* Search inputs */

/* Interactive Elements */
.button--action           /* Action buttons */

/* Success Level Styling */
.success--excellent       /* Excellent performance */
.success--good            /* Good performance */
.success--card            /* Standard success card */
.success--improving       /* Improving performance */

/* State Management */
.loading--state           /* Loading indicators */
```

**Priority:** MEDIUM - Success tracking

---

### 13. OpportunityImpact.tsx
**File Size:** 26KB, 735 lines  
**Functionality:** Opportunity impact analysis with comprehensive calculation framework

#### Components:
- **Impact Calculation Explainer**
  - Expandable explanation section
  - Formula documentation
  - Calculation examples
  - Methodology explanation

- **Opportunity Controls**
  - Impact threshold slider
  - Effort level filtering
  - Priority level filtering
  - Content tier filtering
  - Maximum opportunities limit

- **Impact Overview**
  - Overview metrics
  - Opportunity summaries
  - Impact calculations
  - Priority distributions

- **Prioritized Opportunities**
  - Expandable opportunity cards
  - Ranking system
  - Impact scoring
  - Implementation details

- **AI Strategic Recommendations**
  - AI-generated insights
  - Strategic recommendations
  - Pattern analysis
  - Implementation guidance

- **Criteria Deep Dive**
  - Detailed criteria analysis
  - Performance breakdowns
  - Improvement opportunities
  - Evidence-based insights

- **Action Roadmap**
  - Implementation phases
  - Timeline planning
  - Resource allocation
  - Expected outcomes

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */
.container--feedback       /* Status messages */

/* Typography */
.heading--page             /* "💡 Opportunity & Impact" */
.heading--section          /* Section headings */
.heading--subsection       /* Subsection headings */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized content */

/* Form Controls */
.select--form             /* Filter controls */
.label--form              /* Form labels */
.input--form              /* Range sliders */

/* Interactive Elements */
.button--action           /* Action buttons */

/* Utilities */
.spacing--sm              /* Small spacing */
```

**Priority:** HIGH - Opportunity analysis

---

### 14. ExecutiveDashboard.tsx
**File Size:** 18KB, 445 lines  
**Functionality:** Executive command center with strategic decision-making tools

#### Components:
- **Brand Health Overview**
  - Overall brand health score
  - Critical issues count
  - Quick wins identification
  - Success pages metrics

- **Strategic Focus Controls**
  - Tier filtering
  - Focus area selection
  - Analysis scope control

- **Strategic Brand Assessment**
  - Distinctiveness scoring
  - Resonance measurement
  - Conversion effectiveness
  - Strategic positioning

- **Performance Indicators**
  - Score color coding
  - Status classifications
  - Performance thresholds
  - Health indicators

- **Executive Metrics**
  - 30-second decision metrics
  - Key performance indicators
  - Strategic recommendations
  - Action priorities

- **Integration Components**
  - PagesList integration
  - Success stories display
  - Opportunity highlights
  - Strategic insights

#### Required Classes:
```css
/* Layout Structure */
.container--layout          /* Main page layout */
.container--section         /* Section containers */
.container--card           /* Content cards */

/* Typography */
.heading--page             /* "🎯 Brand Health Command Center" */
.heading--section          /* "Brand Health Overview" */
.heading--subsection       /* "🎯 Strategic Focus" */
.text--body               /* Body text */
.text--display            /* Metric displays */
.text--emphasis           /* Emphasized content */

/* Form Controls */
.select--form             /* Filter controls */
.label--form              /* Form labels */

/* Data Display */
.metric--display          /* Performance metrics */
.badge--status            /* Status indicators */

/* Status Indicators */
.status--critical         /* Critical status */
.status--fair             /* Fair status */
.status--good             /* Good status */
.status--excellent        /* Excellent status */
```

**Priority:** HIGH - Executive overview

---

### 15. PagesList.tsx
**File Size:** 908B, 35 lines  
**Functionality:** Simple pages list with bar chart visualization

#### Components:
- **Pages Display**
  - Simple list format
  - Bar chart visualization
  - Score display
  - Top 10 pages focus

#### Required Classes:
```css
/* Minimal styling needed */
/* Uses Recharts for visualization */
/* Basic headings only */
```

**Priority:** LOW - Simple visualization

---

### 16. DatasetList.tsx
**File Size:** 865B, 36 lines  
**Functionality:** Simple dataset list with navigation links

#### Components:
- **Dataset List**
  - Simple list format
  - Navigation links
  - Basic routing

#### Required Classes:
```css
/* Minimal styling needed */
/* Basic list and link styling */
```

**Priority:** LOW - Simple navigation

---

## Core CSS Classes Summary

Based on the analysis of all 17 pages, here are the essential CSS classes needed:

### Layout Structure (5 classes)
```css
.container--layout          /* Main page layout container */
.container--section         /* Section containers */
.container--content         /* Content containers */
.container--card           /* Card containers */
.container--feedback       /* Feedback/alert containers */
.container--grid           /* Grid layout containers */
```

### Typography Hierarchy (8 classes)
```css
.heading--page             /* Main page titles */
.heading--section          /* Section headings */
.heading--subsection       /* Subsection headings */
.heading--card             /* Card headings */
.text--body               /* Body text */
.text--display            /* Display text (metrics, values) */
.text--emphasis           /* Emphasized text */
.spacing--sm              /* Small spacing utility */
```

### Interactive Elements (8 classes)
```css
.button--action           /* Primary action buttons */
.button--secondary        /* Secondary buttons */
.button--tab              /* Tab navigation */
.select--form             /* Form selects */
.label--form              /* Form labels */
.input--form              /* Form inputs */
.loading--state           /* Loading indicators */
```

### Data Display (6 classes)
```css
.metric--display          /* Metric values */
.badge--status            /* Status badges */
.status--critical         /* Critical status indicator */
.status--fair             /* Fair status indicator */
.status--good             /* Good status indicator */
.status--excellent        /* Excellent status indicator */
```

### Specialized Classes (4 classes)
```css
.success--excellent       /* Excellent success level */
.success--good            /* Good success level */
.success--card            /* Standard success card */
.success--improving       /* Improving success level */
```

**Total: 31 core classes** that handle 90%+ of styling needs across all 17 dashboard pages.

---

## Implementation Priority

### HIGH Priority (Core Functionality)
- AuditReports.tsx
- ContentMatrix.tsx
- PersonaInsights.tsx
- PersonaViewer.tsx
- RunAudit.tsx
- SocialMediaAnalysis.tsx
- StrategicRecommendations.tsx
- VisualBrandHygiene.tsx
- OpportunityImpact.tsx
- ExecutiveDashboard.tsx

### MEDIUM Priority (Supporting Features)
- ReportsExport.tsx
- Methodology.tsx
- SuccessLibrary.tsx

### LOW Priority (Simple Components)
- DatasetDetail.tsx
- PagesList.tsx
- DatasetList.tsx

---

## Next Steps

1. **Create Core CSS Framework**: Implement the 31 core classes
2. **Test High Priority Pages**: Ensure core functionality works
3. **Refine Styling**: Adjust based on visual requirements
4. **Add Specialized Classes**: Implement page-specific needs
5. **Optimize Performance**: Minimize CSS bundle size
6. **Document Usage**: Create usage guidelines for developers

---

*This document serves as the definitive styling map for the dashboard. All 17 pages have been analyzed for their functional components and styling requirements.* 