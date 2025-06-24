#!/usr/bin/env python3
"""
FUNCTION IMPORT AUDIT SCRIPT
Systematically audit all function imports across dashboard pages
and map them to what actually exists in perfect_styling_method.py
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict

def extract_imports_from_file(file_path):
    """Extract function imports from perfect_styling_method in a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to find imports
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if (node.module and 
                    'perfect_styling_method' in node.module):
                    for alias in node.names:
                        imports.append(alias.name)
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def extract_functions_from_perfect_method():
    """Extract all function definitions from perfect_styling_method.py"""
    perfect_method_path = Path("audit_tool/dashboard/components/perfect_styling_method.py")
    
    if not perfect_method_path.exists():
        print(f"ERROR: {perfect_method_path} not found!")
        return []
    
    try:
        with open(perfect_method_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
        
        return sorted(functions)
    except Exception as e:
        print(f"Error parsing perfect_styling_method.py: {e}")
        return []

def audit_all_dashboard_pages():
    """Audit all dashboard pages for function imports"""
    pages_dir = Path("audit_tool/dashboard/pages")
    
    if not pages_dir.exists():
        print(f"ERROR: {pages_dir} not found!")
        return {}
    
    page_imports = {}
    
    for page_file in pages_dir.glob("*.py"):
        if page_file.name.startswith("__"):
            continue
            
        imports = extract_imports_from_file(page_file)
        if imports:
            page_imports[page_file.name] = imports
    
    return page_imports

def create_function_mapping():
    """Create mapping between imported functions and existing functions"""
    
    # Common mappings based on naming patterns
    function_mappings = {
        # Header functions
        'create_page_header': 'create_main_header',
        
        # Alert functions
        'show_success': 'create_success_alert',
        'show_warning': 'create_warning_alert', 
        'show_error': 'create_error_alert',
        'show_info': 'create_info_alert',
        
        # Chart functions
        'get_chart_config': 'get_perfect_chart_config',
        'apply_chart_styling': 'MISSING - use get_perfect_chart_config() directly',
        
        # Data functions
        'display_dataframe': 'create_data_table',
        
        # Layout functions
        'create_columns': 'create_two_column_layout / create_three_column_layout / create_four_column_layout',
        'create_tabs': 'MISSING - use st.tabs() directly',
        'create_expander': 'MISSING - use st.expander() directly',
        
        # Card functions
        'create_status_card': 'create_status_indicator',
        'create_metric_card': 'create_metric_card',  # This one exists
        
        # Missing functions that don't have equivalents
        'apply_chart_styling': 'MISSING - charts should use get_perfect_chart_config()',
        'create_tabs': 'MISSING - use st.tabs() directly',
        'create_expander': 'MISSING - use st.expander() directly'
    }
    
    return function_mappings

def main():
    """Main audit function"""
    print("🔍 FUNCTION IMPORT AUDIT")
    print("=" * 50)
    
    # 1. Extract all functions from perfect_styling_method.py
    print("\n1. Extracting functions from perfect_styling_method.py...")
    existing_functions = extract_functions_from_perfect_method()
    print(f"   Found {len(existing_functions)} functions")
    
    # 2. Extract all imports from dashboard pages
    print("\n2. Extracting imports from dashboard pages...")
    page_imports = audit_all_dashboard_pages()
    print(f"   Audited {len(page_imports)} pages")
    
    # 3. Collect all unique imported functions
    all_imported_functions = set()
    for page, imports in page_imports.items():
        all_imported_functions.update(imports)
    
    print(f"   Found {len(all_imported_functions)} unique imported functions")
    
    # 4. Create mapping
    function_mappings = create_function_mapping()
    
    # 5. Generate detailed report
    print("\n" + "=" * 80)
    print("DETAILED AUDIT REPORT")
    print("=" * 80)
    
    print(f"\n📋 EXISTING FUNCTIONS IN perfect_styling_method.py ({len(existing_functions)}):")
    for func in existing_functions:
        print(f"   ✅ {func}")
    
    print(f"\n📋 FUNCTIONS BEING IMPORTED ({len(all_imported_functions)}):")
    for func in sorted(all_imported_functions):
        if func in existing_functions:
            print(f"   ✅ {func} - EXISTS")
        elif func in function_mappings:
            print(f"   🔄 {func} - MAP TO: {function_mappings[func]}")
        else:
            print(f"   ❌ {func} - MISSING")
    
    print(f"\n📋 PAGE-BY-PAGE BREAKDOWN:")
    for page, imports in page_imports.items():
        print(f"\n📄 {page}:")
        for func in imports:
            if func in existing_functions:
                print(f"     ✅ {func}")
            elif func in function_mappings:
                print(f"     🔄 {func} → {function_mappings[func]}")
            else:
                print(f"     ❌ {func} - MISSING")
    
    # 6. Generate fix recommendations
    print("\n" + "=" * 80)
    print("FIX RECOMMENDATIONS")
    print("=" * 80)
    
    missing_functions = []
    mappable_functions = []
    
    for func in all_imported_functions:
        if func not in existing_functions:
            if func in function_mappings:
                mappable_functions.append((func, function_mappings[func]))
            else:
                missing_functions.append(func)
    
    if mappable_functions:
        print(f"\n🔄 FUNCTIONS TO REMAP ({len(mappable_functions)}):")
        for old_func, new_func in mappable_functions:
            print(f"   {old_func} → {new_func}")
    
    if missing_functions:
        print(f"\n❌ FUNCTIONS THAT NEED TO BE ADDED OR REPLACED ({len(missing_functions)}):")
        for func in missing_functions:
            print(f"   {func}")
    
    # 7. Summary
    total_imports = len(all_imported_functions)
    existing_count = len([f for f in all_imported_functions if f in existing_functions])
    mappable_count = len(mappable_functions)
    missing_count = len(missing_functions)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total imported functions: {total_imports}")
    print(f"   Already exist: {existing_count} ({existing_count/total_imports*100:.1f}%)")
    print(f"   Can be mapped: {mappable_count} ({mappable_count/total_imports*100:.1f}%)")
    print(f"   Missing/need action: {missing_count} ({missing_count/total_imports*100:.1f}%)")
    
    if existing_count + mappable_count == total_imports:
        print(f"\n🎉 ALL FUNCTIONS CAN BE RESOLVED!")
    else:
        print(f"\n⚠️  {missing_count} functions need attention")

if __name__ == "__main__":
    main() 