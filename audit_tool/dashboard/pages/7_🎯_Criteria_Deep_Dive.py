#!/usr/bin/env python3
"""
Criteria Deep Dive Page
Detailed analysis of specific criteria performance
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    st.title("🎯 Criteria Deep Dive")
    
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
    
    st.markdown("### 📊 Criteria Performance Distribution")
    
    # Criteria analysis using correct column names
    if 'criterion_id' in filtered_df.columns:
        unique_criteria = filtered_df['criterion_id'].dropna().astype(str).unique()
        
        # Criteria selector
        selected_criteria = st.multiselect(
            "Select Criteria to Analyze",
            options=sorted(unique_criteria),
            default=sorted(unique_criteria)[:5]  # Show first 5 by default
        )
        
        if selected_criteria:
            criteria_df = filtered_df[filtered_df['criterion_id'].isin(selected_criteria)]
            
            # Performance by criteria using correct column names
            if 'raw_score' in criteria_df.columns:
                st.subheader("📊 Performance by Criteria")
                
                criteria_performance = criteria_df.groupby('criterion_id').agg({
                    'raw_score': ['mean', 'count', 'std']
                }).round(2)
                
                # Flatten column names
                criteria_performance.columns = ['_'.join(col).strip() for col in criteria_performance.columns]
                criteria_performance = criteria_performance.sort_values('raw_score_mean', ascending=False)
                
                st.dataframe(criteria_performance)
            else:
                st.warning("No score data available for criteria analysis")
        else:
            st.info("Please select criteria to analyze")
    else:
        st.warning("No criterion_id column found in the data")

if __name__ == "__main__":
    main() 