"""
Visual Brand Hygiene Dashboard

NOTE: This dashboard uses a separate data source (visual_brand/brand_audit_scores.csv)
and is NOT part of the unified dataset. This is intentional as it analyzes specific
visual brand compliance metrics from a dedicated brand audit.
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_main_header,
    create_section_header,
    create_subsection_header,
    create_metric_card,
    create_status_indicator,
    create_success_alert,
    create_warning_alert,
    create_error_alert,
    create_info_alert,
    get_perfect_chart_config,
    create_data_table,
    create_two_column_layout,
    create_three_column_layout,
    create_four_column_layout,
    create_content_card,
    create_brand_card,
    create_persona_card,
    create_primary_button,
    create_secondary_button,
    create_badge,
    create_spacer,
    create_divider
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os

# Set page config
st.set_page_config(
    page_title="Brand Health Command Center - Visual Brand Hygiene",
    page_icon="🎨",
    layout="wide"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

# Create standardized page header
create_main_header("🎨 Visual Brand Hygiene", "Interactive dashboard for brand consistency")

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

# Calculate brand metrics
total_pages = len(df)
avg_score = df['Final Score'].mean()
top_performers = len(df[df['Final Score'] >= 8.5])

col1, col2, col3, col4 = create_four_column_layout()

with col1:
    create_metric_card(f"{total_pages:,}", "📄 Total Pages", status="info")

with col2:
    create_metric_card(f"{avg_score:.1f}/10", "📊 Average Score", status="success" if avg_score >= 8 else "warning" if avg_score >= 6 else "error")

with col3:
    create_metric_card(str(top_performers), "⭐ Top Performers", status="success")

with col4:
    compliance_rate = (len(df[df['Final Score'] >= 8.0]) / total_pages) * 100
    create_metric_card(f"{compliance_rate:.1f}%", "🎯 Compliance Rate", status="success" if compliance_rate >= 80 else "warning" if compliance_rate >= 60 else "error")

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
    font=dict(family="Inter", size=12))

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
        height=500,
        width=800,
        autosize=False
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig_radar, use_container_width=True, key="criteria_radar")
    
    with col2:
        st.markdown("#### Criteria Insights")
        
        # Best performing criteria
        best_criteria = criteria_avg.idxmax()
        best_score = criteria_avg.max()
        
        # Worst performing criteria
        worst_criteria = criteria_avg.idxmin()
        worst_score = criteria_avg.min()
        
        st.success(f"🏆 Best: {best_criteria} ({best_score:.1f}/10)")
        st.error(f"⚠️ Needs work: {worst_criteria} ({worst_score:.1f}/10)")

    # Detailed criteria breakdown table
    st.markdown("#### Detailed Performance Breakdown")
    
    # Create sortable table with fixed width to prevent expansion
    display_df = df[['URL', 'Page Type'] + criteria_cols + ['Final Score', 'Key Violations']].copy()
    display_df['URL'] = display_df['URL'].apply(lambda x: x.replace('https://www.', ''))
    
    # Truncate long violation text to prevent width expansion
    display_df['Key Violations'] = display_df['Key Violations'].apply(
        lambda x: x[:100] + "..." if len(str(x)) > 100 else x
    )

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

with tab2:
    
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
        height=400,
        width=1200,
        autosize=False
    )
    
    st.plotly_chart(fig_tier, use_container_width=True, key="tier_performance")
    
    # Tier insights
    col1, col2, col3 = st.columns(3)
    
    tiers = tier_stats.index.tolist()
    
    for i, (col, tier) in enumerate(zip([col1, col2, col3], tiers)):
        if i < len(tiers):
            with col:
                avg_score = tier_stats.loc[tier, 'Avg Score']
                page_count = int(tier_stats.loc[tier, 'Page Count'])
                create_metric_card(f"{avg_score:.1f}/10", f"{tier}", status="success" if avg_score >= 8 else "warning" if avg_score >= 6 else "error")
                st.caption(f"{page_count} pages")

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

with tab3:
    
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
        height=500,
        width=1200,
        autosize=False
    )
    
    st.plotly_chart(fig_regional, use_container_width=True, key="regional_comparison")
    
    # Regional insights
    st.markdown("#### Regional Performance Summary")
    
    cols = st.columns(len(regions))
    
    for i, (col, region) in enumerate(zip(cols, regions)):
        with col:
            avg_score = regional_stats.loc[region, 'Avg Score']
            page_count = int(regional_stats.loc[region, 'Page Count'])
            st.metric(f"{region}", f"{avg_score:.1f}/10", f"{page_count} pages")

    # Consistency analysis
    st.markdown("#### Brand Messaging Consistency")
    
    # Analyze tagline presence
    tagline_issues = df[df['Key Violations'].str.contains('tagline|messaging', case=False, na=False)]
    
    if not tagline_issues.empty:
        st.markdown(f"**{len(tagline_issues)} pages** have messaging consistency issues")
        st.dataframe(tagline_issues[['URL', 'Final Score', 'Key Violations']].head())

with tab4:
    
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
        labels={'Effort_Numeric': 'Implementation Effort', 'Impact_Numeric': 'Business Impact'})
    
    fig_priority.update_layout(
        xaxis=dict(tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        yaxis=dict(tickvals=[1, 2, 3], ticktext=['Low', 'Medium', 'High']),
        font=dict(family="Inter", size=12),
        height=500,
        width=1200,
        autosize=False
    )
    
    st.plotly_chart(fig_priority, use_container_width=True, key="priority_matrix")
    
    # Priority recommendations
    st.markdown("#### Recommended Action Plan")
    
    critical_fixes = fix_df[fix_df['Priority'] == 'Critical']
    high_fixes = fix_df[fix_df['Priority'] == 'High']
    
    if not critical_fixes.empty:
        st.markdown("##### 🚨 Phase 1: Critical Fixes (Immediate - Week 1)")
        for _, fix in critical_fixes.iterrows():
            st.markdown(f"**{fix['Page']}** - Score: {fix['Current_Score']:.1f} - {fix['Issues'][:100]}...")

    if not high_fixes.empty:
        st.markdown("##### ⚡ Phase 2: High Priority Fixes (Weeks 2-4)")
        for _, fix in high_fixes.head(3).iterrows():
            st.markdown(f"**{fix['Page']}** - Score: {fix['Current_Score']:.1f} - {fix['Issues'][:100]}...")

with tab5:
    
    st.markdown("### 🎨 Brand Standards Reference")
    
    # Interactive Brand Colors with enhanced visuals
    st.markdown("#### 🌈 Official Brand Colors")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("##### Primary Color Palette")
        
        primary_colors = [
            ("#4D1D82", "Dark Purple", "Primary brand color", "CMYK: 89/100/06/01"),
            ("#8b1d82", "Light Purple", "Secondary brand color", "CMYK: 56/100/00/00"),
            ("#cf022b", "Red", "Accent color", "CMYK: 10/100/95/00"),
            ("#ef7d00", "Orange", "Accent color", "CMYK: 00/60/100/00")
        ]
        
        for color, name, desc, cmyk in primary_colors:
            st.markdown(f'<div style="background-color: {color}; padding: 10px; margin: 5px 0; border-radius: 5px; color: white;"><b>{name}</b><br/>{desc}<br/><small>{cmyk}</small></div>', unsafe_allow_html=True)

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
                st.markdown(f'<div style="background-color: {color}; padding: 8px; margin: 2px 0; border-radius: 3px; color: white; text-align: center;"><b>{name}</b><br/><small>{desc}</small></div>', unsafe_allow_html=True)

    with col2:
        st.markdown("##### 🔤 Typography Standards")
        
        # Typography showcase with proper rendering

        # Typography hierarchy examples
        st.markdown("**Typography Hierarchy Examples:**")
        
        # Clean typography showcase using standard Streamlit
        st.markdown("# H1 Page Title")
        st.markdown("## H2 Section Header") 
        st.markdown("### H3 Subsection Header")
        st.markdown("**Bold body text**")
        st.markdown("Regular body text")
        st.caption("Caption text")
        
        # Font specifications in a clean table
        st.markdown("**Font Specifications:**")
        
        font_specs = {
            "Element": ["H1 Title", "H2 Section", "H3 Subsection", "Body Text", "Caption", "Metric"],
            "Font": ["Crimson Text", "Crimson Text", "Inter", "Inter", "Inter", "Inter"],
            "Weight": ["600", "600", "500", "400", "400", "700"],
            "Size": ["1.8rem", "1.4rem", "1.1rem", "1.0rem", "0.8rem", "2.2rem"]
        }
        
        font_df = pd.DataFrame(font_specs)
        st.dataframe(font_df, use_container_width=True, hide_index=True)
        
        # Color contrast checker
        st.markdown("##### 🎯 Color Accessibility")

    # Logo guidelines
    st.markdown("#### Logo Usage Guidelines")

    # Messaging guidelines
    st.markdown("#### Approved Brand Messaging")

    # Quick reference downloads
    st.markdown("#### Quick Reference Materials")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("📘 Brand Guidelines PDF", help="Download comprehensive brand guidelines")

    with col2:
        st.button("🎨 Asset Library", help="Access brand asset library")

    with col3:
        st.button("📋 Audit Checklist", help="Download brand audit checklist")

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
    st.success(f"🌟 **Top Performer**\n{top_page['URL']} ({top_page['Final Score']:.1f}/10)")

    # Needs attention
    bottom_page = df.loc[df['Final Score'].idxmin()]
    st.error(f"⚠️ **Needs Attention**\n{bottom_page['URL']} ({bottom_page['Final Score']:.1f}/10)")

    # Quick stats
    st.markdown("### Quick Stats")
    st.metric("Avg Logo Score", f"{df['Logo Compliance'].mean():.1f}/10")
    st.metric("Avg Color Score", f"{df['Color Palette'].mean():.1f}/10")
    st.metric("Avg Typography", f"{df['Typography'].mean():.1f}/10") 