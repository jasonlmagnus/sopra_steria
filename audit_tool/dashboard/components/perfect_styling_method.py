#!/usr/bin/env python3
"""
PERFECT STYLING METHOD
Single source of truth for ALL styling across the dashboard.
This file provides one function, apply_perfect_styling(), to load 
the master stylesheet (perfect_stylesheet.css) for all pages.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64
import streamlit.components.v1 as components
import json

def apply_perfect_styling():
    """
    Loads and injects the master CSS file (perfect_stylesheet.css).
    This is the ONLY function that should be called for styling.
    """
    css_file = Path(__file__).parent / "perfect_stylesheet.css"
    if css_file.exists():
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.error("FATAL: Master stylesheet (perfect_stylesheet.css) not found.")

# ===== HEADER FUNCTIONS =====
def create_main_header(title: str, subtitle: str = ""):
    """Create bulletproof main page header"""
    if subtitle:
        st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="main-header">
            <h1>{title}</h1>
        </div>
        """, unsafe_allow_html=True)

def create_section_header(title: str):
    """Create bulletproof section header using Streamlit native"""
    st.markdown(f"## {title}")

def create_subsection_header(title: str):
    """Create bulletproof subsection header using Streamlit native"""
    st.markdown(f"### {title}")

# ===== METRIC FUNCTIONS =====
def create_metric_card(value: str, label: str, status: str = "default", description: str = None, status_text: str = None):
    """
    Creates a robust, standardized metric card using Streamlit's native metric component.
    This is the single source of truth for all metric cards.
    """
    # Use Streamlit's native metric component which is more reliable
    st.metric(label=label, value=value, help=description)
    
    # Add status indicator if provided
    if status_text:
        if status == "success" or status == "excellent":
            st.success(status_text)
        elif status == "warning":
            st.warning(status_text)
        elif status == "error" or status == "critical":
            st.error(status_text)
        else:
            st.info(status_text)

def create_score_display(score: float, max_score: float = 100):
    """Create standardized score display"""
    percentage = (score / max_score) * 100
    if percentage >= 80:
        status = "excellent"
    elif percentage >= 60:
        status = "good"
    elif percentage >= 40:
        status = "warning"
    else:
        status = "critical"
    
    return create_metric_card(f"{score:.1f}", f"Score (out of {max_score})", status)

# ===== CARD FUNCTIONS =====
def create_content_card(content: str, card_type: str = "content"):
    """Create standardized content card that correctly renders markdown."""
    st.markdown(f'<div class="{card_type}-card">{content}</div>', unsafe_allow_html=True)

def create_brand_card(content: str):
    """Create brand-specific card"""
    create_content_card(content, "brand")

def create_persona_performance_card(persona_name: str, score: float, status_text: str, page_count: int, icon: str):
    """Creates a styled card for displaying persona performance metrics."""
    
    status_class_map = {
        "EXCELLENT": "excellent",
        "GOOD": "good",
        "FAIR": "warning",
        "POOR": "critical"
    }
    status_class = status_class_map.get(status_text, "default")

    st.markdown(f"""
    <div class="persona-perf-card {status_class}">
        <div class="persona-perf-header">
            {icon} {persona_name}
        </div>
        <div class="persona-perf-score">{score:.1f}/10</div>
        <div class="persona-perf-label">OVERALL SCORE ({status_text})</div>
        <div class="persona-perf-footer">{page_count} pages analyzed</div>
    </div>
    """, unsafe_allow_html=True)

def create_persona_card(content: str):
    """Create persona-specific card and render HTML content."""
    st.markdown(f'<div class="persona-card">{content}</div>', unsafe_allow_html=True)

def create_matrix_card(content: str):
    """Create matrix-specific card"""
    create_content_card(content, "matrix")

def create_opportunity_card(content: str):
    """Create opportunity-specific card that renders HTML."""
    st.markdown(f'<div class="opportunity-card">{content}</div>', unsafe_allow_html=True)

def create_success_card(content: str):
    """Create success-specific card"""
    create_content_card(content, "success")

def create_report_card(content: str):
    """Create report-specific card"""
    create_content_card(content, "report")

# ===== STATUS FUNCTIONS =====
def create_status_indicator(status: str, label: str = ""):
    """Create standardized status indicator"""
    status_map = {
        "excellent": "status-excellent",
        "good": "status-good", 
        "warning": "status-warning",
        "critical": "status-critical",
        "running": "status-running",
        "complete": "status-complete",
        "error": "status-error"
    }
    
    class_name = status_map.get(status, "status-card")
    display_text = label if label else status.title()
    
    return st.markdown(f'<div class="{class_name}">{display_text}</div>', unsafe_allow_html=True)

