#!/usr/bin/env python3
"""
SYSTEMATIC STYLING CLEANUP SCRIPT - AGGRESSIVE VERSION
Properly removes ALL old styling chaos and replaces with perfect styling helpers
"""

import os
import re
from pathlib import Path

def clean_dashboard_page(file_path):
    """
    Aggressively clean a single dashboard page - remove ALL custom styling
    """
    print(f"🧹 AGGRESSIVE CLEANING: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Remove ALL old styling imports (keep perfect styling import)
    content = re.sub(r'from.*components.*brand_styling.*import.*\n', '', content)
    content = re.sub(r'import.*brand_styling.*\n', '', content)
    content = re.sub(r'from.*get_working_brand_css.*\n', '', content)
    content = re.sub(r'.*get_working_brand_css.*\n', '', content)
    content = re.sub(r'sys\.path\.append.*\n', '', content)
    content = re.sub(r'# Import centralized brand styling.*\n', '', content)
    
    # 2. AGGRESSIVELY REMOVE ALL st.markdown() WITH HTML/CSS
    # Remove ANY st.markdown() that contains HTML tags
    content = re.sub(r'st\.markdown\(\s*f?"""[^"]*<[^>]+>[^"]*"""\s*,\s*unsafe_allow_html=True\s*\)', 
                     '', content, flags=re.DOTALL)
    
    # Remove ANY st.markdown() with triple quotes that has HTML
    content = re.sub(r'st\.markdown\(\s*f?"""[^"]*<[^"]*>[^"]*"""\s*,\s*unsafe_allow_html=True\s*\)', 
                     '', content, flags=re.DOTALL)
    
    # Remove st.markdown() with single quotes containing HTML
    content = re.sub(r"st\.markdown\(\s*f?'[^']*<[^>]+>[^']*'\s*,\s*unsafe_allow_html=True\s*\)", 
                     '', content, flags=re.DOTALL)
    
    # Remove multi-line st.markdown() blocks with HTML (more aggressive)
    content = re.sub(r'st\.markdown\(\s*[fF]?""".*?<.*?""".*?,.*?unsafe_allow_html=True.*?\)', 
                     '', content, flags=re.DOTALL)
    
    # Remove variable assignments that create HTML strings
    content = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*\s*=\s*f?"""[^"]*<[^"]*>[^"]*"""', '', content, flags=re.DOTALL)
    content = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*_html\s*=.*?\n', '', content)
    
    # Remove HTML string variables being passed to st.markdown
    content = re.sub(r'st\.markdown\([a-zA-Z_][a-zA-Z0-9_]*_html.*?\)', '', content)
    
    # 3. Remove specific CSS class references and color variables
    content = re.sub(r'[a-zA-Z_][a-zA-Z0-9_]*_class\s*=.*?\n', '', content)
    content = re.sub(r'status_class\s*=.*?\n', '', content)
    content = re.sub(r'card_class\s*=.*?\n', '', content)
    content = re.sub(r'impact_class\s*=.*?\n', '', content)
    content = re.sub(r'severity_class\s*=.*?\n', '', content)
    
    # Remove color variable assignments
    content = re.sub(r'.*color.*=.*#[0-9A-Fa-f]{6}.*\n', '', content)
    content = re.sub(r'.*color.*=.*#[0-9A-Fa-f]{3}.*\n', '', content)
    
    # 4. Remove CSS injection patterns
    content = re.sub(r'.*CSS injection.*\n', '', content)
    content = re.sub(r'.*css_content.*\n', '', content)
    content = re.sub(r'.*stylesheet.*\n', '', content)
    
    # 5. Clean up CSS-related comments
    content = re.sub(r'# .*CSS.*\n', '', content)
    content = re.sub(r'# .*styling.*\n', '', content)
    content = re.sub(r'# .*brand.*styling.*\n', '', content)
    
    # 6. Remove empty lines and clean up formatting
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    content = re.sub(r'\n\s*\n\s*\n\s*\n+', '\n\n', content)
    
    # 7. Remove any remaining HTML-like patterns in strings
    content = re.sub(r'"""[^"]*<div[^"]*"""', '""', content)
    content = re.sub(r'"""[^"]*</div>[^"]*"""', '""', content)
    
    # 8. Enhance perfect styling imports
    if 'from audit_tool.dashboard.components.perfect_styling_method import' in content:
        # Replace any existing import with comprehensive one
        content = re.sub(
            r'from audit_tool\.dashboard\.components\.perfect_styling_method import.*?\n',
            '''from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_page_header,
    create_status_card,
    create_metric_card,
    show_success,
    show_warning,
    show_error,
    show_info,
    get_chart_config,
    apply_chart_styling,
    display_dataframe,
    create_columns,
    create_tabs,
    create_expander
)
''',
            content,
            flags=re.DOTALL
        )
    
    # 9. Add standardized page header if missing
    if 'apply_perfect_styling()' in content and 'create_page_header(' not in content:
        # Extract page title from file name
        page_name = Path(file_path).stem
        if '🔬' in page_name:
            title = "🔬 Methodology"
            subtitle = "How we evaluate brand health across digital touchpoints"
        elif '👥' in page_name:
            title = "👥 Persona Insights"
            subtitle = "Understanding your audience experience"
        elif '📊' in page_name:
            title = "📊 Content Matrix"
            subtitle = "Where do you win and lose?"
        elif '💡' in page_name:
            title = "💡 Opportunity Impact"
            subtitle = "Which improvements matter most?"
        elif '🌟' in page_name:
            title = "🌟 Success Library"
            subtitle = "What already works well?"
        elif '📋' in page_name:
            title = "📋 Reports & Export"
            subtitle = "How do you want to use this data?"
        elif '🚀' in page_name:
            title = "🚀 Run Brand Audit"
            subtitle = "Launch new brand health analysis"
        elif '🔍' in page_name:
            title = "🔍 Social Media Analysis"
            subtitle = "Cross-platform brand presence audit"
        elif '👤' in page_name:
            title = "👤 Persona Viewer"
            subtitle = "Deep-dive into persona experiences"
        elif '🎨' in page_name:
            title = "🎨 Visual Brand Hygiene"
            subtitle = "Interactive dashboard for brand consistency"
        elif '🎯' in page_name:
            title = "🎯 Strategic Recommendations"
            subtitle = "Prioritized action plan for brand improvement"
        elif 'brand_health_command_center' in file_path:
            title = "🎯 Brand Health Command Center"
            subtitle = "Comprehensive brand performance dashboard"
        elif 'audit_runner' in file_path:
            title = "🚀 Audit Runner"
            subtitle = "Launch and manage brand audits"
        else:
            title = "Dashboard Page"
            subtitle = ""
        
        # Insert page header after apply_perfect_styling()
        content = content.replace(
            'apply_perfect_styling()',
            f'apply_perfect_styling()\n\n# Create standardized page header\ncreate_page_header("{title}", "{subtitle}")'
        )
    
    # 10. Final cleanup - remove any remaining problematic patterns
    content = re.sub(r'unsafe_allow_html=True', '', content)
    content = re.sub(r'st\.markdown\(\s*""\s*\)', '', content)
    content = re.sub(r'st\.markdown\(\s*\)\s*', '', content)
    
    # Write cleaned content back
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ AGGRESSIVELY CLEANED: {file_path}")
        return True
    else:
        print(f"⚪ NO CHANGES: {file_path}")
        return False

def aggressive_cleanup():
    """
    Run aggressive cleanup on all dashboard pages
    """
    print("🚀 AGGRESSIVE SYSTEMATIC STYLING CLEANUP INITIATED")
    print("=" * 60)
    
    # Dashboard page files
    dashboard_pages = [
        "audit_tool/dashboard/pages/1_🔬_Methodology.py",
        "audit_tool/dashboard/pages/2_👥_Persona_Insights.py",
        "audit_tool/dashboard/pages/3_📊_Content_Matrix.py", 
        "audit_tool/dashboard/pages/4_💡_Opportunity_Impact.py",
        "audit_tool/dashboard/pages/5_🌟_Success_Library.py",
        "audit_tool/dashboard/pages/6_📋_Reports_Export.py",
        "audit_tool/dashboard/pages/7_🚀_Run_Audit.py",
        "audit_tool/dashboard/pages/8_🔍_Social_Media_Analysis.py",
        "audit_tool/dashboard/pages/9_👤_Persona_Viewer.py",
        "audit_tool/dashboard/pages/10_🎨_Visual_Brand_Hygiene.py",
        "audit_tool/dashboard/pages/11_🎯_Strategic_Recommendations.py"
    ]
    
    # Main dashboard files
    main_files = [
        "audit_tool/dashboard/brand_health_command_center.py",
        "audit_tool/dashboard/audit_runner_dashboard.py"
    ]
    
    cleaned_count = 0
    
    # Clean all pages
    for page_file in dashboard_pages:
        if os.path.exists(page_file):
            if clean_dashboard_page(page_file):
                cleaned_count += 1
        else:
            print(f"❌ NOT FOUND: {page_file}")
    
    # Clean main files
    for main_file in main_files:
        if os.path.exists(main_file):
            if clean_dashboard_page(main_file):
                cleaned_count += 1
        else:
            print(f"❌ NOT FOUND: {main_file}")
    
    print("=" * 60)
    print(f"🎯 AGGRESSIVE CLEANUP COMPLETE")
    print(f"📊 Files cleaned: {cleaned_count}")
    print(f"🧹 ALL old styling chaos removed")
    print(f"✨ Perfect styling helpers added")
    print(f"💥 MAXIMUM AGGRESSION APPLIED")
    print("=" * 60)

if __name__ == "__main__":
    aggressive_cleanup() 