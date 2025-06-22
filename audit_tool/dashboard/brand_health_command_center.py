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
    
    .executive-question {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--navy-deep);
        margin-bottom: 1rem;
    }
    
    .navigation-guide {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #0ea5e9;
        margin-top: 2rem;
    }
    
    .nav-button {
        background: var(--navy-deep);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        transition: background 0.3s;
    }
    
    .nav-button:hover {
        background: #1e3a8a;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main Brand Health Command Center - Executive Dashboard"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Brand Health Command Center</h1>
        <p>Executive Dashboard - 30-Second Strategic Overview</p>
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
    
    # Add tier filtering at the top
    st.markdown("### 🎯 Strategic Focus")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        tier_filter = st.selectbox(
            "Focus on Content Tier:",
            ["All Tiers", "Tier 1 (Strategic)", "Tier 2 (Tactical)", "Tier 3 (Operational)"],
            help="Filter analysis by content strategy tier"
        )
    
    with col2:
        if tier_filter != "All Tiers":
            st.info(f"📊 Showing {tier_filter} analysis")
    
    # Business Impact Summary - The "So What?" Section
    st.markdown("## 🎯 Executive Summary")
    
    # Get brand health data first
    brand_health = summary['brand_health']
    
    # Calculate key business metrics
    brand_score = brand_health['raw_score']
    critical_count = summary['key_metrics']['critical_issues']
    quick_wins = summary['key_metrics']['quick_wins']
    
    # Determine overall status and priority
    if brand_score >= 8:
        status_message = "Strong brand performance across key metrics"
        impact_color = "green"
        impact_icon = "🚀"
        priority = "MAINTAIN"
    elif brand_score >= 6:
        status_message = "Solid foundation with room for improvement"
        impact_color = "orange" 
        impact_icon = "⚠️"
        priority = "OPTIMIZE"
    else:
        status_message = "Significant improvement opportunities identified"
        impact_color = "red"
        impact_icon = "🚨"
        priority = "URGENT"
    
    st.markdown(f"""
    <div class="business-impact-summary" style="
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid {impact_color};
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    ">
        <h3 style="margin: 0 0 10px 0; color: #333;">
            {impact_icon} <strong>{status_message}</strong>
        </h3>
        <p style="font-size: 16px; margin: 10px 0; color: {impact_color};">
            <strong>Priority Level: {priority}</strong>
        </p>
        <p style="margin: 5px 0;">
            • <strong>{critical_count} critical issues</strong> need immediate attention
        </p>
        <p style="margin: 5px 0;">
            • <strong>{quick_wins} quick wins</strong> identified for fast improvements
        </p>
        <p style="margin: 5px 0;">
            • <strong>Overall Score:</strong> {brand_score:.1f}/10 ({brand_health['status']})
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # EXECUTIVE QUESTION 1: How healthy is our brand?
    st.markdown("## 🏥 Brand Health Overview")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        status_class = f"status-{brand_health['status'].lower()}"
        # Show actual performance context
        score = brand_health['raw_score']
        if score >= 8:
            impact_text = "🚀 Strong performance across criteria"
            impact_color = "green"
        elif score >= 6:
            impact_text = "⚠️ Room for improvement identified"
            impact_color = "orange"
        else:
            impact_text = "🚨 Multiple issues need attention"
            impact_color = "red"
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value {status_class}">
                {brand_health['emoji']} {brand_health['raw_score']}/10
            </div>
            <div class="metric-label">Overall Brand Health - {brand_health['status']}</div>
            <div class="so-what" style="color: {impact_color}; font-weight: bold; margin-top: 8px;">
                💡 {impact_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        critical_count = summary['key_metrics']['critical_issues']
        card_class = "critical" if critical_count > 0 else ""
        
        # Show actual critical issue context
        if critical_count > 0:
            impact_text = f"Requires immediate attention"
            impact_color = "red"
        else:
            impact_text = "✅ No critical issues found"
            impact_color = "green"
            
        st.markdown(f"""
        <div class="metric-card {card_class}">
            <div class="metric-value">🚨 {critical_count}</div>
            <div class="metric-label">Critical Issues</div>
            <div class="so-what" style="color: {impact_color}; font-weight: bold; margin-top: 8px;">
                💡 {impact_text}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        quick_wins = summary['key_metrics']['quick_wins']
        
        # Show quick win context
        if quick_wins > 0:
            impact_text = f"Ready for implementation"
            impact_color = "green"
        else:
            impact_text = "No quick wins identified"
            impact_color = "gray"
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">⚡ {quick_wins}</div>
            <div class="metric-label">Quick Wins</div>
            <div class="so-what" style="color: {impact_color}; font-weight: bold; margin-top: 8px;">
                💡 {impact_text}
            </div>
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
    
    # EXECUTIVE QUESTION 2: What needs immediate attention?
    if critical_count > 0:
        st.markdown("""
        <div class="insights-box" style="border-left: 4px solid var(--red-status);">
            <h4>🚨 CRITICAL ALERT</h4>
            <p><strong>{} pages are scoring below 4.0 and need immediate attention!</strong></p>
            <p>👉 <em>Visit the <strong>Opportunity & Impact</strong> tab for detailed action plans.</em></p>
        </div>
        """.format(critical_count), unsafe_allow_html=True)
    
    # Three Strategic Questions - Focused Executive View
    st.markdown("## 🎯 Strategic Brand Assessment")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="executive-question">
            <h4>🔍 Are we distinct?</h4>
        """, unsafe_allow_html=True)
        
        # Calculate distinctiveness metrics (simplified for executive view)
        tier_performance = metrics_calc.calculate_tier_performance()
        if not tier_performance.empty:
            score_col = 'avg_score_mean' if 'avg_score_mean' in tier_performance.columns else 'avg_score'
            if score_col in tier_performance.columns:
                distinct_score = tier_performance[score_col].mean()
                if distinct_score is not None:
                    distinct_status = "🎯 Strong" if distinct_score >= 7 else "⚠️ Moderate" if distinct_score >= 4 else "🚨 Weak"
                    st.metric("Distinctiveness", f"{distinct_score:.1f}/10", delta=distinct_status)
                else:
                    st.metric("Distinctiveness", "N/A", delta="❓ Unknown")
            else:
                st.metric("Distinctiveness", "N/A", delta="❓ Unknown")
        else:
            st.metric("Distinctiveness", "N/A", delta="❓ Unknown")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="executive-question">
            <h4>💭 Are we resonating?</h4>
        """, unsafe_allow_html=True)
        
        sentiment = summary['sentiment']
        resonance_score = sentiment['net_sentiment']
        if resonance_score is not None:
            resonance_status = "😊 Positive" if resonance_score >= 60 else "😐 Neutral" if resonance_score >= 40 else "😞 Negative"
            st.metric("Net Sentiment", f"{resonance_score:.1f}%", delta=resonance_status)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="executive-question">
            <h4>💰 Are we converting?</h4>
        """, unsafe_allow_html=True)
        
        conversion = summary['conversion']
        convert_status = "🚀 Ready" if conversion['status'] == "High" else "⚠️ Moderate" if conversion['status'] == "Medium" else "🔧 Needs Work"
        
        st.metric("Conversion Readiness", conversion['status'], delta=convert_status)
        # Handle missing score key gracefully
        conversion_score = conversion.get('score', conversion.get('net_sentiment', 0))
        st.metric("Conversion Score", f"{conversion_score:.1f}/10")
        
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
                    st.metric("Current Score", f"{opp['current_score']:.1f}/10")
                
                with col2:
                    st.metric("Effort Level", opp['effort_level'])
                
                with col3:
                    st.metric("Potential Impact", f"{opp['potential_impact']:.1f}")
                
                st.markdown(f"**💡 Quick Action:** {opp['recommendation']}")
                
                # Link to detailed analysis
                st.markdown("*👉 For detailed action plan, visit **Opportunity & Impact** tab*")
    else:
        st.info("📈 No specific opportunities identified. Visit **Content Matrix** for detailed analysis.")
    
    # EXECUTIVE QUESTION 4: What's working well? (Top 3 Success Stories)
    st.markdown("## 🌟 Top 3 Success Stories")
    st.markdown("*For detailed success analysis, visit the **Success Library** tab*")
    
    success_stories = metrics_calc.calculate_success_stories()
    
    if success_stories:
        st.success(f"🎉 Found {len(success_stories)} high-performing pages (score ≥ 7.7)")
        
        for i, story in enumerate(success_stories[:3], 1):
            page_title = story.get('page_title', 'Unknown Page')
            
            with st.expander(f"⭐ #{i} - {page_title} - Score: {story['raw_score']:.1f}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**🎯 Score:** {story['raw_score']:.1f}/10")
                    st.markdown(f"**📊 Tier:** {story['tier']}")
                
                with col2:
                    if story['key_strengths']:
                        st.markdown("**✨ Key Strengths:**")
                        for strength in story['key_strengths'][:2]:  # Show only top 2 for executive view
                            st.markdown(f"• {strength}")
                
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

def display_navigation_guidance():
    """Enhanced navigation guidance to specialized tabs"""
    st.markdown("""
    <div class="navigation-guide">
        <h3>🧭 Deep-Dive Analysis</h3>
        <p><strong>Need more details?</strong> Visit these specialized tabs for comprehensive analysis:</p>
    </div>
    """, unsafe_allow_html=True)
    
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