def create_rag_status(value: str, status: str):
    """Create RAG (Red/Amber/Green) status display"""
    return create_status_indicator(status, value)

def create_performance_indicator(performance: str, value: str = ""):
    """Create performance indicator"""
    display_value = value if value else performance.title()
    return st.markdown(f'<span class="performance-{performance}">{display_value}</span>', unsafe_allow_html=True)

def create_sentiment_indicator(sentiment: str, value: str = ""):
    """Create sentiment indicator"""
    sentiment_map = {"positive": "excellent", "neutral": "good", "negative": "critical"}
    mapped_status = sentiment_map.get(sentiment, sentiment)
    display_value = value if value else sentiment.title()
    return create_status_indicator(mapped_status, display_value)

def create_engagement_indicator(engagement: str, value: str = ""):
    """Create engagement indicator"""
    engagement_map = {"high": "excellent", "medium": "good", "low": "critical"}
    mapped_status = engagement_map.get(engagement, engagement)
    display_value = value if value else engagement.title()
    return create_status_indicator(mapped_status, display_value)

# ===== BUTTON FUNCTIONS =====
def create_primary_button(text: str, key: str = None):
    """Create primary button with perfect styling"""
    return st.button(text, key=key, help=None, type="primary")

def create_secondary_button(text: str, key: str = None):
    """Create secondary button with perfect styling"""
    return st.button(text, key=key, help=None, type="secondary")

def create_action_button(text: str, action_type: str = "apply"):
    """Create action button with specific styling"""
    return st.markdown(f'<button class="{action_type}-button">{text}</button>', unsafe_allow_html=True)

def create_export_button(text: str):
    """Create export button"""
    return create_action_button(text, "export")

def create_audit_button(text: str):
    """Create audit button"""
    return create_action_button(text, "audit")

def create_copy_button(text: str):
    """Create copy button"""
    return create_action_button(text, "copy")

# ===== BADGE FUNCTIONS =====
def create_badge(text: str, badge_type: str = "default"):
    """Create standardized badge"""
    badge_map = {
        "excellent": "badge-excellent",
        "good": "badge-good",
        "warning": "badge-warning", 
        "critical": "badge-critical",
        "strength": "strength-badge",
        "quick-win": "quick-win-badge",
        "pattern": "pattern-tag",
        "default": "badge"
    }
    
    class_name = badge_map.get(badge_type, "badge")
    return st.markdown(f'<span class="{class_name}">{text}</span>', unsafe_allow_html=True)

def create_strength_badge(text: str):
    """Create strength badge"""
    return create_badge(text, "strength")

def create_quick_win_badge(text: str):
    """Create quick win badge"""
    return create_badge(text, "quick-win")

def create_pattern_tag(text: str):
    """Create pattern tag"""
    return create_badge(text, "pattern")

def create_critical_badge(text: str):
    """Create critical badge"""
    return create_badge(text, "critical")

# ===== IMPACT & PRIORITY FUNCTIONS =====
def create_impact_card(content: str, impact_level: str):
    """Create impact card with appropriate styling"""
    return st.markdown(f'<div class="impact-{impact_level}">{content}</div>', unsafe_allow_html=True)

def create_priority_card(content: str, priority_level: str):
    """Create priority card with appropriate styling that renders HTML."""
    st.markdown(f'<div class="priority-{priority_level}">{content}</div>', unsafe_allow_html=True)

def create_success_level_card(content: str, success_level: str):
    """Create success level card"""
    return st.markdown(f'<div class="success-{success_level}">{content}</div>', unsafe_allow_html=True)

# ===== SPECIALIZED CARD FUNCTIONS =====
def create_pattern_card(content: str):
    """Create pattern analysis card"""
    return st.markdown(f'<div class="pattern-card">{content}</div>', unsafe_allow_html=True)

def create_ai_recommendation(content: str):
    """Create AI recommendation card"""
    return st.markdown(f'<div class="ai-recommendation">{content}</div>', unsafe_allow_html=True)

def create_criteria_insight(content: str):
    """Create criteria insight card"""
    return st.markdown(f'<div class="criteria-insight">{content}</div>', unsafe_allow_html=True)

def create_drill_down_section(content: str):
    """Create drill-down section"""
    return st.markdown(f'<div class="drill-down-section">{content}</div>', unsafe_allow_html=True)

