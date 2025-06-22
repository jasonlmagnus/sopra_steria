#!/usr/bin/env python3
"""
Executive Brand Audit Dashboard
Story-driven, decision-focused experience implementing the UX strategy
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def load_enhanced_data():
    """Load enhanced audit data with derived metrics"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    data_dir = project_root / "audit_outputs" / "The_BENELUX_Technology_Innovation_Leader"
    
    if not data_dir.exists():
        return None
    
    # Load all enhanced datasets
    datasets = {}
    
    try:
        datasets['pages'] = pd.read_csv(data_dir / "pages.csv")
        datasets['criteria'] = pd.read_csv(data_dir / "criteria_scores.csv") 
        datasets['recommendations'] = pd.read_csv(data_dir / "recommendations.csv")
        datasets['experience'] = pd.read_csv(data_dir / "experience.csv")
        
        # Create master dataset by joining all data
        master = datasets['pages'].merge(
            datasets['experience'], on='page_id', how='left'
        )
        
        # Add aggregated criteria data
        criteria_agg = datasets['criteria'].groupby('page_id').agg({
            'score': ['mean', 'min', 'max', 'count'],
            'impact_score': ['mean', 'max']
        }).round(2)
        criteria_agg.columns = ['avg_score', 'min_score', 'max_score', 'criteria_count', 'avg_impact', 'max_impact']
        criteria_agg = criteria_agg.reset_index()
        
        master = master.merge(criteria_agg, on='page_id', how='left')
        
        # Add recommendations count
        rec_count = datasets['recommendations'].groupby('page_id').size().rename('rec_count').reset_index()
        master = master.merge(rec_count, on='page_id', how='left')
        
        # Add quick wins count
        quick_wins = datasets['recommendations'][datasets['recommendations']['quick_win_flag'] == True].groupby('page_id').size().rename('quick_wins_count').reset_index()
        master = master.merge(quick_wins, on='page_id', how='left')
        master['quick_wins_count'] = master['quick_wins_count'].fillna(0)
        
        datasets['master'] = master
        
        return datasets
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def calculate_overall_health_score(datasets):
    """Calculate the overall brand health score"""
    if not datasets or 'master' not in datasets:
        return 0.0
    
    master = datasets['master']
    if master.empty:
        return 0.0
    
    # Weight by page importance (tier-based)
    tier_weights = {
        'Corporate Website - Home Page': 1.0,
        'Corporate Website - Top Level': 0.9,
        'Corporate Website - Top-level': 0.9,
        'Thought Leadership Content Page': 0.8,
        'Service Offering Page': 0.8,
        'Industry Solutions Page': 0.7,
        'Services/Solutions Page': 0.7,
        'Thought Leadership Blog Post': 0.7,
        'Thought Leadership Blog': 0.7,
        'Press Release': 0.5,
        'About Us - History Page': 0.4,
        'Corporate Responsibility Overview Page': 0.4
    }
    
    master['tier_weight'] = master['tier'].map(tier_weights).fillna(0.5)
    
    # Calculate weighted average of brand health index
    if master['tier_weight'].sum() > 0:
        weighted_score = (master['brand_health_index'] * master['tier_weight']).sum() / master['tier_weight'].sum()
    else:
        weighted_score = master['brand_health_index'].mean()
    
    return round(weighted_score, 1)

def generate_executive_summary(datasets):
    """Generate AI-powered executive summary (placeholder for now)"""
    if not datasets:
        return "No data available for analysis."
    
    master = datasets['master']
    criteria = datasets['criteria']
    recommendations = datasets['recommendations']
    
    # Calculate key metrics
    avg_score = master['brand_health_index'].mean()
    total_pages = len(master)
    high_impact_issues = len(criteria[criteria['impact_score'] > 5.0])
    quick_wins = len(recommendations[recommendations['quick_win_flag'] == True])
    positive_sentiment = len(master[master['overall_sentiment'] == 'Positive'])
    
    # Generate narrative based on data
    sentiment_pct = (positive_sentiment / total_pages) * 100 if total_pages > 0 else 0
    
    if avg_score >= 7.0:
        health_status = "strong"
    elif avg_score >= 5.0:
        health_status = "moderate"
    else:
        health_status = "concerning"
    
    summary = f"""
    **Brand Health Assessment:** Our digital presence shows {health_status} performance with an overall health score of {avg_score:.1f}/10. 
    
    **Persona Sentiment:** {sentiment_pct:.0f}% of analyzed pages generate positive sentiment from The BENELUX Technology Innovation Leader persona, indicating {"strong" if sentiment_pct > 60 else "mixed" if sentiment_pct > 40 else "weak"} emotional resonance.
    
    **Action Priority:** {high_impact_issues} high-impact issues identified across {total_pages} pages, with {quick_wins} quick-win opportunities ready for immediate implementation.
    """
    
    return summary.strip()

