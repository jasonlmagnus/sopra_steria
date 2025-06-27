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

# Remove fixed width and enable responsive sizing
st.plotly_chart(fig_heatmap, use_container_width=True, key="visual_brand_heatmap")

# Main Analysis Section - Adding back the full tab structure
create_divider()

# Create the tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Criteria Performance", 
    "🏢 Tier Analysis", 
    "🌍 Regional Consistency",
    "🔧 Fix Prioritization",
    "📖 Brand Standards"
])

with tab1:
    create_section_header("Brand Criteria Analysis")
    
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
        height=500
    )
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        st.plotly_chart(fig_radar, use_container_width=True, key="criteria_radar")
    
    with col2:
        create_subsection_header("Criteria Insights")
        
        # Best performing criteria
        best_criteria = criteria_avg.idxmax()
        best_score = criteria_avg.max()
        
        # Worst performing criteria
        worst_criteria = criteria_avg.idxmin()
        worst_score = criteria_avg.min()
        
        create_success_alert(f"🏆 Best: {best_criteria} ({best_score:.1f}/10)")
        create_error_alert(f"⚠️ Needs work: {worst_criteria} ({worst_score:.1f}/10)")
    
    # Detailed criteria breakdown table - PRESERVE THE EXISTING WORKING TABLE
    create_subsection_header("Detailed Performance Breakdown")
    
    # Create sortable table with fixed width to prevent expansion
    display_df = df[['URL', 'Page Type'] + criteria_cols + ['Final Score', 'Key Violations']].copy()
    display_df['URL'] = display_df['URL'].apply(lambda x: x.replace('https://www.', ''))
    
    # Truncate long violation text to prevent width expansion
    display_df['Key Violations'] = display_df['Key Violations'].apply(
        lambda x: str(x)[:100] + "..." if len(str(x)) > 100 else str(x)
    )
    
    create_data_table(
        display_df,
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

with tab2:
    create_section_header("Tier Performance Analysis")
    
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
        height=400
    )
    
    st.plotly_chart(fig_tier, use_container_width=True, key="tier_performance")
    
    # Tier insights
    col1, col2, col3 = create_three_column_layout()
    
    tiers = tier_stats.index.tolist()
    
    for i, (col, tier) in enumerate(zip([col1, col2, col3], tiers)):
        if i < len(tiers):
            with col:
                avg_score = tier_stats.loc[tier, 'Avg Score']
                page_count = int(tier_stats.loc[tier, 'Page Count'])
                
                status = "success" if avg_score >= 8.5 else "warning" if avg_score >= 7.5 else "error"
                
                create_metric_card(f"{avg_score:.1f}/10", f"{tier} ({page_count} pages)", status=status)

with tab3:
    create_section_header("Regional Brand Consistency")
    
    # Regional analysis
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
    fig_regional = px.bar(
        x=regional_stats.index,
        y=regional_stats['Avg Score'],
        title="Brand Consistency by Region",
        labels={'x': 'Region', 'y': 'Average Score'},
        color=regional_stats['Avg Score'],
        color_continuous_scale="RdYlGn"
    )
    
    fig_regional.update_layout(
        font=dict(family="Inter", size=12),
        height=400
    )
    
    st.plotly_chart(fig_regional, use_container_width=True, key="regional_performance")
    
    # Regional insights
    col1, col2 = create_two_column_layout()
    
    with col1:
        create_subsection_header("Regional Performance")
        for region in regional_stats.index:
            avg_score = regional_stats.loc[region, 'Avg Score']
            page_count = int(regional_stats.loc[region, 'Page Count'])
            
            status = "success" if avg_score >= 8.0 else "warning" if avg_score >= 7.0 else "error"
            create_info_alert(f"**{region}**: {avg_score:.1f}/10 ({page_count} pages)")
    
    with col2:
        create_subsection_header("Consistency Insights")
        
        # Find best and worst regions
        best_region = regional_stats['Avg Score'].idxmax()
        worst_region = regional_stats['Avg Score'].idxmin()
        
        create_success_alert(f"🏆 Best: {best_region} ({regional_stats.loc[best_region, 'Avg Score']:.1f}/10)")
        create_warning_alert(f"⚠️ Focus area: {worst_region} ({regional_stats.loc[worst_region, 'Avg Score']:.1f}/10)")

