#!/usr/bin/env python3
"""
Detailed Data Explorer
Raw data explorer and comprehensive export functionality
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    """Main detailed data page"""
    st.set_page_config(page_title="Detailed Data", page_icon="📋", layout="wide")
    
    # Get data from session state
    if 'master_df' not in st.session_state:
        st.error("❌ No data available. Please go to the main dashboard first to load data.")
        return
    
    master_df = st.session_state['master_df']
    datasets = st.session_state.get('datasets', {})
    
    st.title("📋 Detailed Data Explorer")
    st.markdown("### Raw data access and detailed filtering")
    
    # Sidebar filters
    st.sidebar.header("🔍 Data Filters")
    
    # Persona filter
    if 'persona_id' in master_df.columns:
        personas = ['All'] + list(master_df['persona_id'].unique())
        selected_persona = st.sidebar.selectbox("Persona", personas)
        
        if selected_persona != 'All':
            filtered_df = master_df[master_df['persona_id'] == selected_persona]
        else:
            filtered_df = master_df
    else:
        filtered_df = master_df
    
    # Tier filter
    if 'tier' in filtered_df.columns:
        tiers = ['All'] + list(filtered_df['tier'].unique())
        selected_tier = st.sidebar.selectbox("Tier", tiers)
        
        if selected_tier != 'All':
            filtered_df = filtered_df[filtered_df['tier'] == selected_tier]
    
    # Score filter
    if 'avg_score' in filtered_df.columns:
        min_score = st.sidebar.slider("Minimum Score", 0.0, 10.0, 0.0)
        filtered_df = filtered_df[filtered_df['avg_score'] >= min_score]
    
    # Data overview
    st.subheader("📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(filtered_df))
    
    with col2:
        if 'page_id' in filtered_df.columns:
            st.metric("Unique Pages", filtered_df['page_id'].nunique())
        else:
            st.metric("Unique Pages", "N/A")
    
    with col3:
        if 'criterion_id' in filtered_df.columns:
            st.metric("Unique Criteria", filtered_df['criterion_id'].nunique())
        else:
            st.metric("Unique Criteria", "N/A")
    
    with col4:
        if 'avg_score' in filtered_df.columns:
            st.metric("Average Score", f"{filtered_df['avg_score'].mean():.1f}")
        else:
            st.metric("Average Score", "N/A")
    
    st.info("This tab provides comprehensive data export and detailed analysis capabilities.")
    
    # Full data table with advanced filtering
    st.markdown("#### 🔍 Complete Dataset")
    
    # Advanced filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search_all = st.text_input("🔍 Search all fields:", placeholder="Search across all data...")
    with col2:
        score_range = st.slider("Score range:", 0.0, 10.0, (0.0, 10.0), 0.1)
    with col3:
        selected_personas = st.multiselect(
            "Filter by personas:",
            options=filtered_df['persona_id'].unique(),
            default=filtered_df['persona_id'].unique()
        )
    
    # Apply filters
    display_df = filtered_df.copy()
    
    if search_all:
        # Search across multiple text columns
        search_columns = ['url_slug', 'criterion_id', 'tier', 'rationale']
        search_mask = pd.Series([False] * len(display_df))
        for col in search_columns:
            if col in display_df.columns:
                search_mask |= display_df[col].astype(str).str.contains(search_all, case=False, na=False)
        display_df = display_df[search_mask]
    
    # Apply score range filter - use avg_score from unified CSV
    score_col = 'avg_score' if 'avg_score' in display_df.columns else 'raw_score'
    if score_col in display_df.columns:
        display_df = display_df[
            (display_df[score_col] >= score_range[0]) & 
            (display_df[score_col] <= score_range[1])
        ]
    
    # Apply persona filter
    if selected_personas:
        display_df = display_df[display_df['persona_id'].isin(selected_personas)]
    
    st.info(f"Showing {len(display_df)} records (filtered from {len(filtered_df)} total)")
    
    # Enhanced search and sort
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search pages:", placeholder="Enter URL or page name...")
    with col2:
        sort_options = [col for col in [score_col, 'persona_id', 'tier', 'criterion_id'] if col in display_df.columns]
        sort_by = st.selectbox("Sort by:", sort_options)
    with col3:
        sort_order = st.selectbox("Order:", ['Descending', 'Ascending'])
    
    # Filter and display data
    if search_term and 'url_slug' in display_df.columns:
        display_df = display_df[display_df['url_slug'].astype(str).str.contains(search_term, case=False, na=False)]
    
    ascending = sort_order == 'Ascending'
    if sort_by in display_df.columns:
        display_df = display_df.sort_values(sort_by, ascending=ascending)
    
    # Format for display - handle missing columns gracefully
    available_columns = ['persona_id', 'url_slug', 'tier', 'criterion_id', score_col, 'descriptor', 'rationale']
    display_columns = [col for col in available_columns if col in display_df.columns]
    
    if display_columns:
        display_df_formatted = display_df[display_columns].copy()
        
        # Safely format string columns
        if 'url_slug' in display_df_formatted.columns:
            display_df_formatted['url_slug'] = display_df_formatted['url_slug'].astype(str).str.replace('_', ' ').str.title()
        if 'criterion_id' in display_df_formatted.columns:
            display_df_formatted['criterion_id'] = display_df_formatted['criterion_id'].astype(str).str.replace('_', ' ').str.title()
        if 'tier' in display_df_formatted.columns:
            display_df_formatted['tier'] = display_df_formatted['tier'].astype(str).str.replace('_', ' ').str.title()
        
        # Update column names
        column_mapping = {
            'persona_id': 'Persona',
            'url_slug': 'Page',
            'tier': 'Category',
            'criterion_id': 'Criterion',
            score_col: 'Score',
            'descriptor': 'Performance',
            'rationale': 'AI Rationale'
        }
        display_df_formatted = display_df_formatted.rename(columns=column_mapping)
        
        st.dataframe(display_df_formatted, use_container_width=True, height=500)
    else:
        st.error("No suitable columns found for display")
    
    # Enhanced export options
    st.markdown("#### 📥 Export Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Download Full CSV", csv_data, "full_audit_data.csv", "text/csv")
    with col2:
        if 'url_slug' in display_df.columns:
            summary_data = display_df.groupby(['persona_id', 'url_slug'])[score_col].mean().reset_index()
            summary_csv = summary_data.to_csv(index=False).encode('utf-8')
            st.download_button("📊 Download Summary CSV", summary_csv, "audit_summary.csv", "text/csv")
    with col3:
        if all(col in display_df.columns for col in ['persona_id', 'url_slug', 'criterion_id', 'rationale']):
            rationale_data = display_df[['persona_id', 'url_slug', 'criterion_id', score_col, 'rationale']]
            rationale_csv = rationale_data.to_csv(index=False).encode('utf-8')
            st.download_button("💭 Download Rationale CSV", rationale_csv, "audit_rationale.csv", "text/csv")
    
    # Additional export options
    st.markdown("#### 📊 Advanced Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Export Performance Summary"):
            # Create performance summary
            perf_summary = display_df.groupby(['persona_id', 'tier']).agg({
                score_col: ['mean', 'std', 'count', 'min', 'max']
            }).round(2)
            perf_summary.columns = ['_'.join(col).strip() for col in perf_summary.columns]
            perf_csv = perf_summary.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Performance Summary",
                perf_csv,
                "performance_summary.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("🎯 Export Criteria Analysis"):
            # Create criteria analysis
            criteria_analysis = display_df.groupby(['criterion_id', 'persona_id']).agg({
                score_col: ['mean', 'count'],
                'descriptor': lambda x: (x == 'EXCELLENT').sum()
            }).round(2)
            criteria_analysis.columns = ['_'.join(col).strip() for col in criteria_analysis.columns]
            criteria_csv = criteria_analysis.reset_index().to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Criteria Analysis",
                criteria_csv,
                "criteria_analysis.csv",
                "text/csv"
            )
    
    # Raw data inspection
    st.markdown("#### 🔬 Raw Data Inspection")
    
    if st.checkbox("Show raw data structure"):
        st.markdown("**Available Datasets:**")
        for name, df in datasets.items():
            if df is not None:
                st.write(f"- **{name}**: {len(df)} rows, {len(df.columns)} columns")
                with st.expander(f"View {name} columns"):
                    st.write(list(df.columns))
    
    if st.checkbox("Show data quality info"):
        st.markdown("**Data Quality Summary:**")
        quality_info = {
            'Total Records': len(filtered_df),
            'Missing Rationale': filtered_df['rationale'].isna().sum() if 'rationale' in filtered_df.columns else 'N/A',
            'Score Range': f"{filtered_df[score_col].min():.1f} - {filtered_df[score_col].max():.1f}" if score_col in filtered_df.columns else 'N/A',
            'Unique Pages': filtered_df['page_id'].nunique() if 'page_id' in filtered_df.columns else 'N/A',
            'Unique Criteria': filtered_df['criterion_id'].nunique() if 'criterion_id' in filtered_df.columns else 'N/A'
        }
        
        for key, value in quality_info.items():
            st.write(f"- **{key}**: {value}")

if __name__ == "__main__":
    main() 