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
    """Load social media data from markdown file"""
    try:
        # Get the correct path relative to the project root
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent  # Go up 4 levels from pages/ to project root
        data_path = project_root / "audit_inputs" / "social_media" / "sm_dashboard_data.md"
        
        with open(data_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Platform Metrics table
        platform_metrics = extract_table_from_markdown(content, "Platform Metrics")
        if not platform_metrics.empty:
            platform_metrics = standardize_regional_naming(platform_metrics)
        
        # Extract Content Type Analysis table
        content_analysis = extract_table_from_markdown(content, "Content Type Analysis")
        if not content_analysis.empty:
            content_analysis = standardize_regional_naming(content_analysis)
        
        # Extract Tone & Messaging Analysis table
        tone_analysis = extract_table_from_markdown(content, "Tone & Messaging Analysis")
        if not tone_analysis.empty:
            tone_analysis = standardize_regional_naming(tone_analysis)
        
        # Extract Key Insights and Recommendations table
        recommendations = extract_table_from_markdown(content, "Key Insights and Recommendations")
        
        return {
            'platform_metrics': platform_metrics,
            'content_analysis': content_analysis,
            'tone_analysis': tone_analysis,
            'recommendations': recommendations
        }
        
    except Exception as e:
        st.error(f"Error loading social media data: {str(e)}")
        return None

def extract_table_from_markdown(content, table_name):
    """Extract a specific table from markdown content"""
    try:
        # Find the table section - handle both cases with and without double newlines
        pattern = rf"## {table_name}.*?\n\n(.*?)(?:\n\n|$)"
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return pd.DataFrame()
        
        table_content = match.group(1)
        
        # Split into lines and process
        lines = table_content.strip().split('\n')
        
        # Skip empty lines and separator lines
        lines = [line for line in lines if line.strip() and not line.strip().startswith('|---')]
        
        if len(lines) < 2:
            return pd.DataFrame()
        
        # Parse header
        header = [col.strip() for col in lines[0].split('|')[1:-1]]
        
        # Parse data rows
        data_rows = []
        for line in lines[1:]:
            if '|' in line:
                row = [col.strip() for col in line.split('|')[1:-1]]
                if len(row) == len(header):
                    data_rows.append(row)
        
        if not data_rows:
            return pd.DataFrame()
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=header)
        
        # Clean the data - remove separator rows and invalid entries
        if not df.empty:
            # Remove rows where any column contains only dashes or similar separators
            df = df[~df.apply(lambda row: any(
                str(cell).strip() in ['---', '----', '-----', '------', '-------', '--------'] or
                str(cell).strip().replace('-', '').replace('|', '').strip() == ''
                for cell in row
            ), axis=1)]
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Reset index after filtering
            df = df.reset_index(drop=True)
        
        return df
        
    except Exception as e:
        st.error(f"Error extracting table {table_name}: {str(e)}")
        return pd.DataFrame()

def standardize_regional_naming(df):
    """Standardize regional naming to fix Global/UK confusion"""
    if 'Region' not in df.columns:
        return df
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Standardize region names
    region_mapping = {
        'Global/UK': 'UK (Global English)',
        'Global': 'Global',
        'UK': 'UK',
        'Benelux': 'Benelux',
        'France': 'France'
    }
    
    df['Region'] = df['Region'].map(region_mapping).fillna(df['Region'])
    
    # Add platform-region identifier for clarity
    if 'Platform' in df.columns:
        df['Platform_Region'] = df['Platform'] + " (" + df['Region'] + ")"
    
    return df

def consolidate_engagement_levels(level_str):
    """Consolidate ridiculous engagement level variations into meaningful categories"""
    if pd.isna(level_str):
        return 'Unknown'
    
    level = str(level_str).lower()
    
    # High engagement indicators
    if any(word in level for word in ['high', 'solid', 'very high']):
        return 'High'
    
    # Medium engagement indicators  
    elif any(word in level for word in ['moderate', 'medium', 'growing', 'meaningful', 'variable', 'contextual']):
        return 'Medium'
    
    # Low engagement indicators
    else:
        return 'Low'

def parse_follower_count(follower_str):
    """Parse follower count strings into numeric values"""
    if pd.isna(follower_str):
        return 0
    
    follower_str = str(follower_str).lower().replace(',', '')
    
    # Handle 'k' notation
    if 'k' in follower_str:
        return float(follower_str.replace('k', '')) * 1000
    
    # Handle 'm' notation  
    elif 'm' in follower_str:
        return float(follower_str.replace('m', '')) * 1000000
    
    # Handle + notation
    elif '+' in follower_str:
        return float(follower_str.replace('+', ''))
    
    # Handle numeric strings
    else:
        try:
            return float(follower_str)
        except:
            return 0

