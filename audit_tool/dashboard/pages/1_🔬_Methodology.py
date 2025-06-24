import streamlit as st
import sys
from pathlib import Path
import yaml
import os

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

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
    create_content_card,
    create_two_column_layout,
    create_divider
)

# Page configuration
st.set_page_config(
    page_title="Methodology",
    page_icon="🔬",
    layout="wide"
)

# Apply the single source of truth for styling
apply_perfect_styling()

# --- Main Page ---
create_main_header("🔬 Methodology", "How we evaluate brand health across digital touchpoints")

# Load methodology data
methodology_path = project_root / "audit_tool" / "config" / "methodology.yaml"
try:
    with open(methodology_path, 'r') as file:
        methodology = yaml.safe_load(file)
except FileNotFoundError:
    create_error_alert(f"FATAL: Methodology file not found at {methodology_path}")
    st.stop()
except Exception as e:
    create_error_alert(f"Error loading or parsing methodology YAML: {e}")
    st.stop()

# Create tabs as per the functional specification
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview", 
    "Scoring Framework", 
    "Page Classification",
    "Tier Criteria",
    "Brand Standards",
    "Quality Controls"
])

# --- Tab 1: Overview ---
with tab1:
    create_section_header("Brand Health Audit Methodology")

    metadata = methodology.get('metadata', {})
    calculation = methodology.get('calculation', {})
    
    if metadata:
        st.info(f"""
        **{metadata.get('name', 'Brand Audit Methodology')}** (Version {metadata.get('version', 'N/A')})
        
        Last Updated: {metadata.get('last_updated', 'N/A')}
        
        *{metadata.get('description', '' )}*
        """)

    if calculation:
        create_subsection_header("Brand Score Calculation")
        formula = calculation.get('formula', 'Not specified')
        onsite_weight = calculation.get('onsite_weight', 0) * 100
        offsite_weight = calculation.get('offsite_weight', 0) * 100

        st.info(f"""
        **Formula:** `{formula}`
        - **Onsite Weight:** {onsite_weight:.0f}% (Your website and digital properties)
        - **Offsite Weight:** {offsite_weight:.0f}% (Third-party platforms and reviews)
        - **Crisis Impact:** Can reduce overall score by up to 70%.
        """)

    crisis_multipliers = calculation.get('crisis_multipliers', {})
    if crisis_multipliers:
        create_subsection_header("Crisis Impact Multipliers")
        st.info("Reputation issues can significantly impact your overall brand health score.")
        
        for crisis_type, multiplier in crisis_multipliers.items():
            reduction = (1 - multiplier) * 100
            message = f"**{crisis_type.replace('_', ' ').title()}:** {multiplier}x multiplier ({reduction:.0f}% reduction)"
            if multiplier < 0.9:
                st.error(message)
            elif multiplier < 1.0:
                st.warning(message)
            else:
                st.success(message)

    create_subsection_header("Audit Process")
    st.info("""
    The brand health audit follows a structured 5-stage process:
    1.  **Page Classification:** Categorize content into Tier 1 (Brand), Tier 2 (Value Prop), or Tier 3 (Functional).
    2.  **Criteria Assessment:** Apply tier-specific scoring criteria with appropriate brand/performance weightings.
    3.  **Evidence Collection:** Gather verbatim quotes and specific examples to support all scores.
    4.  **Brand Consistency Check:** Validate messaging hierarchy, visual identity, and approved content usage.
    5.  **Strategic Recommendations:** Prioritize improvements by impact, effort, and urgency.
    """)

# --- Tab 2: Scoring Framework ---
with tab2:
    create_section_header("Scoring Framework")
    scoring = methodology.get('scoring', {})
    scale = scoring.get('scale', {})
    descriptors = scoring.get('descriptors', {})
    evidence = methodology.get('evidence', {})

    if scale:
        st.info(f"All criteria are scored on a **{scale.get('min', 0)}-{scale.get('max', 10)} scale** with mandatory evidence requirements.")

    if descriptors:
        create_subsection_header("Score Interpretation")
        for score_range, details in descriptors.items():
            content = f"**{score_range}: {details.get('label', '')}**\n\n{details.get('status', '')}"
            color = details.get('color', 'info')
            if 'red' in color:
                st.error(content)
            elif 'orange' in color or 'yellow' in color:
                st.warning(content)
            elif 'green' in color:
                st.success(content)
            else:
                st.info(content)

    if evidence:
        create_subsection_header("Evidence Requirements")
        high_scores = evidence.get('high_scores', {})
        low_scores = evidence.get('low_scores', {})
        
        col1, col2 = create_two_column_layout()
        with col1:
            st.success(f"""
            **High Scores (≥7)**
            - **Requirement:** {high_scores.get('requirement', '')}
            - **Penalty:** {high_scores.get('penalty', '')}
            """)
        with col2:
            st.error(f"""
            **Low Scores (≤4)**
            - **Requirement:** {low_scores.get('requirement', '')}
            - **Penalty:** {low_scores.get('penalty', '')}
            """)

