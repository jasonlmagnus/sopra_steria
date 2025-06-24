"""
Success Library - Comprehensive Success Analysis
What already works that we can emulate?
Consolidates Page Performance + Evidence Explorer functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from pathlib import Path
import re

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator
from components.perfect_styling_method import (
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
    create_pattern_card,
    get_perfect_chart_config,
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

# Page configuration
st.set_page_config(
    page_title="Success Library",
    page_icon="🌟",
    layout="wide"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

def extract_persona_quotes_success(text):
    """Extract persona voice quotes from success text"""
    if not text or pd.isna(text):
        return []
    
    quotes = []
    text_str = str(text)
    
    # Look for first-person statements and persona voice patterns
    patterns = [
        r'As a[^.]*\.',
        r'I [^.]*\.',
        r'My [^.]*\.',
        r'This [^.]*for me[^.]*\.',
        r'From my perspective[^.]*\.',
        r'[^.]*resonates with me[^.]*\.',
        r'[^.]*aligns with my[^.]*\.',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text_str, re.IGNORECASE)
        quotes.extend(matches)
    
    # Clean and deduplicate quotes
    cleaned_quotes = []
    for quote in quotes:
        quote = quote.strip()
        if len(quote) > 25 and quote not in cleaned_quotes:
            cleaned_quotes.append(quote)
    
    return cleaned_quotes[:3]  # Return top 3 quotes

def main():
    """Success Library - Comprehensive Success Analysis"""
    
    # Create standardized page header
    create_main_header("🌟 Success Library", "What already works that we can emulate?")
    
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
        st.error("❌ No data available for Success Library analysis.")
        return
    
    # Initialize metrics calculator
    recommendations_df = datasets.get('recommendations') if datasets else None
    metrics_calc = BrandHealthMetricsCalculator(master_df, recommendations_df)
    
    # Success analysis controls
    display_success_controls()
    
    # Main analysis sections
    display_success_overview(metrics_calc, master_df)
    
    display_success_stories_detailed(metrics_calc, master_df)
    
    display_pattern_analysis(master_df)
    
    display_evidence_browser(master_df)
    
    display_replication_guide(metrics_calc, master_df)

def display_success_controls():
    """Display controls for success analysis"""
    st.markdown("## 🎛️ Success Analysis Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Success threshold
        success_threshold = st.slider(
            "⭐ Success Threshold",
            5.0, 10.0, 7.5,
            step=0.1,
            key="success_threshold",
            help="Minimum score to be considered a success"
        )
    
    with col2:
        # Persona filter
        personas = ['All'] + sorted(st.session_state['master_df']['persona_id'].unique().tolist())
        selected_persona = st.selectbox(
            "👤 Persona Focus",
            personas,
            key="success_persona_filter"
        )
    
    with col3:
        # Tier filter
        tiers = ['All'] + sorted([t for t in st.session_state['master_df']['tier'].unique() if pd.notna(t)])
        selected_tier = st.selectbox(
            "🏗️ Content Tier",
            tiers,
            key="success_tier_filter"
        )
    
    with col4:
        # Number of success stories to show
        num_stories = st.number_input(
            "📊 Max Success Stories",
            min_value=5, max_value=50, value=10,
            key="max_success_stories"
        )

def display_success_overview(metrics_calc, master_df):
    """Display high-level success overview"""
    st.markdown("## 📊 Success Overview")
    
    # Apply filters
    filtered_df = apply_success_filters(master_df)
    
    if filtered_df.empty:
        st.warning("⚠️ No data matches the selected filters.")
        return
    
    # Calculate success metrics
    success_threshold = st.session_state.get('success_threshold', 7.7)
    
    if 'avg_score' in filtered_df.columns:
        total_pages = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
        success_pages = len(filtered_df[filtered_df['avg_score'] >= success_threshold])
        success_rate = (success_pages / total_pages * 100) if total_pages > 0 else 0
        avg_success_score = filtered_df[filtered_df['avg_score'] >= success_threshold]['avg_score'].mean() if success_pages > 0 else 0
        
        # Performance distribution
        excellent = len(filtered_df[filtered_df['avg_score'] >= 9.0])
        very_good = len(filtered_df[(filtered_df['avg_score'] >= 8.0) & (filtered_df['avg_score'] < 9.0)])
        good = len(filtered_df[(filtered_df['avg_score'] >= 7.5) & (filtered_df['avg_score'] < 8.0)])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            create_metric_card(f"{total_pages}", "Total Pages")
        
        with col2:
            create_metric_card(f"{success_pages}", "Success Pages")
        
        with col3:
            # Determine status based on success rate
            if success_rate >= 80:
                status = "excellent"
            elif success_rate >= 60:
                status = "good"
            elif success_rate >= 40:
                status = "warning"
            else:
                status = "critical"
            create_metric_card(f"{success_rate:.1f}%", "Success Rate", status)
        
        with col4:
            create_metric_card(f"{avg_success_score:.1f}/10", "Avg Success Score")
        
        # Success distribution
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_metric_card(f"{excellent}", "🏆 Excellent (≥9.0)", "excellent")
        
        with col2:
            create_metric_card(f"{very_good}", "⭐ Very Good (8.0-8.9)", "good")
        
        with col3:
            create_metric_card(f"{good}", "✅ Good (7.5-7.9)", "warning")
        
        # Success distribution chart with tier coloring
        if success_pages > 0:
            success_data = filtered_df[filtered_df['avg_score'] >= success_threshold].copy()
            
            # Add tier names for better display
            success_data['tier_name'] = success_data['tier'].apply(lambda x: x.replace('_', ' ').title() if pd.notna(x) else 'Unknown')
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Score distribution histogram
                fig_dist = px.histogram(
                    success_data,
                    x='avg_score',
                    nbins=20,
                    title="Success Score Distribution",
                    color_discrete_sequence=['#10b981']
                )
                fig_dist.update_layout(height=300)
                st.plotly_chart(fig_dist, use_container_width=True)
            
            with col2:
                # Success by tier
                if 'tier' in success_data.columns:
                    tier_success_counts = success_data.groupby('tier_name').size().reset_index(name='count')
                    
                    fig_tier = px.pie(
                        tier_success_counts,
                        values='count',
                        names='tier_name',
                        title="Success Stories by Content Tier"
                    )
                    fig_tier.update_layout(height=300)
                    st.plotly_chart(fig_tier, use_container_width=True)
            
            # Tier performance breakdown
            st.markdown("### 🏗️ Success Performance by Content Tier")
            if 'tier' in success_data.columns:
                tier_summary = success_data.groupby('tier_name').agg({
                    'avg_score': ['count', 'mean', 'max', 'min']
                }).round(2)
                
                tier_summary.columns = ['Count', 'Avg Score', 'Max Score', 'Min Score']
                tier_summary = tier_summary.sort_values('Avg Score', ascending=False)
                
                # Display tier summary
                for tier_name, row in tier_summary.iterrows():
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        create_metric_card(f"{int(row['Count'])}", f"{tier_name} Stories")
                    with col2:
                        # Determine status based on avg score
                        avg_score = row['Avg Score']
                        if avg_score >= 8.0:
                            status = "excellent"
                        elif avg_score >= 7.5:
                            status = "good"
                        elif avg_score >= 7.0:
                            status = "warning"
                        else:
                            status = "critical"
                        create_metric_card(f"{avg_score:.1f}/10", "Avg Score", status)
                    with col3:
                        create_metric_card(f"{row['Max Score']:.1f}/10", "Best Score")
                    with col4:
                        create_metric_card(f"{row['Min Score']:.1f}/10", "Lowest Score")

def apply_success_filters(master_df):
    """Apply selected filters to the success dataset"""
    filtered_df = master_df.copy()
    
    # Persona filter
    if st.session_state.get('success_persona_filter', 'All') != 'All':
        filtered_df = filtered_df[filtered_df['persona_id'] == st.session_state['success_persona_filter']]
    
    # Tier filter
    if st.session_state.get('success_tier_filter', 'All') != 'All':
        filtered_df = filtered_df[filtered_df['tier'] == st.session_state['success_tier_filter']]
    
    return filtered_df

def display_success_stories_detailed(metrics_calc, master_df):
    """Display detailed success stories analysis (from Page Performance page)"""
    st.markdown("## 🏆 Detailed Success Stories")
    
    # Apply filters and get success stories
    filtered_df = apply_success_filters(master_df)
    success_threshold = st.session_state.get('success_threshold', 7.7)
    max_stories = st.session_state.get('max_success_stories', 10)
    
    if 'avg_score' in filtered_df.columns:
        # AGGREGATE TO PAGE LEVEL to avoid duplicates and get richer data
        page_success = filtered_df[filtered_df['avg_score'] >= success_threshold].groupby('page_id').agg({
            'avg_score': 'mean',  # Average score across all criteria for this page
            'tier': 'first',
            'tier_name': 'first',
            'url': 'first',
            'url_slug': 'first',
            'persona_id': 'first',
            # Experience metrics
            'overall_sentiment': 'first',
            'engagement_level': 'first', 
            'conversion_likelihood': 'first',
            # Content examples for concrete evidence
            'effective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
            'ineffective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
            # Evidence and analysis
            'evidence': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip()])[:500],
            'business_impact_analysis': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:300],
            'trust_credibility_assessment': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200],
            'information_gaps': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200]
        }).reset_index()
        
        # Filter to keep only pages that still meet the success threshold after aggregation
        success_stories = page_success[page_success['avg_score'] >= success_threshold].sort_values('avg_score', ascending=False)
        
        if success_stories.empty:
            st.warning(f"⚠️ No pages score above {success_threshold:.1f} with current filters.")
            return
        
        # Limit to max stories
        success_stories = success_stories.head(max_stories)
        
        st.success(f"🎉 Found {len(success_stories)} success stories above {success_threshold:.1f}")
        
        # Group success stories by tier for better organization
        stories_by_tier = {}
        for _, story in success_stories.iterrows():
            tier = story.get('tier', 'Unknown')
            tier_name = story.get('tier_name', tier.replace('_', ' ').title()) if pd.notna(story.get('tier_name')) else tier.replace('_', ' ').title()
            
            if tier not in stories_by_tier:
                stories_by_tier[tier] = {
                    'name': tier_name,
                    'stories': []
                }
            stories_by_tier[tier]['stories'].append(story)
        
        # Display success stories grouped by tier
        overall_rank = 1
        for tier, tier_data in stories_by_tier.items():
            tier_name = tier_data['name']
            tier_stories = tier_data['stories']
            
            # Tier header with summary
            tier_avg_score = sum(story.get('avg_score', 0) for story in tier_stories) / len(tier_stories)
            tier_max_score = max(story.get('avg_score', 0) for story in tier_stories)
            
            st.markdown(f"""
            ## 🏗️ {tier_name} Success Stories ({len(tier_stories)} stories)
            **Avg Score:** {tier_avg_score:.1f}/10 | **Best Score:** {tier_max_score:.1f}/10
            """)
            
            # Display success stories within this tier
            for tier_rank, story in enumerate(tier_stories, 1):
                display_success_story_card(overall_rank, story, master_df, tier_rank=tier_rank, tier_name=tier_name)
                overall_rank += 1
            
            # Add separator between tiers
            if tier != list(stories_by_tier.keys())[-1]:  # Not the last tier
                st.markdown("---")

def display_success_story_card(rank, story, master_df, tier_rank=None, tier_name=None):
    """Display individual success story card"""
    page_id = story.get('page_id', 'Unknown')
    score = story.get('avg_score', 0)
    tier = story.get('tier', 'Unknown')
    persona = story.get('persona_id', 'Unknown')
    url = story.get('url', '')
    
    # Create friendly page title
    page_title = create_friendly_page_title(page_id, url)
    
    # Determine excellence level
    if score >= 9.0:
        excellence_level = "🏆 EXCELLENT"
        card_class = "success-excellent"
    elif score >= 8.0:
        excellence_level = "⭐ VERY GOOD"
        card_class = "success-good"
    elif score >= 7.5:
        excellence_level = "✅ GOOD"
        card_class = "success-card"
    else:
        excellence_level = "📈 IMPROVING"
        card_class = "success-improving"
    
    # Create title with tier context
    if tier_rank and tier_name:
        title = f"#{rank} ({tier_name} #{tier_rank}) - {page_title} ({excellence_level})"
    else:
        title = f"#{rank} - {page_title} ({excellence_level})"
    
    with st.expander(title, expanded=(rank <= 3)):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"#### {page_title}")
        with col2:
            create_metric_card(excellence_level, "Excellence Level", "excellent")
        
        col1, col2, col3, col4 = create_four_column_layout()
        
        with col1:
            create_metric_card(f"{score:.1f}/10", "Success Score", status="success")
        
        with col2:
            create_metric_card(tier, "Content Tier", status="info")
        
        with col3:
            create_metric_card(persona, "Persona", status="info")
        
        with col4:
            # Calculate percentile using master_df
            if 'avg_score' in master_df.columns:
                percentile = (master_df['avg_score'] < score).mean() * 100
                create_metric_card(f"{percentile:.0f}th", "Percentile", status="info")
            else:
                create_metric_card("N/A", "Percentile", status="info")
        
        # Rich Evidence section - show comprehensive supporting data (aligned with Opportunity page)
        st.markdown("### 📋 Success Evidence & Analysis")
        
        # Experience Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            sentiment = story.get('overall_sentiment', 'Unknown')
            sentiment_color = "🟢" if sentiment == "Positive" else "🟡" if sentiment == "Neutral" else "🔴"
            st.markdown(f"**{sentiment_color} Sentiment:** {sentiment}")
        
        with col2:
            engagement = story.get('engagement_level', 'Unknown')
            engagement_color = "🟢" if engagement == "High" else "🟡" if engagement == "Medium" else "🔴"
            st.markdown(f"**{engagement_color} Engagement:** {engagement}")
        
        with col3:
            conversion = story.get('conversion_likelihood', 'Unknown')
            conversion_color = "🟢" if conversion == "High" else "🟡" if conversion == "Medium" else "🔴"
            st.markdown(f"**{conversion_color} Conversion:** {conversion}")
        
        # Content Examples - What's Working vs What Could Improve
        col1, col2 = st.columns(2)
        
        with col1:
            effective_examples = story.get('effective_copy_examples', '')
            if effective_examples and len(str(effective_examples).strip()) > 20:
                create_success_alert("✅ What's Working Exceptionally Well:")
                
                # Extract persona voice quotes
                persona_quotes = extract_persona_quotes_success(str(effective_examples))
                if persona_quotes:
                    st.markdown("**💬 Persona Voice:**")
                    for quote in persona_quotes[:2]:  # Show top 2 quotes
                        st.success(f"*\"{quote}\"*")
                    
                    # Show full text in expander
                    with st.expander("📋 Full Success Analysis"):
                        st.markdown(f"*{str(effective_examples).strip()}*")
                else:
                    st.markdown(f"*{str(effective_examples).strip()}*")
            else:
                create_success_alert("✅ Success Elements: This page demonstrates strong overall performance worth replicating")
        
        with col2:
            ineffective_examples = story.get('ineffective_copy_examples', '')
            if ineffective_examples and len(str(ineffective_examples).strip()) > 20:
                create_warning_alert("⚠️ Areas for Enhancement:")
                st.markdown(f"*{str(ineffective_examples).strip()}*")
            else:
                create_info_alert("💡 Optimization Potential: Even successful pages can be further optimized")
        
        # Success Insights & Business Impact
        trust_assessment = story.get('trust_credibility_assessment', '')
        business_impact = story.get('business_impact_analysis', '')
        
        if trust_assessment and len(str(trust_assessment).strip()) > 10:
            create_success_alert(f"🔒 Trust & Credibility Strengths: {str(trust_assessment).strip()}")
        
        if business_impact and len(str(business_impact).strip()) > 10:
            create_info_alert(f"💼 Business Impact & Value: {str(business_impact).strip()}")
        
        # General Evidence (fallback)
        general_evidence = story.get('evidence', '')
        if general_evidence and len(str(general_evidence).strip()) > 10:
            create_success_alert(f"🔍 Additional Success Factors: {str(general_evidence).strip()}")
        
        # URL and additional info
        if url:
            st.markdown(f"**🔗 URL:** {url}")
        
        # Apply pattern buttons (aligned with Opportunity page style)
        st.markdown("### 🚀 Replicate This Success")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<a href="#" class="action-button">📋 Create Template</a>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<a href="#" class="action-button">🔍 Analyze Pattern</a>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<a href="#" class="action-button">📊 Compare Similar</a>', unsafe_allow_html=True)

def create_friendly_page_title(page_id, url):
    """Create a friendly page title from page ID and URL"""
    if url and url.strip():
        # Extract meaningful part from URL
        url_parts = url.replace('https://', '').replace('http://', '').split('/')
        if len(url_parts) > 1:
            # Get the last meaningful part
            meaningful_part = url_parts[-1] if url_parts[-1] else url_parts[-2]
            return meaningful_part.replace('-', ' ').replace('_', ' ').title()
    
    return page_id

def display_key_strengths(story):
    """Display key strengths analysis for a success story"""
    st.markdown("#### ✨ Key Strengths")
    
    # Find available numeric criteria columns
    criteria_cols = [col for col in story.index if col in [
        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
    ]]
    
    if criteria_cols:
        # Get top performing criteria - only include numeric values
        criteria_scores = {}
        for col in criteria_cols:
            if pd.notna(story[col]):
                try:
                    # Convert to float to ensure numeric comparison
                    score = float(story[col])
                    criteria_scores[col] = score
                except (ValueError, TypeError):
                    # Skip non-numeric values
                    continue
        
        if criteria_scores:
            top_criteria = sorted(criteria_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        else:
            top_criteria = []
        
        for criteria, score in top_criteria:
            if score >= 7.0:  # Only show strong criteria
                criteria_name = criteria.replace('_', ' ').title()
                st.markdown(f'<span class="strength-badge">{criteria_name}: {score:.1f}</span>', unsafe_allow_html=True)
    else:
        st.info("💡 Detailed criteria scores not available for strength analysis.")

def display_evidence_section(story):
    """Display evidence section for a success story"""
    st.markdown("#### 📋 Evidence & Examples")
    
    # Look for evidence columns
    evidence_cols = [col for col in story.index if any(keyword in col.lower() for keyword in ['evidence', 'example', 'copy', 'text', 'content'])]
    
    if evidence_cols:
        for col in evidence_cols:
            if pd.notna(story[col]) and str(story[col]).strip():
                st.markdown(f"""
                <div class="evidence-section">
                    <strong>{col.replace('_', ' ').title()}:</strong><br>
                    <div class="copy-example">
                        {story[col]}
                        <div class="copy-button">📋 Copy</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 No specific evidence examples available for this success story.")

