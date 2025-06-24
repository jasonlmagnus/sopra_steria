import streamlit as st
import yaml
import os
from pathlib import Path
import pandas as pd
import json

# Set page config
st.set_page_config(
    page_title="Brand Health Command Center - Methodology",
    page_icon="🔬",
    layout="wide"
)

# Load Google Fonts and Custom CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    /* Brand Health Command Center Styles */
    :root {
        --primary-color: #E85A4F;
        --primary-hover: #d44a3a;
        --secondary-color: #2C3E50;
        --gray-border: #D1D5DB;
        --background: #FFFFFF;
        --text-selection: #E85A4F;
        --green-status: #34c759;
        --yellow-status: #ffb800;
        --red-status: #ff3b30;
        --orange-status: #ff9500;
        --font-primary: "Inter", sans-serif;
        --font-serif: "Crimson Text", serif;
    }
    
    /* Global Typography */
    .main .block-container {
        font-family: var(--font-primary);
        font-weight: 400;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        font-weight: 600;
    }
    
    /* Text Selection */
    ::selection {
        background-color: var(--text-selection);
        color: white;
    }
    
    .insights-box {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid var(--gray-border);
        margin: 1rem 0;
        font-family: var(--font-primary);
    }
    
    .insights-box h4 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 1rem;
    }
    
    .tier-card {
        background: var(--background);
        border: 2px solid var(--gray-border);
        padding: 20px;
        margin: 15px 0;
        border-radius: 8px;
        font-family: var(--font-primary);
    }
    
    .tier-card h4 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 1rem;
    }
    
    .channel-card {
        background: var(--background);
        border: 1px solid var(--gray-border);
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
        font-family: var(--font-primary);
    }
    
    .channel-card h5 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 0.5rem;
    }
    
    .evidence-requirement {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--gray-border);
        margin: 1rem 0;
        font-family: var(--font-primary);
    }
    
    .evidence-requirement h5 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 0.5rem;
    }
    
    .messaging-hierarchy {
        font-family: var(--font-primary);
    }
    
    .messaging-hierarchy h5 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
    }
    
    .penalty-item {
        background: var(--background);
        border: 1px solid var(--gray-border);
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-family: var(--font-primary);
    }
    
    .penalty-item h5 {
        font-family: var(--font-serif);
        color: var(--secondary-color);
        margin-bottom: 0.5rem;
    }
    
    .footer {
        margin-top: 50px;
        padding: 20px;
        border-top: 1px solid var(--gray-border);
        text-align: center;
        color: #6c757d;
        font-family: var(--font-primary);
    }
