"""
Content Matrix - Comprehensive Content Analysis
Detailed performance analysis by content type, tier, and criteria
Consolidates Overview + Tier Analysis functionality
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
from components.tier_analyzer import TierAnalyzer

# Page configuration
st.set_page_config(
    page_title="Content Matrix",
    page_icon="📊",
    layout="wide"
)

# Import centralized brand styling (fonts already loaded on home page)
from components.brand_styling import get_brand_css
st.markdown(get_brand_css(), unsafe_allow_html=True)

def main():
    """Content Matrix - Comprehensive Content Analysis"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Content Matrix</h1>
        <p>Where do we pass/fail across content types?</p>
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
        st.error("❌ No data available for Content Matrix analysis.")
        return
    
    # Initialize analyzers
    recommendations_df = datasets.get('recommendations') if datasets else None
    metrics_calc = BrandHealthMetricsCalculator(master_df, recommendations_df)
    tier_analyzer = TierAnalyzer(master_df)
    
    # Content filtering controls
    display_content_filters(master_df)
    
    # Apply filters
    filtered_df = apply_content_filters(master_df)
    
    if filtered_df.empty:
        st.warning("⚠️ No data matches the selected filters.")
        return
    
    # Update analyzers with filtered data
    filtered_metrics_calc = BrandHealthMetricsCalculator(filtered_df, recommendations_df)
    filtered_tier_analyzer = TierAnalyzer(filtered_df)
    
    # Main content analysis sections
    display_performance_overview(filtered_metrics_calc, filtered_df)
    
    display_tier_performance_analysis(filtered_tier_analyzer, filtered_df)
    
    display_content_type_heatmap(filtered_df)
    
    display_criteria_deep_dive(filtered_df)
    
    display_page_drill_down(filtered_df)

def display_content_filters(master_df):
    """Display filtering controls for content analysis"""
    st.markdown("## 🎛️ Content Analysis Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Persona filter
        personas = ['All'] + sorted(master_df['persona_id'].unique().tolist())
        selected_persona = st.selectbox(
            "👥 Persona",
            personas,
            key="content_persona_filter"
        )
    
    with col2:
        # Tier filter
        tiers = ['All'] + sorted([t for t in master_df['tier'].unique() if pd.notna(t)])
        selected_tier = st.selectbox(
            "🏗️ Content Tier",
            tiers,
            key="content_tier_filter"
        )
    
    with col3:
        # Score range filter
        min_score = st.slider(
            "📊 Min Score",
            0.0, 10.0, 0.0,
            key="content_min_score"
        )
    
    with col4:
        # Performance level filter
        performance_levels = ['All', 'Excellent (≥8)', 'Good (6-8)', 'Fair (4-6)', 'Poor (<4)']
        selected_performance = st.selectbox(
            "⭐ Performance Level",
            performance_levels,
            key="content_performance_filter"
        )

def apply_content_filters(master_df):
    """Apply selected filters to the dataset"""
    filtered_df = master_df.copy()
    
    # Persona filter
    if st.session_state.get('content_persona_filter', 'All') != 'All':
        filtered_df = filtered_df[filtered_df['persona_id'] == st.session_state['content_persona_filter']]
    
    # Tier filter
    if st.session_state.get('content_tier_filter', 'All') != 'All':
        filtered_df = filtered_df[filtered_df['tier'] == st.session_state['content_tier_filter']]
    
    # Score filter
    min_score = st.session_state.get('content_min_score', 0.0)
    if 'avg_score' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['avg_score'] >= min_score]
    
    # Performance level filter
    performance_filter = st.session_state.get('content_performance_filter', 'All')
    if performance_filter != 'All' and 'avg_score' in filtered_df.columns:
        if 'Excellent' in performance_filter:
            filtered_df = filtered_df[filtered_df['avg_score'] >= 8.0]
        elif 'Good' in performance_filter:
            filtered_df = filtered_df[(filtered_df['avg_score'] >= 6.0) & (filtered_df['avg_score'] < 8.0)]
        elif 'Fair' in performance_filter:
            filtered_df = filtered_df[(filtered_df['avg_score'] >= 4.0) & (filtered_df['avg_score'] < 6.0)]
        elif 'Poor' in performance_filter:
            filtered_df = filtered_df[filtered_df['avg_score'] < 4.0]
    
    return filtered_df

