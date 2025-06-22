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
    """Main persona experience analysis page"""
    st.set_page_config(page_title="Persona Experience", page_icon="👤", layout="wide")
    
    # Get data from session state
    if 'master_df' not in st.session_state:
        st.error("❌ No data available. Please go to the main dashboard first to load data.")
        return
    
    master_df = st.session_state['master_df']
    datasets = st.session_state.get('datasets', {})
    
    st.title("👤 Persona Experience Analysis")
    st.markdown("### Deep dive into persona-specific user experience metrics")
    
    # Check if we have experience data
    if 'overall_sentiment' not in master_df.columns:
        st.warning("⚠️ No experience data available in current dataset")
        st.info("Experience analysis requires sentiment and engagement data")
        return
    
    # Persona filter
    if 'persona_id' in master_df.columns:
        personas = list(master_df['persona_id'].unique())
        selected_persona = st.selectbox("Select Persona for Analysis", personas)
        
        # Filter data for selected persona
        persona_data = master_df[master_df['persona_id'] == selected_persona]
    else:
        st.warning("No persona data available")
        return
    
    if len(persona_data) == 0:
        st.warning(f"No data available for persona: {selected_persona}")
        return
    
    # Experience overview metrics
    st.markdown("### 📊 Experience Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        positive_sentiment = (persona_data['overall_sentiment'] == 'Positive').sum()
        st.metric("Positive Sentiment", f"{positive_sentiment}/{len(persona_data)}")
    
    with col2:
        high_engagement = (persona_data['engagement_level'] == 'High').sum()
        st.metric("High Engagement", f"{high_engagement}/{len(persona_data)}")
    
    with col3:
        high_conversion = (persona_data['conversion_likelihood'] == 'High').sum()
        st.metric("High Conversion", f"{high_conversion}/{len(persona_data)}")
    
    with col4:
        avg_sentiment_score = {'Positive': 3, 'Mixed': 2, 'Negative': 1, 'Neutral': 1.5}
        sentiment_scores = persona_data['overall_sentiment'].map(avg_sentiment_score)
        st.metric("Avg Sentiment", f"{sentiment_scores.mean():.1f}/3.0")
    
    # Sentiment analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment distribution
        sentiment_counts = persona_data['overall_sentiment'].value_counts()
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
        engagement_conversion = persona_data.groupby(['engagement_level', 'conversion_likelihood']).size().reset_index(name='count')
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
    
    # Use persona_data directly - it already has all required columns from unified CSV
    page_experience = persona_data.copy()
    
    # Experience heatmap
    # Use url_slug from unified CSV
    if 'url_slug' in persona_data.columns:
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
    else:
        st.warning("No URL slug data available for experience heatmap")
    
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