def display_pattern_analysis(master_df):
    """Display pattern analysis across success stories"""
    st.markdown("## 🔍 Success Pattern Analysis")
    
    # Apply filters
    filtered_df = apply_success_filters(master_df)
    success_threshold = st.session_state.get('success_threshold', 7.7)
    
    if 'avg_score' in filtered_df.columns:
        success_stories = filtered_df[filtered_df['avg_score'] >= success_threshold]
        
        if success_stories.empty:
            st.info("📊 No success stories available for pattern analysis.")
            return
        
        # Analyze patterns
        display_tier_patterns(success_stories)
        display_persona_patterns(success_stories)
        display_criteria_patterns(success_stories)

def display_tier_patterns(success_stories):
    """Display tier-based success patterns"""
    st.markdown("### 🏗️ Success Patterns by Content Tier")
    
    if 'tier' in success_stories.columns:
        tier_success = success_stories.groupby('tier').agg({
            'avg_score': ['mean', 'count'],
            'page_id': 'count'
        }).round(2)
        
        tier_success.columns = ['avg_score', 'score_count', 'total_pages']
        tier_success = tier_success.sort_values('avg_score', ascending=False)
        
        for tier, data in tier_success.iterrows():
            st.markdown(f"""
            <div class="pattern-card">
                <strong>🏗️ {tier} Content Pattern</strong><br>
                Average Success Score: {data['avg_score']:.1f}/10<br>
                Success Stories: {data['total_pages']} pages<br>
                <span class="pattern-tag">Tier Pattern</span>
            </div>
            """, unsafe_allow_html=True)

