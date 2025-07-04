# Social Media Analysis Dashboard - Master Page Specification

## Overview

**Page Name:** 8_🔍_Social_Media_Analysis.py  
**Purpose:** Provide comprehensive analysis and visualization of Sopra Steria Benelux's social media presence, incorporating master audit findings and persona-based scoring.  
**Target Users:** Marketing teams, brand managers, digital strategists, executives, and social media managers.  
**Data Source:** MASTER_SM_DASHBOARD_DATA.md (updated with audit scores)

## Page Architecture

### 1. Header Section
```python
st.set_page_config(page_title="Social Media Analysis", page_icon="🔍", layout="wide")
st.title("🔍 Social Media Analysis")
st.markdown("### Cross-platform brand presence and engagement insights")
st.markdown("---")
```

### 2. Executive Summary Dashboard
- **Critical Alerts** (Red banner if X/Twitter inactive)
- **Overall Health Score** (4.15/10 with visual gauge)
- **Key Metrics Cards** (4-6 cards in columns)
  - Total Reach: 876,248 followers
  - Platform Coverage: 4/5 platforms active
  - Average Score: 4.15/10
  - Critical Issues: 1 (X/Twitter)
  - Top Platform: LinkedIn (6.8/10)
  - Weakest Platform: X/Twitter (1.2/10)

### 3. Platform Health Overview
```python
# Visual health status grid
# Each platform shown as a card with:
# - Platform icon
# - Score (color-coded)
# - Status indicator (✓, ⚠️, 🚨)
# - Follower count
# - Last activity
```

### 4. Interactive Filters
```python
col1, col2, col3, col4 = st.columns(4)

with col1:
    platform_filter = st.multiselect(
        "Select Platforms",
        ["LinkedIn", "Instagram", "Facebook", "X/Twitter", "YouTube"],
        default=["LinkedIn", "Instagram", "Facebook", "X/Twitter"]
    )

with col2:
    region_filter = st.selectbox(
        "Select Region",
        ["All", "Global", "UK", "Benelux"],
        index=0
    )

with col3:
    persona_filter = st.multiselect(
        "Select Personas",
        ["P1-C-Suite", "P2-Tech Leaders", "P3-Programme", "P4-Cybersecurity", "P5-Tech Influencers"],
        default=["P1-C-Suite", "P2-Tech Leaders", "P3-Programme", "P4-Cybersecurity", "P5-Tech Influencers"]
    )

with col4:
    view_mode = st.radio(
        "View Mode",
        ["Overview", "Detailed Analysis", "Recommendations"],
        horizontal=True
    )
```

### 5. Main Visualizations

#### 5.1 Platform Performance Matrix
```python
# Heatmap showing scores by platform and persona
# Color scale: Red (0-3) → Yellow (4-6) → Green (7-10)
# Interactive tooltips with detailed scores
```

#### 5.2 Follower Distribution
```python
# Treemap or sunburst chart showing follower distribution
# Hierarchical: Platform → Region → Follower Count
# Click to drill down into regions
```

#### 5.3 Content Performance Analysis
```python
# Grouped bar chart: Content types by platform
# Y-axis: Engagement level
# Color: Performance score
# Filterable by platform/region
```

#### 5.4 Trend Analysis (if temporal data available)
```python
# Line chart showing score trends over time
# Multiple lines for different platforms
# Annotations for major events/changes
```

### 6. Detailed Analysis Tabs

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Platform Deep Dive", "Persona Analysis", "Content Strategy", "Regional Insights", "Competitive Position"])

with tab1:
    # Platform-specific detailed metrics
    # Strengths/weaknesses
    # Top performing content
    
with tab2:
    # Persona-platform alignment matrix
    # Gap analysis by persona
    # Recommendations per persona
    
with tab3:
    # Content type performance
    # Content calendar view
    # Content gap analysis
    
with tab4:
    # Regional comparison charts
    # Regional strategy differences
    # Localization insights
    
with tab5:
    # Benchmark against industry
    # Competitive gaps
    # Best practices from competitors
```

### 7. Recommendations Dashboard

#### 7.1 Priority Action Matrix
```python
# 2x2 matrix: Impact vs Effort
# Plotly scatter with sized bubbles
# Color by priority level
# Click for detailed action plans
```

#### 7.2 90-Day Roadmap
```python
# Gantt chart or timeline visualization
# Shows phased approach
# Milestones and success metrics
# Progress tracking capability
```

#### 7.3 Quick Wins Section
```python
# Card-based layout
# Each card shows:
# - Action item
# - Expected impact
# - Time to implement
# - Resources needed
```

### 8. KPI Tracking Section
```python
# Metrics with current vs target
# Progress bars
# Trend sparklines
# Color-coded status
```

## Data Processing Functions

```python
@st.cache_data
def load_social_media_data():
    """Load and process social media master data"""
    # Read from MASTER_SM_DASHBOARD_DATA.md
    # Parse tables using pandas
    # Return structured dataframes
    
