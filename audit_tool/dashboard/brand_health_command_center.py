"""
Brand Health Command Center - Main Dashboard
Strategic marketing decision engine that transforms raw audit data into actionable business intelligence
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

# Custom CSS for Brand Health Command Center
st.markdown("""
<style>
    /* Brand Health Command Center Styles */
    :root {
        --navy-deep: #0d1b2a;
        --white-snow: #ffffff;
        --green-status: #34c759;
        --yellow-status: #ffb800;
        --red-status: #ff3b30;
        --orange-status: #ff9500;
        --font-primary: "Inter", sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--navy-deep) 0%, #1e3a8a 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid var(--green-status);
        margin-bottom: 1rem;
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
        border: 1px solid #e2e8f0;
        margin: 1rem 0;
    }
    
    .quick-win-badge {
        background: var(--green-status);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .critical-badge {
        background: var(--red-status);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Brand Health Command Center application"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Brand Health Command Center</h1>
        <p>Strategic Marketing Decision Engine</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize data loader
    @st.cache_resource
    def get_data_loader():
        return BrandHealthDataLoader()
    
    data_loader = get_data_loader()
    
    # Sidebar for persona selection
    st.sidebar.title("🎯 Command Center")
    st.sidebar.markdown("---")
    
    # Get available personas
    available_personas = data_loader.get_available_personas()
    
    if not available_personas:
        st.error("❌ No persona data found. Please run an audit first.")
        st.info("💡 Use the 'Run Audit' tab to generate brand audit data.")
        return
    
    # Persona selector
    selected_persona = st.sidebar.selectbox(
        "Select Persona",
        available_personas,
        help="Choose which persona's audit data to analyze"
    )
    
    # Load data
    with st.spinner("🔄 Loading brand health data..."):
        df = data_loader.load_enhanced_data(selected_persona)
    
    if df.empty:
        st.error(f"❌ No data found for persona: {selected_persona}")
        return
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(df)
    
    # Generate executive summary
    executive_summary = metrics_calc.generate_executive_summary()
    
    # Display key metrics
    display_executive_dashboard(executive_summary, metrics_calc)
    
    # Navigation guidance
    st.markdown("---")
    st.markdown("### 🧭 Navigation Guide")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Analysis Tabs:**
        - Executive Dashboard (You are here)
        - Persona Insights
        - Content Matrix
        """)
    
    with col2:
        st.markdown("""
        **🎯 Action Tabs:**
        - Opportunity & Impact
        - Success Library
        - Run Audit
        """)
    
    with col3:
        st.markdown("""
        **📋 Export Tabs:**
        - Reports & Export
        - Detailed Data
        """)
    
    # Data quality info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Data Quality")
    
    stats = data_loader.get_summary_stats(df)
    st.sidebar.metric("Total Pages", stats.get('total_pages', 0))
    st.sidebar.metric("Total Records", stats.get('total_records', 0))
    st.sidebar.metric("Avg Score", f"{stats.get('avg_score', 0):.1f}/10")

def display_executive_dashboard(summary, metrics_calc):
    """Display the executive dashboard with key metrics"""
    
    # Brand Health Score - Hero Metric
    st.markdown("## 🏥 Brand Health Overview")
    
    brand_health = summary['brand_health']
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        status_class = f"status-{brand_health['status'].lower()}"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {status_class}">
                {brand_health['emoji']} {brand_health['score']}/10
            </div>
            <div class="metric-label">Brand Health Score - {brand_health['status']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical_count = summary['key_metrics']['critical_issues']
        card_class = "critical" if critical_count > 0 else ""
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <div class="metric-value">🚨 {critical_count}</div>
            <div class="metric-label">Critical Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        quick_wins = summary['key_metrics']['quick_wins']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">⚡ {quick_wins}</div>
            <div class="metric-label">Quick Wins</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        success_pages = summary['key_metrics']['success_pages']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">🌟 {success_pages}</div>
            <div class="metric-label">Success Pages</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Critical Issues Alert
    if critical_count > 0:
        st.error(f"🚨 **CRITICAL ALERT**: {critical_count} pages are scoring below 4.0 and need immediate attention!")
    
    # Three Strategic Questions
    st.markdown("## 🎯 Strategic Brand Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🔍 Are we distinct?")
        # Calculate distinctiveness metrics
        tier_performance = metrics_calc.calculate_tier_performance()
        if not tier_performance.empty:
            distinct_score = tier_performance['avg_score'].mean()
            distinct_status = "✅ Yes" if distinct_score >= 7 else "⚠️ Partially" if distinct_score >= 5 else "❌ No"
            st.metric("Distinctiveness", f"{distinct_score:.1f}/10", delta=distinct_status)
        
        st.markdown("**Key Factors:**")
        st.markdown("- Unique value proposition clarity")
        st.markdown("- Differentiation from competitors")
        st.markdown("- Brand positioning strength")
    
    with col2:
        st.markdown("### 💭 Are we resonating?")
        sentiment = summary['sentiment']
        resonance_score = sentiment['net_sentiment']
        resonance_status = "✅ Yes" if resonance_score >= 20 else "⚠️ Partially" if resonance_score >= 0 else "❌ No"
        
        st.metric("Net Sentiment", f"{resonance_score:.1f}%", delta=resonance_status)
        
        st.markdown("**Sentiment Breakdown:**")
        st.markdown(f"- 😊 Positive: {sentiment['positive']:.1f}%")
        st.markdown(f"- 😐 Neutral: {sentiment['neutral']:.1f}%")
        st.markdown(f"- 😞 Negative: {sentiment['negative']:.1f}%")
    
    with col3:
        st.markdown("### 💰 Are we converting?")
        conversion = summary['conversion']
        convert_status = "✅ Yes" if conversion['status'] == 'High' else "⚠️ Partially" if conversion['status'] == 'Medium' else "❌ No"
        
        st.metric("Conversion Readiness", conversion['status'], delta=convert_status)
        st.metric("Conversion Score", f"{conversion['score']:.1f}/10")
        
        st.markdown("**Conversion Factors:**")
        st.markdown("- Call-to-action effectiveness")
        st.markdown("- Trust & credibility signals")
        st.markdown("- User journey optimization")
    
    # Tier Performance with Experience Data
    st.markdown("## 📊 Tier Performance Analysis")
    
    if not tier_performance.empty:
        # Display tier performance table
        st.dataframe(
            tier_performance.style.format({
                'avg_score': '{:.1f}',
                'avg_sentiment': '{:.1f}',
                'avg_conversion': '{:.1f}'
            }).background_gradient(subset=['avg_score'], cmap='RdYlGn', vmin=0, vmax=10),
            use_container_width=True
        )
    else:
        st.info("📊 Tier performance data not available with current dataset.")
    
    # Top Opportunities
    st.markdown("## 🎯 Top Improvement Opportunities")
    
    opportunities = metrics_calc.get_top_opportunities(limit=3)
    
    if opportunities:
        for i, opp in enumerate(opportunities, 1):
            with st.expander(f"#{i} - {opp['page_id']} (Impact: {opp['potential_impact']:.1f})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Current Score", f"{opp['current_score']:.1f}/10")
                
                with col2:
                    st.metric("Effort Level", opp['effort_level'])
                
                with col3:
                    st.metric("Page Tier", opp['tier'])
                
                if opp['url']:
                    st.markdown(f"**URL:** {opp['url']}")
    else:
        st.info("📈 No specific opportunities identified with current data structure.")
    
    # Success Stories
    st.markdown("## 🌟 Success Stories")
    
    success_stories = metrics_calc.calculate_success_stories()
    
    if success_stories:
        st.success(f"🎉 Found {len(success_stories)} high-performing pages (score ≥ 8.0)")
        
        for story in success_stories[:3]:  # Show top 3
            with st.expander(f"⭐ {story['page_id']} - Score: {story['score']:.1f}"):
                st.markdown(f"**Tier:** {story['tier']}")
                st.markdown(f"**Sentiment:** {story['sentiment']}")
                
                if story['key_strengths']:
                    st.markdown("**Key Strengths:**")
                    for strength in story['key_strengths']:
                        st.markdown(f"- {strength}")
                
                if story['url']:
                    st.markdown(f"**URL:** {story['url']}")
    else:
        st.warning("⚠️ No pages currently scoring 8.0 or above. Focus on improvement opportunities.")
    
    # Strategic Recommendations
    if summary['recommendations']:
        st.markdown("## 💡 Strategic Recommendations")
        
        for i, rec in enumerate(summary['recommendations'], 1):
            st.markdown(f"**{i}.** {rec}")

if __name__ == "__main__":
    main() 