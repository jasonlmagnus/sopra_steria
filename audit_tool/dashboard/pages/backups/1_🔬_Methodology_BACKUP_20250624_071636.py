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

import yaml
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Brand Health Command Center - Methodology",
    page_icon="🔬",
    layout="wide"
)

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

# Create standardized page header
create_main_header("🔬 Methodology", "How we evaluate brand health across digital touchpoints")

# Load methodology data
methodology_path = os.path.join(Path(__file__).parent.parent.parent, "config", "methodology.yaml")
try:
    with open(methodology_path, 'r') as file:
        methodology = yaml.safe_load(file)
except FileNotFoundError:
    st.error("Methodology configuration file not found")
    methodology = {}

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
    
    if metadata:
        st.subheader("Methodology Overview")
        version = metadata.get('version', 'Unknown')
        last_updated = metadata.get('last_updated', 'Unknown')
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Version", version)
        with col2:
            st.metric("Last Updated", last_updated)

    # Core Formula
    calculation = methodology.get('calculation', {})
    
    if calculation:
        st.subheader("Calculation Framework")
        st.write("The brand health score combines multiple factors:")
        
        # Crisis Multipliers
        crisis_multipliers = calculation.get('crisis_multipliers', {})
        
        if crisis_multipliers:
            st.subheader("Crisis Impact Multipliers")
            
            for crisis_type, multiplier in crisis_multipliers.items():
                reduction = (1 - multiplier) * 100
                status_color = "🟢" if multiplier == 1.0 else "🟡" if multiplier >= 0.9 else "🔴"
                
                st.write(f"{status_color} **{crisis_type.replace('_', ' ').title()}**: {multiplier}x multiplier ({reduction:.0f}% reduction)")

with tab2:
    st.header("Scoring Framework")
    
    # Get scoring configuration
    scoring = methodology.get('scoring', {})
    scale = scoring.get('scale', {})
    descriptors = scoring.get('descriptors', {})

    # Score descriptors
    if descriptors:
        st.subheader("Score Interpretation")
        
        for score_range, details in descriptors.items():
            color = details.get('color', 'gray')
            status = details.get('status', '')
            label = details.get('label', '')
            
            color_style = {
                'red': 'background-color: #fee; border-left: 4px solid #dc3545;',
                'orange': 'background-color: #fff3cd; border-left: 4px solid #fd7e14;',
                'yellow': 'background-color: #fff3cd; border-left: 4px solid #ffc107;',
                'green': 'background-color: #d4edda; border-left: 4px solid #28a745;',
                'dark-green': 'background-color: #d4edda; border-left: 4px solid #155724;'
            }.get(color, 'background-color: #f8f9fa; border-left: 4px solid #6c757d;')
            
            st.markdown(f"""
            <div style="padding: 1rem; margin: 0.5rem 0; border-radius: 0.5rem; {color_style}">
                <strong>{score_range}</strong>: {label} - {status}
            </div>
            """, unsafe_allow_html=True)

    # Evidence Requirements
    evidence = methodology.get('evidence', {})
    
    if evidence:
        st.subheader("Evidence Requirements")
        
        high_scores = evidence.get('high_scores', {})
        low_scores = evidence.get('low_scores', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            if high_scores:
                st.markdown("**High Score Evidence:**")
                for requirement in high_scores:
                    st.write(f"• {requirement}")
        
        with col2:
            if low_scores:
                st.markdown("**Low Score Evidence:**")
                for requirement in low_scores:
                    st.write(f"• {requirement}")

with tab3:
    st.header("Page Classification System")
    
    # Get classification data
    classification = methodology.get('classification', {})
    onsite = classification.get('onsite', {})

    if onsite:
        st.subheader("Onsite Page Tiers")
        
        # Display each tier
        for tier_key, tier_data in onsite.items():
            tier_name = tier_data.get('name', '')
            weight_in_onsite = tier_data.get('weight_in_onsite', 0) * 100
            brand_pct = tier_data.get('brand_percentage', 0)
            perf_pct = tier_data.get('performance_percentage', 0)
            triggers = tier_data.get('triggers', [])
            examples = tier_data.get('examples', [])
            
            with st.expander(f"{tier_name} ({weight_in_onsite:.0f}% of onsite score)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Brand Weight", f"{brand_pct}%")
                    st.metric("Performance Weight", f"{perf_pct}%")
                
                with col2:
                    if triggers:
                        st.markdown("**Classification Triggers:**")
                        for trigger in triggers:
                            st.write(f"• {trigger}")
                
                if examples:
                    st.markdown("**Examples:**")
                    st.write(", ".join(examples))

    # Offsite Classification
    offsite = classification.get('offsite', {})
    
    if offsite:
        st.subheader("Offsite Channel Classification")
        
        for channel_key, channel_data in offsite.items():
            channel_name = channel_data.get('name', '')
            weight_in_offsite = channel_data.get('weight_in_offsite', 0) * 100
            examples = channel_data.get('examples', [])
            
            with st.expander(f"{channel_name} ({weight_in_offsite:.0f}% of offsite score)"):
                if examples:
                    st.markdown("**Examples:**")
                    for example in examples:
                        st.write(f"• {example}")

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
                    if requirements:
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
                    if requirements:
                        st.markdown("**Requirements:**")
                        for req in requirements:
                            st.markdown(f"• {req}")
        
        st.markdown("---")

with tab5:
    st.header("Brand Standards & Messaging")
    
    # Get messaging data
    messaging = methodology.get('messaging', {})
    
    if messaging:
        # Corporate Hierarchy
        corporate_hierarchy = messaging.get('corporate_hierarchy', {})

        # Sub-narratives
        sub_narratives = corporate_hierarchy.get('sub_narratives', {})
        
        if sub_narratives:
            st.subheader("Sub-Narratives by Domain")
            
            cols = st.columns(2)
            for i, (domain, narrative) in enumerate(sub_narratives.items()):
                with cols[i % 2]:
                    st.markdown(f"**{domain}**")
                    st.write(narrative)

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
    
    if gating_rules:
        st.subheader("Hard Gating Rules (Non-Negotiable)")

        for rule_key, rule_data in gating_rules.items():
            trigger = rule_data.get('trigger', '')
            penalty = rule_data.get('penalty', '')
            severity = rule_data.get('severity', '')
            
            severity_color = {
                'CRITICAL': '🔴',
                'HIGH': '🟡',
                'MEDIUM': '🟠'
            }.get(severity, '⚪')
            
            st.markdown(f"{severity_color} **{rule_key.replace('_', ' ').title()}**")
            st.write(f"Trigger: {trigger}")
            st.write(f"Penalty: {penalty}")
            st.write("---")

    # Quality Penalties
    quality_penalties = methodology.get('quality_penalties', {})
    
    if quality_penalties:
        st.subheader("Copy Quality Penalties")
        
        for penalty_key, penalty_data in quality_penalties.items():
            penalty_name = penalty_key.replace('_', ' ').title()
            penalty_value = penalty_data.get('penalty', 0)
            description = penalty_data.get('description', '')
            
            st.markdown(f"**{penalty_name}**: -{penalty_value} points")
            if description:
                st.write(description)
            st.write("---")

# Footer
st.markdown("---")
st.markdown("*This methodology is continuously updated based on market research and client feedback.*")