def display_persona_patterns(success_stories):
    """Display persona-based success patterns"""
    st.markdown("### 👥 Success Patterns by Persona")
    
    if 'persona_id' in success_stories.columns:
        persona_success = success_stories.groupby('persona_id').agg({
            'avg_score': ['mean', 'count']
        }).round(2)
        
        persona_success.columns = ['avg_score', 'success_count']
        persona_success = persona_success.sort_values('avg_score', ascending=False)
        
        for persona, data in persona_success.iterrows():
            st.markdown(f"""
            <div class="pattern-card">
                <strong>👤 {persona} Success Pattern</strong><br>
                Average Success Score: {data['avg_score']:.1f}/10<br>
                Success Stories: {data['success_count']} pages<br>
                <span class="pattern-tag">Persona Pattern</span>
            </div>
            """, unsafe_allow_html=True)

def display_criteria_patterns(success_stories):
    """Display criteria-based success patterns"""
    st.markdown("### 🎯 Success Patterns by Criteria")
    
    # Find available numeric criteria columns
    criteria_cols = [col for col in success_stories.columns if col in [
        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
    ]]
    
    if criteria_cols:
        # Calculate average criteria scores for success stories
        criteria_averages = success_stories[criteria_cols].mean().sort_values(ascending=False)
        
        st.markdown("#### 🏆 Top Performing Criteria in Success Stories")
        
        for i, (criteria, score) in enumerate(criteria_averages.head(5).items(), 1):
            criteria_name = criteria.replace('_', ' ').title()
            st.markdown(f"""
            <div class="pattern-card">
                <strong>#{i} - {criteria_name}</strong><br>
                Average Score in Success Stories: {score:.1f}/10<br>
                <span class="pattern-tag">Criteria Pattern</span>
            </div>
            """, unsafe_allow_html=True)

