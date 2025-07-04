# Social Media Dashboard Page Specification

## Overview

**Page Name:** 8_🔍_Social_Media_Analysis.py  
**Purpose:** Provide comprehensive analysis and visualization of Sopra Steria's social media presence across platforms and regions.  
**Target Users:** Marketing teams, brand managers, digital strategists, and executives.

## Page Structure

The Social Media Analysis dashboard page will be structured into the following sections:

### 1. Header and Introduction

- Page title: "🔍 Social Media Analysis"
- Subtitle: "Cross-platform brand presence and engagement insights"
- Brief description of the dashboard's purpose and data sources

### 2. Filters and Controls

- Platform filter (LinkedIn, Twitter, Facebook, Instagram, YouTube, All)
- Region filter (Global, UK, Benelux, All)
- Content type filter (Thought Leadership, Recruitment, CSR, etc.)
- Time period selector (if temporal data becomes available)

### 3. Key Metrics Overview

- Total followers across platforms (with breakdown by platform)
- Average engagement rate across platforms
- Posting frequency metrics
- Brand consistency score
- Overall social media health score

### 4. Platform Performance Analysis

- Bar chart comparing followers across platforms and regions
- Engagement metrics comparison (likes, comments, shares)
- Posting frequency comparison
- Performance score heatmap by platform and region

### 5. Content Strategy Analysis

- Content type distribution by platform
- Performance metrics by content type
- Content type heatmap (platform × content type)
- Top performing content examples

### 6. Brand Consistency Analysis

- Tone & messaging consistency radar chart
- Visual style consistency metrics
- Brand voice consistency across platforms
- Regional variations in brand presentation

### 7. Regional Strategy Comparison

- Side-by-side metrics for Global, UK, and Benelux
- Regional strategy differences visualization
- Audience engagement by region
- Regional strengths and weaknesses

### 8. Recommendations and Insights

- Platform-specific improvement opportunities
- Content strategy recommendations
- Quick wins identification
- Long-term strategy suggestions

## Data Requirements

The dashboard will use data from the structured markdown file `sm_dashboard_data.md`, which contains:

### Platform Metrics Table

```
| Platform | Region | Followers | Engagement Rate | Posting Frequency | Content Quality | Visual Consistency | Overall Score |
|----------|--------|-----------|-----------------|-------------------|-----------------|-------------------|---------------|
```

### Content Analysis Table

```
| Platform | Region | Content Type | Frequency | Engagement | Performance Score |
|----------|--------|--------------|-----------|------------|-------------------|
```

### Brand Consistency Table

```
| Platform | Region | Tone Score | Messaging Score | Visual Style Score | Brand Voice Score | Overall Consistency |
|----------|--------|------------|----------------|-------------------|-------------------|---------------------|
```

### Recommendations Table

```
| Platform | Region | Recommendation | Impact | Effort | Priority |
|----------|--------|----------------|--------|--------|----------|
```

## UI Components and Visualizations

### Key Metrics Cards

- Metric cards with platform icons
- Color-coded performance indicators
- Trend indicators (if temporal data available)

### Platform Comparison Chart

- Grouped bar chart for follower counts
- Stacked bar chart for engagement metrics
- Line chart for posting frequency

### Content Performance Heatmap

- Interactive heatmap showing performance by content type and platform
- Color scale from red (poor) to green (excellent)
- Tooltips with detailed metrics

### Brand Consistency Radar Chart

- Multi-axis radar chart showing consistency dimensions
- Overlaid plots for different platforms or regions
- Interactive legend for filtering

### Regional Comparison Cards

- Side-by-side comparison cards
- Sparklines for key metrics
- Strength/weakness indicators

### Recommendations Section

- Expandable cards for each recommendation
- Priority indicators
- Impact/effort visualization

## Implementation Guidelines

### Code Structure

- Follow existing dashboard page patterns
- Modular functions for data loading, processing, and visualization
- Clear separation of data processing and UI components

### Data Loading

```python
# Example data loading approach
def load_social_media_data():
    """Load social media data from markdown file"""
    # Load platform metrics
    platform_metrics = pd.read_csv("audit_inputs/social_media/sm_dashboard_data.md",
                                  skiprows=[0],
                                  delimiter="|",
                                  skipinitialspace=True)

    # Process and clean data
    platform_metrics = platform_metrics.iloc[:, 1:-1]  # Remove empty first/last columns from markdown table

    return platform_metrics
```

### Visualization Functions

```python
# Example visualization function
def create_platform_comparison_chart(data, metric="Followers"):
    """Create platform comparison chart"""
    fig = px.bar(
        data,
        x="Platform",
        y=metric,
        color="Region",
        title=f"{metric} by Platform and Region",
        barmode="group"
    )

    fig.update_layout(height=400)
    return fig
```

### Filter Implementation

```python
# Example filter implementation
def display_filters(data):
    """Display dashboard filters"""
    col1, col2, col3 = st.columns(3)

    with col1:
        platforms = ["All"] + sorted(data["Platform"].unique().tolist())
        selected_platform = st.selectbox("Platform", platforms)

    with col2:
        regions = ["All"] + sorted(data["Region"].unique().tolist())
        selected_region = st.selectbox("Region", regions)

    with col3:
        content_types = ["All"] + sorted(data["Content Type"].unique().tolist())
        selected_content = st.selectbox("Content Type", content_types)

    return selected_platform, selected_region, selected_content
```

## Performance Considerations

- Use caching for data loading and processing
- Optimize visualizations for performance
- Consider lazy loading for complex visualizations
- Implement efficient filtering that doesn't require reloading data

## Integration with Existing Dashboard

- Maintain consistent styling with other dashboard pages
- Use the same brand colors and fonts
- Ensure navigation consistency
- Consider cross-linking with related dashboard pages (Persona Insights, Content Matrix)

## Future Enhancements

- Temporal analysis of social media performance over time
- Competitor benchmarking
- Sentiment analysis of comments and engagement
- AI-powered content recommendations
- Automated social media health scoring
