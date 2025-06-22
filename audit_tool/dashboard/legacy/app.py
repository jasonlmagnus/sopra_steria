#!/usr/bin/env python3
"""
Brand Audit Dashboard - Main Application
Multi-page Streamlit app for analyzing brand audit results
"""

import streamlit as st
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from data_gateway import DataGateway

def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Brand Audit Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    """Apply custom CSS styling"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 12px 12px;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .filter-section {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .success-metric { color: #059669; }
    .warning-metric { color: #d97706; }
    .error-metric { color: #dc2626; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_data_gateway():
    """Initialize and cache the data gateway"""
    return DataGateway()

def render_sidebar():
    """Render the global sidebar with run selection and filters"""
    gateway = get_data_gateway()
    
    with st.sidebar:
        st.title("🔍 Brand Audit Dashboard")
        
        # Run selection
        st.markdown("### 📊 Select Audit Run")
        available_runs = gateway.load_available_runs()
        
        if not available_runs:
            st.error("No audit runs found. Please run the data packager first.")
            st.code("python audit_tool/packager.py P1")
            st.stop()
        
        selected_run = st.selectbox(
            "Available runs:",
            available_runs,
            key="global_run_selector",
            help="Select an audit run to analyze"
        )
        
        # Load run data
        run_data = gateway.load_run_data(selected_run)
        if not run_data:
            st.error(f"Could not load data for run: {selected_run}")
            st.stop()
        
        # Display run info
        manifest = run_data['manifest']
        st.info(f"""
        **Run:** {manifest['persona_id']}  
        **Date:** {manifest['timestamp'][:10]}  
        **Pages:** {manifest['total_pages']}  
        **Avg Score:** {manifest['average_score']:.2f}/10
        """)
        
        st.markdown("---")
        
        # Global filters
        st.markdown("### 🎛️ Filters")
        
        # Persona filter (if multiple personas in future)
        available_personas = run_data['page_facts']['persona_id'].unique().tolist()
        persona_filter = st.multiselect(
            "Personas:",
            available_personas,
            default=available_personas,
            key="global_persona_filter"
        )
        
        # Tier filter
        available_tiers = run_data['page_facts']['tier'].unique().tolist()
        tier_filter = st.multiselect(
            "Tiers:",
            available_tiers,
            default=available_tiers,
            key="global_tier_filter"
        )
        
        # Score range filter
        score_filter = st.slider(
            "Score Range:",
            0.0, 10.0, (0.0, 10.0),
            key="global_score_filter",
            help="Filter by score range"
        )
        
        # Store in session state for all pages
        st.session_state.update({
            'selected_run': selected_run,
            'run_data': run_data,
            'persona_filter': persona_filter,
            'tier_filter': tier_filter,
            'score_filter': score_filter,
            'gateway': gateway
        })

def render_main_content():
    """Render the main dashboard content"""
    st.title("🏠 Brand Audit Dashboard")
    
    # Check if we have data
    if 'run_data' not in st.session_state:
        st.error("No data loaded. Please check the sidebar.")
        return
    
    gateway = st.session_state['gateway']
    run_data = st.session_state['run_data']
    
    # Get filtered data
    filtered_data = gateway.get_filtered_data(
        run_data,
        st.session_state['persona_filter'],
        st.session_state['score_filter'],
        st.session_state['tier_filter']
    )
    
    if filtered_data.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Get summary stats
    stats = gateway.get_summary_stats(filtered_data)
    
    # Key metrics row
    st.markdown("### 📈 Key Performance Indicators")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Pages Analyzed",
            stats['total_pages'],
            help="Number of unique pages in this analysis"
        )
    
    with col2:
        avg_score = stats['average_score']
        delta_color = "normal"
        if avg_score >= 7:
            delta_color = "normal"
        elif avg_score >= 4:
            delta_color = "normal"
        else:
            delta_color = "inverse"
            
        st.metric(
            "Average Score",
            f"{avg_score:.2f}/10",
            delta=f"{avg_score - 5:.2f} vs baseline",
            help="Average score across all criteria"
        )
    
    with col3:
        st.metric(
            "Success Rate",
            f"{stats['pass_rate']:.1f}%",
            delta=f"{stats['pass_rate'] - 70:.1f}% vs target",
            help="Percentage of criteria scoring PASS (≥4.0)"
        )
    
    with col4:
        st.metric(
            "Critical Issues",
            stats['fail_count'],
            delta=f"-{stats['fail_count']}" if stats['fail_count'] > 0 else "0",
            delta_color="inverse",
            help="Number of criteria scoring FAIL (<2.0)"
        )
    
    with col5:
        st.metric(
            "Total Criteria",
            stats['total_criteria'],
            help="Total number of evaluated criteria"
        )
    
    # Quick insights
    st.markdown("### 🎯 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top Performing Tiers")
        tier_breakdown = gateway.get_tier_breakdown(filtered_data)
        if not tier_breakdown.empty:
            for _, row in tier_breakdown.head(3).iterrows():
                st.write(f"**{row['tier'].title()}**: {row['avg_score']:.2f}/10 ({row['pass_rate']:.1f}% pass rate)")
    
    with col2:
        st.markdown("#### ⚠️ Areas Needing Attention")
        worst_performers = gateway.get_worst_performers(filtered_data, 3)
        if not worst_performers.empty:
            for _, row in worst_performers.iterrows():
                st.write(f"**{row['criterion_id'].replace('_', ' ').title()}**: {row['raw_score']:.1f}/10 on {row['url_slug']}")
    
    # Navigation help
    st.markdown("---")
    st.markdown("### 🧭 Navigation")
    st.info("""
    **Use the pages in the sidebar to explore detailed analytics:**
    
    - **📊 Executive Overview** - High-level KPIs and charts
    - **👥 Persona Comparison** - Compare performance across personas  
    - **🔍 Criteria Explorer** - Drill down into individual criteria
    - **🎯 Priority Actions** - Critical gaps and quick wins
    - **📋 Raw Data** - Export and explore the underlying data
    
    All pages respect the filters you set in the sidebar.
    """)

def main():
    """Main application entry point"""
    configure_page()
    apply_custom_css()
    render_sidebar()
    render_main_content()

if __name__ == "__main__":
    main() 