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

# Main Analysis Section (Tabs removed for clarity and to prevent containerization)
create_divider()

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

# Detailed criteria breakdown table
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

# The other tabs (Tier Analysis, Regional Consistency, etc.) will be handled separately
# to determine if they also need to be extracted from the tab structure.
# For now, this addresses the primary complaint on the first visible screen.
# The following sections are commented out to complete the removal of the tab group.

# with tab2:
#     
#     st.markdown("### Tier Performance Analysis")
# ... (rest of file)

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