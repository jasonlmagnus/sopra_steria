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
    st.title("📋 Detailed Data Explorer")
    
    # Check if we have data
    if 'datasets' not in st.session_state or st.session_state['datasets'] is None:
        st.error("No audit data found. Please ensure data is loaded from the main dashboard.")
        return
    
    datasets = st.session_state['datasets']
    summary = st.session_state['summary']
    filtered_df = datasets['criteria']
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    st.info("This tab provides comprehensive data export and detailed analysis capabilities.")
    
    # Show data summary
    st.markdown("#### 📊 Data Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(filtered_df))
    with col2:
        st.metric("Unique Pages", filtered_df['page_id'].nunique())
    with col3:
        st.metric("Unique Criteria", filtered_df['criterion_id'].nunique())
    with col4:
        st.metric("Average Score", f"{filtered_df['raw_score'].mean():.2f}")
    
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
    
    # Apply score range filter
    display_df = display_df[
        (display_df['raw_score'] >= score_range[0]) & 
        (display_df['raw_score'] <= score_range[1])
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
        sort_by = st.selectbox("Sort by:", ['raw_score', 'persona_id', 'tier', 'criterion_id'])
    with col3:
        sort_order = st.selectbox("Order:", ['Descending', 'Ascending'])
    
    # Filter and display data
    if search_term:
        display_df = display_df[display_df['url_slug'].str.contains(search_term, case=False, na=False)]
    
    ascending = sort_order == 'Ascending'
    display_df = display_df.sort_values(sort_by, ascending=ascending)
    
    # Format for display
    display_columns = ['persona_id', 'url_slug', 'tier', 'criterion_id', 'raw_score', 'descriptor', 'rationale']
    display_df_formatted = display_df[display_columns].copy()
    display_df_formatted['url_slug'] = display_df_formatted['url_slug'].str.replace('_', ' ').str.title()
    display_df_formatted['criterion_id'] = display_df_formatted['criterion_id'].str.replace('_', ' ').str.title()
    display_df_formatted['tier'] = display_df_formatted['tier'].str.replace('_', ' ').str.title()
    display_df_formatted.columns = ['Persona', 'Page', 'Category', 'Criterion', 'Score', 'Performance', 'AI Rationale']
    
    st.dataframe(display_df_formatted, use_container_width=True, height=500)
    
    # Enhanced export options
    st.markdown("#### 📥 Export Data")
    col1, col2, col3 = st.columns(3)
    with col1:
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Download Full CSV", csv_data, "full_audit_data.csv", "text/csv")
    with col2:
        summary_data = display_df.groupby(['persona_id', 'url_slug'])['raw_score'].mean().reset_index()
        summary_csv = summary_data.to_csv(index=False).encode('utf-8')
        st.download_button("📊 Download Summary CSV", summary_csv, "audit_summary.csv", "text/csv")
    with col3:
        rationale_data = display_df[['persona_id', 'url_slug', 'criterion_id', 'raw_score', 'rationale']]
        rationale_csv = rationale_data.to_csv(index=False).encode('utf-8')
        st.download_button("💭 Download Rationale CSV", rationale_csv, "audit_rationale.csv", "text/csv")
    
    # Additional export options
    st.markdown("#### 📊 Advanced Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📈 Export Performance Summary"):
            # Create performance summary
            perf_summary = display_df.groupby(['persona_id', 'tier']).agg({
                'raw_score': ['mean', 'std', 'count', 'min', 'max']
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
                'raw_score': ['mean', 'count'],
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
            'Missing Rationale': filtered_df['rationale'].isna().sum(),
            'Score Range': f"{filtered_df['raw_score'].min():.1f} - {filtered_df['raw_score'].max():.1f}",
            'Unique Pages': filtered_df['page_id'].nunique(),
            'Unique Criteria': filtered_df['criterion_id'].nunique()
        }
        
        for key, value in quality_info.items():
            st.write(f"- **{key}**: {value}")

if __name__ == "__main__":
    main() 