def create_audit_section(content: str):
    """Create audit section"""
    return st.markdown(f'<div class="audit-section">{content}</div>', unsafe_allow_html=True)

def create_insights_box(title: str, content: str):
    """Create insights box with title"""
    return st.markdown(f"""
    <div class="insights-box">
        <h4>{title}</h4>
        {content}
    </div>
    """, unsafe_allow_html=True)

def create_comparison_section(content: str):
    """Create comparison section"""
    return st.markdown(f'<div class="comparison-section">{content}</div>', unsafe_allow_html=True)

def create_tier_section(content: str):
    """Create tier analysis section"""
    return st.markdown(f'<div class="tier-section">{content}</div>', unsafe_allow_html=True)

def create_export_section(content: str):
    """Create export section"""
    return st.markdown(f'<div class="export-section">{content}</div>', unsafe_allow_html=True)

def create_persona_quote(quote: str):
    """Create persona quote section"""
    return st.markdown(f'<div class="persona-quote">"{quote}"</div>', unsafe_allow_html=True)

def create_evidence_section(content: str):
    """Create evidence section"""
    return st.markdown(f'<div class="evidence-section">{content}</div>', unsafe_allow_html=True)

def create_copy_example(content: str):
    """Create copy example section"""
    return st.markdown(f'<div class="copy-example">{content}</div>', unsafe_allow_html=True)

# ===== CHART FUNCTIONS =====
def get_perfect_chart_config():
    """Get standardized chart configuration"""
    return {
        'height': 400,
        'color_discrete_sequence': ['#E85A4F', '#2C3E50', '#10b981', '#f59e0b', '#ef4444'],
        'template': 'plotly_white'
    }

def create_perfect_bar_chart(data, x, y, title="", color=None):
    """Create perfectly styled bar chart"""
    config = get_perfect_chart_config()
    fig = px.bar(data, x=x, y=y, title=title, color=color, 
                 color_discrete_sequence=config['color_discrete_sequence'],
                 template=config['template'])
    fig.update_layout(height=config['height'])
    return fig

def create_perfect_line_chart(data, x, y, title="", color=None):
    """Create perfectly styled line chart"""
    config = get_perfect_chart_config()
    fig = px.line(data, x=x, y=y, title=title, color=color,
                  color_discrete_sequence=config['color_discrete_sequence'],
                  template=config['template'])
    fig.update_layout(height=config['height'])
    return fig

def create_perfect_scatter_chart(data, x, y, title="", color=None, size=None):
    """Create perfectly styled scatter chart"""
    config = get_perfect_chart_config()
    fig = px.scatter(data, x=x, y=y, title=title, color=color, size=size,
                     color_discrete_sequence=config['color_discrete_sequence'],
                     template=config['template'])
    fig.update_layout(height=config['height'])
    return fig

def create_perfect_pie_chart(data, values, names, title=""):
    """Create perfectly styled pie chart"""
    config = get_perfect_chart_config()
    fig = px.pie(data, values=values, names=names, title=title,
                 color_discrete_sequence=config['color_discrete_sequence'],
                 template=config['template'])
    fig.update_layout(height=config['height'])
    return fig

def create_perfect_histogram(data, x, title="", nbins=None):
    """Create perfectly styled histogram"""
    config = get_perfect_chart_config()
    fig = px.histogram(data, x=x, title=title, nbins=nbins,
                       color_discrete_sequence=config['color_discrete_sequence'],
                       template=config['template'])
    fig.update_layout(height=config['height'])
    return fig

def apply_chart_styling(fig, config=None):
    """Apply perfect styling to any chart"""
    if config is None:
        config = get_perfect_chart_config()
    
    fig.update_layout(
        height=config['height'],
        font={"family": "Inter, sans-serif", "size": 12, "color": "#2C3E50"},
        template=config['template'],
        paper_bgcolor="white",
        plot_bgcolor="white"
    )
    return fig

# Chart template and colors for backward compatibility
chart_template = {
    "layout": {
        "font": {"family": "Inter, sans-serif", "size": 12, "color": "#2C3E50"},
        "title": {"font": {"family": "Crimson Text, serif", "size": 16, "color": "#2C3E50"}}
    }
}

colors = {
    "primary": "#E85A4F",
    "secondary": "#2C3E50", 
    "background": "white",
    "chart_colors": ["#E85A4F", "#2C3E50", "#10b981", "#f59e0b", "#ef4444"]
}

# ===== LAYOUT FUNCTIONS =====
def create_two_column_layout():
    """Create standardized two-column layout"""
    return st.columns(2)

