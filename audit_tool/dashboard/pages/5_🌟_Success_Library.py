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

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

# Page configuration
st.set_page_config(
    page_title="Success Library",
    page_icon="🌟",
    layout="wide"
)

# Custom CSS for Success Library
st.markdown("""
<style>
    .success-header {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .success-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #10b981;
        margin-bottom: 1rem;
    }
    
    .success-excellent {
        border-left-color: #059669;
        background: #f0fdf4;
    }
    
    .success-good {
        border-left-color: #10b981;
        background: #f0fdf4;
    }
    
    .pattern-card {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
    
    .evidence-section {
        background: #fef7cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 0.5rem 0;
    }
    
    .copy-example {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin: 0.5rem 0;
        font-family: monospace;
    }
    
    .strength-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .pattern-tag {
        background: #0ea5e9;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .apply-button {
        background: #10b981;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
    }
    
    .copy-button {
        background: #6b7280;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
        float: right;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Success Library - Comprehensive Success Analysis"""
    
    # Header
    st.markdown("""
    <div class="success-header">
        <h1>🌟 Success Library</h1>
        <p>What already works that we can emulate?</p>
        <p><em>Comprehensive success analysis and pattern replication guide</em></p>
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
            5.0, 10.0, 7.7,
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
        good = len(filtered_df[(filtered_df['avg_score'] >= success_threshold) & (filtered_df['avg_score'] < 8.0)])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pages", total_pages)
        
        with col2:
            st.metric("Success Pages", success_pages)
        
        with col3:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        
        with col4:
            st.metric("Avg Success Score", f"{avg_success_score:.1f}/10")
        
        # Success distribution
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="success-card success-excellent">
                <div class="metric-value">🏆 {excellent}</div>
                <div class="metric-label">Excellent (≥9.0)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="success-card success-good">
                <div class="metric-value">⭐ {very_good}</div>
                <div class="metric-label">Very Good (8.0-9.0)</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="success-card">
                <div class="metric-value">✅ {good}</div>
                <div class="metric-label">Good (7.7-8.0)</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Success distribution chart
        if success_pages > 0:
            success_data = filtered_df[filtered_df['avg_score'] >= success_threshold]
            
            fig_dist = px.histogram(
                success_data,
                x='avg_score',
                nbins=20,
                title="Success Score Distribution",
                color_discrete_sequence=['#10b981']
            )
            fig_dist.update_layout(height=300)
            st.plotly_chart(fig_dist, use_container_width=True)

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
        success_stories = filtered_df[filtered_df['avg_score'] >= success_threshold].sort_values('avg_score', ascending=False)
        
        if success_stories.empty:
            st.warning(f"⚠️ No pages score above {success_threshold:.1f} with current filters.")
            return
        
        # Limit to max stories
        success_stories = success_stories.head(max_stories)
        
        st.success(f"🎉 Found {len(success_stories)} success stories above {success_threshold:.1f}")
        
        # Display success stories
        for i, (_, story) in enumerate(success_stories.iterrows(), 1):
            display_success_story_card(i, story, master_df)

def display_success_story_card(rank, story, master_df):
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
    else:
        excellence_level = "✅ GOOD"
        card_class = "success-card"
    
    with st.expander(f"#{rank} - {page_title} ({excellence_level})", expanded=(rank <= 3)):
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0;">{page_title}</h4>
                <div style="background: #10b981; color: white; padding: 0.5rem; border-radius: 6px;">
                    <strong>{excellence_level}</strong>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Success Score", f"{score:.1f}/10")
        
        with col2:
            st.metric("Content Tier", tier)
        
        with col3:
            st.metric("Persona", persona)
        
        with col4:
            # Calculate percentile using master_df
            if 'avg_score' in master_df.columns:
                percentile = (master_df['avg_score'] < score).mean() * 100
                st.metric("Percentile", f"{percentile:.0f}th")
            else:
                st.metric("Percentile", "N/A")
        
        # Key strengths analysis
        display_key_strengths(story)
        
        # Evidence section
        display_evidence_section(story)
        
        # URL and additional info
        if url:
            st.markdown(f"**🔗 URL:** {url}")
        
        # Apply pattern buttons
        st.markdown("### 🚀 Apply This Success Pattern")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<a href="#" class="apply-button">📋 Create Template</a>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<a href="#" class="apply-button">🔍 Analyze Pattern</a>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<a href="#" class="apply-button">📊 Compare Similar</a>', unsafe_allow_html=True)

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
        st.markdown(f"""
        <div class="pattern-card" style="border-left-color: {phase['color']};">
            <h4 style="color: {phase['color']};">{phase['phase']}</h4>
            <ul>
        """, unsafe_allow_html=True)
        
        for task in phase['tasks']:
            st.markdown(f"<li>{task}</li>", unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 