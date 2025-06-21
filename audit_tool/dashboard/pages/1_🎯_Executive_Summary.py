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
    st.title("🎯 Executive Brand Health Summary")
    
    # Check if we have data
    if 'datasets' not in st.session_state or st.session_state['datasets'] is None:
        st.error("No audit data found. Please ensure data is loaded from the main dashboard.")
        st.info("💡 Return to the main page to load audit data")
        return
    
    datasets = st.session_state['datasets']
    summary = st.session_state['summary']
    
    # Get filtered data (apply any sidebar filters if they exist)
    filtered_df = datasets['criteria']
    master_df = datasets['master']
    recommendations_df = datasets['recommendations']
    
    # Hero metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_avg = filtered_df['raw_score'].mean()
        health_status = "🟢 Excellent" if overall_avg >= 7 else "🟡 Good" if overall_avg >= 4 else "🔴 Critical"
        st.metric("Brand Health Score", f"{overall_avg:.1f}/10", help="Overall weighted average across all evaluations")
        st.markdown(f"**Status:** {health_status}")
    
    with col2:
        total_pages = filtered_df['page_id'].nunique()
        critical_pages = len(filtered_df[filtered_df['raw_score'] < 4.0]['page_id'].unique())
        st.metric("Pages Analyzed", total_pages)
        st.metric("Critical Issues", critical_pages)
    
    with col3:
        if summary['has_experience_data']:
            positive_sentiment = (filtered_df['overall_sentiment'] == 'Positive').sum()
            total_with_sentiment = len(filtered_df['overall_sentiment'].dropna())
            sentiment_pct = (positive_sentiment / total_with_sentiment * 100) if total_with_sentiment > 0 else 0
            st.metric("Positive Sentiment", f"{sentiment_pct:.0f}%")
            
            high_conversion = (filtered_df['conversion_likelihood'] == 'High').sum()
            conversion_pct = (high_conversion / total_with_sentiment * 100) if total_with_sentiment > 0 else 0
            st.metric("High Conversion", f"{conversion_pct:.0f}%")
        else:
            pass_rate = (filtered_df['descriptor'].isin(['PASS', 'EXCELLENT'])).mean() * 100
            st.metric("Success Rate", f"{pass_rate:.1f}%")
    
    with col4:
        if summary['has_recommendations']:
            total_recs = summary['total_recommendations']
            quick_wins = len(recommendations_df[recommendations_df['complexity'] == 'Low']) if recommendations_df is not None else 0
            st.metric("Total Recommendations", total_recs)
            st.metric("Quick Wins Available", quick_wins)
        else:
            excellent_count = (filtered_df['descriptor'] == 'EXCELLENT').sum()
            st.metric("Excellence Examples", excellent_count)
    
    # Critical Issues Alert
    critical_issues = filtered_df[filtered_df['raw_score'] < 4.0]
    if not critical_issues.empty:
        st.markdown("---")
        st.markdown("### 🚨 Critical Issues Requiring Immediate Attention")
        
        critical_pages = critical_issues.groupby('url_slug').agg({
            'raw_score': 'mean',
            'criterion_id': 'count'
        }).sort_values('raw_score').head(3)
        
        for page, data in critical_pages.iterrows():
            st.error(f"**{page.replace('_', ' ').title()}** - Average Score: {data['raw_score']:.1f}/10 ({data['criterion_id']} failing criteria)")
    
    # Top Opportunities
    st.markdown("---")
    st.markdown("### 🎯 Top 3 Improvement Opportunities")
    
    # Find worst performing criteria with highest impact
    criteria_impact = filtered_df.groupby('criterion_id').agg({
        'raw_score': ['mean', 'count'],
        'page_id': 'nunique'
    }).round(2)
    criteria_impact.columns = ['avg_score', 'evaluations', 'pages_affected']
    criteria_impact['impact_score'] = (10 - criteria_impact['avg_score']) * criteria_impact['pages_affected']
    top_opportunities = criteria_impact.sort_values('impact_score', ascending=False).head(3)
    
    col1, col2, col3 = st.columns(3)
    
    for i, (criterion, data) in enumerate(top_opportunities.iterrows()):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            **{i+1}. {criterion.replace('_', ' ').title()}**
            
            - Current Score: {data['avg_score']:.1f}/10
            - Pages Affected: {data['pages_affected']}
            - Impact Score: {data['impact_score']:.1f}
            """)
    
    # Segmented Tier Analysis with Experience Data
    st.markdown("---")
    st.markdown("### 📊 Performance by Content Tier")
    
    if summary['has_experience_data'] and master_df is not None:
        # Create comprehensive tier analysis with experience context
        tier_analysis = master_df.groupby('tier').agg({
            'avg_score': 'mean',
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
                tier_pages = master_df[master_df['tier'] == tier].sort_values('avg_score', ascending=False)
                if not tier_pages.empty:
                    col1, col2 = st.columns(2)
                    with col1:
                        best_page = tier_pages.iloc[0]
                        st.markdown("**🏆 Best Performing Page:**")
                        st.write(f"• {best_page['slug'].replace('_', ' ').title()}")
                        st.write(f"• Score: {best_page['avg_score']:.1f}/10")
                        if pd.notna(best_page['overall_sentiment']):
                            st.write(f"• Sentiment: {best_page['overall_sentiment']}")
                    
                    with col2:
                        if len(tier_pages) > 1:
                            worst_page = tier_pages.iloc[-1]
                            st.markdown("**⚠️ Needs Attention:**")
                            st.write(f"• {worst_page['slug'].replace('_', ' ').title()}")
                            st.write(f"• Score: {worst_page['avg_score']:.1f}/10")
                            if pd.notna(worst_page['overall_sentiment']):
                                st.write(f"• Sentiment: {worst_page['overall_sentiment']}")
    else:
        # Fallback tier analysis without experience data
        tier_scores = filtered_df.groupby('tier').agg({
            'raw_score': ['mean', 'count'],
            'descriptor': lambda x: (x == 'EXCELLENT').sum()
        }).round(2)
        tier_scores.columns = ['Avg Score', 'Page Count', 'Excellence Count']
        tier_scores = tier_scores.sort_values('Avg Score', ascending=False)
        
        for tier, data in tier_scores.iterrows():
            tier_display = tier.replace('_', ' ').title()
            score_color = "🟢" if data['Avg Score'] >= 7 else "🟡" if data['Avg Score'] >= 4 else "🔴"
            st.markdown(f"{score_color} **{tier_display}**: {data['Avg Score']:.1f}/10 ({int(data['Page Count'])} pages, {int(data['Excellence Count'])} excellent)")
    
    # Success Stories
    st.markdown("---")
    st.markdown("### 🏆 Success Stories to Replicate")
    
    excellent_examples = filtered_df[filtered_df['raw_score'] >= 8.0]
    if not excellent_examples.empty:
        success_stories = excellent_examples.groupby(['url_slug', 'criterion_id']).first().sort_values('raw_score', ascending=False).head(3)
        
        for i, ((page, criterion), data) in enumerate(success_stories.iterrows()):
            with st.expander(f"🌟 Success #{i+1}: {page.replace('_', ' ').title()} - {criterion.replace('_', ' ').title()}"):
                st.write(f"**Score:** {data['raw_score']}/10")
                st.write(f"**Why it works:** {data['rationale']}")
                if 'url' in data and pd.notna(data['url']):
                    st.write(f"**URL:** {data['url']}")

if __name__ == "__main__":
    main() 