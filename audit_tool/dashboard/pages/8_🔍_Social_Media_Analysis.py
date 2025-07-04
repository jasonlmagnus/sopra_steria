"""
Social Media Analysis - Comprehensive Social Media Performance Dashboard
Cross-platform brand presence and engagement insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import re

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.brand_styling import get_complete_brand_css

# Page configuration
st.set_page_config(
    page_title="Social Media Analysis",
    page_icon="🔍",
    layout="wide"
)

# Apply centralized brand styling with fonts
st.markdown(get_complete_brand_css(), unsafe_allow_html=True)

def load_social_media_data():
    """Load social media data from unified CSV with master audit scores"""
    try:
        # Get the correct path to unified audit data
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent  # Go up 4 levels to project root
        csv_path = project_root / "audit_data" / "unified_audit_data.csv"
        
        if not csv_path.exists():
            st.error(f"Audit data file not found at: {csv_path}")
            return None
        
        # Load CSV data
        df = pd.read_csv(csv_path)
        
        # Filter for social media entries
        social_keywords = ['linkedin', 'twitter', 'facebook', 'instagram', 'x.com']
        social_media_mask = df['url'].str.lower().str.contains('|'.join(social_keywords), na=False)
        social_df = df[social_media_mask].copy()
        
        if social_df.empty:
            st.warning("No social media data found in audit dataset.")
            return None
        
        # Add platform identification
        social_df['platform'] = social_df['url'].apply(identify_platform_from_url)
        social_df['platform_display'] = social_df['platform'].map({
            'linkedin': 'LinkedIn',
            'instagram': 'Instagram', 
            'facebook': 'Facebook',
            'twitter': 'Twitter/X'
        })
        
        # Add persona mapping for cleaner display
        social_df['persona_clean'] = social_df['persona_id'].apply(clean_persona_name)
        
        # Calculate platform averages
        platform_metrics = calculate_platform_metrics(social_df)
        
        # Generate insights and recommendations
        insights = generate_insights_from_csv(social_df)
        recommendations = generate_recommendations_from_csv(social_df)
        
        return {
            'raw_data': social_df,
            'platform_metrics': platform_metrics,
            'insights': insights,
            'recommendations': recommendations
        }
        
    except Exception as e:
        st.error(f"Error loading social media data: {str(e)}")
        return None

def identify_platform_from_url(url):
    """Identify social media platform from URL"""
    url_lower = str(url).lower()
    if 'linkedin' in url_lower:
        return 'linkedin'
    elif 'instagram' in url_lower:
        return 'instagram'
    elif 'facebook' in url_lower:
        return 'facebook'
    elif 'twitter' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    return 'unknown'

def clean_persona_name(persona_id):
    """Clean persona names for display"""
    persona_mapping = {
        'The Benelux Cybersecurity Decision Maker': 'P4 - Cybersecurity',
        'The Benelux Strategic Business Leader (C-Suite Executive)': 'P1 - C-Suite',
        'The Benelux Transformation Programme Leader': 'P3 - Programme',
        'The Technical Influencer': 'P5 - Tech Influencers',
        'The_BENELUX_Technology_Innovation_Leader': 'P2 - Tech Leaders'
    }
    return persona_mapping.get(persona_id, persona_id)

def calculate_platform_metrics(social_df):
    """Calculate comprehensive platform metrics from CSV data"""
    platform_stats = []
    
    for platform in social_df['platform'].unique():
        platform_data = social_df[social_df['platform'] == platform]
        
        # Calculate metrics
        avg_score = platform_data['raw_score'].mean()
        score_range = f"{platform_data['raw_score'].min():.1f} - {platform_data['raw_score'].max():.1f}"
        
        # Determine status based on average score
        if avg_score >= 7:
            status = "✅ Strong"
            status_color = "success"
        elif avg_score >= 5:
            status = "⚠️ Moderate"
            status_color = "warning"
        elif avg_score >= 3:
            status = "🔶 Weak"
            status_color = "warning"
        else:
            status = "🚨 Critical"
            status_color = "error"
        
        # Count personas by performance
        high_performers = len(platform_data[platform_data['raw_score'] >= 7])
        moderate_performers = len(platform_data[(platform_data['raw_score'] >= 5) & (platform_data['raw_score'] < 7)])
        low_performers = len(platform_data[platform_data['raw_score'] < 5])
        
        # Get engagement and sentiment data
        avg_engagement = platform_data['engagement_numeric'].mean()
        avg_sentiment = platform_data['sentiment_numeric'].mean()
        
        platform_stats.append({
            'Platform': platform_data['platform_display'].iloc[0],
            'Platform_Code': platform,
            'Average_Score': avg_score,
            'Score_Range': score_range,
            'Status': status,
            'Status_Color': status_color,
            'Total_Entries': len(platform_data),
            'High_Performers': high_performers,
            'Moderate_Performers': moderate_performers,
            'Low_Performers': low_performers,
            'Avg_Engagement': avg_engagement,
            'Avg_Sentiment': avg_sentiment,
            'Critical_Issues': len(platform_data[platform_data['critical_issue_flag'] == True]),
            'Success_Cases': len(platform_data[platform_data['success_flag'] == True]),
            'Quick_Wins': len(platform_data[platform_data['quick_win_flag'] == True])
        })
    
    return pd.DataFrame(platform_stats)

def generate_insights_from_csv(social_df):
    """Generate key insights from CSV data"""
    insights = []
    
    # Overall performance insight
    overall_avg = social_df['raw_score'].mean()
    insights.append({
        'Category': 'Overall Performance',
        'Insight': f'Average social media score across all platforms and personas is {overall_avg:.1f}/10',
        'Type': 'metric'
    })
    
    # Best performing platform
    platform_avgs = social_df.groupby('platform_display')['raw_score'].mean().sort_values(ascending=False)
    best_platform = platform_avgs.index[0]
    best_score = platform_avgs.iloc[0]
    insights.append({
        'Category': 'Top Performer',
        'Insight': f'{best_platform} is the strongest platform with {best_score:.1f}/10 average score',
        'Type': 'success'
    })
    
    # Worst performing platform
    worst_platform = platform_avgs.index[-1]
    worst_score = platform_avgs.iloc[-1]
    insights.append({
        'Category': 'Critical Issue',
        'Insight': f'{worst_platform} requires immediate attention with {worst_score:.1f}/10 average score',
        'Type': 'critical'
    })
    
    # Critical issues count
    critical_count = len(social_df[social_df['critical_issue_flag'] == True])
    if critical_count > 0:
        insights.append({
            'Category': 'Critical Issues',
            'Insight': f'{critical_count} entries flagged as critical issues requiring immediate action',
            'Type': 'warning'
        })
    
    # Quick wins
    quick_wins = len(social_df[social_df['quick_win_flag'] == True])
    if quick_wins > 0:
        insights.append({
            'Category': 'Quick Wins',
            'Insight': f'{quick_wins} opportunities identified for quick improvement',
            'Type': 'opportunity'
        })
    
    return insights

def generate_recommendations_from_csv(social_df):
    """Generate actionable recommendations from CSV data"""
    recommendations = []
    
    # Platform-specific recommendations
    for platform in social_df['platform_display'].unique():
        platform_data = social_df[social_df['platform_display'] == platform]
        avg_score = platform_data['raw_score'].mean()
        
        if avg_score < 3:
            priority = 'High'
            recommendations.append({
                'Platform': platform,
                'Priority': priority,
                'Category': 'Critical Revival',
                'Recommendation': f'Immediate reactivation required for {platform}. Current score of {avg_score:.1f}/10 indicates platform abandonment.',
                'Expected_Impact': 'High',
                'Timeline': '0-30 days'
            })
        elif avg_score < 5:
            priority = 'High'
            recommendations.append({
                'Platform': platform,
                'Priority': priority,
                'Category': 'Strategic Improvement',
                'Recommendation': f'Comprehensive content strategy needed for {platform}. Score of {avg_score:.1f}/10 shows underperformance.',
                'Expected_Impact': 'Medium',
                'Timeline': '1-3 months'
            })
        elif avg_score < 7:
            priority = 'Medium'
            recommendations.append({
                'Platform': platform,
                'Priority': priority,
                'Category': 'Optimization',
                'Recommendation': f'Enhance content quality and persona targeting for {platform}. Current score: {avg_score:.1f}/10.',
                'Expected_Impact': 'Medium',
                'Timeline': '1-3 months'
            })
    
    # Persona-specific recommendations
    persona_performance = social_df.groupby('persona_clean')['raw_score'].mean().sort_values()
    worst_persona = persona_performance.index[0]
    worst_persona_score = persona_performance.iloc[0]
    
    recommendations.append({
        'Platform': 'Cross-Platform',
        'Priority': 'High',
        'Category': 'Persona Strategy',
        'Recommendation': f'Develop targeted content strategy for {worst_persona} (avg score: {worst_persona_score:.1f}/10)',
        'Expected_Impact': 'High',
        'Timeline': '1-2 months'
    })
    
    return pd.DataFrame(recommendations)

def main():
    """Social Media Analysis Dashboard"""
    
    st.markdown("""
    <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; background: white;">
        <h1 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0;">🔍 Social Media Analysis</h1>
        <p style="color: #6B7280; margin: 0.5rem 0 0 0;">Cross-platform brand presence and engagement insights</p>
        <p style="color: #E85A4F; margin: 0.25rem 0 0 0; font-size: 0.9rem;">📊 <strong>Live Data:</strong> Powered by unified audit data with master scoring</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load social media data
    data = load_social_media_data()
    
    if not data:
        st.error("❌ No social media data available for analysis.")
        return
    
    # Display executive summary
    display_executive_summary(data)
    
    # Display filters and controls
    selected_platforms, selected_personas, analysis_scope, view_mode = display_filters(data)
    
    # Filter data based on selections
    filtered_data = filter_data(data, selected_platforms, selected_personas, analysis_scope, view_mode)
    
    # Display main sections based on view mode
    view_mode = filtered_data.get('view_mode', 'Overview')
    
    if view_mode == "Overview":
        display_platform_health_overview(filtered_data)
        display_platform_performance_analysis(filtered_data)
        display_persona_analysis(filtered_data)
        display_insights_and_recommendations(filtered_data)
        
    elif view_mode == "Detailed Analysis":
        display_detailed_analysis_tabs(filtered_data)
        
    elif view_mode == "Recommendations":
        display_insights_and_recommendations(filtered_data)
        display_action_priority_matrix(filtered_data)

