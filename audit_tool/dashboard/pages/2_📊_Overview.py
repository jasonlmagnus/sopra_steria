#!/usr/bin/env python3
"""
Overview Page
Charts, metrics and performance visualizations
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
    st.title("📊 Performance Overview")
    
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
    
    # Key Performance Metrics
    st.markdown("### 📈 Key Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        avg_score = filtered_df['raw_score'].mean()
        st.metric("Average Score", f"{avg_score:.2f}/10", help="Mean score across all criteria")
    
    with col2:
        total_pages = filtered_df['page_id'].nunique()
        st.metric("Pages Analyzed", total_pages, help="Number of unique pages evaluated")
    
    with col3:
        pass_rate = (filtered_df['raw_score'] >= 4.0).mean() * 100
        st.metric("Pass Rate", f"{pass_rate:.1f}%", help="Percentage scoring ≥4.0")
    
    with col4:
        excellent_rate = (filtered_df['raw_score'] >= 8.0).mean() * 100
        st.metric("Excellence Rate", f"{excellent_rate:.1f}%", help="Percentage scoring ≥8.0")
    
    with col5:
        total_evaluations = len(filtered_df)
        st.metric("Total Evaluations", total_evaluations, help="Total number of criteria evaluations")
    
    # Performance Charts
    st.markdown("### 📊 Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution histogram
        st.markdown("#### Score Distribution")
        fig_hist = px.histogram(
            filtered_df,
            x='raw_score',
            nbins=20,
            title="Distribution of Scores",
            labels={'raw_score': 'Score', 'count': 'Frequency'},
            color_discrete_sequence=['#3b82f6']
        )
        fig_hist.add_vline(x=4.0, line_dash="dash", line_color="orange", annotation_text="Pass Threshold")
        fig_hist.add_vline(x=8.0, line_dash="dash", line_color="green", annotation_text="Excellence Threshold")
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Performance by tier
        st.markdown("#### Performance by Tier")
        if 'tier' in filtered_df.columns:
            tier_avg = filtered_df.groupby('tier')['raw_score'].mean().sort_values(ascending=False)
            fig_bar = px.bar(
                x=tier_avg.index,
                y=tier_avg.values,
                title="Average Score by Tier",
                labels={'x': 'Tier', 'y': 'Average Score'},
                color=tier_avg.values,
                color_continuous_scale='RdYlGn'
            )
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Tier information not available")
    
    # Detailed Performance Tables
    st.markdown("### 📋 Detailed Performance Breakdown")
    
    tab1, tab2, tab3 = st.tabs(["By Criteria", "By Page", "By Tier"])
    
    with tab1:
        st.markdown("#### Performance by Criteria")
        # Use the correct column name based on our unified data structure
        criterion_col = 'criterion_code' if 'criterion_code' in filtered_df.columns else 'criterion_id'
        
        # Use the correct score column from unified CSV
        score_col = None
        if 'final_score' in filtered_df.columns:
            score_col = 'final_score'
        elif 'raw_score' in filtered_df.columns:
            score_col = 'raw_score'
        elif 'avg_score' in filtered_df.columns:
            score_col = 'avg_score'
        
        if criterion_col not in filtered_df.columns or not score_col:
            st.error("❌ Criteria analysis requires proper column structure")
            return
        
        criteria_summary = filtered_df.groupby(criterion_col).agg({
            score_col: ['mean', 'std', 'count', 'min', 'max'],
            'page_id': 'nunique'
        }).round(2)
        
        # Flatten column names
        criteria_summary.columns = ['avg_score', 'std_dev', 'evaluations', 'min_score', 'max_score', 'pages_affected']
        criteria_summary = criteria_summary.sort_values('avg_score')
        
        # Display as interactive table
        st.dataframe(
            criteria_summary,
            use_container_width=True,
            column_config={
                "avg_score": st.column_config.NumberColumn("Average Score", format="%.1f"),
                "std_dev": st.column_config.NumberColumn("Standard Deviation", format="%.2f"),
                "evaluations": st.column_config.NumberColumn("Total Evaluations"),
                "min_score": st.column_config.NumberColumn("Minimum Score", format="%.1f"),
                "max_score": st.column_config.NumberColumn("Maximum Score", format="%.1f"),
                "pages_affected": st.column_config.NumberColumn("Pages Affected")
            }
        )
        
        # Quick stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Avg Overall Score", f"{filtered_df[score_col].mean():.1f}/10")
        with col2:
            if len(criteria_summary) > 0:
                st.metric("Best Criterion", f"{criteria_summary.iloc[-1]['avg_score']:.1f}/10")
            else:
                st.metric("Best Criterion", "N/A")
        with col3:
            if len(criteria_summary) > 0:
                st.metric("Worst Criterion", f"{criteria_summary.iloc[0]['avg_score']:.1f}/10")
            else:
                st.metric("Worst Criterion", "N/A")
        with col4:
            if len(criteria_summary) > 0:
                st.metric("Score Range", f"{criteria_summary['avg_score'].max() - criteria_summary['avg_score'].min():.1f}")
            else:
                st.metric("Score Range", "N/A")
    
    with tab2:
        st.markdown("#### Performance by Page")
        page_summary = filtered_df.groupby('url_slug').agg({
            score_col: ['mean', 'std', 'count', 'min', 'max'],
            criterion_col: 'nunique'
        }).round(2)
        page_summary.columns = ['avg_score', 'std_dev', 'evaluations', 'min_score', 'max_score', 'criteria_count']
        page_summary = page_summary.sort_values('avg_score', ascending=False)
        
        # Add performance indicators
        page_summary['status'] = page_summary['avg_score'].apply(
            lambda x: '🟢 Excellent' if x >= 8.0 else '🟡 Good' if x >= 4.0 else '🔴 Needs Work'
        )
        
        st.dataframe(
            page_summary,
            use_container_width=True,
            column_config={
                "avg_score": st.column_config.NumberColumn("Average Score", format="%.1f"),
                "std_dev": st.column_config.NumberColumn("Standard Deviation", format="%.2f"),
                "evaluations": st.column_config.NumberColumn("Total Evaluations"),
                "min_score": st.column_config.NumberColumn("Minimum Score", format="%.1f"),
                "max_score": st.column_config.NumberColumn("Maximum Score", format="%.1f"),
                "criteria_count": st.column_config.NumberColumn("Criteria Count"),
                "status": st.column_config.TextColumn("Status")
            }
        )
        
        # Download page summary
        page_csv = page_summary.to_csv().encode('utf-8')
        st.download_button("📥 Download Page Summary", page_csv, "page_summary.csv", "text/csv")
    
    with tab3:
        st.markdown("#### Performance by Tier")
        if 'tier' in filtered_df.columns:
            tier_summary = filtered_df.groupby('tier').agg({
                score_col: ['mean', 'std', 'count'],
                criterion_col: 'nunique'  # Use dynamic criterion column
            }).round(2)
            
            # Flatten column names
            tier_summary.columns = ['avg_score', 'std_dev', 'evaluations', 'unique_criteria']
            tier_summary = tier_summary.sort_values('avg_score', ascending=False)
            
            # Display as chart
            fig = px.bar(
                tier_summary.reset_index(), 
                x='tier', 
                y='avg_score',
                title="Average Score by Tier",
                color='avg_score',
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tier stats table
            st.dataframe(
                tier_summary,
                use_container_width=True,
                column_config={
                    "avg_score": st.column_config.NumberColumn("Average Score", format="%.1f"),
                    "std_dev": st.column_config.NumberColumn("Standard Deviation", format="%.2f"),
                    "evaluations": st.column_config.NumberColumn("Total Evaluations"),
                    "unique_criteria": st.column_config.NumberColumn("Unique Criteria")
                }
            )
        else:
            st.info("Tier information not available")
    
    # Experience Data Overview (if available)
    if summary.get('has_experience_data') and datasets['experience'] is not None:
        st.markdown("### 👥 Experience Data Overview")
        
        experience_df = datasets['experience']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Sentiment distribution
            sentiment_counts = experience_df['overall_sentiment'].value_counts()
            fig_pie = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="Sentiment Distribution",
                color_discrete_map={
                    'Positive': '#22c55e',
                    'Neutral': '#eab308',
                    'Negative': '#ef4444'
                }
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Engagement distribution
            engagement_counts = experience_df['engagement_level'].value_counts()
            fig_pie2 = px.pie(
                values=engagement_counts.values,
                names=engagement_counts.index,
                title="Engagement Distribution",
                color_discrete_map={
                    'High': '#22c55e',
                    'Medium': '#eab308',
                    'Low': '#ef4444'
                }
            )
            fig_pie2.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie2, use_container_width=True)
        
        with col3:
            # Conversion likelihood distribution
            conversion_counts = experience_df['conversion_likelihood'].value_counts()
            fig_pie3 = px.pie(
                values=conversion_counts.values,
                names=conversion_counts.index,
                title="Conversion Likelihood",
                color_discrete_map={
                    'High': '#22c55e',
                    'Medium': '#eab308',
                    'Low': '#ef4444'
                }
            )
            fig_pie3.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie3, use_container_width=True)
    
    # Performance Trends (if multiple personas)
    if summary['total_personas'] > 1:
        st.markdown("### 📈 Multi-Persona Comparison")
        
        persona_performance = filtered_df.groupby('persona_id').agg({
            score_col: ['mean', 'count'],
            'page_id': 'nunique'
        }).round(2)
        persona_performance.columns = ['avg_score', 'evaluations', 'pages']
        persona_performance = persona_performance.sort_values('avg_score', ascending=False)
        
        # Persona performance chart
        fig_persona = px.bar(
            x=persona_performance.index,
            y=persona_performance['avg_score'],
            title="Average Score by Persona",
            labels={'x': 'Persona', 'y': 'Average Score'},
            color=persona_performance['avg_score'],
            color_continuous_scale='RdYlGn'
        )
        fig_persona.update_layout(showlegend=False)
        st.plotly_chart(fig_persona, use_container_width=True)
        
        st.dataframe(persona_performance, use_container_width=True)

if __name__ == "__main__":
    main() 