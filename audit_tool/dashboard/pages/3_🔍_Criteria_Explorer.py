#!/usr/bin/env python3
"""
Criteria Explorer Page
Drill down into individual criteria performance and analysis
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
    st.title("🔍 Criteria Explorer")
    
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
    
    # Criteria selection
    st.markdown("### 🎯 Select Criteria to Analyze")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tier selection
        available_tiers = sorted(filtered_data['tier'].unique())
        selected_tier = st.selectbox(
            "Select Performance Tier:",
            ["All"] + available_tiers,
            help="Filter criteria by performance tier"
        )
    
    with col2:
        # Criteria selection
        if selected_tier == "All":
            available_criteria = sorted(filtered_data['criterion_id'].unique())
        else:
            available_criteria = sorted(filtered_data[filtered_data['tier'] == selected_tier]['criterion_id'].unique())
        
        selected_criterion = st.selectbox(
            "Select Specific Criterion:",
            available_criteria,
            help="Choose a specific criterion to analyze"
        )
    
    # Filter data for selected criterion
    if selected_tier != "All":
        criterion_data = filtered_data[
            (filtered_data['tier'] == selected_tier) & 
            (filtered_data['criterion_id'] == selected_criterion)
        ]
    else:
        criterion_data = filtered_data[filtered_data['criterion_id'] == selected_criterion]
    
    if criterion_data.empty:
        st.warning("No data available for the selected criterion.")
        return
    
    # Criterion overview
    st.markdown(f"### 📊 Analysis: {selected_criterion.replace('_', ' ').title()}")
    
    # Key metrics for this criterion
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_score = criterion_data['raw_score'].mean()
        st.metric(
            "Average Score",
            f"{avg_score:.2f}/10",
            delta=f"{avg_score - 5:.2f}",
            help="Average score for this criterion across all pages"
        )
    
    with col2:
        pass_rate = (criterion_data['descriptor'] == 'PASS').mean() * 100
        st.metric(
            "Success Rate",
            f"{pass_rate:.1f}%",
            delta=f"{pass_rate - 70:.1f}%",
            help="Percentage of pages scoring PASS (≥4.0)"
        )
    
    with col3:
        score_range = criterion_data['raw_score'].max() - criterion_data['raw_score'].min()
        st.metric(
            "Score Range",
            f"{score_range:.1f}",
            help="Difference between highest and lowest scores"
        )
    
    with col4:
        pages_count = len(criterion_data)
        st.metric(
            "Pages Analyzed",
            pages_count,
            help="Number of pages evaluated for this criterion"
        )
    
    # Performance distribution
    st.markdown("#### 📈 Score Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Histogram of scores
        fig_hist = px.histogram(
            criterion_data,
            x='raw_score',
            nbins=15,
            title=f"Score Distribution: {selected_criterion.replace('_', ' ').title()}",
            color_discrete_sequence=['#3b82f6']
        )
        
        # Add threshold lines
        fig_hist.add_vline(x=4.0, line_dash="dash", line_color="orange", 
                          annotation_text="PASS (4.0)")
        fig_hist.add_vline(x=2.0, line_dash="dash", line_color="red", 
                          annotation_text="FAIL (2.0)")
        fig_hist.add_vline(x=avg_score, line_dash="solid", line_color="blue", 
                          annotation_text=f"Average ({avg_score:.2f})")
        
        fig_hist.update_layout(
            xaxis_title="Score",
            yaxis_title="Number of Pages"
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Performance breakdown
        st.markdown("**Performance Breakdown:**")
        
        descriptor_counts = criterion_data['descriptor'].value_counts()
        total_count = len(criterion_data)
        
        for descriptor, count in descriptor_counts.items():
            percentage = (count / total_count) * 100
            color = {"PASS": "🟢", "WARN": "🟡", "FAIL": "🔴"}.get(descriptor, "⚪")
            st.write(f"{color} **{descriptor}**: {count} ({percentage:.1f}%)")
        
        st.markdown("---")
        st.markdown("**Statistical Summary:**")
        st.write(f"**Mean:** {criterion_data['raw_score'].mean():.2f}")
        st.write(f"**Median:** {criterion_data['raw_score'].median():.2f}")
        st.write(f"**Std Dev:** {criterion_data['raw_score'].std():.2f}")
        st.write(f"**Min:** {criterion_data['raw_score'].min():.2f}")
        st.write(f"**Max:** {criterion_data['raw_score'].max():.2f}")
    
    # Page-level performance
    st.markdown("#### 📋 Page-Level Performance")
    
    # Sort by score for better visualization
    sorted_data = criterion_data.sort_values('raw_score', ascending=False).copy()
    
    # Create a more readable URL display
    sorted_data['display_url'] = sorted_data['url_slug'].str.replace('_', ' ').str.title()
    
    # Bar chart of page performance
    fig_bar = px.bar(
        sorted_data.head(20),  # Show top 20 pages
        x='display_url',
        y='raw_score',
        title=f"Top 20 Page Scores: {selected_criterion.replace('_', ' ').title()}",
        color='raw_score',
        color_continuous_scale='RdYlGn'
    )
    
    fig_bar.update_layout(
        xaxis_title="Page",
        yaxis_title="Score",
        xaxis_tickangle=-45,
        height=500
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed page table
    st.markdown("#### 📊 Detailed Page Analysis")
    
    # Prepare display data
    display_data = sorted_data[['display_url', 'raw_score', 'descriptor', 'url']].copy()
    display_data.columns = ['Page', 'Score', 'Performance', 'Full URL']
    display_data['Score'] = display_data['Score'].round(2)
    
    # Color-code the performance column
    def color_performance(val):
        if val == 'PASS':
            return 'background-color: #dcfce7; color: #166534'
        elif val == 'WARN':
            return 'background-color: #fef3c7; color: #92400e'
        elif val == 'FAIL':
            return 'background-color: #fee2e2; color: #991b1b'
        return ''
    
    styled_data = display_data.style.map(color_performance, subset=['Performance'])
    st.dataframe(styled_data, use_container_width=True, height=400)
    
    # Performance insights
    st.markdown("### 💡 Performance Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Best Performing Pages")
        best_pages = sorted_data.head(3)
        
        for i, (_, row) in enumerate(best_pages.iterrows(), 1):
            st.write(f"**{i}. {row['display_url']}**")
            st.write(f"Score: {row['raw_score']:.2f}/10 ({row['descriptor']})")
            st.caption(f"URL: {row['url']}")
            st.markdown("---")
    
    with col2:
        st.markdown("#### ⚠️ Areas for Improvement")
        worst_pages = sorted_data.tail(3)
        
        for i, (_, row) in enumerate(worst_pages.iterrows(), 1):
            st.write(f"**{i}. {row['display_url']}**")
            st.write(f"Score: {row['raw_score']:.2f}/10 ({row['descriptor']})")
            st.caption(f"URL: {row['url']}")
            st.markdown("---")
    
    # Recommendations
    st.markdown("### 🎯 Recommendations")
    
    recommendations = []
    
    # Generate recommendations based on performance
    if pass_rate < 50:
        recommendations.append(f"🚨 **Critical**: Only {pass_rate:.1f}% of pages meet success criteria. Immediate action required.")
    elif pass_rate < 70:
        recommendations.append(f"⚠️ **Attention**: {pass_rate:.1f}% success rate is below target (70%). Focus improvement efforts here.")
    
    if score_range > 5:
        recommendations.append(f"⚖️ **Consistency**: Large score variance ({score_range:.1f}) indicates inconsistent implementation.")
    
    if avg_score < 4:
        recommendations.append(f"📈 **Performance**: Average score ({avg_score:.2f}) is below PASS threshold. Systematic improvements needed.")
    
    # Tier-specific recommendations
    if selected_tier != "All":
        tier_avg = filtered_data[filtered_data['tier'] == selected_tier]['raw_score'].mean()
        if avg_score < tier_avg:
            recommendations.append(f"🔧 **Focus Area**: This criterion underperforms the {selected_tier} tier average ({tier_avg:.2f}).")
    
    if recommendations:
        for rec in recommendations:
            st.markdown(f"- {rec}")
    else:
        st.success("🎉 **Excellent Performance!** This criterion is performing well across all metrics.")
    
    # Export criterion data
    st.markdown("### 📥 Export Criterion Data")
    
    csv_data = criterion_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📄 Download {selected_criterion} Data",
        data=csv_data,
        file_name=f"{selected_criterion}_analysis_{st.session_state['selected_run']}.csv",
        mime="text/csv",
        help="Download detailed data for this criterion"
    )

if __name__ == "__main__":
    main() 