def display_evidence_browser(master_df):
    """Display comprehensive evidence browser (from Evidence Explorer page)"""
    st.markdown("## 🔍 Evidence Browser")
    
    # Apply filters
    filtered_df = apply_success_filters(master_df)
    success_threshold = st.session_state.get('success_threshold', 7.7)
    
    if 'avg_score' in filtered_df.columns:
        success_stories = filtered_df[filtered_df['avg_score'] >= success_threshold]
        
        if success_stories.empty:
            st.info("📊 No success stories available for evidence browsing.")
            return
        
        # Evidence browsing controls
        st.markdown("### 🎛️ Evidence Browser Controls")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Evidence type filter
            evidence_types = ['All', 'Copy Examples', 'Design Elements', 'User Feedback', 'Performance Data']
            selected_evidence_type = st.selectbox(
                "📋 Evidence Type",
                evidence_types,
                key="evidence_type_filter"
            )
        
        with col2:
            # Search functionality
            search_term = st.text_input(
                "🔍 Search Evidence",
                key="evidence_search",
                placeholder="Search for specific words or phrases..."
            )
        
        # Display evidence
        display_evidence_results(success_stories, selected_evidence_type, search_term)

def display_evidence_results(success_stories, evidence_type, search_term):
    """Display filtered evidence results"""
    st.markdown("### 📋 Evidence Results")
    
    evidence_found = False
    
    for _, story in success_stories.iterrows():
        page_title = create_friendly_page_title(story.get('page_id', 'Unknown'), story.get('url', ''))
        score = story.get('avg_score', 0)
        
        # Look for evidence in the story
        evidence_items = extract_evidence_items(story, evidence_type, search_term)
        
        if evidence_items:
            evidence_found = True
            
            with st.expander(f"📋 {page_title} - Score: {score:.1f}"):
                for evidence in evidence_items:
                    st.markdown(f"""
                    <div class="evidence-section">
                        <strong>{evidence['type']}:</strong><br>
                        <div class="copy-example">
                            {evidence['content']}
                            <div class="copy-button">📋 Copy</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    if not evidence_found:
        st.info("🔍 No evidence found matching the selected criteria. Try adjusting the filters.")

def extract_evidence_items(story, evidence_type, search_term):
    """Extract evidence items from a success story"""
    evidence_items = []
    
    # Look for evidence in various columns
    for col in story.index:
        if pd.notna(story[col]) and str(story[col]).strip():
            content = str(story[col]).strip()
            
            # Apply search term filter
            if search_term and search_term.lower() not in content.lower():
                continue
            
            # Categorize evidence
            evidence_category = categorize_evidence(col, content)
            
            # Apply evidence type filter
            if evidence_type != 'All' and evidence_category != evidence_type:
                continue
            
            evidence_items.append({
                'type': evidence_category,
                'content': content[:500] + '...' if len(content) > 500 else content  # Truncate long content
            })
    
    return evidence_items

def categorize_evidence(column_name, content):
    """Categorize evidence based on column name and content"""
    col_lower = column_name.lower()
    
    if any(keyword in col_lower for keyword in ['copy', 'text', 'content', 'headline', 'description']):
        return 'Copy Examples'
    elif any(keyword in col_lower for keyword in ['design', 'visual', 'image', 'layout']):
        return 'Design Elements'
    elif any(keyword in col_lower for keyword in ['feedback', 'comment', 'review', 'impression']):
        return 'User Feedback'
    elif any(keyword in col_lower for keyword in ['performance', 'metric', 'score', 'conversion']):
        return 'Performance Data'
    else:
        return 'Other Evidence'

def display_replication_guide(metrics_calc, master_df):
    """Display comprehensive replication guide"""
    st.markdown("## 🔄 Success Replication Guide")
    
    # Apply filters
    filtered_df = apply_success_filters(master_df)
    success_threshold = st.session_state.get('success_threshold', 7.7)
    
    if 'avg_score' in filtered_df.columns:
        success_stories = filtered_df[filtered_df['avg_score'] >= success_threshold]
        
        if success_stories.empty:
            st.info("📊 No success stories available for replication guide.")
            return
        
        # Generate replication templates
        display_replication_templates(success_stories)
        
        # Success checklist
        display_success_checklist(success_stories)
        
        # Implementation roadmap
        display_implementation_roadmap(success_stories)

def display_replication_templates(success_stories):
    """Display replication templates based on success patterns"""
    st.markdown("### 📋 Replication Templates")
    
    # Group by tier to create templates
    if 'tier' in success_stories.columns:
        tier_templates = success_stories.groupby('tier').agg({
            'avg_score': 'mean'
        }).round(2)
        
        for tier, data in tier_templates.iterrows():
            st.markdown(f"""
            <div class="pattern-card">
                <h4>📋 {tier} Success Template</h4>
                <p><strong>Average Success Score:</strong> {data['avg_score']:.1f}/10</p>
                
                <h5>Key Elements to Replicate:</h5>
                <ul>
                    <li>✅ Focus on high-performing criteria patterns</li>
                    <li>✅ Maintain consistent messaging tone</li>
                    <li>✅ Implement proven design elements</li>
                    <li>✅ Apply successful content structure</li>
                </ul>
                
                <a href="#" class="apply-button">📋 Use This Template</a>
            </div>
            """, unsafe_allow_html=True)

def display_success_checklist(success_stories):
    """Display success checklist based on common patterns"""
    st.markdown("### ✅ Success Checklist")
    
    # Find available numeric criteria columns only
    criteria_cols = [col for col in success_stories.columns if col in [
        'raw_score', 'final_score', 'sentiment_numeric', 'engagement_numeric', 'conversion_numeric'
    ]]
    
    if criteria_cols:
        # Calculate average criteria scores for numeric columns only
        criteria_averages = success_stories[criteria_cols].mean().sort_values(ascending=False)
        
        st.markdown("#### 🎯 Essential Success Criteria")
        
        checklist_items = []
        for criteria, score in criteria_averages.head(5).items():
            criteria_name = criteria.replace('_', ' ').title()
            checklist_items.append(f"☐ **{criteria_name}** (Target: {score:.1f}/10)")
        
        for item in checklist_items:
            st.markdown(item)
        
        st.markdown("""
        <div class="pattern-card">
            <h4>📋 How to Use This Checklist</h4>
            <ol>
                <li>Review each criteria for your content</li>
                <li>Score your content against each criteria</li>
                <li>Focus on criteria below the target scores</li>
                <li>Use success story examples as inspiration</li>
                <li>Test and iterate based on results</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📊 Numeric criteria data not available for checklist generation.")
        
        # Provide generic checklist
        st.markdown("#### 🎯 General Success Checklist")
        generic_checklist = [
            "☐ **Clear Value Proposition** - Communicate benefits clearly",
            "☐ **Strong Headlines** - Capture attention immediately", 
            "☐ **Compelling Content** - Engage your target audience",
            "☐ **Trust Signals** - Build credibility and confidence",
            "☐ **Clear Call-to-Action** - Guide users to next steps"
        ]
        
        for item in generic_checklist:
            st.markdown(item)

def display_implementation_roadmap(success_stories):
    """Display implementation roadmap for applying success patterns"""
    st.markdown("### 🗺️ Implementation Roadmap")
    
    # Create implementation phases
    phases = [
        {
            'phase': 'Phase 1: Analysis (Week 1)',
            'tasks': [
                'Analyze top 3 success stories in detail',
                'Identify common patterns and elements',
                'Document key success criteria',
                'Create pattern templates'
            ],
            'color': '#10b981'
        },
        {
            'phase': 'Phase 2: Planning (Week 2)',
            'tasks': [
                'Select content for pattern application',
                'Prioritize by potential impact',
                'Create implementation timeline',
                'Assign responsibilities'
            ],
            'color': '#f59e0b'
        },
        {
            'phase': 'Phase 3: Implementation (Weeks 3-4)',
            'tasks': [
                'Apply success patterns to selected content',
                'Test new content variations',
                'Monitor performance metrics',
                'Iterate based on results'
            ],
            'color': '#0ea5e9'
        },
        {
            'phase': 'Phase 4: Optimization (Week 5+)',
            'tasks': [
                'Analyze results and performance',
                'Refine patterns based on data',
                'Scale successful implementations',
                'Update success library'
            ],
            'color': '#8b5cf6'
        }
    ]
    
    for phase in phases:
        task_list = ''.join([f"<li>{task}</li>" for task in phase['tasks']])
        create_pattern_card(f"""
            <h4>{phase['phase']}</h4>
            <ul>
                {task_list}
            </ul>
        """)

if __name__ == "__main__":
    main() 