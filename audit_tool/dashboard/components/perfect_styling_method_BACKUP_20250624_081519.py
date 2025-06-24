#!/usr/bin/env python3
"""
PERFECT STYLING METHOD
Single source of truth for ALL styling across the dashboard
Replaces 2,228 chaotic styling methods with ONE standardized approach
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64

# Load CSS once
def load_perfect_css():
    """Load the perfect stylesheet once"""
    css_file = Path(__file__).parent / "perfect_stylesheet.css"
    if css_file.exists():
        with open(css_file, 'r') as f:
            return f.read()
    return ""

# Global CSS injection
_CSS_LOADED = False

def apply_perfect_styling():
    """Apply reliable styling using the proven brand_styling.py approach"""
    global _CSS_LOADED
    if not _CSS_LOADED:
        # Use the proven CSS from brand_styling.py - NO JavaScript needed!
        st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
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
                color: var(--secondary-color);
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
            
            /* Clean header styling */
            .main-header, .custom-header {
                background: var(--background);
                border-left: 4px solid var(--primary-color);
                color: var(--secondary-color);
                padding: 1rem 1.5rem;
                border-radius: 8px;
                margin-bottom: 1.5rem;
                border: 1px solid var(--gray-border);
            }
            
            .main-header h1, .custom-header h1 {
                font-family: var(--font-serif);
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
                color: var(--secondary-color);
                margin: 0;
            }
            
            .main-header p, .custom-header p {
                font-family: var(--font-primary);
                font-size: 1rem;
                font-weight: 400;
                color: #666;
                margin: 0.5rem 0 0 0;
            }
            
            /* Standard card styling */
            .brand-card, .persona-card, .matrix-card, .opportunity-card, .success-card, .report-card {
                background: var(--background);
                padding: 1.5rem;
                border-radius: 10px;
                border-left: 4px solid var(--primary-color);
                border: 1px solid var(--gray-border);
                margin-bottom: 1rem;
            }
            
            /* Metric cards */
            .metric-card {
                background: var(--background);
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border: 1px solid var(--gray-border);
                border-left: 4px solid var(--primary-color);
                margin-bottom: 1rem;
                font-family: var(--font-primary);
            }
            
            .metric-card.critical {
                border-left-color: var(--red-status);
            }
            
            .metric-card.warning {
                border-left-color: var(--yellow-status);
            }
            
            .metric-card.fair {
                border-left-color: var(--orange-status);
            }
            
            .metric-value {
                font-size: 2.5rem;
                font-weight: 700;
                margin: 0;
                line-height: 1;
                color: var(--secondary-color);
            }
            
            .metric-label {
                font-size: 0.9rem;
                color: #666;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-top: 0.5rem;
                font-family: var(--font-primary);
                font-weight: 500;
            }
            
            /* BULLETPROOF STREAMLIT METRICS - The key fix! */
            [data-testid="metric-container"] {
                background: white !important;
                border: 1px solid var(--gray-border) !important;
                border-left: 4px solid var(--primary-color) !important;
                padding: 1rem !important;
                border-radius: 8px !important;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            }
            
            [data-testid="metric-container"] > div {
                font-family: var(--font-primary) !important;
            }
            
            [data-testid="metric-container"] [data-testid="metric-value"] {
                color: var(--secondary-color) !important;
                font-weight: 600 !important;
            }
            
            /* Tab styling - COMPREHENSIVE FIX */
            .stTabs [data-baseweb="tab-list"] {
                gap: 4px !important;
                background: transparent !important;
                border-bottom: none !important;
                padding: 0 !important;
                margin-bottom: 1rem !important;
            }
            
            /* ALL TABS - Default inactive state (white background) */
            .stTabs [data-baseweb="tab"] {
                font-family: var(--font-primary) !important;
                font-weight: 500 !important;
                background-color: white !important;
                background: white !important;
                color: var(--secondary-color) !important;
                border: 1px solid var(--gray-border) !important;
                border-radius: 6px !important;
                padding: 0.5rem 1rem !important;
                margin: 0 2px !important;
                min-height: 40px !important;
                transition: all 0.2s ease !important;
            }
            
            /* ACTIVE TAB - Primary color background */
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: var(--primary-color) !important;
                background: var(--primary-color) !important;
                color: white !important;
                border-color: var(--primary-color) !important;
                font-weight: 600 !important;
                box-shadow: 0 2px 4px rgba(232, 90, 79, 0.3) !important;
            }
            
            /* Override Streamlit's default section headers */
            .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
                font-family: var(--font-serif) !important;
                color: var(--secondary-color) !important;
                font-weight: 600 !important;
                padding: 0 !important;
                margin: 1rem 0 0.5rem 0 !important;
                background: none !important;
                border: none !important;
                border-radius: 0 !important;
            }
            
            /* Specific styling for h2 section headers */
            .main h2 {
                font-size: 1.4rem;
                border-left: 3px solid var(--primary-color);
                padding-left: 0.75rem;
                margin: 1.5rem 0 1rem 0;
                background: rgba(232, 90, 79, 0.05) !important;
                padding: 0.5rem 0.75rem;
                border-radius: 4px;
            }
            
            /* Status colors */
            .status-excellent, .sentiment-positive, .engagement-high { color: var(--green-status); }
            .status-good, .sentiment-neutral, .engagement-medium { color: var(--yellow-status); }
            .status-fair, .performance-fair { color: var(--orange-status); }
            .status-critical, .sentiment-negative, .engagement-low { color: var(--red-status); }
            
            /* Performance indicators */
            .performance-excellent { color: var(--green-status); font-weight: 600; }
            .performance-good { color: var(--yellow-status); font-weight: 600; }
            .performance-fair { color: var(--orange-status); font-weight: 600; }
            
            /* Streamlit Link Styling */
            a {
                color: var(--primary-color);
                text-decoration: none;
            }
            
            a:hover {
                color: var(--primary-hover);
                text-decoration: underline;
            }
        </style>
        """, unsafe_allow_html=True)
        _CSS_LOADED = True

# ===== HEADER FUNCTIONS =====
def create_main_header(title: str, subtitle: str = ""):
    """Create bulletproof main page header"""
    if subtitle:
        st.markdown(f"""
        <div class="custom-header">
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="custom-header">
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
def create_metric_card(value: str, label: str, status: str = "default"):
    """Create standardized metric card"""
    status_class = f"metric-card {status}" if status != "default" else "metric-card"
    return st.markdown(f"""
    <div class="{status_class}">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

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
    """Create standardized content card"""
    st.markdown(f'<div class="{card_type}-card">{content}</div>', unsafe_allow_html=True)

def create_brand_card(content: str):
    """Create brand-specific card"""
    create_content_card(content, "brand")

def create_persona_card(content: str):
    """Create persona-specific card"""
    create_content_card(content, "persona")

def create_matrix_card(content: str):
    """Create matrix-specific card"""
    create_content_card(content, "matrix")

def create_opportunity_card(content: str):
    """Create opportunity-specific card"""
    create_content_card(content, "opportunity")

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
    """Create priority card with appropriate styling"""
    return st.markdown(f'<div class="priority-{priority_level}">{content}</div>', unsafe_allow_html=True)

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
def create_data_table(data, use_container_width=True):
    """Create standardized data table"""
    return st.dataframe(data, use_container_width=use_container_width)

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

# Auto-apply styling when module is imported
initialize_perfect_styling()

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