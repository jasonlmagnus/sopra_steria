#!/usr/bin/env python3
"""
Unified Brand Audit Dashboard
Simple, focused dashboard for multi-persona analysis
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent))

@st.cache_data
def load_audit_data():
    """Load the unified audit dataset"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    data_dir = project_root / "audit_data"
    
    if not (data_dir / "unified_audit_data.parquet").exists():
        return None, None
    
    # Load main dataset
    df = pd.read_parquet(data_dir / "unified_audit_data.parquet")
    
    # Load summary stats
    with open(data_dir / "summary_stats.json", 'r') as f:
        summary = json.load(f)
    
    return df, summary

def main():
    st.set_page_config(
        page_title="Brand Audit Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Brand Audit Dashboard")
    st.markdown("**Multi-Persona Website Analysis**")
    
    # Load data
    df, summary = load_audit_data()
    
    if df is None:
        st.error("No audit data found. Please run the multi-persona packager first:")
        st.code("python audit_tool/multi_persona_packager.py")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("🎛️ Filters")
        
        # Persona filter
        available_personas = sorted(df['persona_id'].unique())
        selected_personas = st.multiselect(
            "Select Personas:",
            available_personas,
            default=available_personas,
            help="Choose which personas to analyze"
        )
        
        # Tier filter
        available_tiers = sorted(df['tier'].unique())
        selected_tiers = st.multiselect(
            "Select Tiers:",
            available_tiers,
            default=available_tiers,
            help="Choose which performance tiers to include"
        )
        
        # Score filter
        score_range = st.slider(
            "Score Range:",
            float(df['raw_score'].min()),
            float(df['raw_score'].max()),
            (float(df['raw_score'].min()), float(df['raw_score'].max())),
            help="Filter by score range"
        )
    
    # Apply filters
    filtered_df = df[
        (df['persona_id'].isin(selected_personas)) &
        (df['tier'].isin(selected_tiers)) &
        (df['raw_score'] >= score_range[0]) &
        (df['raw_score'] <= score_range[1])
    ]
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Main dashboard content
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "👥 Persona Comparison", "📋 Detailed Data", "🎯 Insights"])
    
    with tab1:
        st.markdown("### 📈 Performance Overview")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Personas", len(filtered_df['persona_id'].unique()))
        
        with col2:
            st.metric("Pages Analyzed", len(filtered_df['page_id'].unique()))
        
        with col3:
            avg_score = filtered_df['raw_score'].mean()
            st.metric("Average Score", f"{avg_score:.2f}/10")
        
        with col4:
            pass_rate = (filtered_df['descriptor'].isin(['PASS', 'EXCELLENT'])).mean() * 100
            st.metric("Success Rate", f"{pass_rate:.1f}%")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution
            fig_hist = px.histogram(
                filtered_df,
                x='raw_score',
                title="Score Distribution",
                nbins=20,
                color_discrete_sequence=['#3b82f6']
            )
            fig_hist.add_vline(x=4.0, line_dash="dash", line_color="orange", annotation_text="PASS (4.0)")
            fig_hist.add_vline(x=7.0, line_dash="dash", line_color="green", annotation_text="EXCELLENT (7.0)")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Performance by tier
            tier_scores = filtered_df.groupby('tier')['raw_score'].mean().reset_index()
            fig_bar = px.bar(
                tier_scores,
                x='tier',
                y='raw_score',
                title="Average Score by Tier",
                color='raw_score',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.markdown("### 👥 Persona Comparison")
        
        if len(selected_personas) < 2:
            st.warning("Select at least 2 personas to see comparisons.")
        else:
            # Persona performance comparison
            persona_scores = filtered_df.groupby('persona_id')['raw_score'].mean().reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar chart comparison
                fig_persona = px.bar(
                    persona_scores,
                    x='persona_id',
                    y='raw_score',
                    title="Average Score by Persona",
                    color='raw_score',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_persona, use_container_width=True)
            
            with col2:
                # Radar chart if multiple personas
                if len(selected_personas) > 1:
                    # Create radar chart data
                    radar_data = filtered_df.groupby(['persona_id', 'tier'])['raw_score'].mean().unstack(fill_value=0)
                    
                    fig_radar = go.Figure()
                    
                    colors = px.colors.qualitative.Set3
                    for i, persona in enumerate(radar_data.index):
                        fig_radar.add_trace(go.Scatterpolar(
                            r=radar_data.loc[persona].values,
                            theta=radar_data.columns,
                            fill='toself',
                            name=persona,
                            line_color=colors[i % len(colors)]
                        ))
                    
                    fig_radar.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                        title="Persona Performance Radar"
                    )
                    st.plotly_chart(fig_radar, use_container_width=True)
            
            # Detailed comparison table
            st.markdown("#### 📊 Detailed Persona Comparison")
            
            comparison_df = filtered_df.groupby(['persona_id', 'tier']).agg({
                'raw_score': ['mean', 'count', 'std']
            }).round(2)
            comparison_df.columns = ['Avg Score', 'Count', 'Std Dev']
            comparison_df = comparison_df.reset_index()
            
            st.dataframe(comparison_df, use_container_width=True)
    
    with tab3:
        st.markdown("### 📋 Detailed Data Explorer")
        
        # Data table with search and filters
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("🔍 Search pages:", placeholder="Enter URL or page name...")
        
        with col2:
            sort_by = st.selectbox("Sort by:", ['raw_score', 'persona_id', 'tier', 'criterion_id'])
        
        # Filter data by search term
        display_df = filtered_df.copy()
        if search_term:
            display_df = display_df[display_df['url_slug'].str.contains(search_term, case=False, na=False)]
        
        # Sort data
        display_df = display_df.sort_values(sort_by, ascending=False)
        
        # Format for display
        display_columns = ['persona_id', 'url_slug', 'tier', 'criterion_id', 'raw_score', 'descriptor']
        display_df_formatted = display_df[display_columns].copy()
        display_df_formatted['url_slug'] = display_df_formatted['url_slug'].str.replace('_', ' ').str.title()
        display_df_formatted['criterion_id'] = display_df_formatted['criterion_id'].str.replace('_', ' ').str.title()
        display_df_formatted.columns = ['Persona', 'Page', 'Tier', 'Criterion', 'Score', 'Performance']
        
        st.dataframe(display_df_formatted, use_container_width=True, height=400)
        
        # Export options
        st.markdown("#### 📥 Export Data")
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = display_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Download CSV",
                csv_data,
                "audit_data_filtered.csv",
                "text/csv"
            )
        
        with col2:
            json_data = display_df.to_json(orient='records', indent=2).encode('utf-8')
            st.download_button(
                "📋 Download JSON",
                json_data,
                "audit_data_filtered.json",
                "application/json"
            )
    
    with tab4:
        st.markdown("### 🎯 Key Insights & Recommendations")
        
        # Generate insights
        insights = []
        
        # Overall performance insight
        overall_avg = filtered_df['raw_score'].mean()
        if overall_avg >= 7:
            insights.append("🟢 **Excellent Overall Performance** - Average score exceeds 7.0/10")
        elif overall_avg >= 4:
            insights.append("🟡 **Good Performance with Room for Improvement** - Average score is acceptable but could be enhanced")
        else:
            insights.append("🔴 **Performance Needs Attention** - Average score below 4.0/10 requires immediate action")
        
        # Persona-specific insights
        if len(selected_personas) > 1:
            persona_scores = filtered_df.groupby('persona_id')['raw_score'].mean()
            best_persona = persona_scores.idxmax()
            worst_persona = persona_scores.idxmin()
            score_diff = persona_scores.max() - persona_scores.min()
            
            if score_diff > 1.0:
                insights.append(f"⚖️ **Significant Persona Variance** - {score_diff:.2f} point difference between {best_persona} (best) and {worst_persona} (worst)")
            
        # Tier-specific insights
        tier_scores = filtered_df.groupby('tier')['raw_score'].mean()
        worst_tier = tier_scores.idxmin()
        best_tier = tier_scores.idxmax()
        
        insights.append(f"🏆 **Best Performing Tier**: {best_tier.replace('_', ' ').title()} ({tier_scores.max():.2f}/10)")
        insights.append(f"⚠️ **Needs Focus**: {worst_tier.replace('_', ' ').title()} ({tier_scores.min():.2f}/10)")
        
        # Critical issues
        critical_count = len(filtered_df[filtered_df['descriptor'] == 'FAIL'])
        if critical_count > 0:
            insights.append(f"🚨 **Critical Issues**: {critical_count} evaluations scored as FAIL - immediate attention required")
        
        # Display insights
        for insight in insights:
            st.markdown(f"- {insight}")
        
        # Top and bottom performers
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Performers")
            top_performers = filtered_df.nlargest(5, 'raw_score')[['persona_id', 'url_slug', 'criterion_id', 'raw_score']]
            for _, row in top_performers.iterrows():
                st.write(f"**{row['persona_id']}** - {row['criterion_id'].replace('_', ' ').title()}: {row['raw_score']:.1f}/10")
        
        with col2:
            st.markdown("#### ⚠️ Areas for Improvement")
            bottom_performers = filtered_df.nsmallest(5, 'raw_score')[['persona_id', 'url_slug', 'criterion_id', 'raw_score']]
            for _, row in bottom_performers.iterrows():
                st.write(f"**{row['persona_id']}** - {row['criterion_id'].replace('_', ' ').title()}: {row['raw_score']:.1f}/10")

if __name__ == "__main__":
    main() 