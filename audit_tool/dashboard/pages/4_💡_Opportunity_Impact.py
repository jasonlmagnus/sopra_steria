"""
Opportunity & Impact - Comprehensive Improvement Roadmap
Which gaps matter most and what should we do?
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
    create_data_table,
    create_four_column_layout,
    create_three_column_layout,
    create_opportunity_card,
    create_impact_card,
    create_priority_card,
    create_perfect_scatter_chart,
    create_perfect_bar_chart,
    create_divider
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader
from audit_tool.dashboard.components.metrics_calculator import BrandHealthMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Opportunity & Impact",
    page_icon="💡",
    layout="wide"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

def calculate_impact_score(current_score, tier_weight):
    """Calculate impact score using the specified formula"""
    return (10 - current_score) * tier_weight

def main():
    """Opportunity & Impact - Comprehensive Improvement Roadmap"""
    
    # Create standardized page header
    create_main_header("💡 Opportunity & Impact", "Which gaps matter most and what should we do?")
    
    # Load data using BrandHealthDataLoader
    data_loader = BrandHealthDataLoader()
    master_df = data_loader.load_unified_data()
    
    if master_df.empty:
        create_error_alert("No data available for Opportunity & Impact analysis.")
        return
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(master_df)
    
    # Calculate impact scores for all opportunities
    opportunity_data = prepare_opportunity_data(master_df)
    
    if opportunity_data.empty:
        create_warning_alert("No opportunity data available for analysis.")
        return
    
    # Display opportunity controls
    filters = display_opportunity_controls(opportunity_data)
    
    # Apply filters to opportunity data
    filtered_opportunities = apply_opportunity_filters(opportunity_data, filters)
    
    # Display impact calculation explanation
    display_impact_calculation_explanation()
    
    # Display impact overview
    display_impact_overview(filtered_opportunities)
    
    create_divider()
    
    # Display prioritized opportunities
    display_prioritized_opportunities(filtered_opportunities)

def prepare_opportunity_data(master_df):
    """Prepare opportunity data with impact calculations"""
    
    # Ensure required columns exist
    required_cols = ['avg_score', 'tier_weight', 'tier', 'page_id', 'url_slug']
    missing_cols = [col for col in required_cols if col not in master_df.columns]
    
    if missing_cols:
        create_warning_alert(f"Missing required columns for opportunity analysis: {missing_cols}")
        return pd.DataFrame()
    
    # Calculate impact scores
    opportunities = master_df.copy()
    opportunities['impact_score'] = opportunities.apply(
        lambda row: calculate_impact_score(row['avg_score'], row['tier_weight']), 
        axis=1
    )
    
    # Add effort level (simplified logic based on tier)
    effort_mapping = {
        'Tier 1': 'High',
        'Tier 2': 'Medium', 
        'Tier 3': 'Low'
    }
    opportunities['effort_level'] = opportunities['tier'].map(effort_mapping).fillna('Medium')
    
    # Add priority level based on impact score
    def get_priority(impact):
        if impact >= 8: return 'Urgent'
        elif impact >= 6: return 'High'
        elif impact >= 4: return 'Medium'
        else: return 'Low'
    
    opportunities['priority_level'] = opportunities['impact_score'].apply(get_priority)
    
    return opportunities

def display_opportunity_controls(opportunity_data):
    """Display 4-column opportunity filtering controls"""
    
    create_section_header("🎯 Opportunity Analysis Controls")
    
    # Create 4-column layout for filters
    col1, col2, col3, col4 = create_four_column_layout()
    
    with col1:
        min_impact = st.slider(
            "Min Impact Score",
            min_value=0.0,
            max_value=10.0,
            value=0.0,
            step=0.5,
            key="min_impact_filter",
            help="Minimum impact score threshold"
        )
    
    with col2:
        effort_options = ['All'] + sorted(opportunity_data['effort_level'].unique().tolist())
        effort_level = st.selectbox(
            "Effort Level",
            effort_options,
            key="effort_filter",
            help="Filter by implementation effort required"
        )
    
    with col3:
        priority_options = ['All'] + sorted(opportunity_data['priority_level'].unique().tolist())
        priority_level = st.selectbox(
            "Priority Level", 
            priority_options,
            key="priority_filter",
            help="Filter by strategic priority"
        )
    
    with col4:
        tier_options = ['All'] + sorted(opportunity_data['tier'].unique().tolist())
        content_tier = st.selectbox(
            "Content Tier",
            tier_options,
            key="tier_filter",
            help="Filter by content tier classification"
        )
    
    return {
        'min_impact': min_impact,
        'effort_level': effort_level,
        'priority_level': priority_level,
        'content_tier': content_tier
    }

def apply_opportunity_filters(opportunity_data, filters):
    """Apply user-selected filters to opportunity data"""
    
    filtered_data = opportunity_data.copy()
    
    # Apply impact score filter
    filtered_data = filtered_data[filtered_data['impact_score'] >= filters['min_impact']]
    
    # Apply effort level filter
    if filters['effort_level'] != 'All':
        filtered_data = filtered_data[filtered_data['effort_level'] == filters['effort_level']]
    
    # Apply priority level filter
    if filters['priority_level'] != 'All':
        filtered_data = filtered_data[filtered_data['priority_level'] == filters['priority_level']]
    
    # Apply content tier filter
    if filters['content_tier'] != 'All':
        filtered_data = filtered_data[filtered_data['tier'] == filters['content_tier']]
    
    return filtered_data

def display_impact_calculation_explanation():
    """Display expandable impact calculation explanation"""
    
    with st.expander("📊 Impact Calculation Formula", expanded=False):
        create_info_alert("""
        **Impact Score Formula**: `(10 - Current Score) × Tier Weight`
        
        **Components**:
        - **Current Score**: Page's current performance score (0-10)
        - **Tier Weight**: Strategic importance multiplier by content tier
        - **Impact Score**: Potential improvement value
        
        **Example**: Page scoring 4/10 in Tier 1 (weight 0.8) = (10-4) × 0.8 = 4.8 impact score
        """)

def display_impact_overview(filtered_opportunities):
    """Display impact overview with key metrics and visualizations"""
    
    create_section_header("📊 Impact Overview")
    
    if filtered_opportunities.empty:
        create_warning_alert("No opportunities match the selected filters.")
        return
    
    # Calculate key metrics
    total_opportunities = len(filtered_opportunities)
    avg_impact = filtered_opportunities['impact_score'].mean()
    high_impact_count = len(filtered_opportunities[filtered_opportunities['impact_score'] >= 6.0])
    low_effort_count = len(filtered_opportunities[filtered_opportunities['effort_level'] == 'Low'])
    
    # Display key metrics in 4-column layout
    col1, col2, col3, col4 = create_four_column_layout()
    
    with col1:
        create_metric_card(str(total_opportunities), "Total Opportunities")
    
    with col2:
        create_metric_card(f"{avg_impact:.1f}", "Avg Impact Score")
    
    with col3:
        create_metric_card(str(high_impact_count), "High Impact (≥6.0)")
    
    with col4:
        create_metric_card(str(low_effort_count), "Low Effort Items")
    
    # Business impact context
    if avg_impact >= 6.0:
        create_success_alert("🚀 **Excellent opportunity portfolio** - High average impact potential")
    elif avg_impact >= 4.0:
        create_warning_alert("⚠️ **Moderate opportunity portfolio** - Mixed impact potential")
    else:
        create_error_alert("🔴 **Limited opportunity portfolio** - Consider expanding scope")
    
    # Impact vs Effort Matrix
    display_impact_effort_matrix(filtered_opportunities)
    
    # Tier Performance Analysis
    display_tier_performance_analysis(filtered_opportunities)

def display_impact_effort_matrix(filtered_opportunities):
    """Display impact vs effort scatter plot"""
    
    create_subsection_header("🎯 Impact vs Effort Matrix")
    
    # Create effort mapping for visualization
    effort_mapping = {'Low': 1, 'Medium': 2, 'High': 3}
    plot_data = filtered_opportunities.copy()
    plot_data['effort_numeric'] = plot_data['effort_level'].map(effort_mapping)
    
    # Create scatter plot
    fig = px.scatter(
        plot_data,
        x='effort_numeric',
        y='impact_score',
        color='tier',
        size='avg_score',
        hover_data=['page_id', 'url_slug', 'priority_level'],
        title="Opportunity Positioning: Impact vs Effort",
        labels={
            'effort_numeric': 'Effort Level',
            'impact_score': 'Impact Score',
            'tier': 'Content Tier'
        }
    )
    
    # Update x-axis to show effort labels
    fig.update_xaxes(
        tickmode='array',
        tickvals=[1, 2, 3],
        ticktext=['Low', 'Medium', 'High']
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Matrix insights
    quick_wins = len(plot_data[(plot_data['effort_numeric'] == 1) & (plot_data['impact_score'] >= 6.0)])
    major_projects = len(plot_data[(plot_data['effort_numeric'] == 3) & (plot_data['impact_score'] >= 7.0)])
    
    col1, col2 = st.columns(2)
    with col1:
        create_success_alert(f"⚡ **{quick_wins} Quick Wins** (Low Effort, High Impact)")
    with col2:
        create_warning_alert(f"🚀 **{major_projects} Major Projects** (High Effort, High Impact)")

def display_tier_performance_analysis(filtered_opportunities):
    """Display opportunities grouped by content tier"""
    
    create_subsection_header("🏗️ Tier Performance Analysis")
    
    # Calculate tier-level metrics
    tier_summary = filtered_opportunities.groupby('tier').agg({
        'impact_score': ['count', 'mean', 'sum'],
        'avg_score': 'mean'
    }).round(2)
    
    # Flatten column names
    tier_summary.columns = ['opportunity_count', 'avg_impact', 'total_impact', 'avg_current_score']
    tier_summary = tier_summary.sort_values('total_impact', ascending=False)
    
    # Display tier comparison chart
    fig = create_perfect_bar_chart(
        data=tier_summary.reset_index(),
        x='tier',
        y='total_impact',
        title="Total Impact Potential by Content Tier"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Tier insights
    best_tier = tier_summary['total_impact'].idxmax()
    best_impact = tier_summary.loc[best_tier, 'total_impact']
    
    create_info_alert(f"🎯 **{best_tier}** offers the highest total impact potential ({best_impact:.1f})")

def display_prioritized_opportunities(filtered_opportunities):
    """Display filtered and prioritized opportunity list"""
    
    create_section_header("🎯 Prioritized Opportunities")
    
    if filtered_opportunities.empty:
        create_warning_alert("No opportunities match the current filters.")
        return
    
    # Sort by impact score (highest first)
    sorted_opportunities = filtered_opportunities.sort_values('impact_score', ascending=False)
    
    # Group by tier for organized display
    tiers = sorted_opportunities['tier'].unique()
    
    for tier in tiers:
        tier_opportunities = sorted_opportunities[sorted_opportunities['tier'] == tier]
        
        create_subsection_header(f"🏗️ {tier} Opportunities ({len(tier_opportunities)} items)")
        
        # Display top opportunities for this tier
        for idx, (_, opp) in enumerate(tier_opportunities.head(5).iterrows()):
            display_opportunity_card(opp, idx)
        
        if len(tier_opportunities) > 5:
            create_info_alert(f"💡 +{len(tier_opportunities) - 5} more {tier} opportunities available")

def display_opportunity_card(opportunity, index):
    """Display individual opportunity card with detailed analysis"""
    
    # Determine priority styling
    priority = opportunity['priority_level']
    if priority == 'Urgent':
        card_content = create_urgent_opportunity_content(opportunity)
        create_priority_card(card_content, 'urgent')
    elif priority == 'High':
        card_content = create_high_opportunity_content(opportunity)
        create_priority_card(card_content, 'high')
    else:
        card_content = create_standard_opportunity_content(opportunity)
        create_opportunity_card(card_content)

def create_urgent_opportunity_content(opp):
    """Create content for urgent priority opportunities"""
    return f"""
    <h4>🚨 {opp.get('url_slug', 'Page')} (URGENT)</h4>
    <p><strong>Current Score:</strong> {opp.get('avg_score', 0):.1f}/10</p>
    <p><strong>Impact Score:</strong> {opp.get('impact_score', 0):.1f}</p>
    <p><strong>Effort:</strong> {opp.get('effort_level', 'Unknown')}</p>
    <p><strong>Evidence:</strong> {opp.get('evidence', 'No evidence available')[:100]}...</p>
    """

def create_high_opportunity_content(opp):
    """Create content for high priority opportunities"""
    return f"""
    <h4>⚡ {opp.get('url_slug', 'Page')} (HIGH PRIORITY)</h4>
    <p><strong>Current Score:</strong> {opp.get('avg_score', 0):.1f}/10</p>
    <p><strong>Impact Score:</strong> {opp.get('impact_score', 0):.1f}</p>
    <p><strong>Effort:</strong> {opp.get('effort_level', 'Unknown')}</p>
    <p><strong>Recommendation:</strong> {opp.get('business_impact_analysis', 'Analysis pending')[:100]}...</p>
    """

def create_standard_opportunity_content(opp):
    """Create content for standard opportunities"""
    return f"""
    <h4>💡 {opp.get('url_slug', 'Page')}</h4>
    <p><strong>Current Score:</strong> {opp.get('avg_score', 0):.1f}/10</p>
    <p><strong>Impact Score:</strong> {opp.get('impact_score', 0):.1f}</p>
    <p><strong>Effort:</strong> {opp.get('effort_level', 'Unknown')}</p>
    <p><strong>Priority:</strong> {opp.get('priority_level', 'Medium')}</p>
    """

if __name__ == "__main__":
    main() 