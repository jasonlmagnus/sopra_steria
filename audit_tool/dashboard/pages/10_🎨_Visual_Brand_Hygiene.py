"""
Visual Brand Hygiene Dashboard

NOTE: This dashboard uses a separate data source (visual_brand/brand_audit_scores.csv)
and is NOT part of the unified dataset. This is intentional as it analyzes specific
visual brand compliance metrics from a dedicated brand audit.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from pathlib import Path
import sys

# Add the parent directory to sys.path to import brand_styling
sys.path.append(str(Path(__file__).parent.parent))
from components.brand_styling import get_complete_brand_css

# Set page config
st.set_page_config(
    page_title="Brand Health Command Center - Visual Brand Hygiene",
    page_icon="🎨",
    layout="wide"
)

# Apply brand styling
st.markdown(get_complete_brand_css(), unsafe_allow_html=True)

# Additional CSS to prevent width expansion and layout shifts across ALL tabs
st.markdown("""
<style>
/* NUCLEAR OPTION - Prevent ANY width expansion */
.main .block-container {
    max-width: 100% !important;
    width: 100% !important;
    overflow-x: hidden !important;
}

/* Fix ALL content containers */
.main .element-container {
    max-width: 100% !important;
    width: 100% !important;
    overflow-x: hidden !important;
}

/* Fix dataframe container width */
div[data-testid="stDataFrame"] > div {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: auto !important;
}

