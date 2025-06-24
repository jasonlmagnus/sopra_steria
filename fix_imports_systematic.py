#!/usr/bin/env python3
"""
Systematic Import Fix Script
Fixes ModuleNotFoundError: No module named 'audit_tool' across all dashboard pages
"""

import os
import re
from pathlib import Path

def fix_page_imports(file_path):
    """Fix imports in a single page file"""
    print(f"Fixing imports in: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if this file has the problematic import
    if 'from audit_tool.dashboard.components.perfect_styling_method import' not in content:
        print(f"  - No problematic imports found, skipping")
        return
    
    # Check if sys.path fix is already present
    if 'sys.path.insert(0, str(project_root))' in content:
        print(f"  - Import fix already present, skipping")
        return
    
    # Pattern to find the first import statement
    import_pattern = r'(import streamlit as st\n)'
    
    # Replacement with sys.path fix
    replacement = r'''\1import sys
from pathlib import Path

# Add project root to Python path to fix import issues
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

'''
    
    # Apply the fix
    new_content = re.sub(import_pattern, replacement, content, count=1)
    
    if new_content != content:
        # Write the fixed content back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ Fixed imports successfully")
    else:
        print(f"  ⚠️  Could not apply automatic fix")

def main():
    """Fix all dashboard page imports"""
    print("🔧 Systematic Import Fix Script")
    print("=" * 50)
    
    # Find all dashboard page files
    pages_dir = Path("audit_tool/dashboard/pages")
    
    if not pages_dir.exists():
        print(f"❌ Pages directory not found: {pages_dir}")
        return
    
    # Get all Python files in pages directory
    page_files = list(pages_dir.glob("*.py"))
    
    print(f"Found {len(page_files)} page files to check")
    print()
    
    for page_file in page_files:
        # Skip backup files
        if 'BACKUP' in page_file.name or 'backup' in page_file.name:
            continue
            
        fix_page_imports(page_file)
    
    print()
    print("✅ Import fixing complete!")
    print()
    print("🧪 Test the fix by running:")
    print("streamlit run audit_tool/dashboard/brand_health_command_center.py --server.port 8510")

if __name__ == "__main__":
    main() 