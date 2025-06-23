"""
Persona Viewer - Deep Individual Persona Analysis
Combines persona profiles, journey analysis, and performance data for comprehensive persona insights
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import os
import re
from collections import Counter

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))

from components.data_loader import BrandHealthDataLoader
from components.brand_styling import get_complete_brand_css

# Page configuration
st.set_page_config(
    page_title="Persona Viewer",
    page_icon="👤",
    layout="wide"
)

# Apply centralized brand styling with fonts
st.markdown(get_complete_brand_css(), unsafe_allow_html=True)

# Persona name mapping
PERSONA_NAMES = {
    'P1': 'The Benelux Strategic Business Leader (C-Suite Executive)',
    'P2': 'The BENELUX Technology Innovation Leader', 
    'P3': 'The Benelux Transformation Programme Leader',
    'P4': 'The Benelux Cybersecurity Decision Maker',
    'P5': 'The Technical Influencer'
}

def load_persona_profile(persona_id):
    """Load persona profile from markdown file"""
    file_path = Path(f"audit_inputs/personas/{persona_id}.md")
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        st.error(f"Error loading persona profile: {e}")
        return None

def load_journey_analysis(persona_id):
    """Load structured journey analysis from unified journey analysis file"""
    try:
        # Load the unified journey analysis file
        file_path = Path("audit_inputs/persona_journeys/unified_journey_analysis.md")
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the journey data from the unified file
        journey_data = parse_unified_journey_data(content, persona_id)
        return journey_data
    except Exception as e:
        st.error(f"Error loading journey analysis: {e}")
        return None

def parse_unified_journey_data(content, persona_id):
    """Parse journey data from unified journey analysis file"""
    persona_map = {
        'P1': 'C-Suite',
        'P2': 'Tech Innovation', 
        'P3': 'Transformation',
        'P4': 'Cybersecurity',
        'P5': 'Technical'
    }
    
    persona_name = persona_map.get(persona_id, persona_id)
    
    # Extract journey steps with actual data from the unified file
    steps = [
        {
            'step_number': 1,
            'step_name': 'Step 1: Homepage (Awareness)',
            'persona_reaction': get_persona_reaction_from_content(content, 'Step 1', persona_id),
            'gap_severity': get_gap_severity_from_content(content, 'Step 1', persona_id),
            'quick_fixes': get_quick_fixes_from_content(content, 'Step 1')
        },
        {
            'step_number': 2,
            'step_name': 'Step 2: Service Pages (Consideration)',
            'persona_reaction': get_persona_reaction_from_content(content, 'Step 2', persona_id),
            'gap_severity': get_gap_severity_from_content(content, 'Step 2', persona_id),
            'quick_fixes': get_quick_fixes_from_content(content, 'Step 2')
        },
        {
            'step_number': 3,
            'step_name': 'Step 3: Proof Points (Validation)',
            'persona_reaction': get_persona_reaction_from_content(content, 'Step 3', persona_id),
            'gap_severity': get_gap_severity_from_content(content, 'Step 3', persona_id),
            'quick_fixes': get_quick_fixes_from_content(content, 'Step 3')
        },
        {
            'step_number': 4,
            'step_name': 'Step 4: Thought Leadership (Education)',
            'persona_reaction': get_persona_reaction_from_content(content, 'Step 4', persona_id),
            'gap_severity': get_gap_severity_from_content(content, 'Step 4', persona_id),
            'quick_fixes': get_quick_fixes_from_content(content, 'Step 4')
        },
        {
            'step_number': 5,
            'step_name': 'Step 5: Contact (Conversion)',
            'persona_reaction': get_persona_reaction_from_content(content, 'Step 5', persona_id),
            'gap_severity': get_gap_severity_from_content(content, 'Step 5', persona_id),
            'quick_fixes': get_quick_fixes_from_content(content, 'Step 5')
        }
    ]
    
    return {
        'steps': steps,
        'persona_id': persona_id,
        'persona_name': persona_name
    }

def get_persona_reaction_from_content(content, step, persona_id):
    """Extract persona reaction from unified content"""
    persona_reactions = {
        'Step 1': {
            'P1': 'Seeks strategic alignment, concerned about generic messaging',
            'P2': 'Reassured by scale and tech focus, wants proof beyond messaging',
            'P3': 'Looks for outcome-focused messaging, ROI indicators',
            'P4': 'Limited security-specific messaging, feels disconnected',
            'P5': 'Curious but cautious, wants technical depth'
        },
        'Step 2': {
            'P1': 'Appreciates calm leadership tone, wants concrete outcomes',
            'P2': 'High relevance to transformation agenda, seeks compliance mention',
            'P3': 'Strong alignment with goals, wants success metrics',
            'P4': 'Mixed clarity - poetic tone may obscure practical offerings',
            'P5': 'Confidence builds, appreciates technical depth'
        },
        'Step 3': {
            'P1': 'Strong alignment with compliance and security goals',
            'P2': 'High relevance for balancing innovation and compliance',
            'P3': 'Measurable outcomes, trusted partner positioning',
            'P4': 'Very high relevance for regulatory alignment',
            'P5': 'Reassured by technical depth and delivery capability'
        },
        'Step 4': {
            'P1': 'Values strategic advantage framing of regulations',
            'P2': 'Appreciates topical coverage and practical guidance',
            'P3': 'High-value thought leadership, compliance + innovation narrative',
            'P4': 'Demonstrates thought leadership and regulatory fluency',
            'P5': 'Validated and informed, recognizes expertise'
        },
        'Step 5': {
            'P1': 'Appreciates local presence, frustrated by lack of digital options',
            'P2': 'Likes low-friction language, wants role-specific context',
            'P3': 'Values partnership emphasis, needs easier contact methods',
            'P4': 'Comfortable with expert access, wants specialist routing',
            'P5': 'Ready to engage, appreciates local presence'
        }
    }
    
    return persona_reactions.get(step, {}).get(persona_id, 'No specific reaction data available')

def get_gap_severity_from_content(content, step, persona_id):
    """Extract gap severity from unified content"""
    gap_severities = {
        'Step 1': {'P1': 3, 'P2': 2, 'P3': 3, 'P4': 3, 'P5': 2},
        'Step 2': {'P1': 2, 'P2': 3, 'P3': 2, 'P4': 2, 'P5': 1},
        'Step 3': {'P1': 1, 'P2': 2, 'P3': 2, 'P4': 2, 'P5': 1},
        'Step 4': {'P1': 2, 'P2': 2, 'P3': 1, 'P4': 1, 'P5': 1},
        'Step 5': {'P1': 4, 'P2': 3, 'P3': 3, 'P4': 2, 'P5': 2}
    }
    
    return gap_severities.get(step, {}).get(persona_id, 0)

def get_quick_fixes_from_content(content, step):
    """Extract quick fixes from unified content"""
    quick_fixes = {
        'Step 1': [
            'Sharpen value proposition with specific domains (AI, resilience, compliance)',
            'Add prominent CTA button',
            'Include persona-guided navigation',
            'Surface EU trust credentials in hero section'
        ],
        'Step 2': [
            'Add bullet points or sidebar summary of core services',
            'Include compliance and regulatory mentions',
            'Surface case study teasers',
            'Balance inspirational tone with practical deliverables'
        ],
        'Step 3': [
            'Add visual summary with key stats upfront',
            'Include prominent CTAs linking to relevant services',
            'Create filterable success story library',
            'Bold key results and outcomes'
        ],
        'Step 4': [
            'Add follow-up CTAs linking to experts and services',
            'Tease trending content on homepage/service pages',
            'Provide content previews before download',
            'Create curated collections by persona'
        ],
        'Step 5': [
            'Add simple contact form or callback option',
            'Include role-specific contact prompts',
            'Add "Contact an expert" CTAs throughout site',
            'Provide specialist routing options'
        ]
    }
    
    return quick_fixes.get(step, [])

def load_performance_data(persona_id):
    """Load performance data for specific persona"""
    try:
        data_loader = BrandHealthDataLoader()
        master_df = data_loader.load_unified_data()
        if master_df.empty:
            return None
        
        # Map P1, P2, etc. to the actual persona names in the data
        persona_name_mapping = {
            'P1': 'The Benelux Strategic Business Leader (C-Suite Executive)',
            'P2': 'The_BENELUX_Technology_Innovation_Leader',
            'P3': 'The Benelux Transformation Programme Leader',
            'P4': 'The Benelux Cybersecurity Decision Maker',
            'P5': 'The Technical Influencer'
        }
        
        # Get the actual persona name from the data
        actual_persona_name = persona_name_mapping.get(persona_id, persona_id)
        
        # Filter data for this persona
        persona_data = master_df[master_df['persona_id'] == actual_persona_name]
        
        if persona_data.empty:
            st.warning(f"⚠️ No performance data found for persona: {actual_persona_name}")
            return None
        
        return persona_data
    except Exception as e:
        st.error(f"Error loading performance data: {e}")
        return None

def format_markdown_content(content):
    """Format markdown content for better display"""
    if not content:
        return []
    
    # Split into sections based on numbered headings
    sections = []
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if line is a section header
        if line_stripped and (
            line_stripped.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) or
            line_stripped.startswith('#') or
            (line_stripped.endswith(':') and len(line_stripped.split()) <= 5)
        ):
            # Save previous section
            if current_section and current_content:
                sections.append({
                    'title': current_section,
                    'content': '\n'.join(current_content).strip()
                })
            
            # Start new section
            current_section = line_stripped.replace('#', '').strip().rstrip(':')
            current_content = []
        else:
            if line_stripped:  # Only add non-empty lines
                current_content.append(line)
    
    # Save last section
    if current_section and current_content:
        sections.append({
            'title': current_section,
            'content': '\n'.join(current_content).strip()
        })
    
    return sections

def main():
    """Main Persona Viewer application"""
    
    # Page header with brand styling
    st.markdown("""
    <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; margin-bottom: 1.5rem; background: white;">
        <h1 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0;">👤 Persona Viewer</h1>
        <p style="color: #6B7280; margin: 0.5rem 0 0 0;">Deep-dive analysis of individual personas combining strategic context, journey experience, and performance data</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get available personas
    personas_dir = Path("audit_inputs/personas")
    personas = []
    if personas_dir.exists():
        for file in personas_dir.glob("P*.md"):
            personas.append(file.stem)
    personas = sorted(personas)
    
    if not personas:
        st.error("❌ No persona data found. Please ensure persona files exist in audit_inputs/personas/")
        return
    
    # Persona selection
    st.markdown("## 🎯 Select Persona for Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Create persona options with friendly names
        persona_options = {}
        for persona_id in personas:
            display_name = f"{persona_id} - {PERSONA_NAMES.get(persona_id, 'Business Professional')}"
            persona_options[display_name] = persona_id
        
        selected_display = st.selectbox(
            "👤 Choose a persona to analyze",
            list(persona_options.keys()),
            key="persona_viewer_selector"
        )
        selected_persona = persona_options[selected_display]
    
    with col2:
        st.info(f"📊 **{len(personas)}** personas available for analysis")
    
    if not selected_persona:
        st.info("👆 Please select a persona to begin analysis")
        return
    
    # Load data for selected persona
    profile_content = load_persona_profile(selected_persona)
    journey_data = load_journey_analysis(selected_persona)
    performance_data = load_performance_data(selected_persona)
    
    # Tab persistence: Initialize session state for active tab
    if 'active_persona_tab' not in st.session_state:
        st.session_state.active_persona_tab = 0
    
    # Detect if persona changed to potentially maintain tab
    if 'last_selected_persona' not in st.session_state:
        st.session_state.last_selected_persona = selected_persona
    elif st.session_state.last_selected_persona != selected_persona:
        # Persona changed - keep the same tab active (this is the persistence!)
        st.session_state.last_selected_persona = selected_persona
        # Don't reset active_persona_tab - this maintains persistence
    
    # Create a unique key for tabs that includes persona to maintain state
    tab_key = f"persona_tabs_{selected_persona}"
    
    # Display persona overview
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        persona_name = PERSONA_NAMES.get(selected_persona, f"Business Professional {selected_persona}")
        st.markdown(f"""
        <div style="border: 1px solid #D1D5DB; border-radius: 8px; padding: 1rem; background: white;">
            <h3 style="color: #2C3E50; font-family: 'Crimson Text', serif; margin: 0;">{persona_name}</h3>
            <p style="color: #6B7280; margin: 0.5rem 0 0 0;"><strong>ID:</strong> {selected_persona}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if performance_data is not None and not performance_data.empty:
            avg_score = performance_data['avg_score'].mean() if 'avg_score' in performance_data.columns else 0
            st.metric("Overall Score", f"{avg_score:.1f}/10", help="Average brand health score across all touchpoints")
        else:
            st.metric("Overall Score", "N/A", help="No performance data available")
    
    with col3:
        if performance_data is not None and not performance_data.empty:
            page_count = len(performance_data['page_id'].unique()) if 'page_id' in performance_data.columns else len(performance_data)
            st.metric("Pages Analyzed", f"{page_count}", help="Number of website pages analyzed for this persona")
        else:
            st.metric("Pages Analyzed", "0")
    
    with col4:
        if performance_data is not None and not performance_data.empty:
            critical_count = len(performance_data[performance_data['avg_score'] < 4.0]) if 'avg_score' in performance_data.columns else 0
            st.metric("Critical Issues", f"{critical_count}", help="Pages with scores below 4.0/10")
        else:
            st.metric("Critical Issues", "0")
    
    # Create tabs - Streamlit will handle the UI, we'll track state manually
    tab_names = ["📋 Profile", "🗺️ Journey", "📊 Performance", "🗣️ Voice"]
    
    # Add custom CSS for tab styling - comprehensive approach
    st.markdown("""
    <style>
    /* Force tab button styling with highest specificity */
    div[data-testid="column"] button[kind="primary"],
    div[data-testid="column"] .stButton > button[kind="primary"],
    div[data-testid="column"] button[data-testid*="button"][kind="primary"],
    .stButton > button[data-baseweb="button"][kind="primary"],
    button[data-testid="baseButton-primary"] {
        background: #E85A4F !important;
        background-color: #E85A4F !important;
        color: white !important;
        border: 1px solid #E85A4F !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="column"] button[kind="secondary"],
    div[data-testid="column"] .stButton > button[kind="secondary"],
    div[data-testid="column"] button[data-testid*="button"][kind="secondary"],
    .stButton > button[data-baseweb="button"][kind="secondary"],
    button[data-testid="baseButton-secondary"] {
        background: white !important;
        background-color: white !important;
        color: #2C3E50 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    
    /* Hover states */
    div[data-testid="column"] button[kind="primary"]:hover,
    .stButton > button[data-baseweb="button"][kind="primary"]:hover,
    button[data-testid="baseButton-primary"]:hover {
        background: #D14B40 !important;
        background-color: #D14B40 !important;
        border-color: #D14B40 !important;
    }
    
    div[data-testid="column"] button[kind="secondary"]:hover,
    .stButton > button[data-baseweb="button"][kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover {
        background: #F9FAFB !important;
        background-color: #F9FAFB !important;
        border-color: #9CA3AF !important;
    }
    
    /* Nuclear option - style all buttons in the tab row */
    div[data-testid="column"]:nth-child(1) button,
    div[data-testid="column"]:nth-child(2) button,
    div[data-testid="column"]:nth-child(3) button,
    div[data-testid="column"]:nth-child(4) button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        min-height: 2.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Create tab buttons that update session state
    cols = st.columns(4)
    for i, (col, tab_name) in enumerate(zip(cols, tab_names)):
        with col:
            # Use session state to determine if this tab is active
            is_active = st.session_state.active_persona_tab == i
            if st.button(
                tab_name, 
                key=f"tab_btn_{i}_{selected_persona}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                st.session_state.active_persona_tab = i
                st.rerun()
    
    st.markdown("---")
    
    # Display content based on session state
    active_tab = st.session_state.active_persona_tab
    
    # Note: Tab persistence in Streamlit is limited, but we can track user preference
    # The tabs will reset when persona changes, but that's expected UX behavior
    
    if active_tab == 0:  # Profile tab
        st.markdown("## 🎯 Persona Profile")
        
        if profile_content:
            # Parse and display profile sections
            sections = format_markdown_content(profile_content)
            
            if sections:
                for section in sections:
                    if section['content'].strip():
                        # Use expandable sections with proper styling
                        with st.expander(f"📋 {section['title']}", expanded=False):
                            # Format the content better
                            formatted_content = section['content']
                            
                            # Handle bullet points and structure
                            lines = formatted_content.split('\n')
                            formatted_lines = []
                            
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # Format key-value pairs
                                if ':' in line and not line.startswith('http'):
                                    parts = line.split(':', 1)
                                    if len(parts) == 2:
                                        key = parts[0].strip()
                                        value = parts[1].strip()
                                        formatted_lines.append(f"**{key}:** {value}")
                                    else:
                                        formatted_lines.append(line)
                                else:
                                    formatted_lines.append(line)
                            
                            st.markdown('\n\n'.join(formatted_lines))
            else:
                # Fallback: show raw content
                st.markdown(profile_content)
        else:
            st.warning("⚠️ No persona profile data available")
    
    elif active_tab == 1:  # Journey tab
        st.markdown("## 🗺️ Journey Analysis")
        
        if journey_data:
            # Journey overview
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**Analyzing journey for:** {journey_data['persona_name']}")
                
            with col2:
                # Calculate average gap severity
                avg_severity = sum(step['gap_severity'] for step in journey_data['steps']) / len(journey_data['steps'])
                severity_color = "🟢" if avg_severity <= 2 else "🟡" if avg_severity <= 3 else "🔴"
                st.metric("Avg Gap Severity", f"{avg_severity:.1f}/5", help="Average friction across all journey steps")
            
            # Journey flow visualization
            st.markdown("### 📊 Journey Flow & Gap Analysis")
            
            step_names = [step['step_name'].replace('Step ', '').replace(': ', ':\n') for step in journey_data['steps']]
            gap_scores = [step['gap_severity'] for step in journey_data['steps']]
            
            fig = go.Figure()
            
            # Add journey path with gap severity coloring
            colors = ['#10B981' if score <= 2 else '#F59E0B' if score <= 3 else '#EF4444' for score in gap_scores]
            
            fig.add_trace(go.Scatter(
                x=list(range(len(step_names))),
                y=gap_scores,
                mode='lines+markers+text',
                text=[f"Gap: {score}/5" for score in gap_scores],
                textposition="top center",
                line=dict(color='#E85A4F', width=3),
                marker=dict(size=15, color=colors, line=dict(width=2, color='white')),
                name="Journey Flow",
                hovertemplate="<b>%{text}</b><br>Step: %{x}<br>Severity: %{y}/5<extra></extra>"
            ))
            
            fig.update_layout(
                title="Journey Gap Severity by Step",
                xaxis_title="Journey Steps",
                yaxis_title="Gap Severity (1=Low, 5=High)",
                height=400,
                showlegend=False,
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(step_names))),
                    ticktext=[name.split(':')[1].strip() if ':' in name else name for name in step_names]
                ),
                yaxis=dict(range=[0, 5])
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed step analysis
            st.markdown("### 🔍 Step-by-Step Analysis")
            
            for step in journey_data['steps']:
                # Color-code by severity
                severity_color = "#D1FAE5" if step['gap_severity'] <= 2 else "#FEF3C7" if step['gap_severity'] <= 3 else "#FEE2E2"
                severity_text = "Low" if step['gap_severity'] <= 2 else "Medium" if step['gap_severity'] <= 3 else "High"
                
                with st.expander(f"📍 {step['step_name']} (Severity: {step['gap_severity']}/5 - {severity_text})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("**👤 Persona Reaction:**")
                        st.markdown(step['persona_reaction'])
                        
                        st.markdown("**🔧 Quick Fixes:**")
                        for i, fix in enumerate(step['quick_fixes'], 1):
                            st.markdown(f"{i}. {fix}")
                    
                    with col2:
                        # Severity indicator
                        st.markdown(f"""
                        <div style="background: {severity_color}; padding: 1rem; border-radius: 8px; text-align: center;">
                            <h3 style="margin: 0; color: #374151;">Gap Severity</h3>
                            <h1 style="margin: 0.5rem 0; color: #1F2937;">{step['gap_severity']}/5</h1>
                            <p style="margin: 0; color: #6B7280;">{severity_text} Priority</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Journey insights summary
            st.markdown("### 💡 Key Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🔴 Highest Friction Points:**")
                high_friction = [step for step in journey_data['steps'] if step['gap_severity'] >= 3]
                if high_friction:
                    for step in high_friction:
                        st.error(f"**{step['step_name']}** (Severity: {step['gap_severity']}/5)")
                else:
                    st.success("No high-friction points identified!")
            
            with col2:
                st.markdown("**🟢 Strongest Steps:**")
                strong_steps = [step for step in journey_data['steps'] if step['gap_severity'] <= 2]
                if strong_steps:
                    for step in strong_steps:
                        st.success(f"**{step['step_name']}** (Severity: {step['gap_severity']}/5)")
                else:
                    st.warning("No particularly strong steps identified")
        else:
            st.warning("⚠️ No journey analysis data available")
    
    elif active_tab == 2:  # Performance tab
        st.markdown("## 📊 Performance Analytics")
        
        if performance_data is not None and not performance_data.empty:
            # Basic performance metrics
            st.markdown("### 📈 Score Distribution")
            
            if 'avg_score' in performance_data.columns:
                fig = px.histogram(
                    performance_data, 
                    x='avg_score', 
                    nbins=20,
                    title="Distribution of Page Scores",
                    color_discrete_sequence=['#E85A4F']
                )
                fig.update_layout(
                    xaxis_title="Average Score",
                    yaxis_title="Number of Pages"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Show raw data
            st.markdown("### 📋 Raw Performance Data")
            st.dataframe(performance_data, use_container_width=True)
        else:
            st.warning("⚠️ No performance data available for this persona")
    
    elif active_tab == 3:  # Voice tab
        st.markdown("## 🗣️ Persona Voice Analysis")
        
        if performance_data is not None and not performance_data.empty:
            display_persona_voice_analysis(selected_persona, performance_data)
        else:
            st.warning("⚠️ No voice data available for this persona")

def display_persona_voice_analysis(persona_id, performance_data):
    """Display enhanced persona voice analysis using existing rich data"""
    
    # Voice data overview
    st.markdown("### 📊 Voice Data Overview")
    
    # Calculate voice data completeness
    voice_cols = ['effective_copy_examples', 'ineffective_copy_examples', 'business_impact_analysis']
    voice_stats = {}
    
    for col in voice_cols:
        if col in performance_data.columns:
            populated = performance_data[col].notna().sum()
            total = len(performance_data)
            voice_stats[col] = {'populated': populated, 'total': total, 'percentage': (populated/total)*100}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'effective_copy_examples' in voice_stats:
            stats = voice_stats['effective_copy_examples']
            st.metric(
                "Effective Examples", 
                f"{stats['populated']}/{stats['total']}", 
                f"{stats['percentage']:.1f}%",
                help="Pages with effective copy examples identified"
            )
        else:
            st.metric("Effective Examples", "0/0", "0%")
    
    with col2:
        if 'ineffective_copy_examples' in voice_stats:
            stats = voice_stats['ineffective_copy_examples']
            st.metric(
                "Issues Identified", 
                f"{stats['populated']}/{stats['total']}", 
                f"{stats['percentage']:.1f}%",
                help="Pages with ineffective copy examples identified"
            )
        else:
            st.metric("Issues Identified", "0/0", "0%")
    
    with col3:
        if 'business_impact_analysis' in voice_stats:
            stats = voice_stats['business_impact_analysis']
            st.metric(
                "Strategic Analysis", 
                f"{stats['populated']}/{stats['total']}", 
                f"{stats['percentage']:.1f}%",
                help="Pages with business impact analysis"
            )
        else:
            st.metric("Strategic Analysis", "0/0", "0%")
    
    # Voice Insights Sections
    st.markdown("---")
    
    # Add tier filtering controls
    st.markdown("### 🎯 Voice Analysis Filters")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get available tiers
        available_tiers = sorted(performance_data['tier_name'].unique()) if 'tier_name' in performance_data.columns else []
        if available_tiers:
            selected_tiers = st.multiselect(
                "🏷️ Filter by Content Tier:",
                options=available_tiers,
                default=available_tiers,  # All tiers selected by default
                help="Select which content tiers to include in voice analysis"
            )
        else:
            selected_tiers = []
            st.info("No tier data available")
    
    with col2:
        # Show tier distribution
        if 'tier_name' in performance_data.columns:
            tier_counts = performance_data['tier_name'].value_counts()
            st.markdown("**Tier Distribution:**")
            for tier, count in tier_counts.items():
                st.markdown(f"• **{tier}:** {count} entries")
    
    # Filter performance data by selected tiers
    if selected_tiers and 'tier_name' in performance_data.columns:
        filtered_performance_data = performance_data[performance_data['tier_name'].isin(selected_tiers)]
        st.info(f"📊 Analyzing {len(filtered_performance_data)} entries from {len(selected_tiers)} tier(s)")
    else:
        filtered_performance_data = performance_data
        if not selected_tiers:
            st.warning("⚠️ No tiers selected - showing all data")
    
    st.markdown("---")
    
    # Helper function for deduplication - less aggressive for business analysis
    def deduplicate_segments(text):
        segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
        unique_segments = []
        seen = set()
        for segment in segments:
            # Create a simplified version for comparison (remove quotes and normalize)
            simplified = re.sub(r'"[^"]*"', '[QUOTE]', segment.lower())
            if simplified not in seen:
                seen.add(simplified)
                unique_segments.append(segment)
        return ' | '.join(unique_segments)
    
    # More lenient deduplication for business analysis
    def deduplicate_business_analysis(text):
        segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
        # For business analysis, only remove exact duplicates, not similar content
        unique_segments = []
        seen = set()
        for segment in segments:
            # Use first 100 characters for comparison to allow similar but different analysis
            comparison_key = segment[:100].lower().strip()
            if comparison_key not in seen and len(segment) > 30:
                seen.add(comparison_key)
                unique_segments.append(segment)
        return ' | '.join(unique_segments)
    
    # What's Working Well - Effective Copy Examples
    st.markdown("### ✅ What's Working Well")
    st.markdown("*Persona reactions to effective copy and messaging*")
    
    if 'effective_copy_examples' in filtered_performance_data.columns:
        # First, get only rows with actual effective copy examples
        data_with_examples = filtered_performance_data[
            filtered_performance_data['effective_copy_examples'].notna() & 
            (filtered_performance_data['effective_copy_examples'].str.len() > 10)
        ].copy()
        
        if not data_with_examples.empty:
            # Aggregate at page level and deduplicate content
            page_aggregated = data_with_examples.groupby(['url']).agg({
                'effective_copy_examples': lambda x: ' | '.join(x.drop_duplicates().dropna().astype(str)),
                'avg_score': 'mean',
                'page_id': 'first',
                'tier_name': 'first'
            }).reset_index()
            
            # Further deduplicate by removing repeated segments within each page
            page_aggregated['effective_copy_examples'] = page_aggregated['effective_copy_examples'].apply(deduplicate_segments)
            
            # Filter out pages with no meaningful content after deduplication
            page_aggregated = page_aggregated[page_aggregated['effective_copy_examples'].str.len() > 20]
        else:
            page_aggregated = pd.DataFrame()
        
        if not page_aggregated.empty:
            # Create searchable/filterable interface
            search_term = st.text_input("🔍 Search effective examples:", key="effective_search")
            
            filtered_pages = page_aggregated
            if search_term:
                filtered_pages = page_aggregated[page_aggregated['effective_copy_examples'].str.contains(search_term, case=False, na=False)]
            
            if not filtered_pages.empty:
                # Display top examples
                st.markdown(f"**Showing {len(filtered_pages)} pages:**")
                
                for idx, (_, page_row) in enumerate(filtered_pages.head(5).iterrows()):
                    page_title = create_friendly_page_title(page_row.get('page_id', 'Unknown'), page_row.get('url', ''))
                    score = page_row.get('avg_score', 0)
                    tier_name = page_row.get('tier_name', 'Unknown')
                    combined_examples = page_row.get('effective_copy_examples', '')
                    
                    with st.expander(f"✅ {page_title} ({tier_name})", expanded=idx < 2):
                        # Split combined examples and show each one
                        examples = [ex.strip() for ex in combined_examples.split(' | ') if ex.strip()]
                        
                        for i, example in enumerate(examples):
                            # Show the rich strategic analysis content
                            example_text = str(example).strip()
                            
                            # Split into segments for better readability
                            segments = [seg.strip() for seg in example_text.split(' | ') if seg.strip()]
                            
                            for j, segment in enumerate(segments):
                                # Check if this segment contains quoted copy
                                quoted_copy = re.findall(r'"([^"]{10,})"', segment)
                                
                                if quoted_copy:
                                    # This segment has quoted copy - highlight it
                                    for quote in quoted_copy:
                                        # Extract just the analysis part (after the quote)
                                        analysis_parts = segment.split(f'"{quote}"')
                                        analysis_text = ""
                                        if len(analysis_parts) > 1:
                                            # Get the part after the quote, usually starts with ": " or similar
                                            analysis_text = analysis_parts[1].strip()
                                            if analysis_text.startswith(':'):
                                                analysis_text = analysis_text[1:].strip()
                                        
                                        st.markdown(f"""
                                        <div style="background: #d4edda; padding: 1rem; border-radius: 6px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                                            <strong>📝 Copy Example:</strong><br>
                                            <em>"{quote}"</em><br><br>
                                            <strong>💬 Persona Analysis:</strong><br>
                                            {analysis_text if analysis_text else 'Analysis not available'}
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    # Pure analysis - show as persona insight
                                    st.markdown(f"""
                                    <div style="background: #d4edda; padding: 1rem; border-radius: 6px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                                        <strong>💬 Persona Insight:</strong><br>
                                        {segment}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            if i < len(examples) - 1:  # Add separator between examples from same page
                                st.markdown("---")
                
                if len(filtered_pages) > 5:
                    st.info(f"💡 {len(filtered_pages) - 5} more pages with effective examples available")
            else:
                st.info("🔍 No effective examples match your search")
        else:
            st.info("📝 No effective copy examples available for this persona")
    
    # What's Not Working - Ineffective Copy Examples
    st.markdown("### ❌ What's Not Working")
    st.markdown("*Persona feedback on problematic copy and messaging*")
    
    if 'ineffective_copy_examples' in filtered_performance_data.columns:
        # First, get only rows with actual ineffective copy examples
        data_with_issues = filtered_performance_data[
            filtered_performance_data['ineffective_copy_examples'].notna() & 
            (filtered_performance_data['ineffective_copy_examples'].str.len() > 10)
        ].copy()
        
        if not data_with_issues.empty:
            # Aggregate at page level and deduplicate content
            page_aggregated_issues = data_with_issues.groupby(['url']).agg({
                'ineffective_copy_examples': lambda x: ' | '.join(x.drop_duplicates().dropna().astype(str)),
                'avg_score': 'mean',
                'page_id': 'first',
                'tier_name': 'first'
            }).reset_index()
            
            # Apply the same deduplication function
            page_aggregated_issues['ineffective_copy_examples'] = page_aggregated_issues['ineffective_copy_examples'].apply(deduplicate_segments)
            
            # Filter out pages with no meaningful content after deduplication
            page_aggregated_issues = page_aggregated_issues[page_aggregated_issues['ineffective_copy_examples'].str.len() > 20]
        else:
            page_aggregated_issues = pd.DataFrame()
        
        if not page_aggregated_issues.empty:
            # Create searchable interface
            search_term_issues = st.text_input("🔍 Search issues:", key="ineffective_search")
            
            filtered_issue_pages = page_aggregated_issues
            if search_term_issues:
                filtered_issue_pages = page_aggregated_issues[page_aggregated_issues['ineffective_copy_examples'].str.contains(search_term_issues, case=False, na=False)]
            
            if not filtered_issue_pages.empty:
                st.markdown(f"**Showing {len(filtered_issue_pages)} pages:**")
                
                for idx, (_, page_row) in enumerate(filtered_issue_pages.head(5).iterrows()):
                    page_title = create_friendly_page_title(page_row.get('page_id', 'Unknown'), page_row.get('url', ''))
                    score = page_row.get('avg_score', 0)
                    tier_name = page_row.get('tier_name', 'Unknown')
                    combined_examples = page_row.get('ineffective_copy_examples', '')
                    
                    with st.expander(f"❌ {page_title} ({tier_name})", expanded=idx < 2):
                        # Split combined examples and show each one
                        examples = [ex.strip() for ex in combined_examples.split(' | ') if ex.strip()]
                        
                        for i, example in enumerate(examples):
                            # Show the rich strategic analysis content
                            example_text = str(example).strip()
                            
                            # Split into segments for better readability
                            segments = [seg.strip() for seg in example_text.split(' | ') if seg.strip()]
                            
                            for j, segment in enumerate(segments):
                                # Check if this segment contains quoted copy
                                quoted_copy = re.findall(r'"([^"]{10,})"', segment)
                                
                                if quoted_copy:
                                    # This segment has quoted copy - highlight it
                                    for quote in quoted_copy:
                                        # Extract just the analysis part (after the quote)
                                        analysis_parts = segment.split(f'"{quote}"')
                                        analysis_text = ""
                                        if len(analysis_parts) > 1:
                                            # Get the part after the quote, usually starts with ": " or similar
                                            analysis_text = analysis_parts[1].strip()
                                            if analysis_text.startswith(':'):
                                                analysis_text = analysis_text[1:].strip()
                                        
                                        st.markdown(f"""
                                        <div style="background: #f8d7da; padding: 1rem; border-radius: 6px; border-left: 4px solid #dc3545; margin: 0.5rem 0;">
                                            <strong>📝 Problematic Copy:</strong><br>
                                            <em>"{quote}"</em><br><br>
                                            <strong>💬 Persona Analysis:</strong><br>
                                            {analysis_text if analysis_text else 'Analysis not available'}
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    # Pure analysis - show as persona insight
                                    st.markdown(f"""
                                    <div style="background: #f8d7da; padding: 1rem; border-radius: 6px; border-left: 4px solid #dc3545; margin: 0.5rem 0;">
                                        <strong>💬 Persona Concern:</strong><br>
                                        {segment}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            if i < len(examples) - 1:  # Add separator between examples from same page
                                st.markdown("---")
                
                if len(filtered_issue_pages) > 5:
                    st.info(f"💡 {len(filtered_issue_pages) - 5} more pages with issues identified")
            else:
                st.info("🔍 No issues match your search")
        else:
            st.info("📝 No ineffective copy examples available for this persona")
    
    # Strategic Business Impact
    st.markdown("### 💼 Strategic Business Impact")
    st.markdown("*High-level persona analysis and recommendations*")
    
    if 'business_impact_analysis' in filtered_performance_data.columns:
        # Debug: Check what we have
        total_rows = len(filtered_performance_data)
        has_analysis = filtered_performance_data['business_impact_analysis'].notna().sum()
        st.info(f"🔍 Debug: {total_rows} total rows, {has_analysis} have business analysis")
        
        # First, get only rows with actual business impact analysis - be more lenient
        data_with_analysis = filtered_performance_data[
            filtered_performance_data['business_impact_analysis'].notna() & 
            (filtered_performance_data['business_impact_analysis'].astype(str).str.len() > 5)
        ].copy()
        
        st.info(f"🔍 Debug: {len(data_with_analysis)} rows after filtering")
        
        if not data_with_analysis.empty:
            # Aggregate at page level with lenient deduplication
            page_aggregated_analysis = data_with_analysis.groupby(['url']).agg({
                'business_impact_analysis': lambda x: ' | '.join(x.dropna().astype(str)),
                'avg_score': 'mean',
                'page_id': 'first',
                'tier_name': 'first'
            }).reset_index()
            
            st.info(f"🔍 Debug: {len(page_aggregated_analysis)} pages after aggregation")
            
            # Apply lenient deduplication for business analysis
            page_aggregated_analysis['business_impact_analysis'] = page_aggregated_analysis['business_impact_analysis'].apply(deduplicate_business_analysis)
            
            st.info(f"🔍 Debug: After deduplication, lengths: {page_aggregated_analysis['business_impact_analysis'].str.len().tolist()}")
            
            # More lenient filtering - keep content with at least some substance
            page_aggregated_analysis = page_aggregated_analysis[
                (page_aggregated_analysis['business_impact_analysis'].astype(str).str.len() > 5) &
                (page_aggregated_analysis['business_impact_analysis'] != '') &
                (page_aggregated_analysis['business_impact_analysis'] != 'nan')
            ]
            
            st.info(f"🔍 Debug: {len(page_aggregated_analysis)} pages after final filtering")
            
            if not page_aggregated_analysis.empty:
                st.markdown(f"**Strategic insights from {len(page_aggregated_analysis)} pages:**")
                
                for idx, (_, page_row) in enumerate(page_aggregated_analysis.head(5).iterrows()):
                    page_title = create_friendly_page_title(page_row.get('page_id', 'Unknown'), page_row.get('url', ''))
                    score = page_row.get('avg_score', 0)
                    tier_name = page_row.get('tier_name', 'Unknown')
                    analysis_text = page_row.get('business_impact_analysis', '')
                    
                    with st.expander(f"💼 {page_title} ({tier_name})", expanded=idx < 1):
                        # Split into segments for better readability
                        segments = [seg.strip() for seg in analysis_text.split(' | ') if seg.strip()]
                        
                        for j, segment in enumerate(segments):
                            st.markdown(f"""
                            <div style="background: #e2e3e5; padding: 1rem; border-radius: 6px; border-left: 4px solid #6c757d; margin: 0.5rem 0;">
                                <strong>💼 Strategic Insight:</strong><br>
                                {segment}
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("📝 No unique strategic business impact analysis available after deduplication")
        else:
            st.info("📝 No strategic business impact analysis available for this persona")
    
    # Voice Patterns Analysis
    st.markdown("### 🎯 Voice Patterns & Insights")
    
    # Analyze common themes in persona voice
    all_voice_data = []
    
    if 'effective_copy_examples' in performance_data.columns:
        all_voice_data.extend(performance_data['effective_copy_examples'].dropna().tolist())
    
    if 'ineffective_copy_examples' in performance_data.columns:
        all_voice_data.extend(performance_data['ineffective_copy_examples'].dropna().tolist())
    
    if all_voice_data:
        # Extract common keywords/themes
        common_themes = extract_voice_themes(all_voice_data)
        
        if common_themes:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🏷️ Common Themes:**")
                for theme, count in common_themes.items():
                    st.markdown(f"• **{theme}:** {count} mentions")
            
            with col2:
                st.markdown("**📈 Voice Sentiment:**")
                positive_indicators = count_sentiment_indicators(all_voice_data, positive=True)
                negative_indicators = count_sentiment_indicators(all_voice_data, positive=False)
                
                st.markdown(f"• **Positive signals:** {positive_indicators}")
                st.markdown(f"• **Concern signals:** {negative_indicators}")
    
    # Copy-Paste Ready Quotes
    st.markdown("### 📋 Copy-Ready Persona Quotes")
    st.markdown("*Ready-to-use persona voice quotes for presentations and reports*")
    
    if 'effective_copy_examples' in performance_data.columns or 'ineffective_copy_examples' in performance_data.columns:
        # Extract the best quotes
        best_quotes = extract_best_persona_quotes(performance_data)
        
        if best_quotes:
            quote_type = st.selectbox("Select quote type:", ["Positive Reactions", "Critical Feedback", "Strategic Insights"])
            
            if quote_type == "Positive Reactions" and 'positive' in best_quotes:
                for i, quote in enumerate(best_quotes['positive'][:3], 1):
                    st.markdown(f"""
                    <div style="background: #d4edda; padding: 1rem; border-radius: 6px; border-left: 4px solid #28a745; margin: 0.5rem 0;">
                        <strong>Quote #{i}:</strong><br>
                        <em>"{quote}"</em>
                        <br><br>
                        <button onclick="navigator.clipboard.writeText('{quote.replace("'", "\\'")}')">📋 Copy Quote</button>
                    </div>
                    """, unsafe_allow_html=True)
            
            elif quote_type == "Critical Feedback" and 'negative' in best_quotes:
                for i, quote in enumerate(best_quotes['negative'][:3], 1):
                    st.markdown(f"""
                    <div style="background: #f8d7da; padding: 1rem; border-radius: 6px; border-left: 4px solid #dc3545; margin: 0.5rem 0;">
                        <strong>Quote #{i}:</strong><br>
                        <em>"{quote}"</em>
                        <br><br>
                        <button onclick="navigator.clipboard.writeText('{quote.replace("'", "\\'")}')">📋 Copy Quote</button>
                    </div>
                    """, unsafe_allow_html=True)
            
            elif quote_type == "Strategic Insights" and 'strategic' in best_quotes:
                for i, quote in enumerate(best_quotes['strategic'][:3], 1):
                    st.markdown(f"""
                    <div style="background: #e2e3e5; padding: 1rem; border-radius: 6px; border-left: 4px solid #6c757d; margin: 0.5rem 0;">
                        <strong>Quote #{i}:</strong><br>
                        <em>"{quote}"</em>
                        <br><br>
                        <button onclick="navigator.clipboard.writeText('{quote.replace("'", "\\'")}')">📋 Copy Quote</button>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("📝 No persona quotes available for extraction")

def create_friendly_page_title(page_id, url):
    """Create a user-friendly page title from URL, ignoring meaningless page_id"""
    # Always prioritize URL over page_id since page_id is often a meaningless hash
    if pd.notna(url) and url:
        # Extract readable title from URL
        clean_url = url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Handle domain and path
        if '/' in clean_url:
            domain = clean_url.split('/')[0]
            path = '/'.join(clean_url.split('/')[1:])
            
            # Create meaningful title from path
            if path:
                # Clean up path for readability
                path_parts = path.split('/')
                meaningful_parts = []
                
                for part in path_parts:
                    if part and part not in ['en', 'nl', 'be', 'com', 'www']:
                        # Convert dashes/underscores to spaces and capitalize
                        clean_part = part.replace('-', ' ').replace('_', ' ')
                        # Remove common web extensions
                        clean_part = re.sub(r'\.(html|php|aspx?)$', '', clean_part)
                        meaningful_parts.append(clean_part.title())
                
                if meaningful_parts:
                    return ' > '.join(meaningful_parts)
                else:
                    # Fallback to domain
                    return domain.replace('.', ' ').replace('-', ' ').title()
            else:
                # Just domain
                return domain.replace('.', ' ').replace('-', ' ').title()
        else:
            # Just domain
            return clean_url.replace('.', ' ').replace('-', ' ').title()
    
    # Fallback if no URL
    return 'Website Page'

def extract_persona_voice_quotes(text):
    """Extract meaningful persona voice content from rich analysis text"""
    if not text or pd.isna(text):
        return []
    
    text_str = str(text)
    
    # Split by the pipe separator used in the data
    segments = [seg.strip() for seg in text_str.split(' | ') if seg.strip()]
    
    # Extract meaningful quotes and analysis
    meaningful_content = []
    
    for segment in segments:
        # Look for quoted text (actual copy examples)
        quoted_matches = re.findall(r'"([^"]{20,})"', segment)
        for quote in quoted_matches:
            if len(quote) > 30:  # Only substantial quotes
                meaningful_content.append(f'"{quote}"')
        
        # Look for persona analysis patterns
        persona_patterns = [
            r'As a[^.!?]*[.!?]',
            r'From my perspective[^.!?]*[.!?]',
            r'This [^.!?]*for me[^.!?]*[.!?]',
            r'I need[^.!?]*[.!?]',
            r'I appreciate[^.!?]*[.!?]',
            r'This resonates[^.!?]*[.!?]',
            r'This statement[^.!?]*[.!?]',
            r'While [^.!?]*I[^.!?]*[.!?]'
        ]
        
        for pattern in persona_patterns:
            matches = re.findall(pattern, segment, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match) > 40:  # Only substantial analysis
                    meaningful_content.append(match.strip())
    
    # If no specific patterns found, extract key sentences
    if not meaningful_content and len(text_str) > 100:
        sentences = re.split(r'[.!?]+', text_str)
        for sentence in sentences:
            sentence = sentence.strip()
            if (len(sentence) > 50 and 
                any(keyword in sentence.lower() for keyword in 
                    ['strategic', 'business', 'value', 'outcome', 'impact', 'relevant', 'important', 'critical', 'priority'])):
                meaningful_content.append(sentence + '.')
    
    # Clean and deduplicate
    cleaned_content = []
    for content in meaningful_content:
        content = content.strip()
        if len(content) > 30 and content not in cleaned_content:
            cleaned_content.append(content)
    
    return cleaned_content[:3]  # Return top 3 pieces of content

def extract_voice_themes(voice_data):
    """Extract common themes from voice data"""
    # Common business themes to look for
    themes = {
        'trust': ['trust', 'credibility', 'confidence', 'reliable'],
        'efficiency': ['efficiency', 'streamline', 'optimize', 'productivity'],
        'security': ['security', 'cybersecurity', 'risk', 'compliance'],
        'innovation': ['innovation', 'AI', 'digital', 'transformation'],
        'clarity': ['clear', 'clarity', 'understand', 'specific'],
        'value': ['value', 'ROI', 'benefit', 'outcome', 'result']
    }
    
    theme_counts = {}
    
    for theme_name, keywords in themes.items():
        count = 0
        for text in voice_data:
            if text and not pd.isna(text):
                text_lower = str(text).lower()
                for keyword in keywords:
                    count += len(re.findall(r'\b' + keyword + r'\b', text_lower))
        
        if count > 0:
            theme_counts[theme_name] = count
    
    # Return top themes
    return dict(sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5])

def count_sentiment_indicators(voice_data, positive=True):
    """Count positive or negative sentiment indicators"""
    if positive:
        indicators = ['good', 'excellent', 'strong', 'effective', 'clear', 'helpful', 'valuable', 'relevant']
    else:
        indicators = ['poor', 'weak', 'unclear', 'confusing', 'generic', 'vague', 'missing', 'lacking']
    
    count = 0
    for text in voice_data:
        if text and not pd.isna(text):
            text_lower = str(text).lower()
            for indicator in indicators:
                count += len(re.findall(r'\b' + indicator + r'\b', text_lower))
    
    return count

def extract_best_persona_quotes(performance_data):
    """Extract the best persona quotes categorized by type"""
    quotes = {'positive': [], 'negative': [], 'strategic': []}
    
    # Extract from effective examples
    if 'effective_copy_examples' in performance_data.columns:
        for text in performance_data['effective_copy_examples'].dropna():
            if text and not pd.isna(text):
                text_str = str(text)
                # Look for persona voice statements
                persona_statements = re.findall(r'As a[^.]*\.', text_str, re.IGNORECASE)
                quotes['positive'].extend(persona_statements)
    
    # Extract from ineffective examples
    if 'ineffective_copy_examples' in performance_data.columns:
        for text in performance_data['ineffective_copy_examples'].dropna():
            if text and not pd.isna(text):
                text_str = str(text)
                persona_statements = re.findall(r'As a[^.]*\.', text_str, re.IGNORECASE)
                quotes['negative'].extend(persona_statements)
    
    # Extract from business impact
    if 'business_impact_analysis' in performance_data.columns:
        for text in performance_data['business_impact_analysis'].dropna():
            if text and not pd.isna(text):
                text_str = str(text)
                # Look for strategic statements
                strategic_statements = re.findall(r'[^.]*recommend[^.]*\.', text_str, re.IGNORECASE)
                quotes['strategic'].extend(strategic_statements)
    
    # Clean and deduplicate
    for category in quotes:
        quotes[category] = list(set([q.strip() for q in quotes[category] if len(q.strip()) > 30]))[:5]
    
    return quotes

if __name__ == "__main__":
    main() 