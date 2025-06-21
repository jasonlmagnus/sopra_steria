#!/usr/bin/env python3
"""
Main Brand Audit Dashboard
Multi-page application with audit running and analysis capabilities
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def initialize_audit_state():
    """Initialize all audit-related session state variables"""
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'audit_complete' not in st.session_state:
        st.session_state.audit_complete = False
    if 'audit_process' not in st.session_state:
        st.session_state.audit_process = None
    if 'audit_start_time' not in st.session_state:
        st.session_state.audit_start_time = None
    if 'current_url_index' not in st.session_state:
        st.session_state.current_url_index = 0
    if 'total_urls' not in st.session_state:
        st.session_state.total_urls = 0
    if 'persona_name' not in st.session_state:
        st.session_state.persona_name = ""
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""

@st.cache_data
def load_audit_data():
    """Load the enhanced audit dataset from individual persona directories"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    audit_outputs_dir = project_root / "audit_outputs"
    
    if not audit_outputs_dir.exists():
        return None, None
    
    all_data = []
    all_pages = []
    all_recommendations = []
    all_experience = []
    personas_found = []
    
    # Scan for persona directories with enhanced CSV data
    for persona_dir in audit_outputs_dir.iterdir():
        if persona_dir.is_dir():
            criteria_file = persona_dir / "criteria_scores.csv"
            pages_file = persona_dir / "pages.csv"
            recommendations_file = persona_dir / "recommendations.csv"
            
            if criteria_file.exists():
                try:
                    # Load criteria scores (main dataset)
                    criteria_df = pd.read_csv(criteria_file)
                    criteria_df['persona_id'] = persona_dir.name
                    all_data.append(criteria_df)
                    
                    # Load pages metadata
                    if pages_file.exists():
                        pages_df = pd.read_csv(pages_file)
                        pages_df['persona_id'] = persona_dir.name
                        all_pages.append(pages_df)
                    
                    # Load recommendations
                    if recommendations_file.exists():
                        rec_df = pd.read_csv(recommendations_file)
                        rec_df['persona_id'] = persona_dir.name
                        all_recommendations.append(rec_df)
                    
                    # Load experience data
                    experience_file = persona_dir / "experience.csv"
                    if experience_file.exists():
                        exp_df = pd.read_csv(experience_file)
                        exp_df['persona_id'] = persona_dir.name
                        all_experience.append(exp_df)
                    
                    personas_found.append(persona_dir.name)
                    
                except Exception as e:
                    st.warning(f"Error loading data for {persona_dir.name}: {e}")
                    continue
    
    if not all_data:
        return None, None
    
    # Combine all data
    df = pd.concat(all_data, ignore_index=True)
    
    # Combine experience data if available
    experience_df = None
    if all_experience:
        experience_df = pd.concat(all_experience, ignore_index=True)
    
    # Combine pages data if available
    pages_df = None
    if all_pages:
        pages_df = pd.concat(all_pages, ignore_index=True)
    
    # Combine recommendations data if available
    recommendations_df = None
    if all_recommendations:
        recommendations_df = pd.concat(all_recommendations, ignore_index=True)
    
    # Create comprehensive joined dataset
    if pages_df is not None:
        # Start with pages as the master table
        master_df = pages_df.copy()
        
        # Add criteria scores
        criteria_summary = df.groupby(['page_id', 'persona_id']).agg({
            'score': ['mean', 'min', 'max', 'count'],
            'tier': 'first'  # Should be same for all criteria of a page
        }).round(2)
        criteria_summary.columns = ['avg_score', 'min_score', 'max_score', 'criteria_count', 'criteria_tier']
        criteria_summary = criteria_summary.reset_index()
        
        master_df = master_df.merge(criteria_summary, on=['page_id', 'persona_id'], how='left')
        
        # Add experience data
        if experience_df is not None:
            master_df = master_df.merge(experience_df, on=['page_id', 'persona_id'], how='left')
        
        # Add recommendations summary
        if recommendations_df is not None:
            rec_summary = recommendations_df.groupby(['page_id']).agg({
                'recommendation': 'count',
                'strategic_impact': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
            }).rename(columns={'recommendation': 'rec_count', 'strategic_impact': 'primary_impact'})
            rec_summary = rec_summary.reset_index()
            master_df = master_df.merge(rec_summary, on='page_id', how='left')
        
        # Fill missing values
        master_df['rec_count'] = master_df['rec_count'].fillna(0)
        master_df['primary_impact'] = master_df['primary_impact'].fillna('None')
        
        # Create enhanced criteria dataset with experience context
        df_enhanced = df.merge(
            master_df[['page_id', 'persona_id', 'url', 'slug', 'tier', 'final_score', 
                      'overall_sentiment', 'engagement_level', 'conversion_likelihood']],
            on=['page_id', 'persona_id'], how='left', suffixes=('', '_page')
        )
        
        # Use page tier if available, otherwise keep original
        df_enhanced['tier'] = df_enhanced['tier_page'].fillna(df_enhanced['tier'])
        df_enhanced = df_enhanced.drop('tier_page', axis=1)
        df_enhanced['url_slug'] = df_enhanced['slug'].fillna(df_enhanced['page_id'])
        
        # Store the master dataset for comprehensive analysis
        df = df_enhanced
        
    else:
        master_df = None
        df['url_slug'] = df['page_id']
    
    # Rename columns to match expected format
    if 'score' in df.columns:
        df['raw_score'] = df['score']
    if 'criterion_code' in df.columns:
        df['criterion_id'] = df['criterion_code']
    if 'evidence' in df.columns:
        df['rationale'] = df['evidence']
    
    # Create summary statistics
    summary = {
        'total_personas': len(personas_found),
        'total_pages': df['page_id'].nunique(),
        'total_evaluations': len(df),
        'total_experiences': len(experience_df) if experience_df is not None else 0,
        'total_recommendations': len(recommendations_df) if recommendations_df is not None else 0,
        'average_score': df['raw_score'].mean(),
        'personas': personas_found,
        'has_experience_data': experience_df is not None and not experience_df.empty,
        'has_recommendations': recommendations_df is not None and not recommendations_df.empty
    }
    
    # Add descriptor based on score
    def get_descriptor(score):
        if score >= 8.0:
            return 'EXCELLENT'
        elif score >= 4.0:
            return 'PASS'
        else:
            return 'FAIL'
    
    df['descriptor'] = df['raw_score'].apply(get_descriptor)
    
    # Return comprehensive dataset package
    datasets = {
        'criteria': df,  # Enhanced criteria with experience context
        'experience': experience_df,
        'pages': pages_df, 
        'recommendations': recommendations_df,
        'master': master_df  # Comprehensive joined dataset
    }
    
    return datasets, summary