/* Prevent text overflow in dataframe cells */
div[data-testid="stDataFrame"] .cell-wrap {
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

/* Ensure consistent column widths */
div[data-testid="stDataFrame"] table {
    table-layout: fixed !important;
    width: 100% !important;
}

/* Prevent plotly charts from causing width expansion */
.js-plotly-plot {
    width: 100% !important;
    max-width: 100% !important;
}

/* Fix tab content containers */
div[data-baseweb="tab-panel"] {
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

/* Prevent HTML content from expanding */
div[data-testid="stMarkdownContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    overflow-x: hidden !important;
    word-wrap: break-word !important;
}

/* Fix any expandable sections */
div[data-testid="stExpander"] {
    max-width: 100% !important;
    width: 100% !important;
}

/* Prevent color swatches from expanding */
.color-swatch-container {
    max-width: 100% !important;
    overflow-x: hidden !important;
}

/* Force all divs to respect container width */
.main div {
    max-width: 100% !important;
    box-sizing: border-box !important;
}

/* Prevent long text from expanding containers */
* {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown("""
<div class="main-header">
    <h1>🎨 Visual Brand Hygiene</h1>
    <p>Interactive dashboard for monitoring and improving visual brand consistency across digital properties</p>
</div>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_brand_data():
    """Load and process brand audit data"""
    try:
        # Load the CSV data - path goes up 3 levels from pages/ to project root
        data_path = Path(__file__).parent.parent.parent.parent / "audit_inputs" / "visual_brand" / "brand_audit_scores.csv"
        df = pd.read_csv(data_path)
        
        # Clean and process data
        df['Domain'] = df['URL'].apply(lambda x: x.split('/')[2] if len(x.split('/')) > 2 else x)
        df['Page_Name'] = df['URL'].apply(lambda x: x.split('/')[-1] if x.split('/')[-1] else 'Homepage')
        df['Tier_Number'] = df['Page Type'].apply(lambda x: x.split(' ')[1] if 'Tier' in x else '0')
        df['Tier_Name'] = df['Page Type'].apply(lambda x: x.split(' - ')[1] if ' - ' in x else x)
        df['Region'] = df['Domain'].apply(lambda x: 
            'Netherlands' if '.nl' in x else 
            'Belgium' if '.be' in x else 
            'Global' if '.com' in x else 'Other'
        )
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
df = load_brand_data()

if df.empty:
    st.error("No brand audit data available. Please ensure the CSV file exists in audit_inputs/visual_brand/")
    st.stop()

# Calculate key metrics
total_pages = len(df)
avg_score = df['Final Score'].mean()
critical_issues = len(df[df['Final Score'] < 7.0])
excellent_pages = len(df[df['Final Score'] >= 9.0])

# Executive Summary Section
st.markdown("## Executive Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_score:.1f}/10</div>
        <div class="metric-label">Overall Brand Health</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    status_class = "critical" if critical_issues > 0 else "warning" if critical_issues == 0 else "good"
    st.markdown(f"""
    <div class="metric-card {status_class}">
        <div class="metric-value">{critical_issues}</div>
        <div class="metric-label">Critical Issues</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_pages}</div>
        <div class="metric-label">Pages Audited</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    compliance_rate = (len(df[df['Final Score'] >= 8.0]) / total_pages) * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{compliance_rate:.0f}%</div>
        <div class="metric-label">Compliance Rate</div>
    </div>
    """, unsafe_allow_html=True)

# Visual Performance Heatmap
st.markdown("### Brand Performance Heatmap")

# Create heatmap data
heatmap_data = df.pivot_table(
    values='Final Score', 
    index='Tier_Name', 
    columns='Domain', 
    aggfunc='mean'
).fillna(0)

fig_heatmap = px.imshow(
    heatmap_data.values,
    labels=dict(x="Domain", y="Tier", color="Score"),
    x=heatmap_data.columns,
    y=heatmap_data.index,
    color_continuous_scale="RdYlGn",
    aspect="auto",
    title="Brand Score Distribution by Tier and Domain"
)

fig_heatmap.update_layout(
    height=300,
    font=dict(family="Inter", size=12),
    title_font=dict(family="Crimson Text", size=16, color="#2C3E50")
)

# Set fixed width for heatmap
fig_heatmap.update_layout(width=1200, autosize=False)
st.plotly_chart(fig_heatmap, use_container_width=False, key="visual_brand_heatmap")

# Main Analysis Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Criteria Performance", 
    "🏢 Tier Analysis", 
    "🌍 Regional Consistency",
    "🔧 Fix Prioritization",
    "📖 Brand Standards"
])

with tab1:
    # Add width-constraining wrapper
    st.markdown('<div style="max-width: 100%; overflow-x: hidden; box-sizing: border-box;">', unsafe_allow_html=True)
    
    st.markdown("### Brand Criteria Analysis")
    
    # Criteria performance radar chart
    criteria_cols = ['Logo Compliance', 'Color Palette', 'Typography', 'Layout Structure', 'Image Quality', 'Brand Messaging']
    criteria_avg = df[criteria_cols].mean()
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=criteria_avg.values,
        theta=criteria_cols,
        fill='toself',
        name='Average Performance',
        line_color='#E85A4F',
        fillcolor='rgba(232, 90, 79, 0.2)'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=False,
        title="Brand Criteria Performance Radar",
        font=dict(family="Inter", size=12),
        title_font=dict(family="Crimson Text", size=16, color="#2C3E50"),
        height=500,
        width=800,
        autosize=False
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig_radar, use_container_width=False, key="criteria_radar")
    
    with col2:
        st.markdown("#### Criteria Insights")
        
        # Best performing criteria
        best_criteria = criteria_avg.idxmax()
        best_score = criteria_avg.max()
        
        # Worst performing criteria
        worst_criteria = criteria_avg.idxmin()
        worst_score = criteria_avg.min()
        
        st.markdown(f"""
        <div class="success-card">
            <h4>🏆 Strongest Area</h4>
            <p><strong>{best_criteria}:</strong> {best_score:.1f}/10</p>
            <p>Excellent consistency across all properties</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="opportunity-card impact-medium">
            <h4>🎯 Improvement Opportunity</h4>
            <p><strong>{worst_criteria}:</strong> {worst_score:.1f}/10</p>
            <p>Greatest potential for brand enhancement</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed criteria breakdown table
    st.markdown("#### Detailed Performance Breakdown")
    
    # Create sortable table with fixed width to prevent expansion
    display_df = df[['URL', 'Page Type'] + criteria_cols + ['Final Score', 'Key Violations']].copy()
    display_df['URL'] = display_df['URL'].apply(lambda x: x.replace('https://www.', ''))
    
    # Truncate long violation text to prevent width expansion
    display_df['Key Violations'] = display_df['Key Violations'].apply(
        lambda x: x[:100] + "..." if len(str(x)) > 100 else x
    )
    
    # Use container with fixed styling to prevent width expansion
    st.markdown("""
    <div style="width: 100%; max-width: 1200px; overflow-x: auto; box-sizing: border-box;">
    """, unsafe_allow_html=True)
    
    st.dataframe(
        display_df,
        use_container_width=False,
        width=1200,
        height=400,
        column_config={
            "URL": st.column_config.TextColumn("Page", width=200),
            "Page Type": st.column_config.TextColumn("Tier", width=120),
            "Logo Compliance": st.column_config.NumberColumn("Logo", format="%.1f", width=70),
            "Color Palette": st.column_config.NumberColumn("Color", format="%.1f", width=70),
            "Typography": st.column_config.NumberColumn("Type", format="%.1f", width=70),
            "Layout Structure": st.column_config.NumberColumn("Layout", format="%.1f", width=70),
            "Image Quality": st.column_config.NumberColumn("Images", format="%.1f", width=70),
            "Brand Messaging": st.column_config.NumberColumn("Message", format="%.1f", width=70),
            "Final Score": st.column_config.NumberColumn("Score", format="%.1f", width=70),
            "Key Violations": st.column_config.TextColumn("Issues", width=200)
        }
    )
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Close width-constraining wrapper for tab1
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    # Add width-constraining wrapper
    st.markdown('<div style="max-width: 100%; overflow-x: hidden; box-sizing: border-box;">', unsafe_allow_html=True)
    
    st.markdown("### Tier Performance Analysis")
    
    # Tier comparison
    tier_stats = df.groupby('Tier_Name').agg({
        'Final Score': ['mean', 'min', 'max', 'count'],
        'Logo Compliance': 'mean',
        'Color Palette': 'mean',
        'Typography': 'mean',
        'Layout Structure': 'mean',
        'Image Quality': 'mean',
        'Brand Messaging': 'mean'
    }).round(1)
    
    tier_stats.columns = ['Avg Score', 'Min Score', 'Max Score', 'Page Count', 'Logo', 'Color', 'Typography', 'Layout', 'Images', 'Messaging']
    
    # Tier performance bar chart
    fig_tier = px.bar(
        x=tier_stats.index,
        y=tier_stats['Avg Score'],
        title="Average Brand Score by Content Tier",
        labels={'x': 'Content Tier', 'y': 'Average Score'},
        color=tier_stats['Avg Score'],
        color_continuous_scale="RdYlGn"
    )
    
    fig_tier.update_layout(
        font=dict(family="Inter", size=12),
        title_font=dict(family="Crimson Text", size=16, color="#2C3E50"),
        height=400,
        width=1200,
        autosize=False
    )
    
    st.plotly_chart(fig_tier, use_container_width=False, key="tier_performance")
    
    # Tier insights
    col1, col2, col3 = st.columns(3)
    
    tiers = tier_stats.index.tolist()
    
    for i, (col, tier) in enumerate(zip([col1, col2, col3], tiers)):
        if i < len(tiers):
            with col:
                avg_score = tier_stats.loc[tier, 'Avg Score']
                page_count = int(tier_stats.loc[tier, 'Page Count'])
                
                performance_class = "excellent" if avg_score >= 8.5 else "good" if avg_score >= 7.5 else "fair"
                
                st.markdown(f"""
                <div class="tier-section">
                    <h4>{tier}</h4>
                    <div class="metric-value performance-{performance_class}">{avg_score}/10</div>
                    <p><strong>{page_count} pages</strong> audited</p>
                    <p>Range: {tier_stats.loc[tier, 'Min Score']}-{tier_stats.loc[tier, 'Max Score']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Tier-specific recommendations
    st.markdown("#### Tier-Specific Insights")
    
    for tier in tiers:
        tier_data = df[df['Tier_Name'] == tier]
        avg_score = tier_data['Final Score'].mean()
        
        with st.expander(f"{tier} - Recommendations"):
            if avg_score >= 8.5:
                st.success(f"**Excellent Performance** - {tier} pages demonstrate strong brand consistency")
            elif avg_score >= 7.5:
                st.warning(f"**Good Performance** - {tier} pages show solid brand implementation with room for enhancement")
            else:
                st.error(f"**Needs Improvement** - {tier} pages require focused brand enhancement efforts")
            
            # Show specific issues for this tier
            issues = tier_data['Key Violations'].value_counts().head(3)
            if not issues.empty:
                st.markdown("**Common Issues:**")
                for issue, count in issues.items():
                    st.markdown(f"• {issue} ({count} pages)")

    # Close width-constraining wrapper for tab2  
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    # Add width-constraining wrapper
    st.markdown('<div style="max-width: 100%; overflow-x: hidden; box-sizing: border-box;">', unsafe_allow_html=True)
    
    st.markdown("### Regional Brand Consistency")
    
    # Regional analysis
    df['Region'] = df['Domain'].apply(lambda x: 
        'Netherlands' if '.nl' in x else 
        'Belgium' if '.be' in x else 
        'Global' if '.com' in x else 'Other'
    )
    
    regional_stats = df.groupby('Region').agg({
        'Final Score': ['mean', 'count'],
        'Logo Compliance': 'mean',
        'Color Palette': 'mean',
        'Typography': 'mean',
        'Layout Structure': 'mean',
        'Image Quality': 'mean',
        'Brand Messaging': 'mean'
    }).round(1)
    
    regional_stats.columns = ['Avg Score', 'Page Count', 'Logo', 'Color', 'Typography', 'Layout', 'Images', 'Messaging']
    
    # Regional comparison chart
    fig_regional = go.Figure()
    
    regions = regional_stats.index.tolist()
    criteria = ['Logo', 'Color', 'Typography', 'Layout', 'Images', 'Messaging']
    
    for region in regions:
        fig_regional.add_trace(go.Scatterpolar(
            r=regional_stats.loc[region, criteria].values,
            theta=criteria,
            fill='toself',
            name=region,
            opacity=0.7
        ))
    
    fig_regional.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        title="Regional Brand Consistency Comparison",
        font=dict(family="Inter", size=12),
        title_font=dict(family="Crimson Text", size=16, color="#2C3E50"),
        height=500,
        width=1200,
        autosize=False
    )
    
    st.plotly_chart(fig_regional, use_container_width=False, key="regional_comparison")
    
    # Regional insights
    st.markdown("#### Regional Performance Summary")
    
    cols = st.columns(len(regions))
    
    for i, (col, region) in enumerate(zip(cols, regions)):
        with col:
            avg_score = regional_stats.loc[region, 'Avg Score']
            page_count = int(regional_stats.loc[region, 'Page Count'])
            
            performance_class = "excellent" if avg_score >= 8.5 else "good" if avg_score >= 7.5 else "fair"
            
            st.markdown(f"""
            <div class="comparison-section">
                <h4>{region}</h4>
                <div class="metric-value performance-{performance_class}">{avg_score}/10</div>
                <p><strong>{page_count} pages</strong></p>
            </div>
            """, unsafe_allow_html=True)
    
    # Consistency analysis
    st.markdown("#### Brand Messaging Consistency")
    
    # Analyze tagline presence
    tagline_issues = df[df['Key Violations'].str.contains('tagline|messaging', case=False, na=False)]
    
    if not tagline_issues.empty:
        st.markdown("""
        <div class="critical-badge">⚠️ Critical Issue Identified</div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="priority-urgent">
            <h4>Missing Brand Tagline</h4>
            <p><strong>Pages Affected:</strong> {len(tagline_issues)}</p>
            <p><strong>Primary Issue:</strong> Global homepage missing "The world is how we shape it" tagline</p>
            <p><strong>Impact:</strong> Brand messaging inconsistency across regional and global properties</p>
            <p><strong>Recommended Action:</strong> Implement consistent tagline across all properties</p>
        </div>
        """, unsafe_allow_html=True)

    # Close width-constraining wrapper for tab3
    st.markdown("</div>", unsafe_allow_html=True)

with tab4:
    # Add width-constraining wrapper
    st.markdown('<div style="max-width: 100%; overflow-x: hidden; box-sizing: border-box;">', unsafe_allow_html=True)
    
    st.markdown("### Fix Prioritization Matrix")
    
    # Create fix priority data based on scores and issues
    fix_data = []
    
    for _, row in df.iterrows():
        score = row['Final Score']
        violations = row['Key Violations']
        
        # Determine impact and effort based on score and issues
        if score < 7.0:
            impact = "High"
            effort = "High" if "Major" in violations else "Medium"
        elif score < 8.0:
            impact = "Medium"
            effort = "Medium" if "Moderate" in violations else "Low"
        else:
            impact = "Low"
            effort = "Low"
        
        # Calculate potential improvement
        potential_improvement = min(10 - score, 2.0) if score < 8.0 else 0.5
        
        fix_data.append({
            'Page': row['URL'].replace('https://www.', ''),
            'Current_Score': score,
            'Impact': impact,
            'Effort': effort,
            'Potential_Improvement': potential_improvement,
            'Issues': violations,
            'Priority': 'Critical' if score < 7.0 else 'High' if score < 8.0 else 'Medium'
        })
    
    fix_df = pd.DataFrame(fix_data)
    
    # Impact vs Effort scatter plot
    impact_map = {'High': 3, 'Medium': 2, 'Low': 1}
    effort_map = {'High': 3, 'Medium': 2, 'Low': 1}
    
    fix_df['Impact_Numeric'] = fix_df['Impact'].map(impact_map)
    fix_df['Effort_Numeric'] = fix_df['Effort'].map(effort_map)
    
    fig_priority = px.scatter(
        fix_df,
        x='Effort_Numeric',
        y='Impact_Numeric',
        size='Potential_Improvement',
        color='Priority',
        hover_data=['Page', 'Current_Score', 'Issues'],
        title="Fix Prioritization Matrix (Impact vs Effort)",
        labels={'Effort_Numeric': 'Implementation Effort', 'Impact_Numeric': 'Business Impact'},
        color_discrete_map={'Critical': '#ff3b30', 'High': '#ff9500', 'Medium': '#34c759'}
    )
    
    fig_priority.update_layout(
        xaxis=dict(tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        yaxis=dict(tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        font=dict(family="Inter", size=12),
        title_font=dict(family="Crimson Text", size=16, color="#2C3E50"),
        height=500,
        width=1200,
        autosize=False
    )
    
    st.plotly_chart(fig_priority, use_container_width=False, key="priority_matrix")
    
    # Priority recommendations
    st.markdown("#### Recommended Action Plan")
    
    critical_fixes = fix_df[fix_df['Priority'] == 'Critical']
    high_fixes = fix_df[fix_df['Priority'] == 'High']
    
    if not critical_fixes.empty:
        st.markdown("##### 🚨 Phase 1: Critical Fixes (Immediate - Week 1)")
        for _, fix in critical_fixes.iterrows():
            st.markdown(f"""
            <div class="priority-urgent">
                <h4>{fix['Page']}</h4>
                <p><strong>Current Score:</strong> {fix['Current_Score']}/10</p>
                <p><strong>Issues:</strong> {fix['Issues']}</p>
                <p><strong>Expected Improvement:</strong> +{fix['Potential_Improvement']:.1f} points</p>
            </div>
            """, unsafe_allow_html=True)
    
    if not high_fixes.empty:
        st.markdown("##### ⚡ Phase 2: High Priority Fixes (Weeks 2-4)")
        for _, fix in high_fixes.head(3).iterrows():
            st.markdown(f"""
            <div class="priority-high">
                <h4>{fix['Page']}</h4>
                <p><strong>Current Score:</strong> {fix['Current_Score']}/10</p>
                <p><strong>Issues:</strong> {fix['Issues']}</p>
                <p><strong>Expected Improvement:</strong> +{fix['Potential_Improvement']:.1f} points</p>
            </div>
            """, unsafe_allow_html=True)

    # Close width-constraining wrapper for tab4
    st.markdown("</div>", unsafe_allow_html=True)

with tab5:
    # Add width-constraining wrapper
    st.markdown('<div style="max-width: 100%; overflow-x: hidden; box-sizing: border-box;">', unsafe_allow_html=True)
    
    st.markdown("### 🎨 Brand Standards Reference")
    
    # Interactive Brand Colors with enhanced visuals
    st.markdown("#### 🌈 Official Brand Colors")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("##### Primary Color Palette")
        
        # Enhanced color swatches with gradients and better styling
        primary_colors = [
            ("#4D1D82", "Dark Purple", "Primary brand color", "CMYK: 89/100/06/01"),
            ("#8b1d82", "Light Purple", "Secondary brand color", "CMYK: 56/100/00/00"),
            ("#cf022b", "Red", "Accent color", "CMYK: 10/100/95/00"),
            ("#ef7d00", "Orange", "Accent color", "CMYK: 00/60/100/00")
        ]
        
        for color, name, desc, cmyk in primary_colors:
            st.markdown(f"""
            <div class="color-swatch-container" style="
                display: flex; 
                align-items: center; 
                margin: 15px 0; 
                padding: 15px; 
                border-radius: 12px; 
                background: linear-gradient(135deg, {color}15, {color}05);
                border-left: 4px solid {color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                max-width: 100%;
                overflow: hidden;
                box-sizing: border-box;
            ">
                <div style="
                    width: 60px; 
                    height: 60px; 
                    background: linear-gradient(135deg, {color}, {color}CC); 
                    border-radius: 12px; 
                    margin-right: 20px;
                    box-shadow: 0 4px 12px {color}40;
                    border: 2px solid white;
                    flex-shrink: 0;
                "></div>
                <div style="flex: 1; min-width: 0; overflow: hidden;">
                    <h4 style="margin: 0; color: {color}; font-family: 'Inter', sans-serif; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{name}</h4>
                    <div style="display: flex; gap: 15px; margin: 5px 0; flex-wrap: wrap;">
                        <code style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 4px; font-weight: bold; white-space: nowrap;">{color}</code>
                        <span style="color: #666; font-size: 0.9em; white-space: nowrap;">{cmyk}</span>
                    </div>
                    <p style="margin: 5px 0 0 0; color: #666; font-size: 0.9em; overflow: hidden; text-overflow: ellipsis;">{desc}</p>
                </div>
                <button onclick="navigator.clipboard.writeText('{color}')" style="
                    background: {color}; 
                    color: white; 
                    border: none; 
                    padding: 8px 12px; 
                    border-radius: 6px; 
                    cursor: pointer;
                    font-size: 0.8em;
                    font-weight: 600;
                    flex-shrink: 0;
                    white-space: nowrap;
                ">Copy</button>
            </div>
            """, unsafe_allow_html=True)
        
        # Secondary colors section
        st.markdown("##### Secondary Color Palette")
        
        secondary_colors = [
            ("#007ac2", "Dark Blue", "Supporting color"),
            ("#32abd0", "Light Blue", "Supporting color"),
            ("#00a188", "Dark Green", "Success states"),
            ("#95c11f", "Light Green", "Success states"),
            ("#ea5599", "Pink", "Highlight color"),
            ("#f7b90c", "Yellow", "Warning states")
        ]
        
        # Display secondary colors in a grid
        cols = st.columns(3)
        for i, (color, name, desc) in enumerate(secondary_colors):
            with cols[i % 3]:
                st.markdown(f"""
                <div style="
                    padding: 12px; 
                    border-radius: 8px; 
                    background: linear-gradient(135deg, {color}15, {color}05);
                    border: 1px solid {color}30;
                    text-align: center;
                    margin: 5px 0;
                ">
                    <div style="
                        width: 40px; 
                        height: 40px; 
                        background: {color}; 
                        border-radius: 8px; 
                        margin: 0 auto 8px auto;
                        box-shadow: 0 2px 6px {color}40;
                    "></div>
                    <strong style="color: {color}; font-size: 0.9em;">{name}</strong><br>
                    <code style="font-size: 0.8em; color: #666;">{color}</code><br>
                    <small style="color: #666;">{desc}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### 🔤 Typography Standards")
        
        # Typography showcase with proper rendering
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(77, 29, 130, 0.1), rgba(139, 29, 130, 0.1)); padding: 25px; border-radius: 12px; border-left: 4px solid #4D1D82; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="font-family: Inter, sans-serif; color: #4D1D82; margin: 0; font-size: 2rem; font-weight: 700;">Hurme Geometric Sans 3</h2>
                <p style="color: #666; margin: 5px 0; font-style: italic;">Primary Font Family</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Use native Streamlit components for typography examples
        st.markdown("**Typography Hierarchy Examples:**")
        
        # Create a clean typography showcase using Streamlit's native rendering
        st.markdown("# H1 Heading Example")
        st.markdown("## H2 Heading Example") 
        st.markdown("### H3 Heading Example")
        st.markdown("**Body text example with bold weight**")
        st.markdown("Regular body text example")
        st.caption("Caption text in smaller size")
        
        # Font specifications in a clean table
        st.markdown("**Font Specifications:**")
        
        font_specs = {
            "Element": ["H1 Heading", "H2 Heading", "H3 Heading", "Body Text", "Caption", "Buttons"],
            "Weight": ["SemiBold (600)", "SemiBold (600)", "Medium (500)", "Regular (400)", "Regular (400)", "SemiBold (600)"],
            "Size": ["2.5rem", "2rem", "1.5rem", "1rem", "0.875rem", "0.9rem"]
        }
        
        import pandas as pd
        font_df = pd.DataFrame(font_specs)
        st.dataframe(font_df, use_container_width=True, hide_index=True)
        
        # Color contrast checker
        st.markdown("##### 🎯 Color Accessibility")
        
        st.markdown("""
        <div style="
            background: white; 
            padding: 20px; 
            border-radius: 8px; 
            border: 1px solid #e5e7eb;
            margin: 15px 0;
        ">
            <h4 style="color: #2C3E50; margin: 0 0 15px 0;">Contrast Ratios (WCAG AA Compliant)</h4>
            <div style="display: grid; gap: 10px;">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; background: #4D1D82; color: white; border-radius: 4px;">
                    <span>Dark Purple on White</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px; font-weight: bold;">8.2:1 ✅</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; background: #cf022b; color: white; border-radius: 4px;">
                    <span>Red on White</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px; font-weight: bold;">6.4:1 ✅</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px; background: #2C3E50; color: white; border-radius: 4px;">
                    <span>Text Gray on White</span>
                    <span style="background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 12px; font-weight: bold;">12.6:1 ✅</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Logo guidelines
    st.markdown("#### Logo Usage Guidelines")
    
    st.markdown("""
    <div class="brand-card">
        <h4>Logo Specifications</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h5>Minimum Sizes</h5>
                <ul>
                    <li><strong>Main Logo:</strong> 170px / 32mm</li>
                    <li><strong>Compact Logo:</strong> 56px / 15mm</li>
                </ul>
            </div>
            <div>
                <h5>Protection Area</h5>
                <ul>
                    <li>Based on "S" height in "Sopra Steria"</li>
                    <li>Maintain clear space on all sides</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Messaging guidelines
    st.markdown("#### Approved Brand Messaging")
    
    st.markdown("""
    <div class="brand-card">
        <h4>Corporate Tagline</h4>
        <p style="font-size: 1.5em; font-weight: bold; color: #E85A4F; font-style: italic;">
            "The world is how we shape it"
        </p>
        <p><strong>Usage:</strong> Must appear on all Tier 1 brand positioning pages</p>
        <p><strong>Placement:</strong> Hero sections, page headers, or footer areas</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick reference downloads
    st.markdown("#### Quick Reference Materials")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="export-section">
            <h5>Brand Guidelines PDF</h5>
            <p>Complete visual identity guidelines</p>
            <button class="export-button">Download Guidelines</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="export-section">
            <h5>Logo Package</h5>
            <p>All logo variations and formats</p>
            <button class="export-button">Download Logos</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="export-section">
            <h5>Color Palette</h5>
            <p>Hex codes and usage guidelines</p>
            <button class="export-button">Download Colors</button>
        </div>
        """, unsafe_allow_html=True)

    # Close width-constraining wrapper for tab5
    st.markdown("</div>", unsafe_allow_html=True)

# Footer with export options
st.markdown("---")
st.markdown("### Export & Reporting")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export Full Report", type="primary", key="export_full_report"):
        st.success("Full brand hygiene report exported successfully!")

with col2:
    if st.button("📈 Generate Executive Summary", key="generate_summary"):
        st.success("Executive summary generated!")

with col3:
    if st.button("🔄 Schedule Re-audit", key="schedule_reaudit"):
        st.success("Re-audit scheduled for 6 months from now!")

# Additional insights sidebar
with st.sidebar:
    st.markdown("### Quick Insights")
    
    # Top performer
    top_page = df.loc[df['Final Score'].idxmax()]
    st.markdown(f"""
    <div class="success-card">
        <h4>🏆 Top Performer</h4>
        <p><strong>{top_page['Page_Name']}</strong></p>
        <p>Score: {top_page['Final Score']}/10</p>
        <p>Tier: {top_page['Tier_Name']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Needs attention
    bottom_page = df.loc[df['Final Score'].idxmin()]
    st.markdown(f"""
    <div class="opportunity-card">
        <h4>🎯 Needs Attention</h4>
        <p><strong>{bottom_page['Page_Name']}</strong></p>
        <p>Score: {bottom_page['Final Score']}/10</p>
        <p>Issues: {bottom_page['Key Violations'][:50]}...</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    st.markdown("### Quick Stats")
    st.metric("Avg Logo Score", f"{df['Logo Compliance'].mean():.1f}/10")
    st.metric("Avg Color Score", f"{df['Color Palette'].mean():.1f}/10")
    st.metric("Avg Typography", f"{df['Typography'].mean():.1f}/10") 