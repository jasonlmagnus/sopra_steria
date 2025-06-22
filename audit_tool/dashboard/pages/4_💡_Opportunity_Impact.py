"""
Opportunity & Impact - Comprehensive Improvement Roadmap
Which gaps matter most and what should we do?
Consolidates AI Strategic Insights + Criteria Deep Dive functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Opportunity & Impact",
    page_icon="💡",
    layout="wide"
)

# Custom CSS for Opportunity & Impact
st.markdown("""
<style>
    .opportunity-header {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .opportunity-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #f59e0b;
        margin-bottom: 1rem;
    }
    
    .impact-high {
        border-left-color: #dc2626;
        background: #fef2f2;
    }
    
    .impact-medium {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    .impact-low {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    .priority-urgent {
        background: #fee2e2;
        border: 2px solid #dc2626;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .priority-high {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .priority-medium {
        background: #f0fdf4;
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .ai-recommendation {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
    
    .criteria-insight {
        background: #faf5ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #8b5cf6;
        margin: 0.5rem 0;
    }
    
    .impact-score {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
    }
    
    .action-button {
        background: #f59e0b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Opportunity & Impact - Comprehensive Improvement Roadmap"""
    
    # Header
    st.markdown("""
    <div class="opportunity-header">
        <h1>💡 Opportunity & Impact</h1>
        <p>Which gaps matter most and what should we do?</p>
        <p><em>Comprehensive improvement roadmap with AI-powered action recommendations</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data from session state or initialize
    if 'datasets' not in st.session_state or 'master_df' not in st.session_state:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        st.session_state['datasets'] = datasets
        st.session_state['master_df'] = master_df
    else:
        datasets = st.session_state['datasets']
        master_df = st.session_state['master_df']
    
    if master_df.empty:
        st.error("❌ No data available for Opportunity & Impact analysis.")
        return
    
    # Initialize metrics calculator
    recommendations_df = datasets.get('recommendations') if datasets else None
    metrics_calc = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Opportunity analysis controls
    display_opportunity_controls()
    
    # Main analysis sections
    display_impact_overview(metrics_calc, master_df)
    
    display_prioritized_opportunities(metrics_calc, master_df)
    
    display_ai_strategic_recommendations(metrics_calc, master_df)
    
    display_criteria_deep_dive_analysis(master_df)
    
    display_action_roadmap(metrics_calc, master_df)

def display_opportunity_controls():
    """Display controls for opportunity analysis"""
    st.markdown("## 🎛️ Opportunity Analysis Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Impact threshold
        impact_threshold = st.slider(
            "💥 Min Impact Score",
            0.0, 10.0, 5.0,
            key="impact_threshold",
            help="Minimum impact score to show opportunities"
        )
    
    with col2:
        # Effort level filter
        effort_levels = ['All', 'Low', 'Medium', 'High']
        selected_effort = st.selectbox(
            "⚡ Effort Level",
            effort_levels,
            key="effort_filter"
        )
    
    with col3:
        # Priority filter
        priority_levels = ['All', 'Urgent', 'High', 'Medium', 'Low']
        selected_priority = st.selectbox(
            "🎯 Priority Level",
            priority_levels,
            key="priority_filter"
        )
    
    with col4:
        # Number of opportunities to show
        num_opportunities = st.number_input(
            "📊 Max Opportunities",
            min_value=5, max_value=50, value=10,
            key="max_opportunities"
        )

def display_impact_overview(metrics_calc, master_df):
    """Display high-level impact overview"""
    st.markdown("## 📊 Impact Overview")
    
    # Calculate overall impact metrics
    opportunities = metrics_calc.get_top_opportunities(limit=50)  # Get more for analysis
    
    if opportunities:
        # Aggregate impact metrics
        total_impact = sum(opp['potential_impact'] for opp in opportunities)
        avg_impact = total_impact / len(opportunities)
        
        # Impact distribution
        high_impact = len([opp for opp in opportunities if opp['potential_impact'] >= 8.0])
        medium_impact = len([opp for opp in opportunities if 5.0 <= opp['potential_impact'] < 8.0])
        low_impact = len([opp for opp in opportunities if opp['potential_impact'] < 5.0])
        
        # Effort distribution
        low_effort = len([opp for opp in opportunities if opp['effort_level'] == 'Low'])
        medium_effort = len([opp for opp in opportunities if opp['effort_level'] == 'Medium'])
        high_effort = len([opp for opp in opportunities if opp['effort_level'] == 'High'])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Opportunities", len(opportunities))
        
        with col2:
            st.metric("Avg Impact Score", f"{avg_impact:.1f}/10")
        
        with col3:
            st.metric("High Impact Opps", high_impact)
        
        with col4:
            st.metric("Low Effort Opps", low_effort)
        
        # Impact vs Effort scatter plot
        if len(opportunities) > 1:
            impact_effort_data = pd.DataFrame([
                {
                    'page_title': opp.get('page_title', opp.get('page_id', 'Unknown')),
                    'impact': opp['potential_impact'],
                    'effort_numeric': 1 if opp['effort_level'] == 'Low' else 2 if opp['effort_level'] == 'Medium' else 3,
                    'effort_level': opp['effort_level'],
                    'current_score': opp['current_score']
                }
                for opp in opportunities
            ])
            
            fig_scatter = px.scatter(
                impact_effort_data,
                x='effort_numeric',
                y='impact',
                size='current_score',
                color='impact',
                hover_name='page_title',
                hover_data={'effort_level': True, 'current_score': ':.1f'},
                title="Impact vs Effort Matrix",
                labels={'effort_numeric': 'Effort Level', 'impact': 'Potential Impact'},
                color_continuous_scale='RdYlGn',
                range_color=[0, 10]
            )
            
            # Customize x-axis
            fig_scatter.update_xaxes(
                tickmode='array',
                tickvals=[1, 2, 3],
                ticktext=['Low', 'Medium', 'High']
            )
            
            fig_scatter.update_layout(height=400)
            fig_scatter.update_xaxes(title="Impact Score")
            fig_scatter.update_yaxes(title="Effort Level")
            st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("📊 No opportunities identified with current data structure.")

def display_prioritized_opportunities(metrics_calc, master_df):
    """Display prioritized list of improvement opportunities"""
    st.markdown("## 🎯 Prioritized Improvement Opportunities")
    
    # Get opportunities with filters applied
    max_opps = st.session_state.get('max_opportunities', 10)
    opportunities = metrics_calc.get_top_opportunities(limit=max_opps * 2)  # Get extra for filtering
    
    if not opportunities:
        st.info("📊 No opportunities identified. Try adjusting the filters.")
        return
    
    # Apply filters
    filtered_opportunities = apply_opportunity_filters(opportunities)
    
    if not filtered_opportunities:
        st.warning("⚠️ No opportunities match the selected filters. Try adjusting the criteria.")
        return
    
    # Limit to max opportunities
    filtered_opportunities = filtered_opportunities[:max_opps]
    
    st.success(f"🎯 Found {len(filtered_opportunities)} prioritized opportunities")
    
    # Display opportunities
    for i, opp in enumerate(filtered_opportunities, 1):
        display_opportunity_card(i, opp)

def apply_opportunity_filters(opportunities):
    """Apply selected filters to opportunities"""
    filtered = opportunities.copy()
    
    # Impact threshold filter
    impact_threshold = st.session_state.get('impact_threshold', 5.0)
    filtered = [opp for opp in filtered if opp['potential_impact'] >= impact_threshold]
    
    # Effort level filter
    effort_filter = st.session_state.get('effort_filter', 'All')
    if effort_filter != 'All':
        filtered = [opp for opp in filtered if opp['effort_level'] == effort_filter]
    
    # Priority filter (based on impact score)
    priority_filter = st.session_state.get('priority_filter', 'All')
    if priority_filter != 'All':
        if priority_filter == 'Urgent':
            filtered = [opp for opp in filtered if opp['potential_impact'] >= 9.0]
        elif priority_filter == 'High':
            filtered = [opp for opp in filtered if 7.0 <= opp['potential_impact'] < 9.0]
        elif priority_filter == 'Medium':
            filtered = [opp for opp in filtered if 5.0 <= opp['potential_impact'] < 7.0]
        elif priority_filter == 'Low':
            filtered = [opp for opp in filtered if opp['potential_impact'] < 5.0]
    
    return filtered

def display_opportunity_card(rank, opp):
    """Display individual opportunity card"""
    page_title = opp.get('page_title', opp.get('page_id', 'Unknown Page'))
    impact = opp['potential_impact']
    effort = opp['effort_level']
    current_score = opp['current_score']
    recommendation = opp['recommendation']
    
    # Determine priority level and styling
    if impact >= 9.0:
        priority_class = "priority-urgent"
        priority_label = "🚨 URGENT"
    elif impact >= 7.0:
        priority_class = "priority-high"
        priority_label = "🔥 HIGH"
    else:
        priority_class = "priority-medium"
        priority_label = "💡 MEDIUM"
    
    # Determine impact class
    if impact >= 8.0:
        impact_class = "impact-high"
    elif impact >= 5.0:
        impact_class = "impact-medium"
    else:
        impact_class = "impact-low"
    
    with st.expander(f"#{rank} - {page_title} ({priority_label})", expanded=(rank <= 3)):
        st.markdown(f"""
        <div class="opportunity-card {impact_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0;">{page_title}</h4>
                <div class="{priority_class}" style="padding: 0.5rem; border-radius: 6px;">
                    <strong>{priority_label}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Current Score", f"{current_score:.1f}/10")
        
        with col2:
            st.metric("Potential Impact", f"{impact:.1f}/10")
        
        with col3:
            st.metric("Effort Level", effort)
        
        with col4:
            improvement_potential = impact - current_score
            st.metric("Improvement Potential", f"+{improvement_potential:.1f}")
        
        # Recommendation
        st.markdown("### 💡 Recommended Action")
        st.markdown(f"""
        <div class="ai-recommendation">
            <strong>Action:</strong> {recommendation}
        </div>
        """, unsafe_allow_html=True)
        
        # Additional details if available
        if 'url' in opp and opp['url']:
            st.markdown(f"**🔗 URL:** {opp['url']}")
        
        if 'tier' in opp:
            st.markdown(f"**🏗️ Content Tier:** {opp['tier']}")
        
        # Quick action buttons
        st.markdown("### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<a href="#" class="action-button">📋 Create Task</a>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<a href="#" class="action-button">📊 View Details</a>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<a href="#" class="action-button">🔍 Analyze Page</a>', unsafe_allow_html=True)

def display_ai_strategic_recommendations(metrics_calc, master_df):
    """Display AI-generated strategic recommendations (from AI Strategic Insights page)"""
    st.markdown("## 🤖 AI Strategic Recommendations")
    
    # Generate executive summary to get AI recommendations
    executive_summary = metrics_calc.generate_executive_summary()
    
    if executive_summary and 'recommendations' in executive_summary:
        recommendations = executive_summary['recommendations']
        
        if recommendations:
            st.success(f"🎯 Generated {len(recommendations)} strategic recommendations")
            
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"""
                <div class="ai-recommendation">
                    <h4>🤖 AI Recommendation #{i}</h4>
                    <p>{rec}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🤖 No AI recommendations available in current executive summary.")
    else:
        st.info("🤖 AI strategic recommendations not available. Executive summary may need to be regenerated.")
    
    # Additional AI insights section
    display_ai_pattern_analysis(master_df)

def display_ai_pattern_analysis(master_df):
    """Display AI-powered pattern analysis"""
    st.markdown("### 🔍 AI Pattern Analysis")
    
    if 'avg_score' in master_df.columns and 'tier' in master_df.columns:
        # Analyze patterns in the data
        tier_performance = master_df.groupby('tier')['avg_score'].agg(['mean', 'count', 'std']).round(2)
        
        # Generate insights based on patterns
        insights = []
        
        # Best performing tier
        best_tier = tier_performance['mean'].idxmax()
        best_score = tier_performance.loc[best_tier, 'mean']
        insights.append(f"🏆 **{best_tier}** content consistently performs best (avg: {best_score:.1f}/10)")
        
        # Most variable tier
        if 'std' in tier_performance.columns:
            most_variable = tier_performance['std'].idxmax()
            variability = tier_performance.loc[most_variable, 'std']
            insights.append(f"📊 **{most_variable}** content shows highest variability (±{variability:.1f})")
        
        # Sample size insights
        largest_sample = tier_performance['count'].idxmax()
        sample_size = tier_performance.loc[largest_sample, 'count']
        insights.append(f"📈 **{largest_sample}** has the most data points ({sample_size} pages)")
        
        for insight in insights:
            st.markdown(f"""
            <div class="criteria-insight">
                {insight}
            </div>
            """, unsafe_allow_html=True)

def display_criteria_deep_dive_analysis(master_df):
    """Display detailed criteria analysis (from Criteria Deep Dive page)"""
    st.markdown("## 🎯 Criteria Deep Dive Analysis")
    
    # Find available numeric criteria columns from the unified dataset
    criteria_cols = [col for col in master_df.columns if col in [
        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
    ]]
    
    if not criteria_cols:
        st.info("📊 Criteria data not available for deep dive analysis.")
        return
    
    # Calculate criteria performance - use numeric_only to avoid text data errors
    criteria_performance = master_df[criteria_cols].mean(numeric_only=True).sort_values(ascending=True)  # Worst first
    
    st.markdown("### 📊 Criteria Performance Analysis")
    
    # Show bottom 5 criteria (biggest opportunities)
    st.error("🎯 **Biggest Improvement Opportunities (Bottom 5 Criteria)**")
    
    bottom_criteria = criteria_performance.head(5)
    
    for i, (criteria, score) in enumerate(bottom_criteria.items(), 1):
        improvement_potential = 10 - score  # Max possible improvement
        
        st.markdown(f"""
        <div class="opportunity-card impact-high">
            <strong>#{i} - {criteria.replace('_', ' ').title()}</strong><br>
            Current Score: {score:.1f}/10 | Improvement Potential: +{improvement_potential:.1f}
        </div>
        """, unsafe_allow_html=True)
    
    # Criteria performance chart
    fig_criteria = px.bar(
        x=criteria_performance.values,
        y=criteria_performance.index,
        orientation='h',
        title="Criteria Performance (Worst to Best)",
        color=criteria_performance.values,
        color_continuous_scale='RdYlGn',
        range_color=[0, 10]
    )
    fig_criteria.update_layout(height=max(300, len(criteria_performance) * 25))
    fig_criteria.update_xaxes(title="Score")
    fig_criteria.update_yaxes(title="Criteria")
    st.plotly_chart(fig_criteria, use_container_width=True)
    
    # Criteria correlation analysis
    display_criteria_correlation_analysis(master_df, criteria_cols)

def display_criteria_correlation_analysis(master_df, criteria_cols):
    """Display criteria correlation analysis"""
    st.markdown("### 🔗 Criteria Correlation Analysis")
    
    if len(criteria_cols) > 1:
        # Calculate correlation matrix
        correlation_matrix = master_df[criteria_cols].corr(numeric_only=True)
        
        # Create correlation heatmap
        fig_corr = px.imshow(
            correlation_matrix,
            title="Criteria Correlation Matrix",
            color_continuous_scale='RdBu',
            range_color=[-1, 1]
        )
        fig_corr.update_layout(height=400)
        fig_corr.update_xaxes(title="Criteria")
        fig_corr.update_yaxes(title="Criteria")
        st.plotly_chart(fig_corr, use_container_width=True)
        
        # Find strongest correlations
        # Get upper triangle of correlation matrix
        correlation_pairs = []
        for i in range(len(criteria_cols)):
            for j in range(i+1, len(criteria_cols)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:  # Only show strong correlations
                    correlation_pairs.append({
                        'criteria1': criteria_cols[i],
                        'criteria2': criteria_cols[j],
                        'correlation': corr_value
                    })
        
        if correlation_pairs:
            st.markdown("#### 🔗 Strong Correlations (|r| > 0.5)")
            
            correlation_df = pd.DataFrame(correlation_pairs)
            correlation_df = correlation_df.sort_values('correlation', key=abs, ascending=False)
            
            for _, row in correlation_df.head(5).iterrows():
                corr_type = "Positive" if row['correlation'] > 0 else "Negative"
                corr_strength = "Strong" if abs(row['correlation']) > 0.7 else "Moderate"
                
                st.markdown(f"""
                <div class="criteria-insight">
                    <strong>{corr_strength} {corr_type} Correlation:</strong><br>
                    {row['criteria1'].replace('_', ' ').title()} ↔ {row['criteria2'].replace('_', ' ').title()}<br>
                    Correlation: {row['correlation']:.2f}
                </div>
                """, unsafe_allow_html=True)

def display_action_roadmap(metrics_calc, master_df):
    """Display comprehensive action roadmap"""
    st.markdown("## 🗺️ Action Roadmap")
    
    # Get opportunities for roadmap
    opportunities = metrics_calc.get_top_opportunities(limit=20)
    
    if not opportunities:
        st.info("📊 No opportunities available for roadmap generation.")
        return
    
    # Categorize opportunities by effort and impact
    quick_wins = [opp for opp in opportunities if opp['effort_level'] == 'Low' and opp['potential_impact'] >= 6.0]
    major_projects = [opp for opp in opportunities if opp['effort_level'] == 'High' and opp['potential_impact'] >= 7.0]
    fill_ins = [opp for opp in opportunities if opp['effort_level'] == 'Medium']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("⚡ **Quick Wins** (Low Effort, High Impact)")
        st.write(f"**{len(quick_wins)} opportunities**")
        
        for i, opp in enumerate(quick_wins[:3], 1):
            st.markdown(f"""
            <div class="priority-medium">
                <strong>{i}. {opp.get('page_title', 'Unknown')}</strong><br>
                Impact: {opp['potential_impact']:.1f} | Current: {opp['current_score']:.1f}
            </div>
            """, unsafe_allow_html=True)
        
        if len(quick_wins) > 3:
            st.info(f"💡 +{len(quick_wins) - 3} more quick wins available")
    
    with col2:
        st.warning("🔧 **Fill-ins** (Medium Effort)")
        st.write(f"**{len(fill_ins)} opportunities**")
        
        for i, opp in enumerate(fill_ins[:3], 1):
            st.markdown(f"""
            <div class="priority-high">
                <strong>{i}. {opp.get('page_title', 'Unknown')}</strong><br>
                Impact: {opp['potential_impact']:.1f} | Current: {opp['current_score']:.1f}
            </div>
            """, unsafe_allow_html=True)
        
        if len(fill_ins) > 3:
            st.info(f"💡 +{len(fill_ins) - 3} more fill-ins available")
    
    with col3:
        st.error("🚀 **Major Projects** (High Effort, High Impact)")
        st.write(f"**{len(major_projects)} opportunities**")
        
        for i, opp in enumerate(major_projects[:3], 1):
            st.markdown(f"""
            <div class="priority-urgent">
                <strong>{i}. {opp.get('page_title', 'Unknown')}</strong><br>
                Impact: {opp['potential_impact']:.1f} | Current: {opp['current_score']:.1f}
            </div>
            """, unsafe_allow_html=True)
        
        if len(major_projects) > 3:
            st.info(f"💡 +{len(major_projects) - 3} more major projects available")
    
    # Implementation timeline
    st.markdown("### 📅 Suggested Implementation Timeline")
    
    timeline_data = []
    
    # Phase 1: Quick Wins (0-30 days)
    timeline_data.extend([
        {'Phase': 'Phase 1 (0-30 days)', 'Category': 'Quick Wins', 'Count': len(quick_wins), 'Color': '#10b981'}
    ])
    
    # Phase 2: Fill-ins (30-90 days)
    timeline_data.extend([
        {'Phase': 'Phase 2 (30-90 days)', 'Category': 'Fill-ins', 'Count': len(fill_ins), 'Color': '#f59e0b'}
    ])
    
    # Phase 3: Major Projects (90+ days)
    timeline_data.extend([
        {'Phase': 'Phase 3 (90+ days)', 'Category': 'Major Projects', 'Count': len(major_projects), 'Color': '#dc2626'}
    ])
    
    timeline_df = pd.DataFrame(timeline_data)
    
    if not timeline_df.empty:
        fig_timeline = px.bar(
            timeline_df,
            x='Phase',
            y='Count',
            color='Category',
            title="Implementation Timeline by Phase",
            color_discrete_map={
                'Quick Wins': '#10b981',
                'Fill-ins': '#f59e0b',
                'Major Projects': '#dc2626'
            }
        )
        fig_timeline.update_layout(height=400)
        fig_timeline.update_xaxes(title="Phase")
        fig_timeline.update_yaxes(title="Opportunities")
        st.plotly_chart(fig_timeline, use_container_width=True)

if __name__ == "__main__":
    main() 