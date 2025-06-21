#!/usr/bin/env python3
"""
Persona Experience Analysis
Detailed persona experience data and insights
"""

import streamlit as st
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    st.title("👤 Persona Experience Analysis")
    
    # Check if we have data
    if 'datasets' not in st.session_state or st.session_state['datasets'] is None:
        st.error("No audit data found. Please ensure data is loaded from the main dashboard.")
        return
    
    datasets = st.session_state['datasets']
    summary = st.session_state['summary']
    filtered_df = datasets['criteria']
    experience_df = datasets['experience']
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Check if experience data is available
    if experience_df is None or experience_df.empty:
        st.warning("No experience data available. Experience analysis requires enhanced audit data with persona feedback.")
        return
    
    # Experience overview metrics
    st.markdown("### 📊 Experience Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        positive_sentiment = (experience_df['overall_sentiment'] == 'Positive').sum()
        st.metric("Positive Sentiment", f"{positive_sentiment}/{len(experience_df)}")
    
    with col2:
        high_engagement = (experience_df['engagement_level'] == 'High').sum()
        st.metric("High Engagement", f"{high_engagement}/{len(experience_df)}")
    
    with col3:
        high_conversion = (experience_df['conversion_likelihood'] == 'High').sum()
        st.metric("High Conversion", f"{high_conversion}/{len(experience_df)}")
    
    with col4:
        avg_sentiment_score = {'Positive': 3, 'Mixed': 2, 'Negative': 1, 'Neutral': 1.5}
        sentiment_scores = experience_df['overall_sentiment'].map(avg_sentiment_score)
        st.metric("Avg Sentiment", f"{sentiment_scores.mean():.1f}/3.0")
    
    # Sentiment analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment distribution
        sentiment_counts = experience_df['overall_sentiment'].value_counts()
        fig_sentiment = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="📊 Overall Sentiment Distribution",
            color_discrete_map={
                'Positive': '#22c55e',
                'Mixed': '#eab308',
                'Negative': '#ef4444',
                'Neutral': '#94a3b8'
            }
        )
        st.plotly_chart(fig_sentiment, use_container_width=True)
    
    with col2:
        # Engagement vs Conversion
        engagement_conversion = experience_df.groupby(['engagement_level', 'conversion_likelihood']).size().reset_index(name='count')
        fig_eng_conv = px.scatter(
            engagement_conversion,
            x='engagement_level',
            y='conversion_likelihood',
            size='count',
            title="🎯 Engagement vs Conversion Likelihood",
            color='count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_eng_conv, use_container_width=True)
    
    # Page-level experience analysis
    st.markdown("### 📄 Page Experience Breakdown")
    
    # Merge with page data for better display
    if 'url_slug' in filtered_df.columns:
        page_experience = experience_df.merge(
            filtered_df[['page_id', 'url_slug', 'tier']].drop_duplicates(),
            on='page_id',
            how='left'
        )
    else:
        page_experience = experience_df.copy()
        page_experience['url_slug'] = page_experience['page_id']
    
    # Experience heatmap
    experience_metrics = page_experience.groupby('url_slug').agg({
        'overall_sentiment': lambda x: (x == 'Positive').sum() / len(x),
        'engagement_level': lambda x: (x == 'High').sum() / len(x),
        'conversion_likelihood': lambda x: (x == 'High').sum() / len(x)
    }).round(2)
    
    experience_metrics.columns = ['Positive Sentiment %', 'High Engagement %', 'High Conversion %']
    
    fig_heatmap = px.imshow(
        experience_metrics.T.values,
        x=[slug.replace('_', ' ').title()[:30] + '...' if len(slug) > 30 else slug.replace('_', ' ').title() for slug in experience_metrics.index],
        y=experience_metrics.columns,
        color_continuous_scale='RdYlGn',
        aspect='auto',
        title="🔥 Page Experience Heatmap"
    )
    fig_heatmap.update_layout(height=300)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Detailed experience explorer
    st.markdown("### 🔍 Detailed Experience Explorer")
    
    # Page selector - fix sorting error by handling mixed data types
    unique_slugs = page_experience['url_slug'].dropna().astype(str).unique()
    selected_page = st.selectbox(
        "Select page for detailed experience analysis:",
        options=sorted(unique_slugs),
        format_func=lambda x: str(x).replace('_', ' ').title()
    )
    
    if selected_page:
        page_exp = page_experience[page_experience['url_slug'] == selected_page].iloc[0]
        
        # Experience summary
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment_color = {"Positive": "🟢", "Mixed": "🟡", "Negative": "🔴", "Neutral": "⚪"}
            st.metric("Sentiment", f"{sentiment_color.get(page_exp['overall_sentiment'], '⚪')} {page_exp['overall_sentiment']}")
        with col2:
            engagement_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
            st.metric("Engagement", f"{engagement_color.get(page_exp['engagement_level'], '⚪')} {page_exp['engagement_level']}")
        with col3:
            conversion_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
            st.metric("Conversion", f"{conversion_color.get(page_exp['conversion_likelihood'], '⚪')} {page_exp['conversion_likelihood']}")
        
        # Detailed feedback sections
        col1, col2 = st.columns(2)
        
        with col1:
            if pd.notna(page_exp.get('first_impression')):
                st.markdown("#### 👁️ First Impression")
                st.write(page_exp['first_impression'])
            
            if pd.notna(page_exp.get('language_tone_feedback')):
                st.markdown("#### 🗣️ Language & Tone Feedback")
                st.write(page_exp['language_tone_feedback'])
            
            if pd.notna(page_exp.get('information_gaps')):
                st.markdown("#### ❓ Information Gaps")
                st.write(page_exp['information_gaps'])
        
        with col2:
            if pd.notna(page_exp.get('trust_credibility_assessment')):
                st.markdown("#### 🛡️ Trust & Credibility Assessment")
                st.write(page_exp['trust_credibility_assessment'])
            
            if pd.notna(page_exp.get('business_impact_analysis')):
                st.markdown("#### 💼 Business Impact Analysis")
                st.write(page_exp['business_impact_analysis'])
        
        # Copy examples
        if pd.notna(page_exp.get('effective_copy_examples')):
            st.markdown("#### ✅ Effective Copy Examples")
            effective_examples = str(page_exp['effective_copy_examples']).split(' | ')
            for example in effective_examples:
                if example.strip():
                    st.success(example)
        
        if pd.notna(page_exp.get('ineffective_copy_examples')):
            st.markdown("#### ❌ Ineffective Copy Examples")
            ineffective_examples = str(page_exp['ineffective_copy_examples']).split(' | ')
            for example in ineffective_examples:
                if example.strip():
                    st.error(example)

if __name__ == "__main__":
    main() 