def create_three_column_layout():
    """Create standardized three-column layout"""
    return st.columns(3)

def create_four_column_layout():
    """Create standardized four-column layout"""
    return st.columns(4)

def create_custom_column_layout(ratios):
    """Create custom column layout with specified ratios"""
    return st.columns(ratios)

# ===== UTILITY FUNCTIONS =====
def get_status_color(status: str):
    """Get color for status"""
    color_map = {
        "excellent": "#10b981",
        "good": "#059669", 
        "warning": "#f59e0b",
        "critical": "#ef4444",
        "running": "#f59e0b",
        "complete": "#34c759",
        "error": "#ff3b30"
    }
    return color_map.get(status, "#6B7280")

def get_performance_color(performance: str):
    """Get color for performance level"""
    color_map = {
        "excellent": "#34c759",
        "good": "#ffb800", 
        "fair": "#ff9500"
    }
    return color_map.get(performance, "#6B7280")

def create_spacer(height: int = 1):
    """Create vertical spacer"""
    for _ in range(height):
        st.write("")

def create_divider():
    """Create visual divider"""
    st.divider()

# ===== DATA DISPLAY FUNCTIONS =====
def create_data_table(data, **kwargs):
    """
    Creates a standardized, container-width data table that accepts all
    native st.dataframe arguments like `column_config`, `height`, etc.
    This ensures flexibility while maintaining consistent styling.
    """
    # Set use_container_width to True by default, but allow overriding
    if 'use_container_width' not in kwargs:
        kwargs['use_container_width'] = True
    return st.dataframe(data, **kwargs)

def create_metric_grid(metrics_data):
    """Create bulletproof grid of metrics using Streamlit native"""
    cols = st.columns(len(metrics_data))
    for i, metric_info in enumerate(metrics_data):
        with cols[i]:
            if len(metric_info) == 3:
                value, label, delta = metric_info
                st.metric(label, value, delta)
            else:
                value, label = metric_info[:2]
                st.metric(label, value)

# ===== BULLETPROOF ALERT FUNCTIONS =====
def create_alert(message: str, alert_type: str = "info"):
    """Create bulletproof alert using Streamlit's native components"""
    if alert_type == "success":
        return st.success(message)
    elif alert_type == "error":
        return st.error(message)
    elif alert_type == "warning":
        return st.warning(message)
    else:  # info
        return st.info(message)

def create_info_alert(message: str):
    """Create info alert using Streamlit native"""
    return st.info(message)

def create_success_alert(message: str):
    """Create success alert using Streamlit native"""
    return st.success(message)

def create_warning_alert(message: str):
    """Create warning alert using Streamlit native"""
    return st.warning(message)

def create_error_alert(message: str):
    """Create error alert using Streamlit native"""
    return st.error(message)

# ===== FORM FUNCTIONS =====
def create_form_group(label: str, widget_func, *args, **kwargs):
    """Create standardized form group"""
    st.markdown(f'<label class="form-label">{label}</label>', unsafe_allow_html=True)
    return widget_func(*args, **kwargs)

# ===== EXPORT FUNCTIONS =====
def create_download_button(data, filename: str, label: str = "Download"):
    """Create standardized download button"""
    return st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime="text/csv" if filename.endswith('.csv') else "application/octet-stream"
    )

# ===== MAIN STYLING APPLICATION =====
def initialize_perfect_styling():
    """Initialize perfect styling for the entire dashboard"""
    apply_perfect_styling()
    
    # Set page config if not already set
    try:
        st.set_page_config(
            page_title="Brand Health Command Center",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    except:
        pass  # Page config already set

# (no bottom-of-module call)

# Example usage template for pages:
"""
# At the top of every page file:

import streamlit as st
from perfect_styling_method import apply_perfect_styling, create_page_header, create_metric_card

# Apply styling (REQUIRED - call this first)
apply_perfect_styling()

# Create page header
create_page_header("Page Title", "Optional subtitle")

# Use standardized components
create_metric_card("Total Users", "1,234", "+12%", "excellent")

# Use standardized chart config
import plotly.express as px
from perfect_styling_method import get_chart_config, apply_chart_styling

fig = px.bar(data, x='category', y='value')
fig = apply_chart_styling(fig)
st.plotly_chart(fig, use_container_width=True)

# Use standardized layouts
from perfect_styling_method import create_columns, display_dataframe

col1, col2 = create_columns([1, 2])
with col1:
    st.write("Left column")
with col2:
    display_dataframe(df)
""" 