def main():
    """Social Media Analysis Dashboard"""
    
    st.markdown("""
    <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; background: white;">
        <h1 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0;">🔍 Social Media Analysis</h1>
        <p style="color: #6B7280; margin: 0.5rem 0 0 0;">Cross-platform brand presence and engagement insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load social media data
    data = load_social_media_data()
    
    if not data or data['platform_metrics'].empty:
        st.error("❌ No social media data available for analysis.")
        return
    
    # Display filters and controls
    selected_platforms, selected_regions = display_filters(data['platform_metrics'])
    
    # Show current filter status
    if selected_platforms or selected_regions:
        filter_summary = []
        if selected_platforms:
            if len(selected_platforms) == len(data['platform_metrics']['Platform'].unique()):
                filter_summary.append("All Platforms")
            else:
                filter_summary.append(f"{len(selected_platforms)} Platform(s): {', '.join(selected_platforms)}")
        
        if selected_regions:
            if len(selected_regions) == len(data['platform_metrics']['Region'].unique()):
                filter_summary.append("All Regions")
            else:
                filter_summary.append(f"{len(selected_regions)} Region(s): {', '.join(selected_regions)}")
        
        if filter_summary:
            st.info(f"📊 **Current Analysis Scope:** {' | '.join(filter_summary)}")
    
    # Filter data based on selections
    filtered_data = filter_data(data, selected_platforms, selected_regions)
    
    # Display sections
    display_key_metrics_overview(filtered_data)
    display_platform_performance_analysis(filtered_data)
    display_content_strategy_analysis(filtered_data)
    display_recommendations(filtered_data)

def display_filters(platform_metrics):
    """Display dashboard filters"""
    st.markdown("## 🎯 Analysis Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        platforms = sorted(platform_metrics["Platform"].unique().tolist())
        selected_platforms = st.multiselect(
            "📱 Platform", 
            platforms, 
            default=platforms,  # Select all by default
            key="sm_platform_filter",
            help="Select one or more platforms to analyze"
        )
    
    with col2:
        regions = sorted(platform_metrics["Region"].unique().tolist())
        selected_regions = st.multiselect(
            "🌍 Region", 
            regions, 
            default=regions,  # Select all by default
            key="sm_region_filter",
            help="Select one or more regions to analyze"
        )
    
    return selected_platforms, selected_regions

def filter_data(data, selected_platforms, selected_regions):
    """Filter all data tables based on selections"""
    filtered_data = {}
    
    for key, df in data.items():
        if df.empty:
            filtered_data[key] = df
            continue
            
        filtered_df = df.copy()
    
        # Apply platform filter if applicable
        if selected_platforms and "Platform" in df.columns:
            filtered_df = filtered_df[filtered_df["Platform"].isin(selected_platforms)]
        
        # Apply region filter if applicable
        if selected_regions and "Region" in df.columns:
            filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]
        
        filtered_data[key] = filtered_df
    
    return filtered_data

def display_key_metrics_overview(filtered_data):
    """Display key social media metrics"""
    st.markdown("## 📊 Key Metrics Overview")
    
    platform_metrics = filtered_data['platform_metrics']
    
    # Calculate metrics
    active_platforms = len(platform_metrics['Platform'].unique())
    regional_presences = len(platform_metrics['Region'].unique())
    
    # Consolidate engagement and count high engagement
    platform_metrics['Engagement Category'] = platform_metrics['Engagement Level'].apply(consolidate_engagement_levels)
    high_engagement_channels = len(platform_metrics[platform_metrics['Engagement Category'] == 'High'])
    
    # Calculate brand consistency
    tone_analysis = filtered_data['tone_analysis']
    if not tone_analysis.empty and 'Consistency Score (1-5)' in tone_analysis.columns:
        tone_analysis['Consistency Score'] = pd.to_numeric(tone_analysis['Consistency Score (1-5)'], errors='coerce')
        strong_brand_consistency = len(tone_analysis[tone_analysis['Consistency Score'] >= 4])
    else:
        strong_brand_consistency = "N/A"
    
    metrics = {
        "Active Platforms": active_platforms,
        "Regional Presences": regional_presences,
        "High Engagement Channels": high_engagement_channels,
        "Strong Brand Consistency": strong_brand_consistency
    }
    
    cols = st.columns(len(metrics))
    
    for i, (label, value) in enumerate(metrics.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; text-align: center; background: white;">
                <div style="font-size: 2rem; font-weight: bold; color: #E85A4F; font-family: 'Inter', sans-serif;">{value}</div>
                <div style="color: #6B7280; font-family: 'Inter', sans-serif;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def display_platform_performance_analysis(filtered_data):
    """Display platform performance analysis"""
    st.markdown("## 📈 Platform Performance Analysis")
    
    platform_metrics = filtered_data['platform_metrics']
    
    if platform_metrics.empty:
        st.warning("No platform data available for selected filters.")
        return
    
    # Consolidate engagement levels to simple categories
    def consolidate_engagement(level):
        """Consolidate ridiculous engagement levels to High/Moderate/Low"""
        level_str = str(level).lower()
        if any(word in level_str for word in ['high', 'solid']):
            return 'High'
        elif any(word in level_str for word in ['moderate', 'variable', 'varied']):
            return 'Moderate'  
        else:
            return 'Low'
    
    # Apply consolidation
    platform_metrics_clean = platform_metrics.copy()
    platform_metrics_clean['Engagement Level Clean'] = platform_metrics_clean['Engagement Level'].apply(consolidate_engagement)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Engagement levels by platform (consolidated)
        engagement_data = platform_metrics_clean.groupby(['Platform', 'Engagement Level Clean']).size().reset_index(name='count')
        
        fig_engagement = px.bar(
            engagement_data,
            x='Platform',
            y='count',
            color='Engagement Level Clean',
            title='Engagement Levels by Platform',
            color_discrete_map={
                'High': '#10B981',
                'Moderate': '#F59E0B',
                'Low': '#EF4444'
            }
        )
        fig_engagement.update_layout(height=500)
        st.plotly_chart(fig_engagement,  key="engagement_by_platform")
    
    with col2:
        # Brand consistency by platform
        consistency_data = platform_metrics.groupby(['Platform', 'Brand Consistency']).size().reset_index(name='count')
        
        fig_consistency = px.bar(
            consistency_data,
            x='Platform',
            y='count',
            color='Brand Consistency',
            title='Brand Consistency by Platform',
            color_discrete_map={
                'Strong': '#10B981',
                'Moderate': '#F59E0B'
            }
        )
        fig_consistency.update_layout(height=500)
        st.plotly_chart(fig_consistency,  key="brand_consistency")

def display_content_strategy_analysis(filtered_data):
    """Display content strategy analysis"""
    st.markdown("## 📝 Content Strategy Analysis")
    
    content_analysis = filtered_data['content_analysis']
    
    if content_analysis.empty:
        st.warning("No content analysis data available for selected filters.")
        return
    
    # Most engaging content insights
    st.markdown("### 🌟 Most Engaging Content by Platform")
    
    if 'Most Engaging Content' in content_analysis.columns:
        engaging_content = content_analysis[['Platform', 'Region', 'Most Engaging Content']].dropna()
        
        if not engaging_content.empty:
            # Group by platform for collapsible sections
            platforms = engaging_content['Platform'].unique()
            
            for platform in sorted(platforms):
                platform_data = engaging_content[engaging_content['Platform'] == platform]
                
                # Create collapsible section for each platform
                with st.expander(f"📱 {platform} ({len(platform_data)} regions)", expanded=False):
                    for _, row in platform_data.iterrows():
                        st.markdown(f"""
                        <div style="border-left: 3px solid #E85A4F; padding-left: 1rem; margin-bottom: 1rem;">
                            <h5 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0 0 0.5rem 0;">
                                {row['Region']}
                            </h5>
                            <p style="color: #6B7280; margin: 0; font-family: 'Inter', sans-serif;">
                                {row['Most Engaging Content']}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

def display_recommendations(filtered_data):
    """Display strategic recommendations"""
    recommendations = filtered_data['recommendations']
    
    if recommendations.empty:
        st.warning("⚠️ No recommendations available for the selected scope.")
        return
        
    st.markdown("## 💡 Recommendations & Insights")
    
    # High Priority
    st.markdown("<h3 style=\"color: #E85A4F; font-family: 'Crimson Text', serif;\"> 🔥 High Priority Recommendations</h3>", unsafe_allow_html=True)
    high_priority = recommendations[recommendations['Priority'] == 'High']
    for _, row in high_priority.iterrows():
        st.markdown(f"""
        <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background: white;">
            <h4 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0 0 0.5rem 0;">{row.get('Category', 'General Recommendation')}</h4>
            <p style="color: #6B7280; margin: 0 0 0.5rem 0; font-family: 'Inter', sans-serif;">
                <strong>Observation:</strong> {row.get('Key Insight', 'N/A')}
            </p>
            <p style="color: #2C3E50; margin: 0; font-family: 'Inter', sans-serif;">
                <strong>Recommendation:</strong> {row.get('Recommendation', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    # Medium Priority
    st.markdown("<h3 style=\"color: #F59E0B; font-family: 'Crimson Text', serif;\"> ⚡ Medium Priority Recommendations</h3>", unsafe_allow_html=True)
    medium_priority = recommendations[recommendations['Priority'] == 'Medium']
    for _, row in medium_priority.iterrows():
        st.markdown(f"""
        <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; background: white;">
            <h4 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0 0 0.5rem 0;">{row.get('Category', 'General Recommendation')}</h4>
            <p style="color: #6B7280; margin: 0 0 0.5rem 0; font-family: 'Inter', sans-serif;">
                <strong>Observation:</strong> {row.get('Key Insight', 'N/A')}
            </p>
            <p style="color: #2C3E50; margin: 0; font-family: 'Inter', sans-serif;">
                <strong>Recommendation:</strong> {row.get('Recommendation', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 