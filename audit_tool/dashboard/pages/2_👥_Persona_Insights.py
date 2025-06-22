"""
Persona Insights - Comprehensive Persona Analysis
How do our personas feel and act?
Consolidates Persona Comparison + Persona Experience functionality
"""

import streamlit as st
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

# Custom CSS for Persona Insights
st.markdown("""
<style>
    .persona-header {
        background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .persona-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #7c3aed;
        margin-bottom: 1rem;
        height: 100%;
    }
    
    .persona-metric {
        text-align: center;
        padding: 1rem;
    }
    
    .persona-metric .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .persona-metric .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .sentiment-positive { color: #10b981; }
    .sentiment-neutral { color: #f59e0b; }
    .sentiment-negative { color: #ef4444; }
    
    .engagement-high { color: #10b981; }
    .engagement-medium { color: #f59e0b; }
    .engagement-low { color: #ef4444; }
    
    .persona-quote {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #7c3aed;
        margin: 1rem 0;
        font-style: italic;
    }
    
    .comparison-section {
        background: #fef7cd;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #f59e0b;
        margin: 1rem 0;
    }
    
    .experience-highlight {
        background: #ecfdf5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Persona Insights - Comprehensive Persona Analysis"""
    
    # Header
    st.markdown("""
    <div class="persona-header">
        <h1>👥 Persona Insights</h1>
        <p>How do our personas feel and act?</p>
        <p><em>Comprehensive analysis of persona experiences and behaviors</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data from session state or initialize
    if 'datasets' not in st.session_state or 'master_df' not in st.session_state:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        st.session_state['datasets'] = datasets
        st.session_state['master_df'] = master_df
    else:
        datasets = st.session_state['datasets']
        master_df = st.session_state['master_df']
    
    if master_df.empty:
        st.error("❌ No data available for Persona Insights analysis.")
        return
    
    # Initialize metrics calculator
    recommendations_df = datasets.get('recommendations') if datasets else None
    metrics_calc = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Persona selection and filtering
    display_persona_selector(master_df)
    
    # Get selected persona(s)
    selected_persona = st.session_state.get('persona_insights_filter', 'All')
    
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

def display_persona_comparison_analysis(master_df, metrics_calc):
    """Display side-by-side persona comparison (from Persona Comparison page)"""
    st.markdown("## 📊 Persona Performance Comparison")
    
    # Calculate persona-level metrics
    persona_summary = master_df.groupby('persona_id').agg({
        'avg_score': ['mean', 'count'],
        'sentiment_numeric': 'mean',
        'engagement_numeric': 'mean',
        'conversion_numeric': 'mean'
    }).round(2)
    
    # Flatten column names
    persona_summary.columns = ['avg_score', 'page_count', 'avg_sentiment', 'avg_engagement', 'avg_conversion']
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
                status_color = "🌟" if score >= 7 else "✅" if score >= 5 else "⚠️" if score >= 3 else "🚨"
                status_text = "Excellent" if score >= 7 else "Good" if score >= 5 else "Fair" if score >= 3 else "Poor"
                
                st.markdown(f"""
                <div class="persona-card">
                    <h4>{status_color} {persona}</h4>
                    <div class="persona-metric">
                        <div class="metric-value">{score:.1f}/10</div>
                        <div class="metric-label">Overall Score ({status_text})</div>
                    </div>
                    <hr>
                    <div style="display: flex; justify-content: space-between;">
                        <div class="persona-metric">
                            <div class="metric-value sentiment-positive">{data['avg_sentiment']:.1f}</div>
                            <div class="metric-label">Sentiment</div>
                        </div>
                        <div class="persona-metric">
                            <div class="metric-value engagement-high">{data['avg_engagement']:.1f}</div>
                            <div class="metric-label">Engagement</div>
                        </div>
                    </div>
                    <div style="text-align: center; margin-top: 1rem;">
                        <strong>{data['page_count']} pages analyzed</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # Comparison charts
    display_persona_comparison_charts(persona_summary)
    
    # Persona ranking and insights
    display_persona_ranking_insights(persona_summary)

def display_persona_comparison_charts(persona_summary):
    """Display comparison charts between personas"""
    st.markdown("### 📈 Persona Performance Comparison Charts")
    
    # Overall score comparison
    fig_score = px.bar(
        x=persona_summary.index,
        y=persona_summary['avg_score'],
        title="Overall Brand Health Score by Persona",
        color=persona_summary['avg_score'],
        color_continuous_scale='RdYlGn',
        range_color=[0, 10]
    )
    fig_score.update_layout(height=400)
    st.plotly_chart(fig_score, use_container_width=True)
    
    # Multi-metric comparison
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment vs Engagement scatter
        fig_scatter = px.scatter(
            x=persona_summary['avg_sentiment'],
            y=persona_summary['avg_engagement'],
            size=persona_summary['page_count'],
            color=persona_summary['avg_score'],
            hover_name=persona_summary.index,
            title="Sentiment vs Engagement by Persona",
            labels={"x": "Average Sentiment", "y": "Average Engagement"},
            color_continuous_scale='RdYlGn',
            range_color=[0, 10]
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        # Radar chart for top 3 personas
        top_personas = persona_summary.head(3)
        
        if len(top_personas) > 0:
            fig_radar = go.Figure()
            
            metrics = ['avg_score', 'avg_sentiment', 'avg_engagement', 'avg_conversion']
            metric_labels = ['Overall Score', 'Sentiment', 'Engagement', 'Conversion']
            
            for persona in top_personas.index:
                values = [top_personas.loc[persona, metric] for metric in metrics]
                values.append(values[0])  # Close the radar chart
                
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metric_labels + [metric_labels[0]],
                    fill='toself',
                    name=persona
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )),
                showlegend=True,
                title="Top 3 Personas - Multi-Metric Comparison",
                height=400
            )
            st.plotly_chart(fig_radar, use_container_width=True)

