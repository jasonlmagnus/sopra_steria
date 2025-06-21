#!/usr/bin/env python3
"""
Page Performance Analysis
Individual page deep dive and performance analysis
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    st.title("📄 Page Performance Analysis")
    
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
    
    # Page performance overview
    page_performance = filtered_df.groupby('url_slug').agg({
        'raw_score': ['mean', 'std', 'min', 'max', 'count']
    }).round(2)
    page_performance.columns = ['Average', 'Std Dev', 'Min', 'Max', 'Evaluations']
    page_performance = page_performance.sort_values('Average', ascending=False)
    
    # Best and worst performing pages
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Top Performing Pages")
        top_pages = page_performance.head(5)
        for idx, (page, row) in enumerate(top_pages.iterrows()):
            st.markdown(f"""
            **{idx+1}. {page.replace('_', ' ').title()}**  
            Average: {row['Average']:.2f}/10 | Evaluations: {int(row['Evaluations'])}
            """)
    
    with col2:
        st.markdown("#### ⚠️ Pages Needing Improvement")
        bottom_pages = page_performance.tail(5)
        for idx, (page, row) in enumerate(bottom_pages.iterrows()):
            st.markdown(f"""
            **{idx+1}. {page.replace('_', ' ').title()}**  
            Average: {row['Average']:.2f}/10 | Evaluations: {int(row['Evaluations'])}
            """)
    
    # Detailed page analysis
    st.markdown("### 🔍 Individual Page Deep Dive")
    
    unique_pages = filtered_df['url_slug'].dropna().astype(str).unique()
    selected_page = st.selectbox(
        "Select page for detailed analysis:",
        options=sorted(unique_pages),
        format_func=lambda x: str(x).replace('_', ' ').title()
    )
    
    if selected_page:
        page_data = filtered_df[filtered_df['url_slug'] == selected_page]
        
        # Page metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Average Score", f"{page_data['raw_score'].mean():.2f}/10")
        with col2:
            st.metric("Total Evaluations", len(page_data))
        with col3:
            pass_rate = (page_data['descriptor'].isin(['PASS', 'EXCELLENT'])).mean() * 100
            st.metric("Success Rate", f"{pass_rate:.1f}%")
        with col4:
            st.metric("Personas", len(page_data['persona_id'].unique()))
        
        # Performance breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            # Criteria performance for this page
            criteria_scores = page_data.groupby('criterion_id')['raw_score'].mean().sort_values(ascending=True)
            fig_page_criteria = px.bar(
                x=criteria_scores.values,
                y=[c.replace('_', ' ').title() for c in criteria_scores.index],
                orientation='h',
                title=f"Criteria Performance: {selected_page.replace('_', ' ').title()}",
                color=criteria_scores.values,
                color_continuous_scale='RdYlGn'
            )
            fig_page_criteria.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_page_criteria, use_container_width=True)
        
        with col2:
            # Persona comparison for this page
            if len(page_data['persona_id'].unique()) > 1:
                persona_scores = page_data.groupby('persona_id')['raw_score'].mean()
                fig_page_personas = px.bar(
                    x=persona_scores.index,
                    y=persona_scores.values,
                    title=f"Persona Performance: {selected_page.replace('_', ' ').title()}",
                    color=persona_scores.values,
                    color_continuous_scale='RdYlGn'
                )
                fig_page_personas.update_layout(showlegend=False)
                st.plotly_chart(fig_page_personas, use_container_width=True)
            else:
                st.info("Only one persona evaluated this page")
        
        # Show URL and detailed breakdown
        page_url = page_data['url'].iloc[0] if 'url' in page_data.columns else "URL not available"
        st.markdown(f"**Page URL:** {page_url}")
        
        # Detailed evaluation results
        st.markdown("### 📋 Detailed Evaluation Results")
        page_display = page_data[['persona_id', 'tier', 'criterion_id', 'raw_score', 'descriptor', 'rationale']].copy()
        page_display['tier'] = page_display['tier'].str.replace('_', ' ').str.title()
        page_display['criterion_id'] = page_display['criterion_id'].str.replace('_', ' ').str.title()
        page_display.columns = ['Persona', 'Category', 'Criterion', 'Score', 'Performance', 'AI Rationale']
        
        st.dataframe(page_display, use_container_width=True, height=400)

if __name__ == "__main__":
    main() 