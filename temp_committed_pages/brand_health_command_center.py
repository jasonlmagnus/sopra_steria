"""
Brand Health Command Center - Executive Dashboard
30-second strategic marketing decision engine for executives
"""

import streamlit as st
import sys
from pathlib import Path

# Import components with consistent paths
from components.perfect_styling_method import (
    apply_perfect_styling,
    create_main_header,
    create_section_header,
    create_metric_card,
    create_status_indicator,
    create_primary_button,
    create_secondary_button,
    create_content_card
)
from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Brand Health Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

# Create standardized page header
create_main_header("Brand Health Command Center", "30-second strategic marketing decision engine for executives")

def main():
    """Main Brand Health Command Center - Executive Dashboard"""
    
    # Clean Header

    # Initialize data loader
    data_loader = BrandHealthDataLoader()
    
    # Load unified data only
    datasets, master_df = data_loader.load_all_data()
    
    # Store data in session state for other pages to access
    st.session_state['datasets'] = datasets
    st.session_state['master_df'] = master_df
    st.session_state['summary'] = data_loader.get_summary_stats(master_df, datasets)
    
    if master_df.empty:
        st.error("❌ No data available. Please ensure the enhanced unified dataset exists.")
        st.info("💡 Run the multi-persona packager to generate the enhanced unified dataset.")
        return
    
    # Initialize metrics calculator with unified data
    recommendations_df = datasets.get('recommendations') if datasets else None
    metrics_calc = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Generate executive summary
    executive_summary = metrics_calc.generate_executive_summary()
    
    # Display focused executive dashboard
    display_executive_dashboard(executive_summary, metrics_calc)
    
    # Enhanced navigation guidance
    display_navigation_guidance()
    
    # Sidebar with essential data quality info only
    display_sidebar_essentials(data_loader, master_df, datasets)

