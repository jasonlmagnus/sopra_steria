"""
Persona Insights - Comprehensive Persona Analysis
How do our personas feel and act?
Consolidates Persona Comparison + Persona Experience functionality
"""

import streamlit as st

import streamlit as st
from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_main_header,
    create_section_header,
    create_subsection_header,
    create_metric_card,
    create_status_indicator,
    create_success_alert,
    create_warning_alert,
    create_error_alert,
    create_info_alert,
    get_perfect_chart_config,
    apply_chart_styling,
    chart_template,
    colors,
    create_data_table,
    create_two_column_layout,
    create_three_column_layout,
    create_four_column_layout,
    create_content_card,
    create_brand_card,
    create_persona_card,
    create_primary_button,
    create_secondary_button,
    create_badge,
    create_spacer,
    create_divider
)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Persona Insights",
    page_icon="👥",
    layout="wide"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

# Create standardized page header
create_main_header("👥 Persona Insights", "Understanding your audience experience")

def main():
    """Persona Insights - Comprehensive Persona Analysis"""
    
    # Load data using BrandHealthDataLoader
    data_loader = BrandHealthDataLoader()
    master_df = data_loader.load_unified_data()
    
    if master_df.empty:
        st.error("❌ No data available for Persona Insights analysis.")
        return
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(master_df)
    
    # Persona selection and filtering
    selected_persona = display_persona_selector(master_df)
    
    # Filter data based on selection
    if selected_persona == 'All':
        filtered_df = master_df
        analysis_mode = 'comparison'
    else:
        filtered_df = master_df[master_df['persona_id'] == selected_persona]
        analysis_mode = 'individual'
    
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected persona.")
        return
    
    # Display analysis based on mode
    if analysis_mode == 'comparison':
        display_persona_comparison_analysis(master_df, metrics_calc)
    else:
        display_individual_persona_analysis(filtered_df, selected_persona, metrics_calc)
    
    # Always show cross-persona insights at the bottom
    display_cross_persona_insights(master_df)

def display_persona_selector(master_df):
    """Display persona selection controls"""
    st.markdown("## 🎯 Persona Analysis Focus")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Persona selection
        personas = ['All'] + sorted(master_df['persona_id'].unique().tolist())
        selected_persona = st.selectbox(
            "👤 Select Persona for Analysis",
            personas,
            key="persona_insights_filter",
            help="Choose 'All' for comparison view, or specific persona for detailed analysis"
        )
    
    with col2:
        # Analysis mode indicator
        if selected_persona == 'All':
            st.info("📊 **Comparison Mode**\nAnalyzing all personas side-by-side")
        else:
            st.success(f"🔍 **Deep Dive Mode**\nFocused analysis of {selected_persona}")
    
    return selected_persona

def display_persona_comparison_analysis(master_df, metrics_calc):
    """Display side-by-side persona comparison (from Persona Comparison page)"""
    st.markdown("## 📊 Persona Performance Comparison")
    
    # Calculate persona-level metrics - only use meaningful metrics
    persona_summary = master_df.groupby('persona_id').agg({
        'avg_score': ['mean', 'count']
    }).round(2)
    
    # Flatten column names
    persona_summary.columns = ['avg_score', 'page_count']
    persona_summary = persona_summary.sort_values('avg_score', ascending=False)
    
    # Display persona cards
    st.markdown("### 👥 Persona Performance Cards")
    
    personas = persona_summary.index.tolist()
    
    # Create columns for persona cards (max 3 per row)
    rows = [personas[i:i+3] for i in range(0, len(personas), 3)]
    
    for row in rows:
        cols = st.columns(len(row))
        
        for i, persona in enumerate(row):
            with cols[i]:
                data = persona_summary.loc[persona]
                
                # Determine performance status
                score = data['avg_score']
                status_icon = "🌟" if score >= 7 else "✅" if score >= 5 else "⚠️" if score >= 3 else "🚨"
                status_text = "EXCELLENT" if score >= 7 else "GOOD" if score >= 5 else "FAIR" if score >= 3 else "POOR"
                
                # Create persona card with available data
                create_metric_card(
                    value=f"{score:.1f}/10",
                    label=persona.replace('_', ' '),
                    status=status_text.lower()
                )     
    # Comparison charts - simplified without uniform metrics
    display_persona_comparison_charts(persona_summary)
    
    # Persona ranking and insights
    display_persona_ranking_insights(persona_summary)

