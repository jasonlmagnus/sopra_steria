"""
Tier Analysis Dashboard Page
Strategic tier-based brand performance analysis following Sopra Steria methodology
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add the audit_tool directory to the path
current_dir = Path(__file__).parent
audit_tool_dir = current_dir.parent
sys.path.append(str(audit_tool_dir))

from components.tier_analyzer import TierAnalyzer

def main():
    st.set_page_config(
        page_title="Tier Analysis",
        page_icon="🏗️",
        layout="wide"
    )
    
    # Get data from session state (loaded by main dashboard)
    if 'master_df' not in st.session_state or 'datasets' not in st.session_state:
        st.error("❌ No data available. Please go to the main dashboard first to load data.")
        st.stop()
    
    data = st.session_state['master_df']
    datasets = st.session_state['datasets']
    summary_stats = st.session_state.get('summary', {})
    
    # Page header
    st.title("🏗️ Tier-Based Brand Analysis")
    st.markdown("""
    **Strategic Content Tier Analysis**
    
    This analysis follows the Sopra Steria Brand Audit Methodology, which categorizes content into three strategic tiers:
    - **Tier 1 - Brand Positioning** (30% weight): 80% brand criteria, 20% performance criteria
    - **Tier 2 - Value Propositions** (50% weight): 50% brand criteria, 50% performance criteria  
    - **Tier 3 - Functional Content** (20% weight): 30% brand criteria, 70% performance criteria
    
    Each tier has different importance in the overall brand health calculation.
    """)
    
    # Initialize tier analyzer
    tier_analyzer = TierAnalyzer(data)
    
    # Render the complete tier dashboard
    tier_analyzer.render_tier_dashboard()
    
    # Additional methodology details
    with st.expander("📚 Methodology Details"):
        st.markdown("""
        ### Content Tier Classification
        
        **Tier 1 - Brand Positioning (30% of overall score)**
        - Homepage and corporate pages
        - About us, history, corporate responsibility
        - Brand-heavy content (80% brand criteria, 20% performance)
        - Critical for brand identity and positioning
        
        **Tier 2 - Value Propositions (50% of overall score)**
        - Service and solution pages
        - Industry-specific content
        - Balanced content (50% brand criteria, 50% performance)
        - Core business value communication
        
        **Tier 3 - Functional Content (20% of overall score)**
        - Blog posts, news, insights
        - Case studies and thought leadership
        - Performance-heavy content (30% brand criteria, 70% performance)
        - Supporting content and engagement
        
        ### Scoring Methodology
        - Overall brand health = (Tier1_Score × 0.3) + (Tier2_Score × 0.5) + (Tier3_Score × 0.2)
        - Each tier score is calculated using its specific brand/performance criteria weighting
        - Improvement opportunities are prioritized by potential impact (tier weight × score gap)
        """)
    
    # Data quality indicators
    st.sidebar.header("📊 Data Overview")
    st.sidebar.metric("Total Pages", summary_stats.get('total_pages', data['page_id'].nunique() if 'page_id' in data.columns else 0))
    st.sidebar.metric("Total Personas", summary_stats.get('total_personas', data['persona_id'].nunique() if 'persona_id' in data.columns else 0))
    st.sidebar.metric("Total Evaluations", len(data) if data is not None else 0)
    avg_score = data['raw_score'].mean() if 'raw_score' in data.columns else summary_stats.get('avg_score', 0)
    st.sidebar.metric("Average Score", f"{avg_score:.1f}/10")
    
    # Tier distribution
    if not data.empty:
        st.sidebar.subheader("Tier Distribution")
        tier_counts = data['tier'].value_counts()
        tier_names = {
            'tier_1': 'Brand Positioning',
            'tier_2': 'Value Propositions', 
            'tier_3': 'Functional Content'
        }
        
        for tier_id, count in tier_counts.items():
            tier_name = tier_names.get(tier_id, tier_id)
            st.sidebar.metric(tier_name, f"{count} evaluations")

if __name__ == "__main__":
    main() 