def render_hero_metrics(datasets):
    """Render the hero metrics section"""
    if not datasets:
        st.error("No data available")
        return
    
    overall_score = calculate_overall_health_score(datasets)
    master = datasets['master']
    recommendations = datasets['recommendations']
    
    # Color coding based on score
    if overall_score >= 7.0:
        score_color = "#10B981"  # Green
    elif overall_score >= 5.0:
        score_color = "#F59E0B"  # Amber
    else:
        score_color = "#EF4444"  # Red
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Brand Health Score Dial
        fig_dial = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Brand Health Score"},
            gauge = {
                'axis': {'range': [None, 10]},
                'bar': {'color': score_color},
                'steps': [
                    {'range': [0, 4], 'color': "#FEE2E2"},
                    {'range': [4, 7], 'color': "#FEF3C7"},
                    {'range': [7, 10], 'color': "#D1FAE5"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 9
                }
            }
        ))
        fig_dial.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_dial, use_container_width=True)
    
    with col2:
        total_pages = len(master)
        avg_sentiment_score = len(master[master['overall_sentiment'] == 'Positive']) / total_pages * 100 if total_pages > 0 else 0
        st.metric(
            "Pages Analyzed", 
            total_pages,
            help="Total pages audited for this persona"
        )
        st.metric(
            "Positive Sentiment", 
            f"{avg_sentiment_score:.0f}%",
            help="Percentage of pages generating positive persona sentiment"
        )
    
    with col3:
        total_recs = len(recommendations)
        quick_wins = len(recommendations[recommendations['quick_win_flag'] == True])
        st.metric(
            "Total Recommendations", 
            total_recs,
            help="Strategic actions identified across all pages"
        )
        st.metric(
            "Quick Wins Available", 
            quick_wins,
            delta=f"{quick_wins/total_recs*100:.0f}% of total" if total_recs > 0 else "0%",
            help="Low-effort, high-impact opportunities"
        )
    
    with col4:
        high_impact = len(datasets['criteria'][datasets['criteria']['impact_score'] > 5.0])
        critical_issues = len(datasets['criteria'][datasets['criteria']['descriptor'] == 'FAIL'])
        st.metric(
            "High Impact Issues", 
            high_impact,
            help="Criteria with impact score > 5.0"
        )
        st.metric(
            "Critical Failures", 
            critical_issues,
            delta=f"-{critical_issues}" if critical_issues > 0 else "None",
            delta_color="inverse",
            help="Criteria scoring below 4.0"
        )

