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
    
    unique_criteria = filtered_df['criterion_id'].dropna().astype(str).unique()
    selected_criterion = st.selectbox(
        "Select criterion for detailed analysis:",
        options=sorted(unique_criteria),
        format_func=lambda x: str(x).replace('_', ' ').title()
    )
    
    if selected_criterion:
        criterion_data = filtered_df[filtered_df['criterion_id'] == selected_criterion]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution for this criterion
            fig_criterion_dist = px.histogram(
                criterion_data,
                x='raw_score',
                color='persona_id',
                title=f"Score Distribution: {selected_criterion.replace('_', ' ').title()}",
                nbins=10,
                barmode='overlay'
            )
            st.plotly_chart(fig_criterion_dist, use_container_width=True)
        
        with col2:
            # Performance by page for this criterion
            criterion_by_page = criterion_data.groupby('url_slug')['raw_score'].mean().sort_values(ascending=True)
            fig_criterion_pages = px.bar(
                x=criterion_by_page.values,
                y=[slug.replace('_', ' ').title() for slug in criterion_by_page.index],
                orientation='h',
                title=f"Page Performance: {selected_criterion.replace('_', ' ').title()}",
                color=criterion_by_page.values,
                color_continuous_scale='RdYlGn'
            )
            fig_criterion_pages.update_layout(showlegend=False)
            st.plotly_chart(fig_criterion_pages, use_container_width=True)
        
        # Show rationale examples for this criterion
        st.markdown(f"### 💭 AI Rationale Examples for {selected_criterion.replace('_', ' ').title()}")
        
        # Get diverse examples (high, medium, low scores)
        high_score = criterion_data[criterion_data['raw_score'] >= 7.0].sample(min(2, len(criterion_data[criterion_data['raw_score'] >= 7.0])))
        med_score = criterion_data[(criterion_data['raw_score'] >= 4.0) & (criterion_data['raw_score'] < 7.0)].sample(min(2, len(criterion_data[(criterion_data['raw_score'] >= 4.0) & (criterion_data['raw_score'] < 7.0)])))
        low_score = criterion_data[criterion_data['raw_score'] < 4.0].sample(min(2, len(criterion_data[criterion_data['raw_score'] < 4.0])))
        
        examples = pd.concat([high_score, med_score, low_score]).sort_values('raw_score', ascending=False)
        
        for _, row in examples.iterrows():
            score_color = "🟢" if row['raw_score'] >= 7 else "🟡" if row['raw_score'] >= 4 else "🔴"
            with st.expander(f"{score_color} {row['url_slug'].replace('_', ' ').title()} - Score: {row['raw_score']}/10"):
                st.write(f"**Persona:** {row['persona_id']}")
                st.write(f"**Performance:** {row['descriptor']}")
                st.write(f"**AI Rationale:** {row['rationale']}")

if __name__ == "__main__":
    main() 