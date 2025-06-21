#!/usr/bin/env python3
"""
Executive Overview Page
High-level KPIs and performance visualizations
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
    st.title("📊 Executive Overview")
    
    # Check if we have global state
    if 'run_data' not in st.session_state:
        st.error("Please select a run from the home page first.")
        st.info("👈 Use the sidebar to select an audit run")
        return
    
    gateway = st.session_state['gateway']
    run_data = st.session_state['run_data']
    
    # Get filtered data
    filtered_data = gateway.get_filtered_data(
        run_data,
        st.session_state['persona_filter'],
        st.session_state['score_filter'],
        st.session_state['tier_filter']
    )
    
    if filtered_data.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Get summary stats
    stats = gateway.get_summary_stats(filtered_data)
    
    # Executive Summary Header
    st.markdown("### 🎯 Executive Summary")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        avg_score = stats['average_score']
        if avg_score >= 7:
            status = "🟢 **Excellent Performance**"
            summary = "The brand audit shows strong performance across most criteria."
        elif avg_score >= 5:
            status = "🟡 **Good Performance with Opportunities**"
            summary = "Solid foundation with clear areas for improvement identified."
        else:
            status = "🔴 **Needs Immediate Attention**"
            summary = "Critical issues require immediate strategic intervention."
        
        st.markdown(f"{status}")
        st.markdown(summary)
        
        # Key findings
        st.markdown("**Key Findings:**")
        st.write(f"• {stats['total_pages']} pages analyzed across {len(filtered_data['tier'].unique())} performance tiers")
        st.write(f"• {stats['pass_rate']:.1f}% of criteria meet success standards (≥4.0/10)")
        st.write(f"• {stats['fail_count']} critical issues identified requiring immediate action")
    
    with col2:
        # Score gauge
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = avg_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Overall Score"},
            delta = {'reference': 5.0},
            gauge = {
                'axis': {'range': [None, 10]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 4], 'color': "lightgray"},
                    {'range': [4, 7], 'color': "yellow"},
                    {'range': [7, 10], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 7
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Detailed KPI Row
    st.markdown("### 📈 Detailed Performance Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Pages Analyzed",
            stats['total_pages'],
            help="Number of unique pages evaluated"
        )
    
    with col2:
        st.metric(
            "Average Score",
            f"{stats['average_score']:.2f}/10",
            delta=f"{stats['average_score'] - 5:.2f}",
            help="Mean score across all criteria"
        )
    
    with col3:
        st.metric(
            "Success Rate",
            f"{stats['pass_rate']:.1f}%",
            delta=f"{stats['pass_rate'] - 70:.1f}%",
            help="Percentage scoring ≥4.0 (PASS threshold)"
        )
    
    with col4:
        st.metric(
            "Critical Issues",
            stats['fail_count'],
            delta=f"-{stats['fail_count']}" if stats['fail_count'] > 0 else "0",
            delta_color="inverse",
            help="Criteria scoring <2.0 (FAIL threshold)"
        )
    
    with col5:
        st.metric(
            "Score Range",
            f"{stats['min_score']:.1f} - {stats['max_score']:.1f}",
            help="Minimum to maximum scores observed"
        )
    
    # Charts Row
    st.markdown("### 📊 Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Performance by Tier")
        
        # Tier performance bar chart
        tier_breakdown = gateway.get_tier_breakdown(filtered_data)
        if not tier_breakdown.empty:
            fig_bar = px.bar(
                tier_breakdown,
                x='tier',
                y='avg_score',
                title="Average Score by Performance Tier",
                color='avg_score',
                color_continuous_scale='RdYlGn',
                text='avg_score'
            )
            fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig_bar.update_layout(
                showlegend=False,
                yaxis_title="Average Score",
                xaxis_title="Performance Tier",
                yaxis=dict(range=[0, 10])
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No tier data available")
    
    with col2:
        st.markdown("#### 🚦 Score Distribution")
        
        # Descriptor distribution pie chart
        descriptor_counts = filtered_data['descriptor'].value_counts()
        
        fig_pie = px.pie(
            values=descriptor_counts.values,
            names=descriptor_counts.index,
            title="Performance Distribution",
            color_discrete_map={
                'PASS': '#22c55e',
                'WARN': '#eab308',
                'FAIL': '#ef4444'
            }
        )
        fig_pie.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Score distribution histogram
    st.markdown("#### 📈 Score Distribution Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_hist = px.histogram(
            filtered_data,
            x='raw_score',
            nbins=20,
            title="Distribution of All Scores",
            color_discrete_sequence=['#3b82f6']
        )
        fig_hist.add_vline(x=4.0, line_dash="dash", line_color="orange", 
                          annotation_text="PASS Threshold (4.0)")
        fig_hist.add_vline(x=2.0, line_dash="dash", line_color="red", 
                          annotation_text="FAIL Threshold (2.0)")
        fig_hist.update_layout(
            xaxis_title="Score",
            yaxis_title="Number of Criteria"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.markdown("**Statistical Summary:**")
        st.write(f"**Mean:** {stats['average_score']:.2f}")
        st.write(f"**Median:** {stats['median_score']:.2f}")
        st.write(f"**Std Dev:** {stats['std_score']:.2f}")
        st.write(f"**Range:** {stats['max_score'] - stats['min_score']:.2f}")
        
        st.markdown("**Performance Bands:**")
        st.write(f"🟢 **Excellent (7-10):** {len(filtered_data[filtered_data['raw_score'] >= 7])}")
        st.write(f"🟡 **Good (4-7):** {len(filtered_data[(filtered_data['raw_score'] >= 4) & (filtered_data['raw_score'] < 7)])}")
        st.write(f"🔴 **Needs Work (0-4):** {len(filtered_data[filtered_data['raw_score'] < 4])}")
    
    # Top and Bottom Performers
    st.markdown("### 🏆 Performance Highlights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🥇 Top Performers")
        best_performers = gateway.get_best_performers(filtered_data, 5)
        if not best_performers.empty:
            for i, (_, row) in enumerate(best_performers.iterrows(), 1):
                st.write(f"{i}. **{row['criterion_id'].replace('_', ' ').title()}** - {row['raw_score']:.1f}/10")
                st.caption(f"Page: {row['url_slug']}")
        else:
            st.info("No top performers data available")
    
    with col2:
        st.markdown("#### ⚠️ Areas for Improvement")
        worst_performers = gateway.get_worst_performers(filtered_data, 5)
        if not worst_performers.empty:
            for i, (_, row) in enumerate(worst_performers.iterrows(), 1):
                st.write(f"{i}. **{row['criterion_id'].replace('_', ' ').title()}** - {row['raw_score']:.1f}/10")
                st.caption(f"Page: {row['url_slug']}")
        else:
            st.info("No improvement areas data available")
    
    # Action Items
    st.markdown("### 🎯 Strategic Recommendations")
    
    # Generate recommendations based on data
    recommendations = []
    
    if stats['fail_count'] > 0:
        recommendations.append(f"🚨 **Immediate Action Required:** Address {stats['fail_count']} critical issues scoring below 2.0")
    
    if stats['pass_rate'] < 70:
        recommendations.append(f"📈 **Improve Success Rate:** Currently {stats['pass_rate']:.1f}%, target 70%+")
    
    if stats['std_score'] > 2.0:
        recommendations.append(f"⚖️ **Reduce Inconsistency:** High score variance ({stats['std_score']:.2f}) indicates inconsistent performance")
    
    # Tier-specific recommendations
    tier_breakdown = gateway.get_tier_breakdown(filtered_data)
    if not tier_breakdown.empty:
        worst_tier = tier_breakdown.loc[tier_breakdown['avg_score'].idxmin()]
        if worst_tier['avg_score'] < 5.0:
            recommendations.append(f"🔧 **Focus on {worst_tier['tier'].title()}:** Lowest performing tier at {worst_tier['avg_score']:.2f}/10")
    
    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.success("🎉 **Excellent Performance!** All key metrics are within target ranges.")

if __name__ == "__main__":
    main() 