def calculate_health_scores(df):
    """Calculate platform and overall health scores"""
    # Weight by follower reach
    # Apply persona importance weights
    # Return aggregated scores
    
def identify_critical_issues(df):
    """Identify and flag critical issues"""
    # Check for inactive platforms
    # Low scores (<3)
    # Missing persona coverage
    # Return issues list with severity
    
def generate_recommendations(df, issues):
    """Generate actionable recommendations"""
    # Map issues to actions
    # Prioritize by impact
    # Estimate effort
    # Return recommendations dataframe
```

## Visualization Functions

```python
def create_platform_heatmap(df, personas, platforms):
    """Create interactive heatmap of platform-persona scores"""
    fig = px.imshow(
        score_matrix,
        labels=dict(x="Platform", y="Persona", color="Score"),
        x=platforms,
        y=personas,
        color_continuous_scale="RdYlGn",
        range_color=[0, 10]
    )
    return fig

def create_follower_treemap(df):
    """Create hierarchical follower distribution"""
    fig = px.treemap(
        df,
        path=['Platform', 'Region'],
        values='Followers',
        color='Score',
        color_continuous_scale="RdYlGn"
    )
    return fig

def create_action_matrix(recommendations):
    """Create impact vs effort matrix"""
    fig = px.scatter(
        recommendations,
        x="Effort",
        y="Impact",
        size="Priority",
        color="Category",
        hover_data=['Action', 'Timeline'],
        title="Priority Action Matrix"
    )
    return fig
```

## Interactive Features

### 1. Drill-Down Capability
- Click on platform → Show detailed metrics
- Click on persona → Show specific recommendations
- Click on region → Show localized insights

### 2. Export Functionality
```python
# Export buttons for:
# - Executive summary (PDF)
# - Detailed data (Excel)
# - Recommendations (PowerPoint)
# - Raw data (CSV)
```

### 3. Comparison Tools
- Period-over-period comparison
- Platform comparison
- Regional comparison
- Persona performance comparison

### 4. What-If Scenarios
```python
# Sliders to simulate:
# - Posting frequency changes
# - Content mix adjustments
# - Resource allocation
# Show projected impact on scores
```

## Performance Optimizations

```python
# Use session state for filters
if 'platform_filter' not in st.session_state:
    st.session_state.platform_filter = ["LinkedIn", "Instagram", "Facebook", "X/Twitter"]

# Cache expensive calculations
@st.cache_data(ttl=3600)
def calculate_metrics(df):
    return processed_metrics

# Lazy loading for detailed views
if view_mode == "Detailed Analysis":
    load_detailed_metrics()
```

## Integration Points

### 1. Link to Other Dashboard Pages
- Persona Insights (for detailed persona analysis)
- Content Performance (for content deep-dive)
- Audit Results (for page-level issues)

### 2. Data Refresh Mechanism
```python
# Manual refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# Auto-refresh indicator
st.text(f"Last updated: {last_update_time}")
```

### 3. Alerts and Notifications
```python
# Check for critical issues
if critical_issues:
    st.error(f"🚨 {len(critical_issues)} critical issues require immediate attention!")
    with st.expander("View Critical Issues"):
        for issue in critical_issues:
            st.write(f"- {issue}")
```

## Mobile Responsiveness

```python
# Detect mobile and adjust layout
if st.session_state.get('mobile_view', False):
    # Single column layout
    # Simplified visualizations
    # Touch-friendly controls
else:
    # Full desktop experience
```

## Future Enhancements

### Phase 1 (Next Sprint)
- Temporal data integration
- Automated score updates
- Email alerts for critical issues

### Phase 2 (Q2 2025)
- AI-powered content recommendations
- Competitor tracking integration
- Sentiment analysis

### Phase 3 (Q3 2025)
- Predictive analytics
- ROI calculation
- Automated reporting

## Success Metrics

| Metric | Target | Measurement |
|--------|---------|------------|
| Page Load Time | <2 seconds | Performance monitoring |
| User Engagement | >5 min average session | Analytics tracking |
| Action Items Completed | >80% within timeline | Progress tracking |
| Score Improvement | +2 points in 6 months | Platform scores |

## Implementation Checklist

- [ ] Set up page structure and navigation
- [ ] Implement data loading functions
- [ ] Create executive summary section
- [ ] Build platform health overview
- [ ] Implement interactive filters
- [ ] Create main visualizations
- [ ] Build detailed analysis tabs
- [ ] Implement recommendations dashboard
- [ ] Add export functionality
- [ ] Test mobile responsiveness
- [ ] Integrate with other pages
- [ ] Add performance monitoring
- [ ] Deploy to production
- [ ] Create user documentation
- [ ] Schedule training sessions