def display_executive_summary(data):
    """Display executive summary metrics with enhanced features from spec"""
    st.markdown("## 📊 Executive Summary")
    
    social_df = data['raw_data']
    platform_metrics = data['platform_metrics']
    
    # Calculate key metrics
    total_platforms = len(platform_metrics)
    avg_score = social_df['raw_score'].mean()
    critical_issues = len(social_df[social_df['critical_issue_flag'] == True])
    success_cases = len(social_df[social_df['success_flag'] == True])
    quick_wins = len(social_df[social_df['quick_win_flag'] == True])
    
    # Check for critical platform failures (Twitter/X)
    twitter_data = social_df[social_df['platform'] == 'twitter']
    twitter_critical = len(twitter_data[twitter_data['raw_score'] < 2]) > 0 if not twitter_data.empty else False
    
    # Critical Alert Banner - toned down
    if twitter_critical or critical_issues > 0:
        st.markdown("""
        <div style="border: 1px solid #F59E0B; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background: #FFFBEB; border-left: 4px solid #F59E0B;">
            <h4 style="margin: 0; color: #92400E;">⚠️ Attention Required</h4>
            <p style="margin: 0.5rem 0 0 0; color: #78350F;">Twitter/X platform showing low performance scores - review and optimization recommended</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Determine overall health status with visual gauge
    if avg_score >= 7:
        health_status = "🟢 Healthy"
        health_color = "#10B981"
        gauge_color = "success"
    elif avg_score >= 5:
        health_status = "🟡 Moderate"
        health_color = "#F59E0B"
        gauge_color = "warning"
    elif avg_score >= 3:
        health_status = "🟠 At Risk"
        health_color = "#F97316"
        gauge_color = "warning"
            else:
        health_status = "🔴 Critical"
        health_color = "#EF4444"
        gauge_color = "error"
    
    # Enhanced metrics with visual health gauge
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        # Visual health gauge using progress bar
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem; border: 1px solid #E5E7EB; border-radius: 8px; background: white;">
            <h4 style="margin: 0; color: #374151;">Overall Health</h4>
            <div style="font-size: 2rem; font-weight: bold; color: {health_color}; margin: 0.5rem 0;">
                {avg_score:.1f}/10
            </div>
            <div style="background: #F3F4F6; border-radius: 10px; height: 10px; margin: 0.5rem 0;">
                <div style="background: {health_color}; width: {avg_score*10}%; height: 100%; border-radius: 10px;"></div>
            </div>
            <div style="font-size: 0.8rem; color: #6B7280;">{health_status}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Find top and weakest platforms
        top_platform = platform_metrics.loc[platform_metrics['Average_Score'].idxmax(), 'Platform']
        top_score = platform_metrics['Average_Score'].max()
        weakest_platform = platform_metrics.loc[platform_metrics['Average_Score'].idxmin(), 'Platform']
        weakest_score = platform_metrics['Average_Score'].min()
        
        st.metric(
            label="🏆 Top Platform",
            value=f"{top_platform}",
            delta=f"{top_score:.1f}/10"
        )
    
    with col3:
        st.metric(
            label="⚠️ Weakest Platform", 
            value=f"{weakest_platform}",
            delta=f"{weakest_score:.1f}/10",
            delta_color="inverse"
        )
    
    with col4:
        # Platform coverage
        total_expected_platforms = 4  # LinkedIn, Instagram, Facebook, Twitter/X
        coverage_pct = (total_platforms / total_expected_platforms) * 100
        st.metric(
            label="📱 Platform Coverage",
            value=f"{total_platforms}/{total_expected_platforms}",
            delta=f"{coverage_pct:.0f}% Active"
        )
    
    with col5:
        st.metric(
            label="🚨 Critical Issues",
            value=critical_issues,
            delta="Require Immediate Action" if critical_issues > 0 else "None"
        )
    
    with col6:
        st.metric(
            label="⚡ Quick Wins",
            value=quick_wins,
            delta="Easy Improvements"
        )

def display_filters(data):
    """Display enhanced dashboard filters with view modes"""
    st.markdown("## 🎯 Analysis Controls")
    
    social_df = data['raw_data']
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        platforms = sorted(social_df["platform_display"].unique().tolist())
        selected_platforms = st.multiselect(
            "📱 Select Platforms", 
            platforms, 
            default=platforms,
            key="sm_platform_filter",
            help="Select one or more platforms to analyze"
        )
    
    with col2:
        personas = sorted(social_df["persona_clean"].unique().tolist())
        selected_personas = st.multiselect(
            "👥 Select Personas", 
            personas, 
            default=personas,
            key="sm_persona_filter",
            help="Select one or more personas to analyze"
        )
    
    with col3:
        # Analysis scope filter (simulating regional capability with data grouping)
        analysis_scope = st.selectbox(
            "🌍 Analysis Scope",
            ["All Data", "High Performers Only", "Problem Areas", "Quick Wins"],
            index=0,
            help="Focus analysis on specific data subsets"
        )
    
    with col4:
        view_mode = st.radio(
            "📊 View Mode",
            ["Overview", "Detailed Analysis", "Recommendations"],
            horizontal=True,
            help="Choose analysis depth and focus"
        )
    
    return selected_platforms, selected_personas, analysis_scope, view_mode

def filter_data(data, selected_platforms, selected_personas, analysis_scope, view_mode):
    """Filter data based on user selections including analysis scope"""
    social_df = data['raw_data'].copy()
    
    # Apply platform and persona filters
    if selected_platforms:
        social_df = social_df[social_df["platform_display"].isin(selected_platforms)]
    
    if selected_personas:
        social_df = social_df[social_df["persona_clean"].isin(selected_personas)]
    
    # Apply analysis scope filter
    if analysis_scope == "High Performers Only":
        social_df = social_df[social_df['raw_score'] >= 7]
    elif analysis_scope == "Problem Areas":
        social_df = social_df[social_df['raw_score'] < 5]
    elif analysis_scope == "Quick Wins":
        social_df = social_df[social_df['quick_win_flag'] == True]
    # "All Data" requires no additional filtering
    
    # Recalculate metrics with filtered data
    filtered_platform_metrics = calculate_platform_metrics(social_df)
    filtered_insights = generate_insights_from_csv(social_df)
    filtered_recommendations = generate_recommendations_from_csv(social_df)
    
    return {
        'raw_data': social_df,
        'platform_metrics': filtered_platform_metrics,
        'insights': filtered_insights,
        'recommendations': filtered_recommendations,
        'view_mode': view_mode,
        'analysis_scope': analysis_scope
    }

def display_platform_performance_analysis(data):
    """Display platform performance analysis"""
    st.markdown("## 📈 Platform Performance Analysis")
    
    social_df = data['raw_data']
    platform_metrics = data['platform_metrics']
    
    if social_df.empty:
        st.warning("No data available for selected filters.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Platform scores bar chart
        fig_scores = px.bar(
            platform_metrics,
            x='Platform',
            y='Average_Score',
            title='Average Scores by Platform',
            color='Average_Score',
            color_continuous_scale='RdYlGn',
            range_color=[0, 10],
            text='Average_Score'
        )
        fig_scores.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_scores.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_scores, use_container_width=True, key="platform_scores")
    
    with col2:
        # Performance distribution
        performance_data = []
        for _, row in platform_metrics.iterrows():
            performance_data.extend([
                {'Platform': row['Platform'], 'Performance': 'High (7-10)', 'Count': row['High_Performers']},
                {'Platform': row['Platform'], 'Performance': 'Moderate (5-7)', 'Count': row['Moderate_Performers']},
                {'Platform': row['Platform'], 'Performance': 'Low (<5)', 'Count': row['Low_Performers']}
            ])
        
        perf_df = pd.DataFrame(performance_data)
        fig_perf = px.bar(
            perf_df,
            x='Platform',
            y='Count',
            color='Performance',
            title='Performance Distribution by Platform',
            color_discrete_map={
                'High (7-10)': '#10B981',
                'Moderate (5-7)': '#F59E0B',
                'Low (<5)': '#EF4444'
            }
        )
        fig_perf.update_layout(height=400)
        st.plotly_chart(fig_perf, use_container_width=True, key="performance_distribution")

def display_persona_analysis(data):
    """Display persona-specific analysis"""
    st.markdown("## 👥 Persona Performance Analysis")
    
    social_df = data['raw_data']
    
    if social_df.empty:
        st.warning("No persona data available for selected filters.")
        return
    
    # Create persona-platform matrix
    persona_platform_matrix = social_df.pivot_table(
        values='raw_score',
        index='persona_clean',
        columns='platform_display',
        aggfunc='mean'
    ).fillna(0)
    
    # Heatmap
    fig_heatmap = px.imshow(
        persona_platform_matrix.values,
        labels=dict(x="Platform", y="Persona", color="Score"),
        x=persona_platform_matrix.columns,
        y=persona_platform_matrix.index,
        color_continuous_scale="RdYlGn",
        range_color=[0, 10],
        title="Persona-Platform Performance Matrix"
    )
    fig_heatmap.update_layout(height=400)
    st.plotly_chart(fig_heatmap, use_container_width=True, key="persona_heatmap")
    
    # Persona summary table
    st.markdown("### 📋 Persona Performance Summary")
    persona_summary = social_df.groupby('persona_clean').agg({
        'raw_score': ['mean', 'min', 'max'],
        'critical_issue_flag': 'sum',
        'success_flag': 'sum',
        'quick_win_flag': 'sum'
    }).round(1)
    
    persona_summary.columns = ['Avg Score', 'Min Score', 'Max Score', 'Critical Issues', 'Success Cases', 'Quick Wins']
    st.dataframe(persona_summary, use_container_width=True)

def display_insights_and_recommendations(data):
    """Display insights and actionable recommendations"""
    st.markdown("## 💡 Strategic Insights & Recommendations")
    
    insights = data['insights']
    recommendations = data['recommendations']
    
    # Key Insights with better visual hierarchy
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("### 🔍 Key Insights")
        for insight in insights:
            if insight['Type'] == 'critical':
                st.error(f"**{insight['Category']}:** {insight['Insight']}")
            elif insight['Type'] == 'warning':
                st.warning(f"**{insight['Category']}:** {insight['Insight']}")
            elif insight['Type'] == 'success':
                st.success(f"**{insight['Category']}:** {insight['Insight']}")
            else:
                st.info(f"**{insight['Category']}:** {insight['Insight']}")
    
    with col2:
        st.markdown("### 🎯 Priority Actions")
        
        # Recommendations with better formatting
        if not recommendations.empty:
            # High priority recommendations
            high_priority = recommendations[recommendations['Priority'] == 'High']
            if not high_priority.empty:
                st.markdown("#### 🔴 High Priority (Immediate Action)")
                for _, rec in high_priority.iterrows():
            st.markdown(f"""
                    <div style="border-left: 4px solid #EF4444; padding: 0.5rem 1rem; margin: 0.5rem 0; background: #FEF2F2;">
                        <strong>{rec['Platform']} - {rec['Category']}</strong><br/>
                        {rec['Recommendation']}<br/>
                        <small><em>Timeline: {rec['Timeline']} | Impact: {rec['Expected_Impact']}</em></small>
            </div>
            """, unsafe_allow_html=True)

            # Medium priority recommendations
            medium_priority = recommendations[recommendations['Priority'] == 'Medium']
            if not medium_priority.empty:
                st.markdown("#### 🟡 Medium Priority (Next 1-3 months)")
                for _, rec in medium_priority.iterrows():
                    st.markdown(f"""
                    <div style="border-left: 4px solid #F59E0B; padding: 0.5rem 1rem; margin: 0.5rem 0; background: #FFFBEB;">
                        <strong>{rec['Platform']} - {rec['Category']}</strong><br/>
                        {rec['Recommendation']}<br/>
                        <small><em>Timeline: {rec['Timeline']} | Impact: {rec['Expected_Impact']}</em></small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("✅ No specific strategic recommendations required based on current performance levels.")

def display_platform_health_overview(data):
    """Display platform health status grid with visual cards"""
    st.markdown("## 📱 Platform Health Overview")
    
    platform_metrics = data['platform_metrics']
    
    if platform_metrics.empty:
        st.warning("No platform data available for selected filters.")
        return
    
    # Create visual health status cards
    cols = st.columns(len(platform_metrics))
    
    for idx, (_, platform) in enumerate(platform_metrics.iterrows()):
        with cols[idx]:
            # Determine platform icon
            platform_icons = {
                'LinkedIn': '💼',
                'Instagram': '📸', 
                'Facebook': '👥',
                'Twitter/X': '🐦'
            }
            icon = platform_icons.get(platform['Platform'], '📱')
            
            # Status indicator based on score
            if platform['Average_Score'] >= 7:
                status_indicator = "✅"
                status_text = "Healthy"
                card_color = "#10B981"
                bg_color = "#ECFDF5"
            elif platform['Average_Score'] >= 5:
                status_indicator = "⚠️"
                status_text = "Moderate"
                card_color = "#F59E0B"
                bg_color = "#FFFBEB"
            elif platform['Average_Score'] >= 3:
                status_indicator = "🔶"
                status_text = "At Risk"
                card_color = "#F97316"
                bg_color = "#FFF7ED"
            else:
                status_indicator = "🚨"
                status_text = "Critical"
                card_color = "#EF4444"
                bg_color = "#FEF2F2"
            
            # Create platform health card
            st.markdown(f"""
            <div style="border: 2px solid {card_color}; border-radius: 12px; padding: 1rem; text-align: center; background: {bg_color}; margin-bottom: 1rem; min-height: 180px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                <h4 style="margin: 0; color: #374151; font-size: 1rem;">{platform['Platform']}</h4>
                <div style="margin: 1rem 0;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: {card_color};">{platform['Average_Score']:.1f}/10</div>
                    <div style="font-size: 0.9rem; color: #6B7280; margin-top: 0.25rem;">{status_indicator} {status_text}</div>
                </div>
                <div style="font-size: 0.8rem; color: #6B7280;">
                    📊 {platform['Total_Entries']} entries<br/>
                    🎯 {platform['High_Performers']} high performers<br/>
                    ⚡ {platform['Quick_Wins']} quick wins
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_detailed_analysis_tabs(data):
    """Display detailed analysis in tab format"""
    st.markdown("## 🔬 Detailed Analysis")
    
    social_df = data['raw_data']
    platform_metrics = data['platform_metrics']
    
    if social_df.empty:
        st.warning("No data available for detailed analysis.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Platform Deep Dive", 
        "📝 Content Strategy", 
        "🎯 Performance Analytics",
        "⚡ Quick Wins & Actions"
    ])
    
    with tab1:
        display_platform_deep_dive(data)
    
    with tab2:
        display_content_strategy_analysis(data)
    
    with tab3:
        display_performance_analytics(data)
    
    with tab4:
        display_quick_wins_analysis(data)

def display_platform_deep_dive(data):
    """Platform-specific detailed metrics and analysis"""
    st.markdown("### 🔍 Platform-Specific Analysis")
    
    social_df = data['raw_data']
    platform_metrics = data['platform_metrics']
    
    # Platform selector for detailed view
    selected_platform = st.selectbox(
        "Choose platform for deep dive:",
        platform_metrics['Platform'].tolist(),
        key="detailed_platform"
    )
    
    platform_data = social_df[social_df['platform_display'] == selected_platform]
    
    if platform_data.empty:
        st.warning(f"No data available for {selected_platform}")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Performance Breakdown")
        
        # Score distribution
        score_ranges = {
            'Excellent (8-10)': len(platform_data[platform_data['raw_score'] >= 8]),
            'Good (6-8)': len(platform_data[(platform_data['raw_score'] >= 6) & (platform_data['raw_score'] < 8)]),
            'Fair (4-6)': len(platform_data[(platform_data['raw_score'] >= 4) & (platform_data['raw_score'] < 6)]),
            'Poor (<4)': len(platform_data[platform_data['raw_score'] < 4])
        }
        
        for range_label, count in score_ranges.items():
            if count > 0:
                st.metric(range_label, count)
    
    with col2:
        st.markdown("#### 👥 Persona Performance")
        
        persona_scores = platform_data.groupby('persona_clean')['raw_score'].agg(['mean', 'count']).round(1)
        persona_scores.columns = ['Average Score', 'Entries']
        st.dataframe(persona_scores, use_container_width=True)
    
    # Strengths and Weaknesses
    st.markdown("#### 💪 Strengths & Weaknesses")
    
    col1, col2 = st.columns(2)
    
    avg_score = platform_data['raw_score'].mean()
    high_scoring_personas = platform_data[platform_data['raw_score'] >= 7]['persona_clean'].unique()
    low_scoring_personas = platform_data[platform_data['raw_score'] < 5]['persona_clean'].unique()
    
    with col1:
        st.markdown("**🟢 Strengths:**")
        if len(high_scoring_personas) > 0:
            for persona in high_scoring_personas:
                st.write(f"• Strong performance with {persona}")
        if avg_score >= 6:
            st.write(f"• Above-average overall performance ({avg_score:.1f}/10)")
        else:
            st.write("• Identify and build on best-performing content")
    
    with col2:
        st.markdown("**🔴 Areas for Improvement:**")
        if len(low_scoring_personas) > 0:
            for persona in low_scoring_personas:
                st.write(f"• Needs improvement with {persona}")
        if avg_score < 5:
            st.write(f"• Below-average overall performance ({avg_score:.1f}/10)")
        
        critical_issues = len(platform_data[platform_data['critical_issue_flag'] == True])
        if critical_issues > 0:
            st.write(f"• {critical_issues} critical issues require attention")

def display_content_strategy_analysis(data):
    """Content strategy insights and recommendations"""
    st.markdown("### 📝 Content Strategy Insights")
    
    social_df = data['raw_data']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Content Performance by Platform")
        
        # Engagement analysis
        engagement_by_platform = social_df.groupby('platform_display').agg({
            'engagement_numeric': 'mean',
            'sentiment_numeric': 'mean',
            'raw_score': 'mean'
        }).round(2)
        
        engagement_by_platform.columns = ['Avg Engagement', 'Avg Sentiment', 'Avg Score']
        st.dataframe(engagement_by_platform, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 Performance Correlation")
        
        # Create correlation insights
        if len(social_df) > 1:
            correlation = social_df['engagement_numeric'].corr(social_df['raw_score'])
            st.metric(
                "Engagement-Score Correlation", 
                f"{correlation:.2f}",
                delta="Strong correlation" if abs(correlation) > 0.7 else "Moderate correlation" if abs(correlation) > 0.4 else "Weak correlation"
            )
    
    # Content gaps analysis
    st.markdown("#### 🔍 Content Gap Analysis")
    
    # Platform-persona matrix to identify gaps
    gaps_matrix = social_df.pivot_table(
        values='raw_score',
        index='platform_display',
        columns='persona_clean',
        aggfunc='mean'
    ).fillna(0)
    
    # Identify lowest scoring combinations
    gaps_identified = []
    for platform in gaps_matrix.index:
        for persona in gaps_matrix.columns:
            score = gaps_matrix.loc[platform, persona]
            if score > 0 and score < 5:  # Has data but low score
                gaps_identified.append(f"{platform} → {persona}: {score:.1f}/10")
    
    if gaps_identified:
        st.markdown("**🎯 Priority Content Gaps:**")
        for gap in gaps_identified[:5]:  # Show top 5 gaps
            st.write(f"• {gap}")
    else:
        st.success("✅ No significant content gaps identified!")

def display_performance_analytics(data):
    """Advanced performance analytics and metrics"""
    st.markdown("### 📊 Performance Analytics")
    
    social_df = data['raw_data']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Performance Distribution")
        
        # Create performance bins
        social_df_temp = social_df.copy()
        social_df_temp['performance_tier'] = pd.cut(
            social_df_temp['raw_score'], 
            bins=[0, 3, 5, 7, 10], 
            labels=['Critical', 'Poor', 'Good', 'Excellent']
        )
        
        tier_counts = social_df_temp['performance_tier'].value_counts()
        
        fig_tiers = px.pie(
            values=tier_counts.values,
            names=tier_counts.index,
            title="Performance Tier Distribution",
            color_discrete_map={
                'Excellent': '#10B981',
                'Good': '#F59E0B', 
                'Poor': '#F97316',
                'Critical': '#EF4444'
            }
        )
        st.plotly_chart(fig_tiers, use_container_width=True, key="performance_tiers")
    
    with col2:
        st.markdown("#### 📈 Score Range Analysis")
        
        # Score statistics by platform
        score_stats = social_df.groupby('platform_display')['raw_score'].agg([
            'min', 'max', 'mean', 'std'
        ]).round(2)
        
        score_stats.columns = ['Min Score', 'Max Score', 'Avg Score', 'Std Dev']
        st.dataframe(score_stats, use_container_width=True)
    
    # Improvement potential analysis
    st.markdown("#### 🚀 Improvement Potential")
    
    quick_wins = len(social_df[social_df['quick_win_flag'] == True])
    success_cases = len(social_df[social_df['success_flag'] == True])
    critical_issues = len(social_df[social_df['critical_issue_flag'] == True])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("⚡ Quick Wins Available", quick_wins)
    with col2:
        st.metric("🎯 Success Cases to Replicate", success_cases)
    with col3:
        st.metric("🚨 Critical Issues to Fix", critical_issues)

def display_quick_wins_analysis(data):
    """Quick wins and immediate action opportunities"""
    st.markdown("### ⚡ Quick Wins & Immediate Actions")
    
    social_df = data['raw_data']
    
    # Quick wins identification
    quick_wins_data = social_df[social_df['quick_win_flag'] == True]
    
    if not quick_wins_data.empty:
        st.markdown("#### 🎯 Identified Quick Wins")
        
        for _, row in quick_wins_data.iterrows():
            platform = row['platform_display']
            persona = row['persona_clean']
            score = row['raw_score']
            
            st.markdown(f"""
            <div style="border: 1px solid #10B981; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; background: #ECFDF5;">
                <h5 style="color: #059669; margin: 0 0 0.5rem 0;">
                    {platform} → {persona}
                </h5>
                <p style="margin: 0 0 0.5rem 0; color: #374151;">
                    Current Score: {score:.1f}/10 | <strong>Improvement potential identified</strong>
                </p>
                <small style="color: #6B7280;">
                    💡 Focus on content optimization and persona alignment
                </small>
            </div>
            """, unsafe_allow_html=True)
    
    # Success cases to replicate
    success_cases = social_df[social_df['success_flag'] == True]
    
    if not success_cases.empty:
        st.markdown("#### 🏆 Success Cases to Replicate")
        
        for _, row in success_cases.iterrows():
            platform = row['platform_display']
            persona = row['persona_clean']
            score = row['raw_score']
            
                        st.markdown(f"""
            <div style="border: 1px solid #3B82F6; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; background: #EFF6FF;">
                <h5 style="color: #1D4ED8; margin: 0 0 0.5rem 0;">
                    {platform} → {persona}
                            </h5>
                <p style="margin: 0 0 0.5rem 0; color: #374151;">
                    High Performance: {score:.1f}/10 | <strong>Best practice identified</strong>
                            </p>
                <small style="color: #6B7280;">
                    ✨ Apply this approach to other platforms/personas
                </small>
                        </div>
                        """, unsafe_allow_html=True)

def display_action_priority_matrix(data):
    """Display impact vs effort priority matrix for recommendations"""
    st.markdown("## 🎯 Action Priority Matrix")
    
    recommendations = data['recommendations']
    
    if recommendations.empty:
        st.info("No specific recommendations available for current filter selection.")
        return
        
    # Create impact vs effort matrix data
    matrix_data = []
    
    for _, rec in recommendations.iterrows():
        # Map priority to effort (inverse relationship)
        effort_map = {'High': 1, 'Medium': 2, 'Low': 3}  # High priority = low effort number for plotting
        
        # Map expected impact to numeric value
        impact_map = {'High': 3, 'Medium': 2, 'Low': 1}
        
        # Map timeline to size
        timeline_size_map = {
            '0-30 days': 20,
            '1-3 months': 15, 
            '1-2 months': 15,
            '3-6 months': 10
        }
        
        matrix_data.append({
            'Action': rec['Recommendation'][:50] + "..." if len(rec['Recommendation']) > 50 else rec['Recommendation'],
            'Platform': rec['Platform'],
            'Category': rec['Category'],
            'Priority': rec['Priority'],
            'Timeline': rec['Timeline'],
            'Effort': effort_map.get(rec['Priority'], 2),
            'Impact': impact_map.get(rec['Expected_Impact'], 2),
            'Size': timeline_size_map.get(rec['Timeline'], 15)
        })
    
    if not matrix_data:
        st.warning("No recommendations data available for matrix visualization.")
        return
    
    matrix_df = pd.DataFrame(matrix_data)
    
    # Create scatter plot
    fig_matrix = px.scatter(
        matrix_df,
        x='Effort',
        y='Impact', 
        size='Size',
        color='Priority',
        hover_data=['Platform', 'Category', 'Timeline'],
        title='Action Priority Matrix: Impact vs Effort',
        labels={
            'Effort': 'Implementation Effort (1=High Effort, 3=Low Effort)',
            'Impact': 'Expected Impact (1=Low, 3=High)'
        },
        color_discrete_map={
            'High': '#EF4444',
            'Medium': '#F59E0B', 
            'Low': '#10B981'
        }
    )
    
    # Add quadrant annotations
    fig_matrix.add_annotation(
        x=3, y=3, text="Quick Wins<br>(Low Effort, High Impact)",
        showarrow=False, font=dict(size=10, color="green"),
        bgcolor="rgba(16, 185, 129, 0.1)", bordercolor="green"
    )
    
    fig_matrix.add_annotation(
        x=1, y=3, text="Strategic Projects<br>(High Effort, High Impact)", 
        showarrow=False, font=dict(size=10, color="blue"),
        bgcolor="rgba(59, 130, 246, 0.1)", bordercolor="blue"
    )
    
    fig_matrix.add_annotation(
        x=3, y=1, text="Fill-ins<br>(Low Effort, Low Impact)",
        showarrow=False, font=dict(size=10, color="gray"),
        bgcolor="rgba(156, 163, 175, 0.1)", bordercolor="gray"
    )
    
    fig_matrix.add_annotation(
        x=1, y=1, text="Questionable<br>(High Effort, Low Impact)",
        showarrow=False, font=dict(size=10, color="red"), 
        bgcolor="rgba(239, 68, 68, 0.1)", bordercolor="red"
    )
    
    fig_matrix.update_layout(
        height=500,
        xaxis=dict(range=[0.5, 3.5], dtick=1),
        yaxis=dict(range=[0.5, 3.5], dtick=1)
    )
    
    st.plotly_chart(fig_matrix, use_container_width=True, key="priority_matrix")
    
    # Quick wins section
    st.markdown("### ⚡ Recommended Quick Wins")
    
    quick_wins = matrix_df[(matrix_df['Effort'] >= 2.5) & (matrix_df['Impact'] >= 2.5)]
    
    if not quick_wins.empty:
        for _, win in quick_wins.iterrows():
        st.markdown(f"""
            <div style="border: 1px solid #10B981; border-radius: 8px; padding: 1rem; margin: 0.5rem 0; background: #ECFDF5;">
                <h5 style="color: #059669; margin: 0 0 0.5rem 0;">
                    🎯 {win['Platform']} - {win['Category']}
                </h5>
                <p style="margin: 0 0 0.5rem 0; color: #374151;">
                    {win['Action']}
                </p>
                <small style="color: #6B7280;">
                    <strong>Timeline:</strong> {win['Timeline']} | <strong>Priority:</strong> {win['Priority']}
                </small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("💡 Focus on high-impact strategic projects for maximum long-term value.")

if __name__ == "__main__":
    main() 