"""
Centralized brand styling for all dashboard pages
Matches the home page (brand_health_command_center.py) styling exactly
"""

import os
from pathlib import Path

def get_brand_css_rules():
    """Return raw CSS rules from perfect_stylesheet.css"""
    css_file_path = Path(__file__).parent / "perfect_stylesheet.css"
    
    try:
        with open(css_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to basic CSS if file not found
        return """
        :root {
            --primary-color: #E85A4F;
            --secondary-color: #2C3E50;
            --gray-border: #D1D5DB;
        }
        
        .main-header {
            background: white;
            border-left: 4px solid var(--primary-color);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 1px solid var(--gray-border);
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid var(--gray-border);
            border-left: 4px solid var(--primary-color);
            margin-bottom: 1rem;
        }
        
        /* Remove ALL borders from raw Streamlit components */
        .element-container,
        .stMarkdown,
        .stTabs,
        .stExpander,
        .stColumns,
        .stColumn,
        div[data-testid="column"],
        div[data-testid="stExpander"],
        div[data-testid="stMarkdown"],
        div[data-testid="stTabs"],
        .block-container > div,
        .main > div,
        .stApp > div {
            border: none !important;
            box-shadow: none !important;
            background: transparent !important;
        }
        
        /* Override any remaining borders */
        * {
            border: none !important;
            box-shadow: none !important;
        }
        
        /* Restore borders ONLY for our styled components */
        .metric-card,
        .main-header {
            border: 1px solid var(--gray-border) !important;
            border-left: 4px solid var(--primary-color) !important;
        }
        """

def get_google_fonts_css():
    """Return Google Fonts CSS - only use if fonts not already loaded"""
    return """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:wght@400;600;700&display=swap" rel="stylesheet">
"""

def get_brand_css():
    """Compatibility function - wraps raw CSS in style tags"""
    return f"<style>{get_brand_css_rules()}</style>"

def get_complete_brand_css():
    """Return complete CSS including Google Fonts - for pages that need everything"""
    return get_google_fonts_css() + get_brand_css() 