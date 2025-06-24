#!/usr/bin/env python3
"""
EMERGENCY SYNTAX FIX SCRIPT
Fixes all remaining syntax errors in dashboard pages
"""

import os
import re
from pathlib import Path

def fix_syntax_errors(file_path):
    """Fix syntax errors in a single file"""
    print(f"🔧 Emergency fixing {file_path.name}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        cleaned_lines = []
        skip_next = False
        in_broken_import = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            # Remove broken import fragments
            if ('create_page_header,' in line or 
                'create_status_card,' in line or
                'show_success,' in line or
                'show_warning,' in line or
                'show_error,' in line or
                'show_info,' in line) and 'from audit_tool' not in line:
                # This is a leftover import fragment - skip it and related lines
                in_broken_import = True
                continue
            
            # Skip closing parentheses of broken imports
            if in_broken_import and line.strip() == ')':
                in_broken_import = False
                continue
                
            # Skip lines that are just function names (broken imports)
            if (line.strip() in ['create_page_header,', 'create_status_card,', 'show_success,', 
                                'show_warning,', 'show_error,', 'show_info,'] or
                line.strip().startswith('create_page_header') or
                line.strip().startswith('create_status_card') or
                line.strip().startswith('show_success') or
                line.strip().startswith('show_warning') or
                line.strip().startswith('show_error') or
                line.strip().startswith('show_info')):
                continue
            
            # Remove duplicate empty import blocks
            if line.strip() == ')' and i > 0 and lines[i-1].strip() == '':
                # Check if this is a stray closing parenthesis
                has_matching_open = False
                for j in range(max(0, i-10), i):
                    if '(' in lines[j] and 'import' in lines[j]:
                        has_matching_open = True
                        break
                if not has_matching_open:
                    continue
            
            cleaned_lines.append(line)
        
        # Write back the cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(cleaned_lines))
            
        print(f"   ✅ Emergency fixed {file_path.name}")
        return True
        
    except Exception as e:
        print(f"   ❌ Error fixing {file_path.name}: {e}")
        return False

def main():
    """Main emergency fix"""
    pages_dir = Path("audit_tool/dashboard/pages")
    
    if not pages_dir.exists():
        print(f"❌ ERROR: {pages_dir} not found!")
        return
    
    print("🚨 EMERGENCY SYNTAX FIX")
    print("=" * 40)
    
    page_files = list(pages_dir.glob("*.py"))
    page_files = [f for f in page_files if not f.name.startswith("__")]
    
    success_count = 0
    for page_file in page_files:
        if fix_syntax_errors(page_file):
            success_count += 1
    
    print(f"\n📊 EMERGENCY FIX RESULTS:")
    print(f"   Total pages: {len(page_files)}")
    print(f"   Successfully fixed: {success_count}")
    print(f"   Failed: {len(page_files) - success_count}")

if __name__ == "__main__":
    main() 