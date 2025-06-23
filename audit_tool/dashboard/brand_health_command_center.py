"""
Brand Health Command Center - Executive Dashboard
30-second strategic marketing decision engine for executives
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Import components
from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Brand Health Command Center",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Google Fonts and Custom CSS for Brand Health Command Center
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    /* Brand Health Command Center Styles */
    :root {
        --primary-color: #E85A4F;
        --primary-hover: #d44a3a;
        --secondary-color: #2C3E50;
        --gray-border: #D1D5DB;
        --background: #FFFFFF;
        --text-selection: #E85A4F;
        --green-status: #34c759;
        --yellow-status: #ffb800;
        --red-status: #ff3b30;
        --orange-status: #ff9500;
        --font-primary: "Inter", sans-serif;
        --font-serif: "Crimson Text", serif;
    }
    
    /* Global Typography */
    .main .block-container {
        font-family: var(--font-primary);
        font-weight: 400;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        font-weight: 600;
    }
    
    /* Text Selection */
    ::selection {
        background-color: var(--text-selection);
        color: white;
    }
    
    .main-header {
        background: var(--background);
        border-left: 4px solid var(--primary-color);
        color: var(--secondary-color);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--gray-border);
    }
    
    .main-header h1 {
        font-family: var(--font-serif);
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: var(--secondary-color);
    }
    
    .main-header p {
        font-family: var(--font-primary);
        font-size: 1rem;
        font-weight: 400;
        color: #666;
        margin: 0;
    }
    
    .metric-card {
        background: var(--background);
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid var(--gray-border);
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        font-family: var(--font-primary);
    }
    
    .metric-card.critical {
        border-left-color: var(--red-status);
    }
    
    .metric-card.warning {
        border-left-color: var(--yellow-status);
    }
    
    .metric-card.fair {
        border-left-color: var(--orange-status);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    .status-excellent { color: var(--green-status); }
    .status-good { color: var(--yellow-status); }
    .status-fair { color: var(--orange-status); }
    .status-critical { color: var(--red-status); }
    
    .insights-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--gray-border);
        margin: 1rem 0;
        font-family: var(--font-primary);
    }
    
    .insights-box h4 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 1rem;
    }
    
    .quick-win-badge {
        background: var(--green-status);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-family: var(--font-primary);
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .critical-badge {
        background: var(--red-status);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-family: var(--font-primary);
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Business Impact Summary Styling */
    .business-impact-summary {
        font-family: var(--font-primary);
    }
    
    .business-impact-summary h3 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
    }
    
    /* Metric Labels */
    .metric-label {
        font-family: var(--font-primary);
        font-size: 0.9rem;
        color: var(--secondary-color);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    .metric-value {
        font-family: var(--font-primary);
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }
    
    /* So What Context */
    .so-what {
        font-family: var(--font-primary);
        font-weight: 500;
        margin-top: 8px;
    }
    
    .executive-question {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--primary-color);
        margin-bottom: 1rem;
        font-family: var(--font-primary);
    }
    
    .executive-question h4 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 1rem;
    }
    
    .navigation-guide {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--primary-color);
        margin-top: 2rem;
    }
    
    .navigation-guide h3 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
    }
    
    .nav-button {
        background: var(--primary-color);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-family: var(--font-primary);
        font-weight: 600;
        transition: background 0.3s;
    }
    
    .nav-button:hover {
        background: var(--primary-hover);
        color: white;
    }
    
    /* Streamlit Button Overrides */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        font-family: var(--font-primary);
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-hover);
        color: white;
    }
    
    /* Streamlit Link Styling */
    a {
        color: var(--primary-color);
        text-decoration: none;
    }
    
    a:hover {
        color: var(--primary-hover);
        text-decoration: underline;
    }
    
    /* Override Streamlit's default section headers */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        font-weight: 600;
        padding: 0;
        margin: 1rem 0 0.5rem 0;
        background: none !important;
        border: none !important;
        border-radius: 0 !important;
    }
    
    /* Specific styling for h2 section headers */
    .main h2 {
        font-size: 1.4rem;
        border-left: 3px solid var(--primary-color);
        padding-left: 0.75rem;
        margin: 1.5rem 0 1rem 0;
        background: rgba(232, 90, 79, 0.05) !important;
        padding: 0.5rem 0.75rem;
        border-radius: 4px;
    }
    
    /* Specific styling for h3 subsection headers */
    .main h3 {
        font-size: 1.2rem;
        color: var(--secondary-color);
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
    }
    
    /* Remove any colored backgrounds from section containers */
    .stMarkdown div[data-testid="stMarkdownContainer"] {
        background: none !important;
    }
    
    /* Target Streamlit's auto-generated header styling */
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        background: none !important;
        border: none !important;
        color: var(--secondary-color) !important;
        font-family: var(--font-serif) !important;
        padding: 0.25rem 0 !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Override the colored header banners completely */
    .stMarkdown > div > div > div {
        background: none !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Force remove any element-ui header styling */
    .element-container div[data-testid="stMarkdownContainer"] h2 {
        background: rgba(232, 90, 79, 0.05) !important;
        border-left: 3px solid var(--primary-color) !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 4px !important;
        font-size: 1.3rem !important;
        margin: 1rem 0 0.75rem 0 !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Brand Health Command Center - Executive Dashboard"""
    
    # Clean Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Brand Health Command Center</h1>
        <p>Executive Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
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
        status_class = f"status-{brand_health['status'].lower()}"
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {status_class}">
                {brand_health['raw_score']}/10
            </div>
            <div class="metric-label">Overall Brand Health - {brand_health['status']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical_count = summary['key_metrics']['critical_issues']
        card_class = "critical" if critical_count > 0 else ""
            
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <div class="metric-value">{critical_count}</div>
            <div class="metric-label">Critical Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        quick_wins = summary['key_metrics']['quick_wins']
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{quick_wins}</div>
            <div class="metric-label">Quick Wins</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        success_pages = summary['key_metrics']['success_pages']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{success_pages}</div>
            <div class="metric-label">Success Pages</div>
        </div>
        """, unsafe_allow_html=True)
    

    
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
        st.markdown("""
        <div class="executive-question">
            <h4>Are we distinct?</h4>
        """, unsafe_allow_html=True)
        
        # Calculate distinctiveness using new algorithm
        distinctiveness = metrics_calc.calculate_distinctiveness_score()
        score = distinctiveness['score']
        
        # Color coding: Red (<4), Amber (4-6.9), Green (7+)
        if score >= 7.0:
            color = "#22C55E"  # Green
            status_text = "HIGH"
        elif score >= 4.0:
            color = "#F59E0B"  # Amber
            status_text = "MODERATE"
        else:
            color = "#EF4444"  # Red
            status_text = "LOW"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid {color};">
            <div style="font-size: 2rem; font-weight: bold; color: {color};">{score:.1f}/10</div>
            <div style="color: {color}; font-weight: 600; margin: 0.5rem 0;">{status_text}</div>
            <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;">
                <strong>How we measure:</strong><br/>
                First impression uniqueness (40%)<br/>
                Brand visibility (30%)<br/>
                Distinctive language tone (30%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="executive-question">
            <h4>Are we resonating?</h4>
        """, unsafe_allow_html=True)
        
        # Calculate resonance using new algorithm
        resonance = metrics_calc.calculate_resonance_score()
        sentiment = resonance['net_sentiment']
        
        # Convert sentiment percentage to 0-10 scale for consistency
        resonance_score = sentiment / 10  # 34.4% becomes 3.4/10
        
        # Color coding: Red (<4), Amber (4-6.9), Green (7+) - same as other metrics
        if resonance_score >= 7.0:
            color = "#22C55E"  # Green
            status_text = "HIGH"
        elif resonance_score >= 4.0:
            color = "#F59E0B"  # Amber
            status_text = "MODERATE"
        else:
            color = "#EF4444"  # Red
            status_text = "LOW"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid {color};">
            <div style="font-size: 2rem; font-weight: bold; color: {color};">{resonance_score:.1f}/10</div>
            <div style="color: {color}; font-weight: 600; margin: 0.5rem 0;">{status_text}</div>
            <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;">
                <strong>How we measure:</strong><br/>
                User sentiment scores (50%)<br/>
                Content engagement (30%)<br/>
                Success rate (20%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="executive-question">
            <h4>Are we converting?</h4>
        """, unsafe_allow_html=True)
        
        # Calculate conversion using new algorithm
        conversion = metrics_calc.calculate_conversion_score()
        score = conversion['score']
        status = conversion['status']
        
        # Map status to consistent HIGH/MODERATE/LOW format
        if status == "High":
            color = "#22C55E"  # Green
            status_text = "HIGH"
        elif status == "Medium":
            color = "#F59E0B"  # Amber
            status_text = "MODERATE"
        else:
            color = "#EF4444"  # Red
            status_text = "LOW"
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 4px solid {color};">
            <div style="font-size: 2rem; font-weight: bold; color: {color};">{score:.1f}/10</div>
            <div style="color: {color}; font-weight: 600; margin: 0.5rem 0;">{status_text}</div>
            <div style="font-size: 0.85rem; color: #6B7280; margin-top: 0.5rem;">
                <strong>How we measure:</strong><br/>
                Conversion likelihood (50%)<br/>
                Trust & credibility (30%)<br/>
                Performance metrics (20%)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
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
            st.markdown(f"""
            <div class="insights-box">
                <strong>{i}.</strong> {rec}
            </div>
            """, unsafe_allow_html=True)
            
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
            
            st.markdown("")  # Add spacing
    
    # Restore original dataframe if it was filtered
    if tier_filter != "All Tiers" and 'original_df' in locals():
        metrics_calc.df = original_df

def display_navigation_guidance():
    """Enhanced navigation guidance to specialized tabs"""
    st.markdown("## 🧭 Deep-Dive Analysis")
    st.markdown("**Need more details?** Visit these specialized tabs for comprehensive analysis:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Analysis Tabs:**
        - **👥 Persona Insights** - How different personas experience your brand
        - **📊 Content Matrix** - Detailed performance by content type and tier
        """)
    
    with col2:
        st.markdown("""
        **🎯 Action Tabs:**
        - **💡 Opportunity & Impact** - Comprehensive improvement roadmap
        - **🌟 Success Library** - Pattern analysis and replication guides
        """)
    
    with col3:
        st.markdown("""
        **📋 Data & Tools:**
        - **📋 Reports & Export** - Custom reports and data exports
        - **🚀 Run Audit** - Generate fresh audit data
        """)

def display_sidebar_essentials(data_loader, master_df, datasets):
    """Display essential sidebar information only"""
    
    # Magnus Consulting Logo at top of sidebar
    try:
        st.sidebar.image("logo.png", width=150)
    except:
        st.sidebar.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <strong style="color: #E85A4F; font-size: 1.2rem;">MAGNUS</strong><br/>
            <span style="color: #2C3E50; font-size: 0.9rem;">CONSULTING</span>
        </div>
        """, unsafe_allow_html=True)
    
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