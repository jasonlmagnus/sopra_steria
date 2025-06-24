"""
Centralized brand styling for all dashboard pages
Matches the home page (brand_health_command_center.py) styling exactly
"""

def get_brand_css():
    """Return brand CSS styling for the dashboard"""
    return """
<style>
    /* ---- CUSTOM LAYOUT FIX ---- */
    .main .block-container {
        max-width: 1400px;
        margin: 0 auto;
    }
    /* ---- END CUSTOM LAYOUT FIX ---- */

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
    .main-header {
        background: var(--background);
        border-left: 4px solid var(--primary-color);
        color: var(--secondary-color);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid var(--gray-border);
    }
    
    .main-header h1 {
        font-family: var(--font-serif);
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.25rem;
        color: var(--secondary-color);
    }
    
    .main-header p {
        font-family: var(--font-primary);
        font-size: 1rem;
        font-weight: 400;
        color: #666;
        margin: 0;
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
    
    /* Status colors */
    .status-excellent, .sentiment-positive, .engagement-high { color: var(--green-status); }
    .status-good, .sentiment-neutral, .engagement-medium { color: var(--yellow-status); }
    .status-fair, .performance-fair { color: var(--orange-status); }
    .status-critical, .sentiment-negative, .engagement-low { color: var(--red-status); }
    
    /* Performance indicators */
    .performance-excellent { color: var(--green-status); font-weight: 600; }
    .performance-good { color: var(--yellow-status); font-weight: 600; }
    .performance-fair { color: var(--orange-status); font-weight: 600; }
    
    /* Info sections */
    .insights-box, .comparison-section, .tier-section, .export-section {
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
    
    /* Quote and evidence styling */
    .persona-quote, .evidence-section {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
        font-style: italic;
        color: var(--secondary-color);
    }
    
    /* Pattern and insight sections */
    .pattern-card, .ai-recommendation, .criteria-insight {
        background: #f0f9ff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid var(--primary-color);
        margin: 1rem 0;
    }
    
    .drill-down-section, .audit-section {
        background: #fef7cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    
    /* Copy examples */
    .copy-example {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--gray-border);
        margin: 0.5rem 0;
        font-family: "Inter", monospace;
        color: var(--secondary-color);
    }
    
    /* Badges and tags */
    .strength-badge, .quick-win-badge {
        background: var(--green-status);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
        font-family: var(--font-primary);
    }
    
    .pattern-tag {
        background: var(--primary-color);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
        font-family: var(--font-primary);
    }
    
    .critical-badge {
        background: var(--red-status);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-family: var(--font-primary);
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Action buttons */
    .apply-button, .action-button, .nav-button {
        background: var(--green-status);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        font-family: var(--font-primary);
    }
    
    .apply-button:hover {
        background: #059669;
    }
    
    .export-button {
        background: var(--primary-color);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        font-family: var(--font-primary);
    }
    
    .export-button:hover {
        background: var(--primary-hover);
        color: white;
    }
    
    .audit-button {
        background: #f59e0b;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        text-decoration: none;
        display: inline-block;
        margin: 0.25rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        font-family: var(--font-primary);
    }
    
    .audit-button:hover {
        background: #d97706;
    }
    
    .copy-button {
        background: #6b7280;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        cursor: pointer;
        float: right;
        font-family: var(--font-primary);
    }
    
    .copy-button:hover {
        background: #4b5563;
    }
    
    /* Impact level styling */
    .impact-high {
        border-left-color: #dc2626;
        background: #fef2f2;
    }
    
    .impact-medium {
        border-left-color: #f59e0b;
        background: #fffbeb;
    }
    
    .impact-low {
        border-left-color: var(--green-status);
        background: #f0fdf4;
    }
    
    /* Priority styling */
    .priority-urgent {
        background: #fee2e2;
        border: 2px solid #dc2626;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .priority-high {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .priority-medium {
        background: #f0fdf4;
        border: 2px solid var(--green-status);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Success level styling */
    .success-excellent {
        border-left-color: #059669;
        background: #f0fdf4;
    }
    
    .success-good {
        border-left-color: var(--green-status);
        background: #f0fdf4;
    }
    
    /* Status indicators */
    .status-running {
        color: #f59e0b;
        font-weight: 600;
    }
    
    .status-complete {
        color: var(--green-status);
        font-weight: 600;
    }
    
    .status-error {
        color: var(--red-status);
        font-weight: 600;
    }
    
    /* Score display */
    .impact-score {
        font-size: 1.5rem;
        font-weight: 600;
        text-align: center;
        color: var(--secondary-color);
    }
    
    /* Data table */
    .data-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid var(--gray-border);
    }
    
    /* Streamlit component styling */
    .stSelectbox > div > div, .stSlider > div > div, .stNumberInput > div > div {
        font-family: var(--font-primary);
    }
    
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 6px;
        font-family: var(--font-primary);
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background-color: var(--primary-hover);
        color: white;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid var(--gray-border);
        border-left: 4px solid var(--primary-color);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    [data-testid="metric-container"] > div {
        font-family: var(--font-primary);
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: var(--secondary-color);
        font-weight: 600;
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
    
    /* HOVER STATES */
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background-color: #F9FAFB !important;
        background: #F9FAFB !important;
        border-color: #9CA3AF !important;
        transform: translateY(-1px) !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"]:hover {
        background-color: var(--primary-hover) !important;
        background: var(--primary-hover) !important;
        border-color: var(--primary-hover) !important;
    }
    
    /* FOCUS STATES */
    .stTabs [data-baseweb="tab"]:focus {
        outline: 2px solid var(--primary-color) !important;
        outline-offset: 2px !important;
    }
    
    /* Tab content area */
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 1rem !important;
        border: none !important;
    }
    
    /* NUCLEAR OPTION - Force styling with highest specificity */
    div[data-testid="stTabs"] div[role="tablist"] button {
        background-color: white !important;
        color: var(--secondary-color) !important;
        border: 1px solid var(--gray-border) !important;
        border-radius: 6px !important;
        font-family: var(--font-primary) !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
        margin: 0 2px !important;
    }
    
    div[data-testid="stTabs"] div[role="tablist"] button[aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
        font-weight: 600 !important;
    }
    
    /* Override any Streamlit default tab styling */
    .stTabs > div > div > div > div {
        border-bottom: none !important;
    }
    
    .stTabs > div > div > div > div > div {
        background: white !important;
        border: 1px solid var(--gray-border) !important;
        border-radius: 6px !important;
    }
    
    .stTabs > div > div > div > div > div[aria-selected="true"] {
        background: var(--primary-color) !important;
        color: white !important;
        border-color: var(--primary-color) !important;
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
    
    /* Specific styling for h3 subsection headers */
    .main h3 {
        font-size: 1.2rem;
        color: var(--secondary-color);
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
    }
    
    /* Remove any colored backgrounds from section containers */
    .stMarkdown div[data-testid="stMarkdownContainer"] {
        background: none !important;
    }
    
    /* Target Streamlit's auto-generated header styling */
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3 {
        background: none !important;
        border: none !important;
        color: var(--secondary-color) !important;
        font-family: var(--font-serif) !important;
        padding: 0.25rem 0 !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Override the colored header banners completely */
    .stMarkdown > div > div > div {
        background: none !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Force remove any element-ui header styling */
    .element-container div[data-testid="stMarkdownContainer"] h2 {
        background: rgba(232, 90, 79, 0.05) !important;
        border-left: 3px solid var(--primary-color) !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 4px !important;
        font-size: 1.3rem !important;
        margin: 1rem 0 0.75rem 0 !important;
    }
    
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
"""

def get_google_fonts_css():
    """Return Google Fonts CSS - only use if fonts not already loaded"""
    return """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:wght@400;600;700&display=swap" rel="stylesheet">
"""

def get_complete_brand_css():
    """Return complete CSS including Google Fonts - for pages that need everything"""
    return get_google_fonts_css() + get_brand_css() 