def display_executive_dashboard(summary, metrics_calc):
    """Display the focused executive dashboard - 30-second overview"""
    
    # Brand Health Overview (not affected by tier filtering)
    st.markdown("## Brand Health Overview")
    
    # Get brand health data from summary
    brand_health = summary['brand_health']
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        # Overall brand health score
        overall_score = brand_health.get('overall_score', 0)
        create_metric_card(f"{overall_score:.1f}/10", "Overall Brand Health", "excellent" if overall_score >= 7 else "warning" if overall_score >= 4 else "critical")

    with col2:
        critical_count = summary['key_metrics']['critical_issues']
        create_metric_card(str(critical_count), "Critical Issues", "critical" if critical_count > 0 else "good")

    with col3:
        quick_wins = summary['key_metrics']['quick_wins']
        create_metric_card(str(quick_wins), "Quick Wins", "excellent")

    with col4:
        success_pages = summary['key_metrics']['success_pages']
        create_metric_card(str(success_pages), "Success Stories", "good")

    # Add tier filtering for Strategic Brand Assessment
    st.markdown("### 🎯 Strategic Focus")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        tier_filter = st.selectbox(
            "Focus on Content Tier:",
            ["All Tiers", "Tier 1 (Strategic)", "Tier 2 (Tactical)", "Tier 3 (Operational)"],
            help="Filter Strategic Brand Assessment by content strategy tier"
        )
    
    with col2:
        if tier_filter != "All Tiers":
            st.info(f"📊 Filtering analysis by {tier_filter}")
    
    # Apply tier filtering to metrics calculator
    if tier_filter != "All Tiers":
        # Extract tier number (1, 2, or 3)
        tier_num = tier_filter.split()[1]  # "Tier 1 (Strategic)" -> "1"
        tier_name = f"tier_{tier_num}"
        # Filter the dataframe in metrics calculator
        original_df = metrics_calc.df.copy()
        metrics_calc.df = metrics_calc.df[metrics_calc.df['tier'] == tier_name]
        
        # If no data for this tier, show message and reset
        if metrics_calc.df.empty:
            st.warning(f"⚠️ No data available for {tier_filter}")
            metrics_calc.df = original_df
            tier_filter = "All Tiers"
    
    # Strategic Brand Assessment
    st.markdown("## Strategic Brand Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:

        # Calculate distinctiveness using new algorithm
        distinctiveness = metrics_calc.calculate_distinctiveness_score()
        score = distinctiveness['score']
        
        # Color coding: Red (<4), Amber (4-6.9), Green (7+)
        if score >= 7.0:
            status_text = "HIGH"
        elif score >= 4.0:
            status_text = "MODERATE"
        else:
            status_text = "LOW"

        create_metric_card(f"{score:.1f}/10", "Distinctiveness", status_text.lower())
     
    with col2:

        # Calculate resonance using new algorithm
        resonance = metrics_calc.calculate_resonance_score()
        sentiment = resonance['net_sentiment']
        
        # Convert sentiment percentage to 0-10 scale for consistency
        resonance_score = sentiment / 10  # 34.4% becomes 3.4/10
        
        # Color coding: Red (<4), Amber (4-6.9), Green (7+) - same as other metrics
        if resonance_score >= 7.0:
            status_text = "HIGH"
        elif resonance_score >= 4.0:
            status_text = "MODERATE"
        else:
            status_text = "LOW"

        create_metric_card(f"{resonance_score:.1f}/10", "Resonance", status_text.lower())
     
    with col3:

        # Calculate conversion using new algorithm
        conversion = metrics_calc.calculate_conversion_score()
        score = conversion['score']
        status = conversion['status']
        
        # Map status to consistent HIGH/MODERATE/LOW format
        if status == "High":
            status_text = "HIGH"
        elif status == "Medium":
            status_text = "MODERATE"
        else:
            status_text = "LOW"

        create_metric_card(f"{score:.1f}/10", "Conversion", status_text.lower())
     
    # EXECUTIVE QUESTION 3: What can we fix quickly? (Top 3 Opportunities)
    st.markdown("## 🎯 Top 3 Improvement Opportunities")
    st.markdown("*For comprehensive analysis, visit the **Opportunity & Impact** tab*")
    
    opportunities = metrics_calc.get_top_opportunities(limit=3)
    
    if opportunities:
        for i, opp in enumerate(opportunities, 1):
            page_title = opp.get('page_title', 'Unknown Page')
            
            with st.expander(f"#{i} - {page_title} (Impact: {opp['potential_impact']:.1f})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if opp.get('current_score', 0) > 0:
                        st.metric("Current Score", f"{opp['current_score']:.1f}/10")
                    else:
                        st.metric("Strategic Impact", opp.get('strategic_impact', 'General'))
                
                with col2:
                    st.metric("Effort Level", opp['effort_level'])
                
                with col3:
                    st.metric("Potential Impact", f"{opp['potential_impact']:.1f}")
                
                # Show actual detailed recommendation
                st.markdown(f"**💡 Recommendation:**")
                st.markdown(f"*{opp['recommendation']}*")
                
                # Show evidence if available
                if opp.get('evidence') and opp['evidence'] != opp['recommendation']:
                    st.markdown(f"**📋 Evidence:** {opp['evidence']}")
                
                # Show urgency if available
                if opp.get('urgency'):
                    st.markdown(f"**⏰ Urgency:** {opp['urgency']}")
                
                # Link to detailed analysis
                st.markdown("*👉 For detailed action plan, visit **Opportunity & Impact** tab*")
    else:
        st.info("📈 No specific opportunities identified. Visit **Content Matrix** for detailed analysis.")
    
    # EXECUTIVE QUESTION 4: What's working well? (Top 5 Success Stories)
    st.markdown("## 🌟 Top 5 Success Stories")
    st.markdown("*For detailed success analysis, visit the **Success Library** tab*")
    
    success_stories = metrics_calc.calculate_success_stories(min_score=7.5)  # Temporarily lower threshold
    
    # Debug info
    st.write(f"DEBUG: Found {len(success_stories)} success stories")
    
    if success_stories:
        st.success(f"🎉 Found {len(success_stories)} high-performing pages (score ≥ 7.7)")
        
        for i, story in enumerate(success_stories, 1):
            page_title = story.get('page_title', 'Unknown Page')
            
            with st.expander(f"⭐ #{i} - {page_title} - Score: {story['raw_score']:.1f}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🎯 Score:** {story['raw_score']:.1f}/10")
                    st.markdown(f"**📊 Tier:** {story['tier']}")
                    
                    # Show key strengths
                    if story['key_strengths']:
                        st.markdown("**✨ Key Strengths:**")
                        for strength in story['key_strengths'][:2]:  # Show top 2 for executive view
                            st.markdown(f"• {strength}")
                
                with col2:
                    # Show evidence
                    evidence_text = str(story.get('evidence', '')).strip()
                    if evidence_text and evidence_text != 'nan' and len(evidence_text) > 10:
                        st.markdown("**📋 Evidence:**")
                        if len(evidence_text) > 200:
                            st.markdown(f"*{evidence_text[:200]}...*")
                        else:
                            st.markdown(f"*{evidence_text}*")
                    else:
                        st.markdown("**📋 Evidence:**")
                        st.markdown("*Evidence details available in Success Library tab*")
                
                # Link to detailed analysis
                st.markdown("*👉 For pattern analysis and replication guide, visit **Success Library** tab*")
    else:
        st.warning("⚠️ No pages currently scoring 7.7 or above. Focus on improvement opportunities.")
    
    # EXECUTIVE QUESTION 5: What should we do next? (Strategic Recommendations)
    if summary['recommendations']:
        st.markdown("## 💡 Strategic Recommendations")
        st.markdown("*AI-generated action priorities based on current brand health*")
        
        for i, rec in enumerate(summary['recommendations'], 1):
            st.markdown(f"**{i}.** {rec}")

            # Add contextual action buttons with proper filtering
            col1, col2 = st.columns([3, 1])
            
            with col2:
                if "critical pages" in rec.lower() or "scoring below" in rec.lower():
                    if st.button("🔍 View Critical Pages", key=f"critical_btn_{i}"):
                        # Set filters for critical pages (score < 4.0)
                        st.session_state['content_min_score'] = 0.0
                        st.session_state['content_performance_filter'] = 'Poor (<4)'
                        st.session_state['content_persona_filter'] = 'All'
                        st.session_state['content_tier_filter'] = 'All'
                        st.switch_page("pages/3_📊_Content_Matrix.py")
                        
                elif "quick wins" in rec.lower() or "immediate impact" in rec.lower():
                    if st.button("⚡ See Quick Wins", key=f"quick_wins_btn_{i}"):
                        # Set filters for quick wins (low effort, high impact)
                        st.session_state['effort_filter'] = 'Low'
                        st.session_state['impact_threshold'] = 6.0
                        st.session_state['priority_filter'] = 'High'
                        st.session_state['max_opportunities'] = 20
                        st.switch_page("pages/4_💡_Opportunity_Impact.py")
                        
                elif "persona" in rec.lower():
                    # Extract persona name from recommendation if possible
                    persona_name = None
                    if "Benelux Cybersecurity Decision Maker" in rec:
                        persona_name = "The Benelux Cybersecurity Decision Maker"
                    elif "Strategic Business Leader" in rec:
                        persona_name = "The Benelux Strategic Business Leader (C-Suite Executive)"
                    elif "Transformation Programme Leader" in rec:
                        persona_name = "The Benelux Transformation Programme Leader"
                    elif "Technical Influencer" in rec:
                        persona_name = "The Technical Influencer"
                    elif "Technology Innovation Leader" in rec:
                        persona_name = "The_BENELUX_Technology_Innovation_Leader"
                    
                    if st.button("👥 Analyze Persona", key=f"persona_btn_{i}"):
                        # Set persona filter
                        if persona_name:
                            st.session_state['persona_insights_filter'] = persona_name
                        else:
                            st.session_state['persona_insights_filter'] = 'All'
                        st.switch_page("pages/2_👥_Persona_Insights.py")
                        
                elif "improvements" in rec.lower() or "opportunities" in rec.lower():
                    if st.button("💡 Get Action Plan", key=f"action_btn_{i}"):
                        # Set filters for improvement opportunities
                        st.session_state['impact_threshold'] = 5.0
                        st.session_state['effort_filter'] = 'All'
                        st.session_state['priority_filter'] = 'All'
                        st.session_state['max_opportunities'] = 15
                        st.switch_page("pages/4_💡_Opportunity_Impact.py")
                        
                else:
                    if st.button("📊 Explore Analysis", key=f"explore_btn_{i}"):
                        # Default to content matrix with no specific filters
                        st.session_state['content_persona_filter'] = 'All'
                        st.session_state['content_tier_filter'] = 'All'
                        st.session_state['content_min_score'] = 0.0
                        st.session_state['content_performance_filter'] = 'All'
                        st.switch_page("pages/3_📊_Content_Matrix.py")
            
              # Add spacing
    
    # Restore original dataframe if it was filtered
    if tier_filter != "All Tiers" and 'original_df' in locals():
        metrics_calc.df = original_df

def display_navigation_guidance():
    """Enhanced navigation guidance to specialized tabs"""
    st.markdown("## 🧭 Deep-Dive Analysis")
    st.markdown("**Need more details?** Visit these specialized tabs for comprehensive analysis:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_content_card("📊 **Content Matrix** - Detailed page analysis and tier breakdown")
    
    with col2:
        create_content_card("💡 **Opportunity & Impact** - Action roadmap with effort/impact analysis")
    
    with col3:
        create_content_card("🌟 **Success Library** - Learn from high-performing content patterns")

def display_sidebar_essentials(data_loader, master_df, datasets):
    """Display essential sidebar information"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Overview")
    
    stats = data_loader.get_summary_stats(master_df, datasets)
    st.sidebar.metric("Total Pages", stats.get('total_pages', 0))
    st.sidebar.metric("Total Records", stats.get('total_records', 0))
    st.sidebar.metric("Avg Score", f"{stats.get('avg_score', 0):.1f}/10")
    
    # Show data quality indicators
    if stats.get('experience_records', 0) > 0:
        st.sidebar.success(f"✅ Experience Data: {stats['experience_records']} records")
    if stats.get('total_recommendations', 0) > 0:
        st.sidebar.success(f"✅ Recommendations: {stats['total_recommendations']} items")
    
    # Quick navigation
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚀 Quick Actions")
    st.sidebar.markdown("- 👥 **Persona Insights** - Filter by persona")
    st.sidebar.markdown("- 📊 **Content Matrix** - Detailed tier analysis")
    st.sidebar.markdown("- 💡 **Opportunity & Impact** - Action roadmap")

if __name__ == "__main__":
    main() 