def display_performance_overview(metrics_calc, filtered_df):
    """Display high-level performance overview with business context"""
    st.markdown("## 📈 Performance Overview")
    
    # Add business impact context at the top
    if 'avg_score' in filtered_df.columns:
        avg_score = filtered_df['avg_score'].mean()
        total_pages = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
        poor_performers = len(filtered_df[filtered_df['avg_score'] < 6.0])
        
        # Content performance status
        if avg_score >= 8:
            business_impact = "🚀 Strong content performance across pages"
            impact_color = "green"
        elif avg_score >= 6:
            business_impact = f"⚠️ {poor_performers} pages need improvement"
            impact_color = "orange"
        else:
            business_impact = f"🚨 {poor_performers} pages require attention"
            impact_color = "red"
        
        st.markdown(f"""
        <div style="background: #f8f9fa; border-left: 4px solid {impact_color}; padding: 15px; margin: 15px 0; border-radius: 5px;">
            <h4 style="margin: 0; color: #333;">💡 Content Status</h4>
            <p style="margin: 8px 0; color: {impact_color}; font-weight: bold;">{business_impact}</p>
            <p style="margin: 5px 0; font-size: 14px;">
                <strong>Focus:</strong> Prioritize pages scoring below 6.0 for maximum impact
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Calculate key performance metrics
    if 'avg_score' in filtered_df.columns:
        avg_score = filtered_df['avg_score'].mean()
        total_pages = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
        
        # Performance distribution
        excellent = len(filtered_df[filtered_df['avg_score'] >= 8.0])
        good = len(filtered_df[(filtered_df['avg_score'] >= 6.0) & (filtered_df['avg_score'] < 8.0)])
        fair = len(filtered_df[(filtered_df['avg_score'] >= 4.0) & (filtered_df['avg_score'] < 6.0)])
        poor = len(filtered_df[filtered_df['avg_score'] < 4.0])
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Average Score", f"{avg_score:.1f}/10")
        
        with col2:
            st.metric("Total Pages", total_pages)
        
        with col3:
            st.markdown(f"""
            <div class="matrix-card">
                <div class="metric-value performance-excellent">🌟 {excellent}</div>
                <div class="metric-label">Excellent (≥8.0)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="matrix-card">
                <div class="metric-value performance-good">✅ {good}</div>
                <div class="metric-label">Good (6.0-8.0)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="matrix-card">
                <div class="metric-value performance-fair">⚠️ {fair + poor}</div>
                <div class="metric-label">Needs Work (<6.0)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Performance distribution chart
        performance_data = pd.DataFrame({
            'Performance Level': ['Excellent (≥8)', 'Good (6-8)', 'Fair (4-6)', 'Poor (<4)'],
            'Count': [excellent, good, fair, poor],
            'Color': ['#10b981', '#f59e0b', '#ef4444', '#dc2626']
        })
        
        fig = px.bar(
            performance_data,
            x='Performance Level',
            y='Count',
            color='Color',
            color_discrete_map=dict(zip(performance_data['Color'], performance_data['Color'])),
            title="Performance Distribution"
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True, key="performance_distribution")

def display_tier_performance_analysis(tier_analyzer, filtered_df):
    """Display detailed tier performance analysis (from Tier Analysis page)"""
    st.markdown("## 🏗️ Tier Performance Analysis")
    
    # Calculate tier performance
    tier_summary = tier_analyzer.get_tier_summary()
    
    # Convert to DataFrame for display
    if tier_summary:
        tier_performance = pd.DataFrame.from_dict(tier_summary, orient='index')
    else:
        tier_performance = pd.DataFrame()
    
    if not tier_performance.empty:
        st.markdown("### 📊 Performance by Content Tier")
        
        # Display tier performance table with styling
        format_dict = {}
        gradient_cols = []
        
        for col in tier_performance.columns:
            if col in ['avg_score', 'avg_sentiment', 'avg_conversion', 'avg_engagement']:
                format_dict[col] = '{:.1f}'
                if col == 'avg_score':
                    gradient_cols.append(col)
        
        styled_df = tier_performance.style.format(format_dict)
        if gradient_cols:
            styled_df = styled_df.background_gradient(subset=gradient_cols, cmap='RdYlGn', vmin=0, vmax=10)
        
        st.dataframe(styled_df, use_container_width=True)
        
        # Tier comparison chart
        if 'avg_score' in tier_performance.columns:
            # Reset index to make tier IDs a column
            chart_data = tier_performance.reset_index()
            chart_data = chart_data.rename(columns={'index': 'tier_id'})
            
            fig = px.bar(
                chart_data,
                x='tier_id',
                y='avg_score',
                title="Average Score by Content Tier",
                color='avg_score',
                color_continuous_scale='RdYlGn',
                range_color=[0, 10]
            )
            fig.update_layout(height=400, xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True, key="tier_performance_bar")
        
        # Tier insights
        display_tier_insights(tier_performance)
    else:
        st.info("📊 Tier performance data not available with current filters.")

def display_tier_insights(tier_performance):
    """Display insights about tier performance"""
    st.markdown("### 💡 Tier Performance Insights")
    
    if 'avg_score' in tier_performance.columns:
        # Find best and worst performing tiers
        best_tier = tier_performance['avg_score'].idxmax()
        worst_tier = tier_performance['avg_score'].idxmin()
        best_score = tier_performance.loc[best_tier, 'avg_score']
        worst_score = tier_performance.loc[worst_tier, 'avg_score']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🏆 **Best Performing Tier:** {best_tier}")
            st.write(f"Average Score: {best_score:.1f}/10")
            
            if best_score >= 8.0:
                st.write("✨ **Status:** Excellent - Use as template for other tiers")
            elif best_score >= 6.0:
                st.write("✅ **Status:** Good - Minor optimizations needed")
            else:
                st.write("⚠️ **Status:** Needs improvement across all tiers")
        
        with col2:
            st.error(f"📉 **Lowest Performing Tier:** {worst_tier}")
            st.write(f"Average Score: {worst_score:.1f}/10")
            
            if worst_score < 4.0:
                st.write("🚨 **Priority:** Critical - Immediate attention required")
            elif worst_score < 6.0:
                st.write("⚠️ **Priority:** High - Significant improvements needed")
            else:
                st.write("💡 **Priority:** Medium - Optimization opportunities")

def display_content_type_heatmap(filtered_df):
    """Display interactive content type performance heatmap"""
    st.markdown("## 🔥 Content Performance Heatmap")
    
    if 'tier' in filtered_df.columns and 'avg_score' in filtered_df.columns:
        # Create tier vs criteria heatmap using available numeric columns
        criteria_cols = [col for col in filtered_df.columns if col in [
            'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
        ]]
        
        if criteria_cols:
            # Aggregate by tier and criteria
            heatmap_data = filtered_df.groupby('tier')[criteria_cols].mean(numeric_only=True).round(1)
            
            if not heatmap_data.empty:
                # Create heatmap
                fig = px.imshow(
                    heatmap_data.T,
                    labels=dict(x="Content Tier", y="Criteria", color="Score"),
                    title="Content Performance Heatmap: Tier × Criteria",
                    color_continuous_scale='RdYlGn',
                    range_color=[0, 10]
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True, key="content_heatmap")
                
                # Heatmap insights
                st.markdown("### 🔍 Heatmap Insights")
                
                # Find hotspots and cold spots
                flat_data = heatmap_data.stack().reset_index()
                flat_data.columns = ['tier', 'criteria', 'raw_score']
                
                hotspots = flat_data.nlargest(3, 'raw_score')
                coldspots = flat_data.nsmallest(3, 'raw_score')
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.success("🔥 **Top Performing Areas:**")
                    for _, row in hotspots.iterrows():
                        st.write(f"• **{row['tier']}** - {row['criteria']}: {row['raw_score']:.1f}")
                
                with col2:
                    st.error("❄️ **Areas Needing Attention:**")
                    for _, row in coldspots.iterrows():
                        st.write(f"• **{row['tier']}** - {row['criteria']}: {row['raw_score']:.1f}")
        else:
            st.info("📊 Criteria data not available for heatmap analysis.")
    else:
        st.info("📊 Tier and score data required for heatmap analysis.")

def display_criteria_deep_dive(filtered_df):
    """Display detailed criteria analysis (from Criteria Deep Dive page)"""
    st.markdown("## 🎯 Criteria Deep Dive")
    
    # Find available numeric criteria columns
    criteria_cols = [col for col in filtered_df.columns if col in [
        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
    ]]
    
    if criteria_cols:
        # Calculate criteria performance
        criteria_performance = filtered_df[criteria_cols].mean(numeric_only=True).sort_values(ascending=False)
        
        # Display criteria performance
        st.markdown("### 📊 Criteria Performance Ranking")
        
        criteria_df = pd.DataFrame({
            'Criteria': criteria_performance.index,
            'Average Score': criteria_performance.values,
            'Performance Level': ['Excellent' if score >= 8 else 'Good' if score >= 6 else 'Fair' if score >= 4 else 'Poor' for score in criteria_performance.values]
        })
        
        # Color code the performance levels
        def color_performance(val):
            if val == 'Excellent':
                return 'background-color: #d1fae5'
            elif val == 'Good':
                return 'background-color: #fef3c7'
            elif val == 'Fair':
                return 'background-color: #fee2e2'
            else:
                return 'background-color: #fecaca'
        
        styled_criteria = criteria_df.style.map(color_performance, subset=['Performance Level']).format({'Average Score': '{:.1f}'})
        st.dataframe(styled_criteria, use_container_width=True)
        
        # Best and worst criteria
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("🏆 **Top 3 Performing Criteria:**")
            for i, (criteria, score) in enumerate(criteria_performance.head(3).items(), 1):
                st.write(f"{i}. **{criteria}**: {score:.1f}/10")
        
        with col2:
            st.error("📉 **Bottom 3 Performing Criteria:**")
            for i, (criteria, score) in enumerate(criteria_performance.tail(3).items(), 1):
                st.write(f"{i}. **{criteria}**: {score:.1f}/10")
        
        # Criteria distribution chart
        fig = px.bar(
            x=criteria_performance.values,
            y=criteria_performance.index,
            orientation='h',
            title="Criteria Performance Distribution",
            color=criteria_performance.values,
            color_continuous_scale='RdYlGn',
            range_color=[0, 10]
        )
        fig.update_layout(height=max(400, len(criteria_cols) * 30))
        st.plotly_chart(fig, use_container_width=True, key="criteria_performance_bar")
    else:
        st.info("📊 Criteria data not available for deep dive analysis.")

def display_page_drill_down(filtered_df):
    """Display page-level drill-down functionality"""
    st.markdown("## 🔍 Page-Level Drill Down")
    
    if 'page_id' in filtered_df.columns:
        # Group by page for drill-down
        page_summary = filtered_df.groupby('page_id').agg({
            'avg_score': 'mean',
            'tier': 'first',
            'persona_id': lambda x: ', '.join(x.unique())
        }).round(2)
        
        # Add page titles if available
        if 'url' in filtered_df.columns:
            page_urls = filtered_df.groupby('page_id')['url'].first()
            page_summary['url'] = page_urls
            
            # Also get url_slug if available for better display names
            if 'url_slug' in filtered_df.columns:
                page_slugs = filtered_df.groupby('page_id')['url_slug'].first()
                page_summary['url_slug'] = page_slugs
            
            # Create readable page titles from URLs
            def create_display_name(row):
                # Prefer url_slug if available, otherwise use url
                if 'url_slug' in row and pd.notna(row['url_slug']) and row['url_slug'] != '':
                    slug = row['url_slug']
                    # Clean up the slug for display
                    if slug.startswith('www'):
                        parts = slug.split('/')
                        if len(parts) > 1:
                            domain = parts[0].replace('www', '').replace('.', ' ').strip()
                            path = parts[1].replace('-', ' ').replace('_', ' ')
                            return f"{domain.title()} - {path.title()}"
                        else:
                            return slug.replace('www', '').replace('.', ' ').replace('-', ' ').title()
                    else:
                        return slug.replace('-', ' ').replace('_', ' ').title()
                
                # Fallback to URL processing
                url = row.get('url', '')
                if pd.isna(url) or url == '':
                    return 'Unknown Page'
                
                # Remove protocol and www
                clean_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
                # Split by / and take meaningful parts
                parts = clean_url.split('/')
                if len(parts) > 1:
                    # Take domain and first meaningful path
                    domain = parts[0].split('.')[0]  # Get main domain name
                    path = parts[1] if len(parts) > 1 and parts[1] != '' else 'home'
                    return f"{domain.capitalize()} - {path.replace('-', ' ').title()}"
                else:
                    return parts[0].split('.')[0].capitalize()
            
            page_summary['display_name'] = page_summary.apply(create_display_name, axis=1)
        else:
            page_summary['display_name'] = 'Unknown Page'
        
        # Sort by score
        page_summary = page_summary.sort_values('avg_score', ascending=False)
        
        st.markdown("### 📄 Individual Page Performance")
        
        # Performance level selector for drill-down
        drill_down_options = ['All Pages', 'Top Performers (≥7)', 'Average Performers (4-7)', 'Underperformers (<4)']
        selected_drill_down = st.selectbox("🎯 Focus on:", drill_down_options)
        
        # Filter based on selection
        if selected_drill_down == 'Top Performers (≥7)':
            display_pages = page_summary[page_summary['avg_score'] >= 7.0]
        elif selected_drill_down == 'Average Performers (4-7)':
            display_pages = page_summary[(page_summary['avg_score'] >= 4.0) & (page_summary['avg_score'] < 7.0)]
        elif selected_drill_down == 'Underperformers (<4)':
            display_pages = page_summary[page_summary['avg_score'] < 4.0]
        else:
            display_pages = page_summary
        
        if not display_pages.empty:
            # Display pages in expandable format
            for page_id, row in display_pages.head(10).iterrows():  # Limit to top 10 for performance
                score_color = "🌟" if row['avg_score'] >= 7 else "✅" if row['avg_score'] >= 5 else "⚠️" if row['avg_score'] >= 3 else "🚨"
                display_name = row.get('display_name', 'Unknown Page')
                
                with st.expander(f"{score_color} {display_name} - Score: {row['avg_score']:.1f} ({row['tier']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Score", f"{row['avg_score']:.1f}/10")
                    
                    with col2:
                        st.metric("Tier", row['tier'])
                    
                    with col3:
                        st.write(f"**Personas:** {row['persona_id']}")
                    
                    if 'url' in row and pd.notna(row['url']):
                        st.write(f"**URL:** {row['url']}")
                    
                    # Show page ID for reference (small text)
                    st.caption(f"Page ID: {page_id}")
                    
                    # Show detailed criteria for this page
                    page_data = filtered_df[filtered_df['page_id'] == page_id]
                    criteria_cols = [col for col in page_data.columns if col in [
                        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
                    ]]
                    
                    if criteria_cols:
                        criteria_scores = page_data[criteria_cols].iloc[0]
                        st.write("**Criteria Breakdown:**")
                        
                        criteria_chart_data = pd.DataFrame({
                            'Criteria': criteria_scores.index,
                            'Score': criteria_scores.values
                        }).sort_values('Score', ascending=True)
                        
                        fig = px.bar(
                            criteria_chart_data,
                            x='Score',
                            y='Criteria',
                            orientation='h',
                            color='Score',
                            color_continuous_scale='RdYlGn',
                            range_color=[0, 10],
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True, key=f"page_criteria_{page_id}")
        else:
            st.info(f"📄 No pages match the selected criteria: {selected_drill_down}")
    else:
        st.info("📄 Page-level data not available for drill-down analysis.")

if __name__ == "__main__":
    main() 