# --- Tab 3: Page Classification ---
with tab3:
    create_section_header("Page Classification System")
    classification = methodology.get('classification', {})
    onsite = classification.get('onsite', {})
    offsite = classification.get('offsite', {})

    st.info("Every page is classified into one of three tiers, each with different brand/performance weightings and criteria.")

    if onsite:
        create_subsection_header("Onsite Page Tiers")
        for tier_key, tier_data in onsite.items():
            with st.expander(f"**{tier_key.replace('_', ' ').title()}:** {tier_data.get('name', '')}"):
                col1, col2 = create_two_column_layout()
                with col1:
                    create_metric_card(f"{tier_data.get('brand_percentage', 0)}%", "Brand Focus")
                    create_metric_card(f"{tier_data.get('performance_percentage', 0)}%", "Performance Focus")
                    create_metric_card(f"{tier_data.get('weight_in_onsite', 0)*100:.0f}%", "Weight in Onsite Score")
                with col2:
                    st.markdown("**Classification Triggers:**")
                    for trigger in tier_data.get('triggers', []):
                        st.markdown(f"- {trigger}")
                    st.markdown("**Examples:**")
                    for example in tier_data.get('examples', []):
                        st.markdown(f"- {example}")

    if offsite:
        create_subsection_header("Offsite Channel Classification")
        for channel_key, channel_data in offsite.items():
            with st.expander(f"**{channel_data.get('name', '')}**"):
                st.metric("Weight in Offsite Score", f"{channel_data.get('weight_in_offsite', 0)*100:.0f}%")
                st.markdown("**Examples:**")
                for example in channel_data.get('examples', []):
                    st.markdown(f"- {example}")

# --- Tab 4: Tier Criteria ---
with tab4:
    create_section_header("Tier-Specific Criteria")
    criteria = methodology.get('criteria', {})
    
    for tier_key, tier_criteria in criteria.items():
        with st.expander(f"**{tier_key.replace('_', ' ').title()} Criteria**"):
            brand_criteria = tier_criteria.get('brand_criteria', {})
            performance_criteria = tier_criteria.get('performance_criteria', {})

            if brand_criteria:
                create_subsection_header("Brand Criteria")
                for crit_key, crit_data in brand_criteria.items():
                    st.markdown(f"**{crit_key.replace('_', ' ').title()}** ({crit_data.get('weight', 0)}%)")
                    st.caption(crit_data.get('description', ''))
                    for req in crit_data.get('requirements', []):
                        st.markdown(f"- {req}")
                    create_divider()

            if performance_criteria:
                create_subsection_header("Performance Criteria")
                for crit_key, crit_data in performance_criteria.items():
                    st.markdown(f"**{crit_key.replace('_', ' ').title()}** ({crit_data.get('weight', 0)}%)")
                    st.caption(crit_data.get('description', ''))
                    for req in crit_data.get('requirements', []):
                        st.markdown(f"- {req}")
                    create_divider()

# --- Tab 5: Brand Standards ---
with tab5:
    create_section_header("Brand Standards & Messaging")
    messaging = methodology.get('messaging', {})
    
    if messaging:
        hierarchy = messaging.get('corporate_hierarchy', {})
        if hierarchy:
            create_subsection_header("Brand Messaging Hierarchy")
            create_content_card(f"""
            **Global Corporate Positioning:** "{hierarchy.get('global', '')}"
            
            **Regional Narrative (BENELUX):** "{hierarchy.get('regional', '')}"
            """)
        
        sub_narratives = hierarchy.get('sub_narratives', {})
        if sub_narratives:
            create_subsection_header("Sub-Narratives by Domain")
            sub_narrative_content = ""
            for domain, narrative in sub_narratives.items():
                sub_narrative_content += f'- **{domain.replace("_", " ").title()}:** "{narrative}"\n'
            create_content_card(sub_narrative_content)

        value_props = messaging.get('value_propositions', [])
        if value_props:
            create_subsection_header("Approved Value Propositions")
            vp_content = ""
            for prop in value_props:
                vp_content += f"- {prop}\n"
            create_content_card(vp_content)

        ctas = messaging.get('strategic_ctas', [])
        if ctas:
            create_subsection_header("Approved Strategic CTAs")
            cta_content = ""
            for cta in ctas:
                cta_content += f"- {cta}\n"
            create_content_card(cta_content)

# --- Tab 6: Quality Controls ---
with tab6:
    create_section_header("Quality Controls & Validation")
    gating_rules = methodology.get('gating_rules', {})
    quality_penalties = methodology.get('quality_penalties', {})

    if gating_rules:
        create_subsection_header("Hard Gating Rules (Non-Negotiable)")
        st.info("These rules automatically trigger score penalties and cannot be overridden.")
        for rule_key, rule_data in gating_rules.items():
            message = f"""
            **Trigger:** {rule_data.get('trigger', '')}
            
            **Penalty:** {rule_data.get('penalty', '')}
            """
            severity = rule_data.get('severity', 'MEDIUM')
            if severity == 'CRITICAL':
                st.error(f"**{rule_key.replace('_', ' ').title()}**\n\n{message}")
            else:
                st.warning(f"**{rule_key.replace('_', ' ').title()}**\n\n{message}")
    
    if quality_penalties:
        create_subsection_header("Copy Quality Penalties")
        for penalty_key, penalty_data in quality_penalties.items():
            with st.expander(f"**{penalty_key.replace('_', ' ').title()}:** {penalty_data.get('penalty', '0 points')}"):
                st.caption(penalty_data.get('description', ''))
                if 'examples' in penalty_data:
                    for ex in penalty_data.get('examples', []):
                        st.markdown(f"- {ex}")

create_divider()
create_info_alert("This methodology is continuously updated based on market research and client feedback.") 