def display_persona_ranking_insights(persona_summary):
    """Display persona ranking and insights"""
    st.markdown("### 🏆 Persona Performance Ranking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success("🥇 **Top Performing Personas**")
        for i, (persona, data) in enumerate(persona_summary.head(3).iterrows(), 1):
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            st.write(f"{medal} **{persona}**: {data['avg_score']:.1f}/10")
            st.write(f"   • Sentiment: {data['avg_sentiment']:.1f} | Engagement: {data['avg_engagement']:.1f}")
    
    with col2:
        st.error("📉 **Areas for Improvement**")
        bottom_personas = persona_summary.tail(2)
        for persona, data in bottom_personas.iterrows():
            st.write(f"⚠️ **{persona}**: {data['avg_score']:.1f}/10")
            
            # Identify specific improvement areas
            improvements = []
            if data['avg_sentiment'] < 5:
                improvements.append("Sentiment")
            if data['avg_engagement'] < 5:
                improvements.append("Engagement")
            if data['avg_conversion'] < 5:
                improvements.append("Conversion")
            
            if improvements:
                st.write(f"   • Focus on: {', '.join(improvements)}")

def display_individual_persona_analysis(filtered_df, persona_name, metrics_calc):
    """Display detailed analysis for individual persona (from Persona Experience page)"""
    st.markdown(f"## 🔍 Deep Dive: {persona_name}")
    
    # Persona overview metrics
    display_persona_overview_metrics(filtered_df, persona_name)
    
    # Sentiment and engagement analysis
    display_sentiment_engagement_analysis(filtered_df, persona_name)
    
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
    avg_sentiment = filtered_df['sentiment_numeric'].mean() if 'sentiment_numeric' in filtered_df.columns else 0
    avg_engagement = filtered_df['engagement_numeric'].mean() if 'engagement_numeric' in filtered_df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_color = "🌟" if avg_score >= 7 else "✅" if avg_score >= 5 else "⚠️" if avg_score >= 3 else "🚨"
        st.metric("Overall Score", f"{avg_score:.1f}/10", delta=status_color)
    
    with col2:
        st.metric("Pages Analyzed", page_count)
    
    with col3:
        sentiment_status = "😊" if avg_sentiment >= 7 else "😐" if avg_sentiment >= 4 else "😞"
        st.metric("Avg Sentiment", f"{avg_sentiment:.1f}/10", delta=sentiment_status)
    
    with col4:
        engagement_status = "🔥" if avg_engagement >= 7 else "👍" if avg_engagement >= 4 else "👎"
        st.metric("Avg Engagement", f"{avg_engagement:.1f}/10", delta=engagement_status)

def display_sentiment_engagement_analysis(filtered_df, persona_name):
    """Display detailed sentiment and engagement analysis"""
    st.markdown("### 💭 Sentiment & Engagement Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'sentiment_numeric' in filtered_df.columns:
            # Sentiment distribution
            sentiment_data = filtered_df['sentiment_numeric'].dropna()
            
            if not sentiment_data.empty:
                fig_sentiment = px.histogram(
                    sentiment_data,
                    nbins=10,
                    title=f"Sentiment Distribution - {persona_name}",
                    color_discrete_sequence=['#7c3aed']
                )
                fig_sentiment.update_layout(height=300)
                st.plotly_chart(fig_sentiment, use_container_width=True)
                
                # Sentiment insights
                positive_pct = len(sentiment_data[sentiment_data >= 7]) / len(sentiment_data) * 100
                negative_pct = len(sentiment_data[sentiment_data < 4]) / len(sentiment_data) * 100
                
                st.markdown(f"""
                <div class="experience-highlight">
                    <strong>Sentiment Insights:</strong><br>
                    • {positive_pct:.1f}% of experiences are positive (≥7)<br>
                    • {negative_pct:.1f}% of experiences are negative (<4)
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        if 'engagement_numeric' in filtered_df.columns:
            # Engagement distribution
            engagement_data = filtered_df['engagement_numeric'].dropna()
            
            if not engagement_data.empty:
                fig_engagement = px.histogram(
                    engagement_data,
                    nbins=10,
                    title=f"Engagement Distribution - {persona_name}",
                    color_discrete_sequence=['#a855f7']
                )
                fig_engagement.update_layout(height=300)
                st.plotly_chart(fig_engagement, use_container_width=True)
                
                # Engagement insights
                high_engagement_pct = len(engagement_data[engagement_data >= 7]) / len(engagement_data) * 100
                low_engagement_pct = len(engagement_data[engagement_data < 4]) / len(engagement_data) * 100
                
                st.markdown(f"""
                <div class="experience-highlight">
                    <strong>Engagement Insights:</strong><br>
                    • {high_engagement_pct:.1f}% show high engagement (≥7)<br>
                    • {low_engagement_pct:.1f}% show low engagement (<4)
                </div>
                """, unsafe_allow_html=True)

def display_persona_page_performance(filtered_df, persona_name):
    """Display page-level performance for the persona"""
    st.markdown("### 📄 Page Performance Analysis")
    
    if 'page_id' in filtered_df.columns and 'avg_score' in filtered_df.columns:
        # Aggregate by page
        page_performance = filtered_df.groupby('page_id').agg({
            'avg_score': 'mean',
            'sentiment_numeric': 'mean',
            'engagement_numeric': 'mean',
            'tier': 'first',
            'url': 'first'
        }).round(2)
        
        page_performance = page_performance.sort_values('avg_score', ascending=False)
        
        # Show top and bottom performing pages
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🏆 **Top Performing Pages for {persona_name}**")
            top_pages = page_performance.head(3)
            
            for page_id, data in top_pages.iterrows():
                st.markdown(f"""
                <div class="experience-highlight">
                    <strong>{page_id}</strong> ({data['tier']})<br>
                    Score: {data['avg_score']:.1f} | Sentiment: {data['sentiment_numeric']:.1f} | Engagement: {data['engagement_numeric']:.1f}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.error(f"📉 **Improvement Opportunities for {persona_name}**")
            bottom_pages = page_performance.tail(3)
            
            for page_id, data in bottom_pages.iterrows():
                st.markdown(f"""
                <div style="background: #fee2e2; padding: 1rem; border-radius: 8px; border-left: 4px solid #ef4444; margin: 0.5rem 0;">
                    <strong>{page_id}</strong> ({data['tier']})<br>
                    Score: {data['avg_score']:.1f} | Sentiment: {data['sentiment_numeric']:.1f} | Engagement: {data['engagement_numeric']:.1f}
                </div>
                """, unsafe_allow_html=True)
        
        # Page performance chart
        if len(page_performance) > 1:
            fig_pages = px.bar(
                x=page_performance.index[:10],  # Top 10 pages
                y=page_performance['avg_score'][:10],
                title=f"Top 10 Page Scores - {persona_name}",
                color=page_performance['avg_score'][:10],
                color_continuous_scale='RdYlGn',
                range_color=[0, 10]
            )
            fig_pages.update_layout(height=400)
            fig_pages.update_xaxes(tickangle=45)
            st.plotly_chart(fig_pages, use_container_width=True)

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
                        st.markdown(f"""
                        <div class="persona-quote">
                            "{quote}"
                        </div>
                        """, unsafe_allow_html=True)
                
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
            
            st.markdown(f"""
            <div class="comparison-section">
                <strong>🏆 Benchmark Persona:</strong> {best_persona}<br>
                <em>Use their experience patterns as templates</em><br><br>
                
                <strong>🎯 Priority Persona:</strong> {worst_persona}<br>
                <em>Focus improvement efforts here first</em>
            </div>
            """, unsafe_allow_html=True)
        
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