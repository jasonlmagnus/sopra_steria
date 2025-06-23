"""
Brand Health Command Center - Color Scheme & Typography Configuration
"""

# Color Palette
BRAND_COLORS = {
    # Primary Colors
    "primary": "#E85A4F",           # Warm coral/red-orange
    "primary_hover": "#d44a3a",     # Darker version for hover states
    "secondary": "#2C3E50",         # Dark blue-gray
    
    # Supporting Colors
    "gray_border": "#D1D5DB",       # Gray-300 for borders
    "background": "#FFFFFF",        # White background
    "text_selection": "#E85A4F",    # Text selection background
    
    # Status Colors
    "green_status": "#34c759",      # Success/good
    "yellow_status": "#ffb800",     # Warning/fair
    "red_status": "#ff3b30",        # Critical/error
    "orange_status": "#ff9500",     # Moderate warning
}

# Typography
BRAND_FONTS = {
    "primary": "Inter",             # Modern sans-serif for body text and UI
    "secondary": "Crimson Text",    # Serif font for headings and emphasis
}

# Font Weights
FONT_WEIGHTS = {
    "light": 300,
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
}

# Google Fonts URL
GOOGLE_FONTS_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Crimson+Text:wght@400;600;700&display=swap"

# CSS Variables String for Streamlit
CSS_VARIABLES = f"""
    :root {{
        --primary-color: {BRAND_COLORS['primary']};
        --primary-hover: {BRAND_COLORS['primary_hover']};
        --secondary-color: {BRAND_COLORS['secondary']};
        --gray-border: {BRAND_COLORS['gray_border']};
        --background: {BRAND_COLORS['background']};
        --text-selection: {BRAND_COLORS['text_selection']};
        --green-status: {BRAND_COLORS['green_status']};
        --yellow-status: {BRAND_COLORS['yellow_status']};
        --red-status: {BRAND_COLORS['red_status']};
        --orange-status: {BRAND_COLORS['orange_status']};
        --font-primary: "{BRAND_FONTS['primary']}", sans-serif;
        --font-serif: "{BRAND_FONTS['secondary']}", serif;
    }}
""" 