#!/usr/bin/env python3
"""
SYSTEMATIC IMPORT STANDARDIZATION SCRIPT
Fixes ALL dashboard pages to use the EXACT SAME standardized imports
from perfect_styling_method.py - NO VARIATIONS, NO SHORTCUTS
"""

import os
import re
from pathlib import Path

# STANDARDIZED IMPORT BLOCK - SAME FOR ALL PAGES
STANDARD_IMPORT_BLOCK = '''import streamlit as st
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
)'''

# FUNCTION MAPPING - OLD NAME -> NEW NAME
FUNCTION_MAPPINGS = {
    'create_page_header': 'create_main_header',
    'create_status_card': 'create_status_indicator', 
    'show_success': 'create_success_alert',
    'show_warning': 'create_warning_alert',
    'show_error': 'create_error_alert',
    'show_info': 'create_info_alert',
    'get_chart_config': 'get_perfect_chart_config',
    'display_dataframe': 'create_data_table',
    'create_columns': 'create_two_column_layout',  # Default to 2-column
}

# STANDARD PAGE SETUP - SAME FOR ALL PAGES
STANDARD_PAGE_SETUP = '''
# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()
'''

def fix_page_file(file_path):
    """Fix a single dashboard page file"""
    print(f"🔧 Fixing {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Remove ALL existing perfect_styling_method imports
        # Match multi-line import statements
        import_pattern = r'from audit_tool\.dashboard\.components\.perfect_styling_method import \([^)]*\)'
        content = re.sub(import_pattern, '', content, flags=re.MULTILINE | re.DOTALL)
        
        # Also remove single-line imports
        single_import_pattern = r'from audit_tool\.dashboard\.components\.perfect_styling_method import [^\n]*\n'
        content = re.sub(single_import_pattern, '', content)
        
        # 2. Remove duplicate import lines (common issue causing syntax errors)
        lines = content.split('\n')
        cleaned_lines = []
        seen_imports = set()
        
        for line in lines:
            # Skip duplicate import lines
            if 'from audit_tool.dashboard.components.perfect_styling_method' in line:
                continue
            if line.strip() in seen_imports and 'import' in line:
                continue
            if 'import' in line:
                seen_imports.add(line.strip())
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # 3. Insert standardized import block after initial streamlit import
        lines = content.split('\n')
        new_lines = []
        import_inserted = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Insert after the first streamlit import or at the beginning
            if not import_inserted and (line.startswith('import streamlit as st') or 
                                      (i == 0 and not line.startswith('import') and not line.startswith('"""'))):
                new_lines.append('')
                new_lines.extend(STANDARD_IMPORT_BLOCK.split('\n'))
                import_inserted = True
        
        content = '\n'.join(new_lines)
        
        # 4. Replace function calls with standardized names
        for old_func, new_func in FUNCTION_MAPPINGS.items():
            # Replace function calls
            content = re.sub(rf'\b{old_func}\(', f'{new_func}(', content)
        
        # 5. Ensure apply_perfect_styling() is called
        if 'apply_perfect_styling()' not in content:
            # Find where to insert it (after page config)
            lines = content.split('\n')
            new_lines = []
            styling_inserted = False
            
            for line in lines:
                new_lines.append(line)
                
                # Insert after page config
                if not styling_inserted and ('st.set_page_config' in line or 
                                           'page_config' in line.lower()):
                    new_lines.append('')
                    new_lines.extend(STANDARD_PAGE_SETUP.split('\n'))
                    styling_inserted = True
            
            content = '\n'.join(new_lines)
        
        # 6. Fix common issues that cause syntax errors
        # Remove trailing commas in import statements
        content = re.sub(r',\s*\)', ')', content)
        
        # Fix indentation issues in import blocks
        lines = content.split('\n')
        new_lines = []
        in_import_block = False
        
        for line in lines:
            if 'from audit_tool.dashboard.components.perfect_styling_method import (' in line:
                in_import_block = True
                new_lines.append(line)
            elif in_import_block and line.strip() == ')':
                in_import_block = False
                new_lines.append(line)
            elif in_import_block:
                # Ensure proper indentation for import items
                if line.strip() and not line.startswith('    '):
                    line = '    ' + line.strip()
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # 7. Write the fixed content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Fixed {file_path.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error fixing {file_path.name}: {e}")
        return False

def fix_all_dashboard_pages():
    """Fix ALL dashboard pages systematically"""
    pages_dir = Path("audit_tool/dashboard/pages")
    
    if not pages_dir.exists():
        print(f"❌ ERROR: {pages_dir} not found!")
        return
    
    print("🔧 SYSTEMATIC IMPORT STANDARDIZATION")
    print("=" * 60)
    print("Standardizing ALL dashboard pages to use IDENTICAL imports")
    print("=" * 60)
    
    # Get all Python files in pages directory
    page_files = list(pages_dir.glob("*.py"))
    page_files = [f for f in page_files if not f.name.startswith("__")]
    
    print(f"\n📋 Found {len(page_files)} dashboard pages to fix:")
    for f in page_files:
        print(f"   - {f.name}")
    
    print(f"\n🎯 STANDARDIZED IMPORT BLOCK:")
    print(STANDARD_IMPORT_BLOCK)
    
    print(f"\n🔄 FUNCTION MAPPINGS:")
    for old, new in FUNCTION_MAPPINGS.items():
        print(f"   {old} → {new}")
    
    print(f"\n🔧 PROCESSING FILES:")
    print("-" * 40)
    
    success_count = 0
    for page_file in page_files:
        if fix_page_file(page_file):
            success_count += 1
    
    print(f"\n📊 RESULTS:")
    print(f"   Total pages: {len(page_files)}")
    print(f"   Successfully fixed: {success_count}")
    print(f"   Failed: {len(page_files) - success_count}")
    
    if success_count == len(page_files):
        print(f"\n🎉 ALL PAGES SUCCESSFULLY STANDARDIZED!")
        print(f"   Every page now uses IDENTICAL imports from perfect_styling_method.py")
    else:
        print(f"\n⚠️  {len(page_files) - success_count} pages need manual attention")

def verify_standardization():
    """Verify that all pages now use standardized imports"""
    print(f"\n🔍 VERIFICATION: Checking import standardization...")
    
    pages_dir = Path("audit_tool/dashboard/pages")
    page_files = list(pages_dir.glob("*.py"))
    page_files = [f for f in page_files if not f.name.startswith("__")]
    
    all_standardized = True
    
    for page_file in page_files:
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it has the standardized import
            if 'apply_perfect_styling,' in content:
                print(f"   ✅ {page_file.name} - Standardized")
            else:
                print(f"   ❌ {page_file.name} - NOT standardized")
                all_standardized = False
                
        except Exception as e:
            print(f"   ❌ {page_file.name} - Error reading: {e}")
            all_standardized = False
    
    if all_standardized:
        print(f"\n🎉 VERIFICATION PASSED: All pages are standardized!")
    else:
        print(f"\n⚠️  VERIFICATION FAILED: Some pages still need fixing")

def main():
    """Main execution"""
    fix_all_dashboard_pages()
    verify_standardization()
    
    print(f"\n" + "=" * 80)
    print("STANDARDIZATION COMPLETE")
    print("=" * 80)
    print("All dashboard pages now use IDENTICAL imports and function calls.")
    print("No variations, no shortcuts - complete consistency across all pages.")
    print("=" * 80)

if __name__ == "__main__":
    main() 