def render_top_insights(datasets):
    """Render top wins and risks cards"""
    if not datasets:
        return
    
    master = datasets['master']
    criteria = datasets['criteria']
    recommendations = datasets['recommendations']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 3 Strengths")
        
        # Find best performing pages
        top_pages = master.nlargest(3, 'brand_health_index')
        
        for i, (_, page) in enumerate(top_pages.iterrows()):
            with st.container():
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin-bottom: 0.5rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <h4 style="margin: 0; font-size: 1.1rem;">#{i+1} {page['slug'].replace('_', ' ').title()[:40]}...</h4>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                        Health Score: {page['brand_health_index']:.1f}/10 | 
                        Sentiment: {page['overall_sentiment']} |
                        Tier: {page['tier']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🚨 Top 3 Risks")
        
        # Find highest impact issues
        high_impact_criteria = criteria.nlargest(3, 'impact_score')
        
        for i, (_, criterion) in enumerate(high_impact_criteria.iterrows()):
            # Get page info
            page = master[master['page_id'] == criterion['page_id']].iloc[0]
            
            with st.container():
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
                    color: white;
                    padding: 1rem;
                    border-radius: 0.5rem;
                    margin-bottom: 0.5rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                ">
                    <h4 style="margin: 0; font-size: 1.1rem;">#{i+1} {criterion['criterion_name']}</h4>
                    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">
                        Impact Score: {criterion['impact_score']:.1f}/10 | 
                        Page: {page['slug'].replace('_', ' ').title()[:30]}... |
                        Score: {criterion['score']:.1f}/10
                    </p>
                </div>
                """, unsafe_allow_html=True)

def render_quick_actions(datasets):
    """Render quick actions section"""
    if not datasets:
        return
    
    st.markdown("### ⚡ Quick Actions (Next 30 Days)")
    
    # Get top 3 quick wins
    quick_wins = datasets['recommendations'][
        datasets['recommendations']['quick_win_flag'] == True
    ].nlargest(3, 'impact_score')
    
    if quick_wins.empty:
        st.info("No quick wins identified. Focus on high-impact items in the Action Roadmap.")
        return
    
    for i, (_, rec) in enumerate(quick_wins.iterrows()):
        # Get page info
        page = datasets['master'][datasets['master']['page_id'] == rec['page_id']].iloc[0]
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"""
            **{i+1}. {rec['recommendation'][:80]}...**
            
            *Page: {page['slug'].replace('_', ' ').title()[:40]}...*
            """)
        
        with col2:
            st.metric("Impact", f"{rec['impact_score']:.1f}/10")
            st.write(f"**{rec['strategic_impact']}**")
        
        with col3:
            if st.button(f"Assign Owner", key=f"assign_{i}"):
                st.info("Owner assignment feature coming soon!")
            st.write(f"*{rec['complexity']} complexity*")

def render_performance_trends(datasets):
    """Render performance trends and distribution"""
    if not datasets:
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Score Distribution by Tier")
        
        master = datasets['master']
        
        # Create box plot by tier
        fig_box = px.box(
            master,
            x='tier',
            y='brand_health_index',
            color='overall_sentiment',
            title="Brand Health Score by Content Tier",
            labels={'brand_health_index': 'Brand Health Score', 'tier': 'Content Tier'}
        )
        fig_box.update_xaxes(tickangle=45)
        fig_box.update_layout(height=400)
        st.plotly_chart(fig_box, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Impact vs Effort Analysis")
        
        recommendations = datasets['recommendations']
        
        # Create complexity mapping
        complexity_map = {'Low': 1, 'Medium': 2, 'High': 3}
        recommendations['complexity_num'] = recommendations['complexity'].map(complexity_map)
        
        # Create scatter plot
        fig_scatter = px.scatter(
            recommendations,
            x='complexity_num',
            y='impact_score',
            color='quick_win_flag',
            size='impact_score',
            hover_data=['strategic_impact'],
            title="Recommendation Impact vs Effort",
            labels={'complexity_num': 'Effort (1=Low, 3=High)', 'impact_score': 'Impact Score'},
            color_discrete_map={True: '#10B981', False: '#6B7280'}
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)

def main():
    """Main executive dashboard"""
    st.set_page_config(
        page_title="Executive Brand Dashboard",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Custom CSS for executive styling
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric > label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }
    .stMetric > div {
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    h1 {
        color: #1F2937;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    h3 {
        color: #374151;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    ">
        <h1 style="margin: 0; color: white; font-size: 2.5rem;">🏠 Executive Brand Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
            Strategic insights and actionable recommendations for brand optimization
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    datasets = load_enhanced_data()
    
    if not datasets:
        st.error("No audit data found. Please run an audit first.")
        return
    
    # Hero Metrics
    render_hero_metrics(datasets)
    
    st.markdown("---")
    
    # Executive Summary
    st.markdown("### 📋 Executive Summary")
    summary = generate_executive_summary(datasets)
    st.markdown(summary)
    
    st.markdown("---")
    
    # Top Insights
    render_top_insights(datasets)
    
    st.markdown("---")
    
    # Quick Actions
    render_quick_actions(datasets)
    
    st.markdown("---")
    
    # Performance Trends
    render_performance_trends(datasets)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 View Detailed Analytics", type="primary"):
            st.info("Navigate to detailed dashboard for deep-dive analysis")
    
    with col2:
        if st.button("📄 Download Executive Report"):
            st.info("PDF export feature coming soon!")
    
    with col3:
        if st.button("🎯 Access Action Roadmap"):
            st.info("Action roadmap feature coming soon!")

if __name__ == "__main__":
    main() 