def display_persona_comparison_charts(persona_summary):
    """Display comparison charts between personas"""
    st.markdown("### 📈 Persona Performance Comparison Charts")
    
    # Use the perfect styling system
    chart_config = get_perfect_chart_config()
    
    # Overall score comparison
    fig_score = px.bar(
        x=persona_summary.index,
        y=persona_summary['avg_score'],
        title="Overall Brand Health Score by Persona",
        color=persona_summary['avg_score'],
        color_continuous_scale="Viridis",
        range_color=[0, 10]
    )
    apply_chart_styling(fig_score, chart_config)
    st.plotly_chart(fig_score, use_container_width=True, key="persona_score_comparison")
    
    # Page coverage comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Page count comparison
        fig_pages = px.bar(
            x=persona_summary.index,
            y=persona_summary['page_count'],
            title="Pages Analyzed per Persona",
            color_discrete_sequence=[colors['secondary']]
        )
        fig_pages.update_layout(
            height=400,
            font=chart_template['layout']['font'],
            title_font=chart_template['layout']['title']['font'],
            paper_bgcolor=colors['background'],
            plot_bgcolor=colors['background']
        )
        st.plotly_chart(fig_pages, use_container_width=True, key="persona_page_count")
    
    with col2:
        # Score distribution pie chart
        fig_pie = px.pie(
            values=persona_summary['avg_score'],
            names=persona_summary.index,
            title="Score Distribution Across Personas",
            color_discrete_sequence=colors['chart_colors']
        )
        fig_pie.update_layout(
            height=400,
            font=chart_template['layout']['font'],
            title_font=chart_template['layout']['title']['font'],
            paper_bgcolor=colors['background']
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="persona_score_distribution")