</style>
""", unsafe_allow_html=True)

# Title with icon
st.title("🔬 Methodology")

# Load methodology data
methodology_path = os.path.join(Path(__file__).parent.parent.parent, "config", "methodology.yaml")
with open(methodology_path, 'r') as file:
    methodology = yaml.safe_load(file)

# Create tabs - updated to reflect actual methodology structure
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", 
    "Scoring Framework", 
    "Page Classification",
    "Tier Criteria",
    "Brand Standards",
    "Quality Controls"
])

with tab1:
    st.header("Brand Health Audit Methodology")
    
    # Get metadata
    metadata = methodology.get('metadata', {})
    
    st.markdown(f"""
    <div class="insights-box">
        <h4>{metadata.get('name', 'Brand Audit Methodology')}</h4>
        <p><strong>Version:</strong> {metadata.get('version', 'N/A')} | <strong>Updated:</strong> {metadata.get('updated', 'N/A')}</p>
        <p><strong>Corporate Tagline:</strong> "{metadata.get('tagline', 'The world is how we shape it')}"</p>
        <p>{metadata.get('description', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Core Formula
    calculation = methodology.get('calculation', {})
    
    st.markdown(f"""
    <div class="insights-box">
        <h4>Brand Score Calculation</h4>
        <p><strong>Formula:</strong> <code>{calculation.get('formula', '')}</code></p>
        <ul>
            <li><strong>Onsite Weight:</strong> {calculation.get('onsite_weight', 0.7)*100}% (Your website and digital properties)</li>
            <li><strong>Offsite Weight:</strong> {calculation.get('offsite_weight', 0.3)*100}% (Third-party platforms and reviews)</li>
            <li><strong>Crisis Impact:</strong> Can reduce overall score by up to 70%</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Crisis Multipliers
    crisis_multipliers = calculation.get('crisis_multipliers', {})
    
    st.markdown("""
    <div class="insights-box">
        <h4>Crisis Impact Multipliers</h4>
        <p>Reputation issues can significantly impact your overall brand health score:</p>
    </div>
    """, unsafe_allow_html=True)
    
    for crisis_type, multiplier in crisis_multipliers.items():
        reduction = (1 - multiplier) * 100
        status_color = "green" if multiplier == 1.0 else "orange" if multiplier >= 0.9 else "red"
        
        st.markdown(f"""
        <div class="crisis-multiplier" style="border-left: 4px solid {status_color}; padding: 10px; margin: 5px 0;">
            <strong>{crisis_type.replace('_', ' ').title()}:</strong> {multiplier} multiplier 
            {f'({reduction:.0f}% reduction)' if reduction > 0 else '(no reduction)'}
        </div>
        """, unsafe_allow_html=True)
    
    # Process Overview
    st.markdown("""
    <div class="insights-box">
        <h4>Audit Process</h4>
        <p>The brand health audit follows a structured 5-stage process:</p>
        <ol>
            <li><strong>Page Classification:</strong> Categorize content into Tier 1 (Brand), Tier 2 (Value Prop), or Tier 3 (Functional)</li>
            <li><strong>Criteria Assessment:</strong> Apply tier-specific scoring criteria with appropriate brand/performance weightings</li>
            <li><strong>Evidence Collection:</strong> Gather verbatim quotes and specific examples to support all scores</li>
            <li><strong>Brand Consistency Check:</strong> Validate messaging hierarchy, visual identity, and approved content usage</li>
            <li><strong>Strategic Recommendations:</strong> Prioritize improvements by impact, effort, and urgency</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.header("Scoring Framework")
    
    # Get scoring configuration
    scoring = methodology.get('scoring', {})
    scale = scoring.get('scale', {})
    descriptors = scoring.get('descriptors', {})
    
    st.markdown(f"""
    <div class="insights-box">
        <h4>Scoring Scale</h4>
        <p>All criteria are scored on a <strong>{scale.get('min', 0)}-{scale.get('max', 10)} scale</strong> with mandatory evidence requirements.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Score descriptors
    st.subheader("Score Interpretation")
    
    for score_range, details in descriptors.items():
        color = details.get('color', 'gray')
        status = details.get('status', '')
        label = details.get('label', '')
        
        # Map colors to CSS classes or inline styles
        color_style = {
            'red': 'background-color: #fee; border-left: 4px solid #dc3545;',
            'orange': 'background-color: #fff3cd; border-left: 4px solid #fd7e14;',
            'yellow': 'background-color: #fff3cd; border-left: 4px solid #ffc107;',
            'green': 'background-color: #d4edda; border-left: 4px solid #28a745;',
            'dark-green': 'background-color: #d4edda; border-left: 4px solid #155724;'
        }.get(color, 'background-color: #f8f9fa; border-left: 4px solid #6c757d;')
        
        st.markdown(f"""
        <div style="padding: 15px; margin: 10px 0; border-radius: 5px; {color_style}">
            <h5 style="margin: 0 0 5px 0;">{score_range}: {label}</h5>
            <p style="margin: 0;"><strong>Status:</strong> {status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Evidence Requirements
    evidence = methodology.get('evidence', {})
    
    st.subheader("Evidence Requirements")
    
    st.markdown("""
    <div class="insights-box">
        <h4>Mandatory Evidence Standards</h4>
        <p>All scores must be supported by specific evidence from the audited content:</p>
    </div>
    """, unsafe_allow_html=True)
    
    high_scores = evidence.get('high_scores', {})
    low_scores = evidence.get('low_scores', {})
    
    st.markdown(f"""
    <div class="evidence-requirement">
        <h5>High Scores (≥7)</h5>
        <p><strong>Requirement:</strong> {high_scores.get('requirement', '')}</p>
        <p><strong>Penalty:</strong> {high_scores.get('penalty', '')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="evidence-requirement">
        <h5>Low Scores (≤4)</h5>
        <p><strong>Requirement:</strong> {low_scores.get('requirement', '')}</p>
        <p><strong>Penalty:</strong> {low_scores.get('penalty', '')}</p>
    </div>
    """, unsafe_allow_html=True)

with tab3:
    st.header("Page Classification System")
    
    # Get classification data
    classification = methodology.get('classification', {})
    onsite = classification.get('onsite', {})
    
    st.markdown("""
    <div class="insights-box">
        <h4>Three-Tier Classification</h4>
        <p>Every page is classified into one of three tiers, each with different brand/performance weightings and criteria:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display each tier
    for tier_key, tier_data in onsite.items():
        tier_name = tier_data.get('name', '')
        weight_in_onsite = tier_data.get('weight_in_onsite', 0) * 100
        brand_pct = tier_data.get('brand_percentage', 0)
        perf_pct = tier_data.get('performance_percentage', 0)
        triggers = tier_data.get('triggers', [])
        examples = tier_data.get('examples', [])
        
        # --- ROBUST HTML GENERATION ---
        triggers_html = "".join(f"<li>{trigger}</li>" for trigger in triggers)
        examples_html = "".join(f"<li>{example}</li>" for example in examples)

        card_html = f"""
        <div class="tier-card" style="border: 2px solid #dee2e6; padding: 20px; margin: 15px 0; border-radius: 8px;">
            <h4>{tier_key.replace('_', ' ').title()}: {tier_name}</h4>
            <div style="display: flex; gap: 20px; margin: 10px 0;">
                <div><strong>Weight in Onsite:</strong> {weight_in_onsite:.0f}%</div>
                <div><strong>Brand Focus:</strong> {brand_pct}%</div>
                <div><strong>Performance Focus:</strong> {perf_pct}%</div>
            </div>
            <div style="margin: 15px 0;">
                <strong>Classification Triggers:</strong>
                <ul>{triggers_html}</ul>
            </div>
            <div>
                <strong>Examples:</strong>
                <ul>{examples_html}</ul>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
    
    # Offsite Classification
    offsite = classification.get('offsite', {})
    
    st.subheader("Offsite Channel Classification")
    
    for channel_key, channel_data in offsite.items():
        channel_name = channel_data.get('name', '')
        weight_in_offsite = channel_data.get('weight_in_offsite', 0) * 100
        examples = channel_data.get('examples', [])
        
        st.markdown(f"""
        <div class="channel-card" style="border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h5>{channel_name}</h5>
            <p><strong>Weight in Offsite:</strong> {weight_in_offsite:.0f}%</p>
            <p><strong>Examples:</strong> {', '.join(examples)}</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.header("Tier-Specific Criteria")
    
    # Get criteria data
    criteria = methodology.get('criteria', {})
    
    for tier_key, tier_criteria in criteria.items():
        tier_name = tier_key.replace('_', ' ').title()
        st.subheader(f"{tier_name} Criteria")
        
        # Brand criteria
        brand_criteria = tier_criteria.get('brand_criteria', {})
        if brand_criteria:
            st.markdown("**Brand Criteria:**")
            
            for criterion_key, criterion_data in brand_criteria.items():
                weight = criterion_data.get('weight', 0)
                description = criterion_data.get('description', '')
                requirements = criterion_data.get('requirements', [])
                
                with st.expander(f"{criterion_key.replace('_', ' ').title()} ({weight}%)"):
                    st.markdown(f"**Description:** {description}")
                    st.markdown("**Requirements:**")
                    for req in requirements:
                        st.markdown(f"• {req}")
        
        # Performance criteria
        performance_criteria = tier_criteria.get('performance_criteria', {})
        if performance_criteria:
            st.markdown("**Performance Criteria:**")
            
            for criterion_key, criterion_data in performance_criteria.items():
                weight = criterion_data.get('weight', 0)
                description = criterion_data.get('description', '')
                requirements = criterion_data.get('requirements', [])
                
                with st.expander(f"{criterion_key.replace('_', ' ').title()} ({weight}%)"):
                    st.markdown(f"**Description:** {description}")
                    st.markdown("**Requirements:**")
                    for req in requirements:
                        st.markdown(f"• {req}")
        
        st.markdown("---")

with tab5:
    st.header("Brand Standards & Messaging")
    
    # Get messaging data
    messaging = methodology.get('messaging', {})
    
    # Corporate Hierarchy
    corporate_hierarchy = messaging.get('corporate_hierarchy', {})
    
    st.markdown("""
    <div class="insights-box">
        <h4>Brand Messaging Hierarchy</h4>
        <p>Approved messaging elements that must be used consistently across all digital properties:</p>
    </div>
    """, unsafe_allow_html=True)
    
    # --- ROBUST HTML GENERATION ---
    global_pos = corporate_hierarchy.get('global', '')
    regional_nav = corporate_hierarchy.get('regional', '')

    messaging_html = f"""
    <div class="messaging-hierarchy">
        <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h5>Global Corporate Positioning</h5>
            <p style="font-weight: bold; color: #E85A4F;">"{global_pos}"</p>
        </div>
        <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px;">
            <h5>Regional Narrative (BENELUX)</h5>
            <p style="font-weight: bold; color: #2C3E50;">"{regional_nav}"</p>
        </div>
    </div>
    """
    st.markdown(messaging_html, unsafe_allow_html=True)
    
    # Sub-narratives
    sub_narratives = corporate_hierarchy.get('sub_narratives', {})
    
    if sub_narratives:
        st.subheader("Sub-Narratives by Domain")
        
        cols = st.columns(2)
        for i, (domain, narrative) in enumerate(sub_narratives.items()):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="border: 1px solid #dee2e6; padding: 10px; margin: 5px 0; border-radius: 5px;">
                    <strong>{domain.replace('_', ' ').title()}:</strong><br>
                    "{narrative}"
                </div>
                """, unsafe_allow_html=True)
    
    # Value Propositions
    value_props = messaging.get('value_propositions', [])
    
    if value_props:
        st.subheader("Approved Value Propositions")
        
        for prop in value_props:
            st.markdown(f"• {prop}")
    
    # Strategic CTAs
    strategic_ctas = messaging.get('strategic_ctas', [])
    
    if strategic_ctas:
        st.subheader("Approved Strategic CTAs")
        
        for cta in strategic_ctas:
            st.markdown(f"• {cta}")
    
    # BENELUX Positioning
    benelux_positioning = messaging.get('benelux_positioning', [])
    
    if benelux_positioning:
        st.subheader("BENELUX Market Positioning")
        
        for position in benelux_positioning:
            st.markdown(f"• {position}")

with tab6:
    st.header("Quality Controls & Validation")
    
    # Gating Rules
    gating_rules = methodology.get('gating_rules', {})
    
    st.subheader("Hard Gating Rules (Non-Negotiable)")
    
    st.markdown("""
    <div class="insights-box">
        <h4>Critical Quality Gates</h4>
        <p>These rules automatically trigger score penalties and cannot be overridden:</p>
    </div>
    """, unsafe_allow_html=True)
    
    for rule_key, rule_data in gating_rules.items():
        trigger = rule_data.get('trigger', '')
        penalty = rule_data.get('penalty', '')
        severity = rule_data.get('severity', '')
        
        severity_color = {
            'CRITICAL': '#dc3545',
            'HIGH': '#fd7e14',
            'MEDIUM': '#ffc107'
        }.get(severity, '#6c757d')
        
        st.markdown(f"""
        <div style="border-left: 4px solid {severity_color}; padding: 15px; margin: 10px 0; background: #f8f9fa;">
            <h5 style="margin: 0 0 5px 0; color: {severity_color};">{severity} - {rule_key.replace('_', ' ').title()}</h5>
            <p><strong>Trigger:</strong> {trigger}</p>
            <p><strong>Penalty:</strong> {penalty}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quality Penalties
    quality_penalties = methodology.get('quality_penalties', {})
    
    st.subheader("Copy Quality Penalties")
    
    for penalty_key, penalty_data in quality_penalties.items():
        points = penalty_data.get('points', 0)
        example = penalty_data.get('example', '')
        examples = penalty_data.get('examples', [])

        st.markdown(f"""
        <div class="penalty-item" style="border: 1px solid #dee2e6; padding: 10px; margin: 5px 0; border-radius: 5px;">
            <h5>{penalty_key.replace('_', ' ').title()}: {points} points</h5>
        </div>
        """, unsafe_allow_html=True)

        if example:
            st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;<strong>Example:</strong> {example}", unsafe_allow_html=True)
        
        if examples:
            st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;<strong>Examples:</strong>", unsafe_allow_html=True)
            for ex in examples:
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;• {ex}")

    # Validation Flags
    validation_flags = methodology.get('validation_flags', {})
    
    st.subheader("Validation Flags")
    
    for flag_category, flags in validation_flags.items():
        st.markdown(f"**{flag_category.title()} Flags:**")
        
        for flag_key, flag_data in flags.items():
            penalty = flag_data.get('penalty', '')
            st.markdown(f"• **{flag_key.replace('_', ' ').title()}:** {penalty}")
    
    # Examples
    examples = methodology.get('examples', {})
    
    if examples:
        st.subheader("Scoring Examples")
        
        for example_key, example_data in examples.items():
            score = example_data.get('score', 0)
            text = example_data.get('text', '')
            why_good = example_data.get('why_good', [])
            why_bad = example_data.get('why_bad', [])
            
            score_color = '#28a745' if score >= 8 else '#dc3545' if score <= 4 else '#ffc107'
            
            with st.expander(f"{example_key.replace('_', ' ').title()} (Score: {score}/10)"):
                st.markdown(f"""
                <div style="border-left: 4px solid {score_color}; padding: 10px; background: #f8f9fa;">
                    <p><strong>Example Text:</strong></p>
                    <blockquote>"{text}"</blockquote>
                </div>
                """, unsafe_allow_html=True)
                
                if why_good:
                    st.markdown("**Why this scores well:**")
                    for reason in why_good:
                        st.markdown(f"• {reason}")
                
                if why_bad:
                    st.markdown("**Why this scores poorly:**")
                    for reason in why_bad:
                        st.markdown(f"• {reason}")

# Footer
st.markdown("""
<div class="footer" style="margin-top: 50px; padding: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d;">
    <p>Brand Health Command Center • Comprehensive Audit Methodology</p>
    <p>Sopra Steria Brand Standards • "The world is how we shape it"</p>
</div>
""", unsafe_allow_html=True)
