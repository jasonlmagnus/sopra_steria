"""
Opportunity & Impact - Comprehensive Improvement Roadmap
Which gaps matter most and what should we do?
Consolidates AI Strategic Insights + Criteria Deep Dive functionality
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path to fix import issues
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


import streamlit as st
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
import sys
from pathlib import Path
import re

# Add parent directory to path to import components

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Opportunity & Impact",
    page_icon="💡",
    layout="wide"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()


def extract_persona_quotes(text):
    """Extract persona voice quotes from text"""
    if not text or pd.isna(text):
        return []
    
    quotes = []
    text_str = str(text)
    
    # Look for first-person statements and persona voice patterns
    patterns = [
        r'As a[^.]*\.',
        r'I [^.]*\.',
        r'My [^.]*\.',
        r'This [^.]*for me[^.]*\.',
        r'From my perspective[^.]*\.',
        r'[^.]*would [^.]*me[^.]*\.',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_str, re.IGNORECASE)
        quotes.extend(matches)
    
    # Clean and deduplicate quotes
    cleaned_quotes = []
    for quote in quotes:
        quote = quote.strip()
        if len(quote) > 25 and quote not in cleaned_quotes:
            cleaned_quotes.append(quote)
    
    return cleaned_quotes[:3]  # Return top 3 quotes

def main():
    """Opportunity & Impact - Comprehensive Improvement Roadmap"""
    
    # Create standardized page header
    create_main_header("💡 Opportunity Impact", "Which improvements matter most?")
    
    # Load data using BrandHealthDataLoader
    data_loader = BrandHealthDataLoader()
    master_df = data_loader.load_unified_data()
    
    if master_df.empty:
        st.error("❌ No data available for Opportunity & Impact analysis.")
        return
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(master_df)
    
    # Get top opportunities
    try:
        opportunities = metrics_calc.get_top_opportunities(limit=10)
    except:
        # Fallback if method doesn't exist - create sample opportunities from data
        opportunities = []
        if 'avg_score' in master_df.columns:
            # Get worst performing pages as opportunities
            worst_pages = master_df.nsmallest(10, 'avg_score')
            for idx, row in worst_pages.iterrows():
                opportunities.append({
                    'title': f"Improve {row.get('url_slug', 'Page')}",
                    'current_score': row.get('avg_score', 0),
                    'potential_impact': min(10, row.get('avg_score', 0) + 3),
                    'effort_level': 'Medium',
                    'page_id': row.get('page_id', ''),
                    'url': row.get('url', ''),
                    'tier': row.get('tier', ''),
                    'descriptor': row.get('descriptor', ''),
                    'overall_sentiment': row.get('overall_sentiment', 'Unknown'),
                    'engagement_level': row.get('engagement_level', 'Unknown'),
                    'conversion_likelihood': row.get('conversion_likelihood', 'Unknown'),
                    'effective_copy_examples': row.get('effective_copy_examples', ''),
                    'ineffective_copy_examples': row.get('ineffective_copy_examples', ''),
                    'trust_credibility_assessment': row.get('trust_credibility_assessment', ''),
                    'information_gaps': row.get('information_gaps', ''),
                    'business_impact_analysis': row.get('business_impact_analysis', ''),
                    'evidence': row.get('evidence', '')
                })
    
    if not opportunities:
        st.info("📊 No opportunities available for analysis.")
        display_ai_strategic_recommendations(metrics_calc, master_df)
        display_criteria_deep_dive_analysis(master_df)
        display_action_roadmap(metrics_calc, master_df)
        return
    
    # Display top opportunity as example
    st.markdown("## 🎯 Top Opportunity Analysis")
    
    if opportunities:
        # Use first opportunity as example
        opp = opportunities[0]
        current_score = opp.get('current_score', 0)
        impact = opp.get('potential_impact', 0)
        effort = opp.get('effort_level', 'Unknown')
        i = 0  # Index for button keys
        
        st.markdown(f"### {opp.get('title', 'Improvement Opportunity')}")
        
        # Impact Calculation Explanation
        with st.expander("📊 How Impact is Calculated", expanded=False):
            st.markdown("Impact is calculated based on current performance, improvement potential, and strategic importance.")

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
        if improvement_potential > 2:
            st.success("🚀 High priority - significant improvement potential")
        elif improvement_potential > 1:
            st.warning("⚠️ Medium priority - moderate improvement potential")
        else:
            st.info("💡 Low priority - minor improvement potential")

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
                st.markdown(f"**{i}. {rec.get('title', 'Recommendation')}**")
                st.write(rec.get('description', 'No description available'))
                
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
            st.info(insight)

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
        st.write(f"{i}. **{criteria}**: {score:.1f}/10 (↗️ +{improvement_potential:.1f} potential)")

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
                st.write(f"• **{row['criteria1']}** ↔ **{row['criteria2']}**: {corr_strength} {corr_type} correlation ({row['correlation']:.2f})")
        else:
            st.info("No strong correlations found between criteria.")
    else:
        st.info("Need at least 2 criteria for correlation analysis.")

def display_action_roadmap(metrics_calc, master_df):
    """Display comprehensive action roadmap"""
    st.markdown("## 🗺️ Action Roadmap")
    
    # Get opportunities for roadmap - simplified since we may not have the exact method
    try:
        opportunities = metrics_calc.get_top_opportunities(limit=20)
    except:
        # Fallback if method doesn't exist
        opportunities = []
    
    if not opportunities:
        st.info("📊 No opportunities available for roadmap generation.")
        return
    
    # Categorize opportunities by effort and impact
    quick_wins = [opp for opp in opportunities if opp.get('effort_level') == 'Low' and opp.get('potential_impact', 0) >= 6.0]
    major_projects = [opp for opp in opportunities if opp.get('effort_level') == 'High' and opp.get('potential_impact', 0) >= 7.0]
    fill_ins = [opp for opp in opportunities if opp.get('effort_level') == 'Medium']
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("⚡ **Quick Wins** (Low Effort, High Impact)")
        st.write(f"**{len(quick_wins)} opportunities**")
        
        for i, opp in enumerate(quick_wins[:3], 1):
            st.write(f"{i}. {opp.get('title', 'Opportunity')} (Impact: {opp.get('potential_impact', 0):.1f})")

        if len(quick_wins) > 3:
            st.info(f"💡 +{len(quick_wins) - 3} more quick wins available")
    
    with col2:
        st.warning("🔧 **Fill-ins** (Medium Effort)")
        st.write(f"**{len(fill_ins)} opportunities**")
        
        for i, opp in enumerate(fill_ins[:3], 1):
            st.write(f"{i}. {opp.get('title', 'Opportunity')} (Impact: {opp.get('potential_impact', 0):.1f})")

        if len(fill_ins) > 3:
            st.info(f"💡 +{len(fill_ins) - 3} more fill-ins available")
    
    with col3:
        st.error("🚀 **Major Projects** (High Effort, High Impact)")
        st.write(f"**{len(major_projects)} opportunities**")
        
        for i, opp in enumerate(major_projects[:3], 1):
            st.write(f"{i}. {opp.get('title', 'Opportunity')} (Impact: {opp.get('potential_impact', 0):.1f})")

if __name__ == "__main__":
    main() 