def display_persona_ranking_insights(persona_summary):
    """Display persona ranking and insights"""
    st.markdown("### 🏆 Persona Performance Ranking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🥇 **Top Performing Personas**")
        for i, (persona, data) in enumerate(persona_summary.head(3).iterrows(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.write(f"{medal} **{persona.replace('_', ' ')}**: {data['avg_score']:.1f}/10")
            st.write(f"   • {data['page_count']} pages analyzed")
    
    with col2:
        st.error("📉 **Areas for Improvement**")
        bottom_personas = persona_summary.tail(2)
        for persona, data in bottom_personas.iterrows():
            st.write(f"⚠️ **{persona.replace('_', ' ')}**: {data['avg_score']:.1f}/10")
            st.write(f"   • Focus on improving content quality and alignment")

def display_individual_persona_analysis(filtered_df, persona_name, metrics_calc):
    """Display detailed analysis for individual persona (from Persona Experience page)"""
    st.markdown(f"## 🔍 Deep Dive: {persona_name.replace('_', ' ')}")
    
    # Persona overview metrics
    display_persona_overview_metrics(filtered_df, persona_name)
    
    # Page-level performance for this persona
    display_persona_page_performance(filtered_df, persona_name)
    
    # First impressions and quotes
    display_persona_quotes_insights(filtered_df, persona_name)

def display_persona_overview_metrics(filtered_df, persona_name):
    """Display overview metrics for individual persona"""
    st.markdown("### 📊 Performance Overview")
    
    # Calculate key metrics
    avg_score = filtered_df['avg_score'].mean() if 'avg_score' in filtered_df.columns else 0
    page_count = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
    
    # Calculate tier distribution
    tier_counts = filtered_df['tier'].value_counts() if 'tier' in filtered_df.columns else {}
    top_tier = tier_counts.index[0] if len(tier_counts) > 0 else "Unknown"
    
    # Calculate critical issues
    critical_count = len(filtered_df[filtered_df['avg_score'] < 4.0]) if 'avg_score' in filtered_df.columns else 0
    
    # Display metrics using simple columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Overall Score", f"{avg_score:.1f}/10")
    with col2:
        st.metric("Pages Analyzed", page_count)
    with col3:
        st.metric("Primary Tier", top_tier.replace('tier_', 'Tier ').title())
    with col4:
        st.metric("Critical Issues", critical_count)

def display_persona_page_performance(filtered_df, persona_name):
    """Display page-level performance for the persona"""
    st.markdown("### 📄 Page Performance Analysis")
    
    if 'page_id' in filtered_df.columns and 'avg_score' in filtered_df.columns:
        # Aggregate by page
        page_performance = filtered_df.groupby('page_id').agg({
            'avg_score': 'mean',
            'tier': 'first',
            'tier_name': 'first',
            'url': 'first',
            'url_slug': 'first'
        }).round(2)
        
        page_performance = page_performance.sort_values('avg_score', ascending=False)
        
        # Show top and bottom performing pages
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🏆 **Top Performing Pages for {persona_name.replace('_', ' ')}**")
            top_pages = page_performance.head(3)
            
            for page_id, data in top_pages.iterrows():
                # Create friendly title from URL slug
                friendly_title = data['url_slug'].replace('www', '').replace('com', '').replace('be', '').replace('nl', '')
                friendly_title = friendly_title.replace('-', ' ').title()[:50]
                st.write(f"📄 **{friendly_title}**: {data['avg_score']:.1f}/10")
        
        with col2:
            st.error(f"📉 **Improvement Opportunities for {persona_name.replace('_', ' ')}**")
            bottom_pages = page_performance.tail(3)
            
            for page_id, data in bottom_pages.iterrows():
                # Create friendly title from URL slug
                friendly_title = data['url_slug'].replace('www', '').replace('com', '').replace('be', '').replace('nl', '')
                friendly_title = friendly_title.replace('-', ' ').title()[:50]
                st.write(f"📄 **{friendly_title}**: {data['avg_score']:.1f}/10")
        
        # Page performance chart
        if len(page_performance) > 1:
            # Create friendly names for chart
            page_names = []
            for idx in page_performance.index[:10]:
                slug = page_performance.loc[idx, 'url_slug']
                friendly = slug.replace('www', '').replace('com', '').replace('be', '').replace('nl', '')
                friendly = friendly.replace('-', ' ').title()[:30] + "..."
                page_names.append(friendly)
            
            # Use chart config from perfect styling
            chart_config = get_perfect_chart_config()
            
            fig_pages = px.bar(
                x=page_names,
                y=page_performance['avg_score'][:10],
                title=f"Top 10 Page Scores - {persona_name.replace('_', ' ')}",
                color=page_performance['avg_score'][:10],
                color_continuous_scale="Viridis",
                range_color=[0, 10]
            )
            fig_pages.update_layout(height=400)
            fig_pages.update_xaxes(tickangle=45)
            st.plotly_chart(fig_pages, use_container_width=True, key=f"page_performance_{persona_name}")

def display_persona_quotes_insights(filtered_df, persona_name):
    """Display first impressions and qualitative insights"""
    st.markdown("### 💬 First Impressions & Insights")
    
    # Look for first impression or feedback columns
    quote_columns = [col for col in filtered_df.columns if any(keyword in col.lower() for keyword in ['first_impression', 'feedback', 'quote', 'comment'])]
    
    if quote_columns:
        for col in quote_columns:
            quotes = filtered_df[col].dropna().unique()
            
            if len(quotes) > 0:
                st.markdown(f"#### 💭 {col.replace('_', ' ').title()}")
                
                # Show a sample of quotes
                sample_quotes = quotes[:3] if len(quotes) >= 3 else quotes
                
                for i, quote in enumerate(sample_quotes, 1):
                    if quote and str(quote).strip():
                        st.write(f"💬 \"{quote}\"")
                
                if len(quotes) > 3:
                    st.info(f"💡 Showing 3 of {len(quotes)} total {col.replace('_', ' ')} entries")
    else:
        st.info("💬 No qualitative feedback data available for detailed quote analysis.")

def display_cross_persona_insights(master_df):
    """Display insights that compare across all personas"""
    st.markdown("---")
    st.markdown("## 🔄 Cross-Persona Insights")
    
    # Calculate cross-persona metrics
    if 'persona_id' in master_df.columns and 'avg_score' in master_df.columns:
        persona_comparison = master_df.groupby('persona_id')['avg_score'].agg(['mean', 'std', 'count']).round(2)
        persona_comparison.columns = ['avg_score', 'score_variation', 'sample_size']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Persona Consistency Analysis")
            
            # Find most and least consistent personas
            if 'score_variation' in persona_comparison.columns:
                most_consistent = persona_comparison['score_variation'].idxmin()
                least_consistent = persona_comparison['score_variation'].idxmax()
                
                st.success(f"🎯 **Most Consistent Experience:** {most_consistent}")
                st.write(f"Score variation: ±{persona_comparison.loc[most_consistent, 'score_variation']:.1f}")
                
                st.warning(f"📊 **Most Variable Experience:** {least_consistent}")
                st.write(f"Score variation: ±{persona_comparison.loc[least_consistent, 'score_variation']:.1f}")
        
        with col2:
            st.markdown("### 🎯 Strategic Recommendations")
            
            # Generate persona-based recommendations
            best_persona = persona_comparison['avg_score'].idxmax()
            worst_persona = persona_comparison['avg_score'].idxmin()
        
        # Overall persona performance summary
        st.markdown("### 📈 Overall Persona Performance Summary")
        
        summary_df = persona_comparison.copy()
        summary_df['performance_level'] = summary_df['avg_score'].apply(
            lambda x: 'Excellent' if x >= 7 else 'Good' if x >= 5 else 'Fair' if x >= 3 else 'Poor'
        )
        
        # Style the summary table
        def color_performance_level(val):
            if val == 'Excellent':
                return 'background-color: #d1fae5'
            elif val == 'Good':
                return 'background-color: #fef3c7'
            elif val == 'Fair':
                return 'background-color: #fee2e2'
            else:
                return 'background-color: #fecaca'
        
        styled_summary = summary_df.style.map(color_performance_level, subset=['performance_level'])
        styled_summary = styled_summary.format({
            'avg_score': '{:.1f}',
            'score_variation': '{:.1f}',
            'sample_size': '{:.0f}'
        })
        
        st.dataframe(styled_summary, use_container_width=True)

if __name__ == "__main__":
    main() 