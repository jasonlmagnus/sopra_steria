#!/usr/bin/env python3
"""
SYNTAX ERROR AUDIT SCRIPT
Systematically audit all syntax errors in dashboard pages
to understand exactly what needs to be fixed
"""

import ast
import os
from pathlib import Path
from collections import defaultdict

def audit_file_syntax(file_path):
    """Audit syntax errors in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse the file
        try:
            ast.parse(content)
            return {"status": "OK", "errors": []}
        except SyntaxError as e:
            return {
                "status": "SYNTAX_ERROR",
                "errors": [{
                    "line": e.lineno,
                    "offset": e.offset,
                    "text": e.text.strip() if e.text else "",
                    "msg": e.msg
                }]
            }
        except Exception as e:
            return {
                "status": "OTHER_ERROR", 
                "errors": [{"msg": str(e)}]
            }
            
    except Exception as e:
        return {
            "status": "READ_ERROR",
            "errors": [{"msg": f"Cannot read file: {e}"}]
        }

def analyze_import_issues(file_path):
    """Analyze import-related issues in a file"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for broken import fragments
            if any(func in line_stripped for func in [
                'create_page_header', 'create_status_card', 'show_success', 
                'show_warning', 'show_error', 'show_info'
            ]) and 'from audit_tool' not in line:
                issues.append({
                    "line": i,
                    "type": "BROKEN_IMPORT_FRAGMENT",
                    "text": line_stripped,
                    "issue": "Leftover import fragment without proper import statement"
                })
            
            # Check for duplicate import blocks
            if 'from audit_tool.dashboard.components.perfect_styling_method import' in line:
                # Count how many times this appears
                import_count = sum(1 for l in lines if 'from audit_tool.dashboard.components.perfect_styling_method import' in l)
                if import_count > 1:
                    issues.append({
                        "line": i,
                        "type": "DUPLICATE_IMPORT",
                        "text": line_stripped,
                        "issue": f"Duplicate import statement (appears {import_count} times)"
                    })
            
            # Check for stray closing parentheses
            if line_stripped == ')' and i > 1:
                # Look backwards for matching opening parenthesis
                has_match = False
                for j in range(max(0, i-20), i-1):
                    if '(' in lines[j] and ('import' in lines[j] or 'from' in lines[j]):
                        has_match = True
                        break
                if not has_match:
                    issues.append({
                        "line": i,
                        "type": "STRAY_CLOSING_PAREN",
                        "text": line_stripped,
                        "issue": "Closing parenthesis without matching opening parenthesis"
                    })
            
            # Check for indentation issues
            if line_stripped and not line.startswith(' ') and not line.startswith('\t'):
                # This is not indented, check if it should be
                if i > 1 and lines[i-2].strip().endswith('('):
                    issues.append({
                        "line": i,
                        "type": "INDENTATION_ERROR",
                        "text": line_stripped,
                        "issue": "Should be indented (part of multi-line statement)"
                    })
    
    except Exception as e:
        issues.append({
            "line": 0,
            "type": "ANALYSIS_ERROR",
            "text": "",
            "issue": f"Error analyzing file: {e}"
        })
    
    return issues

def main():
    """Main audit function"""
    print("🔍 SYNTAX ERROR AUDIT")
    print("=" * 60)
    print("Auditing ALL dashboard pages for syntax errors")
    print("=" * 60)
    
    pages_dir = Path("audit_tool/dashboard/pages")
    
    if not pages_dir.exists():
        print(f"❌ ERROR: {pages_dir} not found!")
        return
    
    # Get all Python files
    page_files = list(pages_dir.glob("*.py"))
    page_files = [f for f in page_files if not f.name.startswith("__")]
    
    print(f"\n📋 Auditing {len(page_files)} dashboard pages:")
    
    # Track results
    syntax_ok = []
    syntax_errors = []
    other_errors = []
    all_import_issues = defaultdict(list)
    
    # Audit each file
    for page_file in page_files:
        print(f"\n🔍 Auditing {page_file.name}...")
        
        # Check syntax
        syntax_result = audit_file_syntax(page_file)
        
        if syntax_result["status"] == "OK":
            syntax_ok.append(page_file.name)
            print(f"   ✅ Syntax OK")
        elif syntax_result["status"] == "SYNTAX_ERROR":
            syntax_errors.append((page_file.name, syntax_result["errors"]))
            for error in syntax_result["errors"]:
                print(f"   ❌ SYNTAX ERROR Line {error['line']}: {error['msg']}")
                print(f"      Text: {error['text']}")
        else:
            other_errors.append((page_file.name, syntax_result["errors"]))
            for error in syntax_result["errors"]:
                print(f"   ❌ ERROR: {error['msg']}")
        
        # Check import issues
        import_issues = analyze_import_issues(page_file)
        if import_issues:
            all_import_issues[page_file.name] = import_issues
            print(f"   🔄 Found {len(import_issues)} import issues")
            for issue in import_issues:
                print(f"      Line {issue['line']} ({issue['type']}): {issue['issue']}")
        else:
            print(f"   ✅ No import issues")
    
    # Summary report
    print("\n" + "=" * 80)
    print("COMPREHENSIVE AUDIT SUMMARY")
    print("=" * 80)
    
    print(f"\n📊 SYNTAX STATUS:")
    print(f"   ✅ Files with no syntax errors: {len(syntax_ok)}")
    print(f"   ❌ Files with syntax errors: {len(syntax_errors)}")
    print(f"   ⚠️  Files with other errors: {len(other_errors)}")
    
    if syntax_ok:
        print(f"\n✅ FILES WITH CLEAN SYNTAX:")
        for file in syntax_ok:
            print(f"   - {file}")
    
    if syntax_errors:
        print(f"\n❌ FILES WITH SYNTAX ERRORS:")
        for file, errors in syntax_errors:
            print(f"\n   📄 {file}:")
            for error in errors:
                print(f"      Line {error['line']}: {error['msg']}")
                if error['text']:
                    print(f"      Code: {error['text']}")
    
    if all_import_issues:
        print(f"\n🔄 IMPORT ISSUES BREAKDOWN:")
        issue_types = defaultdict(int)
        for file, issues in all_import_issues.items():
            print(f"\n   📄 {file} ({len(issues)} issues):")
            for issue in issues:
                issue_types[issue['type']] += 1
                print(f"      Line {issue['line']} ({issue['type']}): {issue['issue']}")
        
        print(f"\n📈 ISSUE TYPE SUMMARY:")
        for issue_type, count in issue_types.items():
            print(f"   {issue_type}: {count} occurrences")
    
    # Recommendations
    print(f"\n🎯 RECOMMENDATIONS:")
    if syntax_errors:
        print(f"   1. Fix {len(syntax_errors)} files with syntax errors first")
    if all_import_issues:
        total_import_issues = sum(len(issues) for issues in all_import_issues.values())
        print(f"   2. Clean up {total_import_issues} import issues across {len(all_import_issues)} files")
    if len(syntax_ok) == len(page_files):
        print(f"   🎉 All files have clean syntax!")
    
    print(f"\n" + "=" * 80)

if __name__ == "__main__":
    main() 