def main():
    st.set_page_config(
        page_title="Brand Audit Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add Sopra Steria inspired styling
    st.markdown("""
    <style>
    /* Import Sopra Steria-inspired fonts and colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom header styling */
    .sopra-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .sopra-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .sopra-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize audit state
    initialize_audit_state()
    
    # Custom Sopra Steria inspired header
    st.markdown("""
    <div class="sopra-header">
        <h1>🔍 Brand Audit Dashboard</h1>
        <p>Complete audit solution - run new audits and analyze multi-persona results</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data and store in session state
    datasets, summary = load_audit_data()
    
    if datasets is not None:
        st.session_state['datasets'] = datasets
        st.session_state['summary'] = summary
        
        # Show data status
        experience_info = f", {summary['total_experiences']} experiences" if summary['total_experiences'] > 0 else ""
        rec_info = f", {summary['total_recommendations']} recommendations" if summary['total_recommendations'] > 0 else ""
        st.success(f"📊 Data loaded: {summary['total_personas']} personas, {summary['total_pages']} pages, {summary['total_evaluations']} evaluations{experience_info}{rec_info}")
    else:
        st.warning("No audit data found. Please run an audit first or check if data exists.")
        st.info("💡 Use the 'Run Audit' page to create new audit data")

if __name__ == "__main__":
    main() 