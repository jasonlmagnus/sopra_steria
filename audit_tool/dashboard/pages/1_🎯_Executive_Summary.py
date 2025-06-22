#!/usr/bin/env python3
"""
Executive Summary Page
High-level brand health overview with critical issues and opportunities
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    """Main executive summary page"""
    st.set_page_config(page_title="Executive Summary", page_icon="🎯", layout="wide")
    
    # Get data from session state
    if 'master_df' not in st.session_state or 'datasets' not in st.session_state:
        st.error("❌ No data available. Please go to the main dashboard first to load data.")
        return
    
    master_df = st.session_state['master_df']
    datasets = st.session_state['datasets']
    summary = st.session_state.get('summary', {})
    
    st.title("🎯 Executive Summary")
    st.markdown("### Strategic Overview & Key Performance Indicators")
    
    # Persona filter
    if 'persona_id' in master_df.columns:
        personas = ['All'] + list(master_df['persona_id'].unique())
        selected_persona = st.selectbox("Select Persona", personas)
        
        if selected_persona != 'All':
            filtered_df = master_df[master_df['persona_id'] == selected_persona]
        else:
            filtered_df = master_df
    else:
        filtered_df = master_df
        st.info("ℹ️ No persona filtering available")
    
    # Key metrics using correct column names from unified data
    total_pages = len(filtered_df)
    
    # Use the correct score column from unified CSV
    score_col = None
    if 'final_score' in filtered_df.columns:
        score_col = 'final_score'
    elif 'raw_score' in filtered_df.columns:
        score_col = 'raw_score'
    elif 'avg_score' in filtered_df.columns:
        score_col = 'avg_score'
    
    avg_score = filtered_df[score_col].mean() if score_col else 0
    positive_sentiment = (filtered_df['overall_sentiment'] == 'Positive').sum() if 'overall_sentiment' in filtered_df.columns else 0
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Pages", total_pages)
    with col2:
        st.metric("Average Score", f"{avg_score:.1f}/10")
    with col3:
        st.metric("Positive Sentiment", f"{positive_sentiment}/{total_pages}")
    with col4:
        conversion_high = (filtered_df['conversion_likelihood'] == 'High').sum() if 'conversion_likelihood' in filtered_df.columns else 0
        st.metric("High Conversion", f"{conversion_high}/{total_pages}")
    
    # Performance by tier using correct column names
    if 'tier' in filtered_df.columns and score_col:
        st.subheader("📊 Performance by Tier")
        
        # Build aggregation dict based on available columns - use the correct score column
        agg_dict = {score_col: ['mean', 'count']}
        if 'overall_sentiment' in filtered_df.columns:
            agg_dict['overall_sentiment'] = lambda x: (x == 'Positive').sum()
        
        tier_analysis = filtered_df.groupby('tier').agg(agg_dict).round(2)
        
        # Flatten column names
        tier_analysis.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in tier_analysis.columns]
        
        st.dataframe(tier_analysis)
    
    # Critical Issues Alert - use correct score column
    if score_col:
        critical_issues = filtered_df[filtered_df[score_col] < 4.0]
        if not critical_issues.empty:
            st.markdown("---")
            st.markdown("### 🚨 Critical Issues Requiring Immediate Attention")
            
            critical_pages = critical_issues.groupby('url_slug').agg({
                score_col: 'mean',
                'criterion_id': 'count'
            }).sort_values(score_col).head(3)
            
            for page, data in critical_pages.iterrows():
                st.error(f"**{page.replace('_', ' ').title()}** - Average Score: {data[score_col]:.1f}/10 ({data['criterion_id']} failing criteria)")
    
    # Top Opportunities - use correct score column
    st.markdown("---")
    st.markdown("### 🎯 Top 3 Improvement Opportunities")
    
    # Find worst performing criteria with highest impact
    criterion_col = 'criterion_code' if 'criterion_code' in filtered_df.columns else 'criterion_id'
    
    if criterion_col in filtered_df.columns and score_col:
        criteria_impact = filtered_df.groupby(criterion_col).agg({
            score_col: ['mean', 'count'],
            'page_id': 'nunique'
        }).round(2)
        criteria_impact.columns = ['avg_score', 'evaluations', 'pages_affected']
        criteria_impact['impact_score'] = (10 - criteria_impact['avg_score']) * criteria_impact['pages_affected']
        top_opportunities = criteria_impact.sort_values('impact_score', ascending=False).head(3)
    else:
        top_opportunities = pd.DataFrame()
    
    col1, col2, col3 = st.columns(3)
    
    if not top_opportunities.empty:
        for i, (criterion, data) in enumerate(top_opportunities.iterrows()):
            if i < 3:  # Only show top 3
                with [col1, col2, col3][i]:
                    st.markdown(f"""
                    **{i+1}. {criterion.replace('_', ' ').title()}**
                    
                    - Current Score: {data['avg_score']:.1f}/10
                    - Pages Affected: {data['pages_affected']}
                    - Impact Score: {data['impact_score']:.1f}
                    """)
    else:
        st.info("📊 Opportunity analysis requires criteria data with proper column structure.")
    
    # Segmented Tier Analysis with Experience Data
    st.markdown("---")
    st.markdown("### 📊 Performance by Content Tier")
    
    if summary.get('has_experience_data', False) and master_df is not None and score_col:
        # Create comprehensive tier analysis with experience context
        tier_analysis = master_df.groupby('tier').agg({
            score_col: 'mean',
            'overall_sentiment': lambda x: (x == 'Positive').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
            'engagement_level': lambda x: (x == 'High').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
            'conversion_likelihood': lambda x: (x == 'High').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
            'page_id': 'count'
        }).round(1)
        tier_analysis.columns = ['Avg Score', 'Positive Sentiment %', 'High Engagement %', 'High Conversion %', 'Page Count']
        tier_analysis = tier_analysis.sort_values('Avg Score', ascending=False)
        
        # Display tier cards
        for tier, data in tier_analysis.iterrows():
            tier_display = tier.replace('_', ' ').title()
            score_color = "🟢" if data['Avg Score'] >= 7 else "🟡" if data['Avg Score'] >= 4 else "🔴"
            
            with st.expander(f"{score_color} {tier_display} ({int(data['Page Count'])} pages) - Score: {data['Avg Score']:.1f}/10"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Average Score", f"{data['Avg Score']:.1f}/10")
                with col2:
                    sentiment_icon = "🟢" if data['Positive Sentiment %'] >= 60 else "🟡" if data['Positive Sentiment %'] >= 40 else "🔴"
                    st.metric("Positive Sentiment", f"{sentiment_icon} {data['Positive Sentiment %']:.0f}%")
                with col3:
                    engagement_icon = "🟢" if data['High Engagement %'] >= 60 else "🟡" if data['High Engagement %'] >= 40 else "🔴"
                    st.metric("High Engagement", f"{engagement_icon} {data['High Engagement %']:.0f}%")
                with col4:
                    conversion_icon = "🟢" if data['High Conversion %'] >= 60 else "🟡" if data['High Conversion %'] >= 40 else "🔴"
                    st.metric("High Conversion", f"{conversion_icon} {data['High Conversion %']:.0f}%")
                
                # Show best and worst performing pages in this tier
                tier_pages = master_df[master_df['tier'] == tier].sort_values(score_col, ascending=False)
                if not tier_pages.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        best_page = tier_pages.iloc[0]
                        st.markdown("**🏆 Best Performing Page:**")
                        st.write(f"• {best_page['slug'].replace('_', ' ').title()}")
                        st.write(f"• Score: {best_page[score_col]:.1f}/10")
                        if pd.notna(best_page['overall_sentiment']):
                            st.write(f"• Sentiment: {best_page['overall_sentiment']}")
                    
                    with col2:
                        if len(tier_pages) > 1:
                            worst_page = tier_pages.iloc[-1]
                            st.markdown("**⚠️ Needs Attention:**")
                            st.write(f"• {worst_page['slug'].replace('_', ' ').title()}")
                            st.write(f"• Score: {worst_page[score_col]:.1f}/10")
                            if pd.notna(worst_page['overall_sentiment']):
                                st.write(f"• Sentiment: {worst_page['overall_sentiment']}")
    else:
        # Fallback tier analysis without experience data - use correct score column
        if score_col:
            tier_scores = filtered_df.groupby('tier').agg({
                score_col: ['mean', 'count'],
                'descriptor': lambda x: (x == 'EXCELLENT').sum()
            }).round(2)
            tier_scores.columns = ['Avg Score', 'Page Count', 'Excellence Count']
            tier_scores = tier_scores.sort_values('Avg Score', ascending=False)
            
            for tier, data in tier_scores.iterrows():
                tier_display = tier.replace('_', ' ').title()
                score_color = "🟢" if data['Avg Score'] >= 7 else "🟡" if data['Avg Score'] >= 4 else "🔴"
                st.markdown(f"{score_color} **{tier_display}**: {data['Avg Score']:.1f}/10 ({int(data['Page Count'])} pages, {int(data['Excellence Count'])} excellent)")
    
    # Success Stories - use correct score column
    st.markdown("---")
    st.markdown("### 🏆 Success Stories to Replicate")
    
    if score_col:
        excellent_examples = filtered_df[filtered_df[score_col] >= 8.0]
        if not excellent_examples.empty:
            success_stories = excellent_examples.groupby(['url_slug', 'criterion_id']).first().sort_values(score_col, ascending=False).head(3)
            
            for i, ((page, criterion), data) in enumerate(success_stories.iterrows()):
                with st.expander(f"🌟 Success #{i+1}: {page.replace('_', ' ').title()} - {criterion.replace('_', ' ').title()}"):
                    st.write(f"**Score:** {data[score_col]}/10")
                    st.write(f"**Why it works:** {data['rationale']}")
                    if 'url' in data and pd.notna(data['url']):
                        st.write(f"**URL:** {data['url']}")

if __name__ == "__main__":
    main() 