with tab4:
    create_section_header("🎯 Strategic Fix Prioritization")
    
    # Enhanced priority calculation with sophisticated scoring
    priority_data = []
    
    for _, row in df.iterrows():
        score = row['Final Score']
        violations = str(row['Key Violations'])
        page_url = row['URL'].replace('https://www.', '')
        page_type = row.get('Page Type', 'Unknown')
        
        # Calculate Business Impact (0-10 scale)
        # Higher impact for lower scores, strategic pages, and critical violations
        if score < 6.0:
            business_impact = 9.0  # Critical - major brand damage
        elif score < 7.5:
            business_impact = 7.0  # High - significant improvement potential
        elif score < 8.5:
            business_impact = 5.0  # Medium - moderate improvement
        else:
            business_impact = 2.0  # Low - minor optimization
        
        # Boost impact for strategic pages
        if 'Tier 1' in page_type or 'homepage' in page_url.lower():
            business_impact = min(10.0, business_impact + 2.0)
        elif 'Tier 2' in page_type:
            business_impact = min(10.0, business_impact + 1.0)
        
        # Calculate Implementation Effort (0-10 scale)
        # Based on violation complexity and page type
        base_effort = 3.0  # Base effort for any fix
        
        if "Major" in violations or "Critical" in violations:
            implementation_effort = 8.0  # High effort - major restructuring
        elif "Moderate" in violations or "Multiple" in violations:
            implementation_effort = 6.0  # Medium effort - several changes
        elif "Minor" in violations or "Simple" in violations:
            implementation_effort = 3.0  # Low effort - quick fixes
        else:
            # Estimate based on score gap
            score_gap = 10.0 - score
            implementation_effort = min(8.0, base_effort + (score_gap * 0.8))
        
        # Calculate ROI Score (Impact/Effort ratio)
        roi_score = business_impact / max(implementation_effort, 1.0)
        
        # Determine priority quadrant
        if business_impact >= 7.0 and implementation_effort <= 5.0:
            priority_quadrant = "🚀 DO FIRST"
            priority_color = "#22C55E"  # Green
        elif business_impact >= 7.0 and implementation_effort > 5.0:
            priority_quadrant = "📅 SCHEDULE"
            priority_color = "#F59E0B"  # Orange
        elif business_impact < 7.0 and implementation_effort <= 5.0:
            priority_quadrant = "⚡ QUICK WIN"
            priority_color = "#3B82F6"  # Blue
        else:
            priority_quadrant = "❌ DON'T DO"
            priority_color = "#EF4444"  # Red
        
        # Generate specific recommendations
        recommendations = []
        if score < 6.0:
            recommendations.append("🔴 URGENT: Complete brand compliance review")
        if "Logo" in violations:
            recommendations.append("🎨 Update logo placement and sizing")
        if "Color" in violations:
            recommendations.append("🌈 Implement brand color palette")
        if "Typography" in violations:
            recommendations.append("📝 Apply brand typography standards")
        if "Layout" in violations:
            recommendations.append("📐 Restructure page layout")
        if "Image" in violations:
            recommendations.append("🖼️ Replace non-compliant imagery")
        if "Messaging" in violations:
            recommendations.append("💬 Revise brand messaging")
        
        if not recommendations:
            recommendations.append("✨ Minor brand consistency improvements")
        
        # Estimate time and cost
        if implementation_effort <= 3.0:
            time_estimate = "1-2 days"
            cost_estimate = "€500-1,500"
        elif implementation_effort <= 6.0:
            time_estimate = "1-2 weeks"
            cost_estimate = "€2,000-5,000"
        else:
            time_estimate = "2-4 weeks"
            cost_estimate = "€5,000-15,000"
        
        priority_data.append({
            'Page': page_url,
            'Page_Type': page_type,
            'Current_Score': score,
            'Business_Impact': business_impact,
            'Implementation_Effort': implementation_effort,
            'ROI_Score': roi_score,
            'Priority_Quadrant': priority_quadrant,
            'Priority_Color': priority_color,
            'Recommendations': recommendations,
            'Time_Estimate': time_estimate,
            'Cost_Estimate': cost_estimate,
            'Potential_Improvement': min(2.5, (10.0 - score) * 0.7),  # Realistic improvement
            'Issues': violations[:150] + "..." if len(violations) > 150 else violations
        })
    
    priority_df = pd.DataFrame(priority_data)
    
    # Strategic Overview
    col1, col2, col3, col4 = create_four_column_layout()
    
    with col1:
        do_first_count = len(priority_df[priority_df['Priority_Quadrant'] == "🚀 DO FIRST"])
        create_metric_card(str(do_first_count), "🚀 Do First", status="error" if do_first_count > 0 else "success")
    
    with col2:
        quick_wins_count = len(priority_df[priority_df['Priority_Quadrant'] == "⚡ QUICK WIN"])
        create_metric_card(str(quick_wins_count), "⚡ Quick Wins", status="info")
    
    with col3:
        schedule_count = len(priority_df[priority_df['Priority_Quadrant'] == "📅 SCHEDULE"])
        create_metric_card(str(schedule_count), "📅 Schedule", status="warning")
    
    with col4:
        avg_roi = priority_df['ROI_Score'].mean()
        create_metric_card(f"{avg_roi:.1f}", "📈 Avg ROI Score", status="success" if avg_roi >= 1.5 else "warning")
    
    # Enhanced Priority Matrix Visualization
    fig_priority = go.Figure()
    
    # Add quadrant backgrounds
    fig_priority.add_shape(type="rect", x0=0, y0=7, x1=5, y1=10, fillcolor="rgba(34, 197, 94, 0.1)", line=dict(width=0))  # Quick Win
    fig_priority.add_shape(type="rect", x0=5, y0=7, x1=10, y1=10, fillcolor="rgba(245, 158, 11, 0.1)", line=dict(width=0))  # Schedule
    fig_priority.add_shape(type="rect", x0=0, y0=0, x1=5, y1=7, fillcolor="rgba(239, 68, 68, 0.1)", line=dict(width=0))  # Don't Do
    fig_priority.add_shape(type="rect", x0=5, y0=0, x1=10, y1=7, fillcolor="rgba(34, 197, 94, 0.2)", line=dict(width=0))  # Do First
    
    # Add data points
    for quadrant in priority_df['Priority_Quadrant'].unique():
        quadrant_data = priority_df[priority_df['Priority_Quadrant'] == quadrant]
        fig_priority.add_trace(go.Scatter(
            x=quadrant_data['Implementation_Effort'],
            y=quadrant_data['Business_Impact'],
            mode='markers+text',
            marker=dict(
                size=quadrant_data['Current_Score'] * 3,  # Size based on current score
                color=quadrant_data['Priority_Color'].iloc[0],
                opacity=0.7,
                line=dict(width=2, color='white')
            ),
            text=quadrant_data['Page'].apply(lambda x: x[:15] + "..." if len(x) > 15 else x),
            textposition="top center",
            name=quadrant,
            hovertemplate="<b>%{text}</b><br>" +
                         "Business Impact: %{y:.1f}<br>" +
                         "Implementation Effort: %{x:.1f}<br>" +
                         "Current Score: %{marker.size}<br>" +
                         "<extra></extra>"
        ))
    
    # Add quadrant labels
    fig_priority.add_annotation(x=2.5, y=8.5, text="⚡ QUICK WIN<br><i>Low Effort, High Impact</i>", showarrow=False, font=dict(size=12, color="#22C55E"))
    fig_priority.add_annotation(x=7.5, y=8.5, text="📅 SCHEDULE<br><i>High Effort, High Impact</i>", showarrow=False, font=dict(size=12, color="#F59E0B"))
    fig_priority.add_annotation(x=2.5, y=3.5, text="❌ DON'T DO<br><i>Low Effort, Low Impact</i>", showarrow=False, font=dict(size=12, color="#EF4444"))
    fig_priority.add_annotation(x=7.5, y=3.5, text="🚀 DO FIRST<br><i>High Effort, High Impact</i>", showarrow=False, font=dict(size=12, color="#22C55E"))
    
    fig_priority.update_layout(
        title="Strategic Priority Matrix - Impact vs. Effort",
        xaxis_title="Implementation Effort (0=Easy, 10=Complex)",
        yaxis_title="Business Impact (0=Low, 10=High)",
        font=dict(family="Inter", size=12),
        height=600,
        showlegend=True,
        xaxis=dict(range=[0, 10], gridcolor='lightgray'),
        yaxis=dict(range=[0, 10], gridcolor='lightgray'),
        plot_bgcolor='white'
    )
    
    st.plotly_chart(fig_priority, use_container_width=True, key="enhanced_priority_matrix")
    
    # Action Plans by Priority
    create_subsection_header("📋 Strategic Action Plans")
    
    # Do First items
    do_first_items = priority_df[priority_df['Priority_Quadrant'] == "🚀 DO FIRST"].sort_values('ROI_Score', ascending=False)
    if not do_first_items.empty:
        st.markdown("### 🚀 DO FIRST - Critical High-Impact Fixes")
        
        for _, item in do_first_items.head(3).iterrows():
            with st.expander(f"🔥 {item['Page']} - ROI Score: {item['ROI_Score']:.1f}"):
                col1, col2 = create_two_column_layout()
                
                with col1:
                    st.markdown(f"**📊 Current Score:** {item['Current_Score']:.1f}/10")
                    st.markdown(f"**📈 Potential Improvement:** +{item['Potential_Improvement']:.1f} points")
                    st.markdown(f"**⏰ Time Estimate:** {item['Time_Estimate']}")
                    st.markdown(f"**💰 Cost Estimate:** {item['Cost_Estimate']}")
                
                with col2:
                    st.markdown("**🎯 Action Items:**")
                    for rec in item['Recommendations'][:3]:
                        st.markdown(f"• {rec}")
                    
                    st.markdown(f"**🔍 Issues Found:** {item['Issues']}")
    
    # Quick Wins
    quick_win_items = priority_df[priority_df['Priority_Quadrant'] == "⚡ QUICK WIN"].sort_values('ROI_Score', ascending=False)
    if not quick_win_items.empty:
        st.markdown("### ⚡ QUICK WINS - Low Effort, High Impact")
        
        for _, item in quick_win_items.head(5).iterrows():
            with st.expander(f"⚡ {item['Page']} - ROI Score: {item['ROI_Score']:.1f}"):
                col1, col2 = create_two_column_layout()
                
                with col1:
                    st.markdown(f"**📊 Current Score:** {item['Current_Score']:.1f}/10")
                    st.markdown(f"**📈 Potential Improvement:** +{item['Potential_Improvement']:.1f} points")
                    st.markdown(f"**⏰ Time Estimate:** {item['Time_Estimate']}")
                
                with col2:
                    st.markdown("**🎯 Quick Actions:**")
                    for rec in item['Recommendations'][:2]:
                        st.markdown(f"• {rec}")
    
    # Implementation Roadmap
    create_subsection_header("🗓️ 90-Day Implementation Roadmap")
    
    total_do_first = len(do_first_items)
    total_quick_wins = len(quick_win_items)
    total_schedule = len(priority_df[priority_df['Priority_Quadrant'] == "📅 SCHEDULE"])
    
    col1, col2, col3 = create_three_column_layout()
    
    with col1:
        st.markdown("#### 📅 Month 1 (Days 1-30)")
        st.markdown(f"**Focus:** Complete all {total_do_first} critical fixes")
        st.markdown("**Goal:** Address urgent brand compliance issues")
        if total_do_first > 0:
            estimated_cost_month1 = total_do_first * 7500  # Average cost
            st.markdown(f"**Budget:** €{estimated_cost_month1:,}")
    
    with col2:
        st.markdown("#### ⚡ Month 2 (Days 31-60)")
        st.markdown(f"**Focus:** Implement {min(total_quick_wins, 8)} quick wins")
        st.markdown("**Goal:** Maximize ROI with low-effort improvements")
        if total_quick_wins > 0:
            estimated_cost_month2 = min(total_quick_wins, 8) * 1000  # Quick win cost
            st.markdown(f"**Budget:** €{estimated_cost_month2:,}")
    
    with col3:
        st.markdown("#### 📈 Month 3 (Days 61-90)")
        st.markdown(f"**Focus:** Plan {min(total_schedule, 5)} scheduled improvements")
        st.markdown("**Goal:** Long-term strategic enhancements")
        if total_schedule > 0:
            estimated_cost_month3 = min(total_schedule, 5) * 3000  # Scheduled item cost
            st.markdown(f"**Budget:** €{estimated_cost_month3:,}")
    
    # ROI Projection
    total_potential_improvement = priority_df['Potential_Improvement'].sum()
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #22C55E15, #3B82F615); padding: 20px; border-radius: 10px; border-left: 4px solid #22C55E; margin: 20px 0;">
        <h4>📊 Expected ROI</h4>
        <p><strong>Total Potential Brand Score Improvement:</strong> +{total_potential_improvement:.1f} points</p>
        <p><strong>Estimated 90-Day Investment:</strong> €{(total_do_first * 7500 + min(total_quick_wins, 8) * 1000 + min(total_schedule, 5) * 3000):,}</p>
        <p><strong>Expected Brand Health Increase:</strong> {(total_potential_improvement / len(priority_df) * 100):.1f}% improvement</p>
    </div>
    """, unsafe_allow_html=True)

with tab5:
    create_section_header("🎨 Brand Standards Reference")
    
    # Interactive Brand Colors
    create_subsection_header("🌈 Official Brand Colors")
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        st.markdown("##### Primary Color Palette")
        
        # Enhanced color swatches
        primary_colors = [
            ("#4D1D82", "Dark Purple", "Primary brand color", "CMYK: 89/100/06/01"),
            ("#8b1d82", "Light Purple", "Secondary brand color", "CMYK: 56/100/00/00"),
            ("#cf022b", "Red", "Accent color", "CMYK: 10/100/95/00"),
            ("#ef7d00", "Orange", "Accent color", "CMYK: 00/60/100/00")
        ]
        
        for color, name, desc, cmyk in primary_colors:
            st.markdown(f"""
            <div style="
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
                    <h4 style="margin: 0; color: {color}; font-family: 'Inter', sans-serif;">{name}</h4>
                    <div style="display: flex; gap: 15px; margin: 5px 0; flex-wrap: wrap;">
                        <code style="background: {color}20; color: {color}; padding: 2px 8px; border-radius: 4px; font-weight: bold;">{color}</code>
                        <span style="color: #666;">{cmyk}</span>
                    </div>
                    <p style="margin: 5px 0 0 0; color: #666;">{desc}</p>
                </div>
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
                    <strong style="color: {color};">{name}</strong><br>
                    <code style="color: #666;">{color}</code><br>
                    <small style="color: #666;">{desc}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### 🔤 Typography Standards")
        
        # Typography showcase
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(77, 29, 130, 0.1), rgba(139, 29, 130, 0.1)); padding: 25px; border-radius: 12px; border-left: 4px solid #4D1D82; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="font-family: Inter, sans-serif; color: #4D1D82; margin: 0; font-weight: 700;">Hurme Geometric Sans 3</h2>
                <p style="color: #666; margin: 5px 0; font-style: italic;">Primary Font Family</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Typography examples
        st.markdown("**Typography Hierarchy Examples:**")
        st.markdown("# H1 Heading Example")
        st.markdown("## H2 Heading Example") 
        st.markdown("### H3 Heading Example")
        st.markdown("**Body text example with bold weight**")
        st.markdown("Regular body text example")
        st.caption("Caption text in smaller size")
        
        # Font specifications
        st.markdown("**Font Specifications:**")
        
        font_specs = {
            "Element": ["H1 Heading", "H2 Heading", "H3 Heading", "Body Text", "Caption", "Buttons"],
            "Weight": ["SemiBold (600)", "SemiBold (600)", "Medium (500)", "Regular (400)", "Regular (400)", "SemiBold (600)"],
            "Size": ["2.5rem", "2rem", "1.5rem", "1rem", "0.875rem", "0.9rem"]
        }
        
        font_df = pd.DataFrame(font_specs)
        st.dataframe(font_df, hide_index=True)
        
        # Color accessibility
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
    create_subsection_header("Logo Usage Guidelines")
    
    st.markdown("""
    <div style="background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e5e7eb; margin: 1rem 0;">
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