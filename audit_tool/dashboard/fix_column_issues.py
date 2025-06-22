"""
Automated Column Issue Fixer
Fixes critical column reference issues identified by the dashboard integrity checker
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColumnIssueFixer:
    """Automatically fixes common column reference issues in dashboard files"""
    
    def __init__(self):
        self.dashboard_dir = Path(__file__).parent
        self.fixes_applied = []
        
        # Define critical column fixes (old -> new)
        self.column_fixes = {
            'rationale': 'evidence',
            "'score'": "'raw_score'",
            '"score"': '"raw_score"',
            "['score']": "['raw_score']",
            '["score"]': '["raw_score"]'
        }
        
        # Define patterns that should NOT be changed (session state variables, etc.)
        self.exclude_patterns = [
            r"st\.session_state\[.*\]",
            r"summary\[.*\]",
            r"datasets\[.*\]",
            r"results\[.*\]",
            r"config\[.*\]",
            r"stats\[.*\]"
        ]
    
    def should_exclude_line(self, line: str) -> bool:
        """Check if a line should be excluded from fixes"""
        for pattern in self.exclude_patterns:
            if re.search(pattern, line):
                return True
        return False
    
    def fix_file(self, file_path: Path, dry_run: bool = True) -> Dict:
        """Fix column issues in a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            original_content = ''.join(lines)
            modified_lines = []
            changes_made = []
            
            for line_num, line in enumerate(lines, 1):
                original_line = line
                modified_line = line
                
                # Skip lines that should be excluded
                if self.should_exclude_line(line):
                    modified_lines.append(modified_line)
                    continue
                
                # Apply column fixes
                for old_pattern, new_pattern in self.column_fixes.items():
                    if old_pattern in modified_line:
                        # Special handling for rationale -> evidence
                        if old_pattern == 'rationale':
                            # Only replace in column access patterns
                            patterns = [
                                r"\['rationale'\]",
                                r'\["rationale"\]',
                                r"'rationale'(?=\s*[,\]])",
                                r'"rationale"(?=\s*[,\]])'
                            ]
                            for pattern in patterns:
                                replacement = pattern.replace('rationale', 'evidence')
                                if re.search(pattern, modified_line):
                                    modified_line = re.sub(pattern, replacement, modified_line)
                                    changes_made.append({
                                        'line': line_num,
                                        'old': pattern,
                                        'new': replacement,
                                        'context': original_line.strip()
                                    })
                        else:
                            # Direct replacement for score patterns
                            if old_pattern in modified_line:
                                modified_line = modified_line.replace(old_pattern, new_pattern)
                                changes_made.append({
                                    'line': line_num,
                                    'old': old_pattern,
                                    'new': new_pattern,
                                    'context': original_line.strip()
                                })
                
                modified_lines.append(modified_line)
            
            modified_content = ''.join(modified_lines)
            
            # Write changes if not dry run
            if not dry_run and modified_content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                logger.info(f"✅ Fixed {len(changes_made)} issues in {file_path.name}")
            
            return {
                'file': file_path.name,
                'path': str(file_path),
                'changes': changes_made,
                'modified': modified_content != original_content,
                'dry_run': dry_run
            }
            
        except Exception as e:
            logger.error(f"Error fixing {file_path}: {e}")
            return {
                'file': file_path.name,
                'path': str(file_path),
                'changes': [],
                'modified': False,
                'error': str(e),
                'dry_run': dry_run
            }
    
    def fix_all_files(self, dry_run: bool = True) -> Dict:
        """Fix column issues in all dashboard files"""
        logger.info(f"Starting {'dry run' if dry_run else 'actual'} column issue fixes...")
        
        # Find all Python files
        python_files = []
        
        # Main dashboard file
        main_dashboard = self.dashboard_dir / "brand_health_command_center.py"
        if main_dashboard.exists():
            python_files.append(main_dashboard)
        
        # All page files
        pages_dir = self.dashboard_dir / "pages"
        if pages_dir.exists():
            python_files.extend(pages_dir.glob("*.py"))
        
        # Component files (but exclude __pycache__ and our own files)
        components_dir = self.dashboard_dir / "components"
        if components_dir.exists():
            python_files.extend([
                f for f in components_dir.glob("*.py") 
                if not f.name.startswith('__') and f.name not in ['tier_analyzer.py']
            ])
        
        results = {
            'summary': {
                'total_files': len(python_files),
                'files_modified': 0,
                'total_changes': 0,
                'dry_run': dry_run
            },
            'files': [],
            'critical_fixes': []
        }
        
        # Process each file
        for file_path in python_files:
            file_result = self.fix_file(file_path, dry_run)
            results['files'].append(file_result)
            
            if file_result['modified']:
                results['summary']['files_modified'] += 1
                results['summary']['total_changes'] += len(file_result['changes'])
                
                # Track critical fixes (rationale -> evidence)
                for change in file_result['changes']:
                    if 'rationale' in change['old']:
                        results['critical_fixes'].append({
                            'file': file_result['file'],
                            'line': change['line'],
                            'fix': f"{change['old']} → {change['new']}"
                        })
        
        return results
    
    def generate_fix_report(self, results: Dict) -> str:
        """Generate a report of fixes applied"""
        report = []
        report.append("=" * 80)
        report.append("🔧 COLUMN ISSUE FIX REPORT")
        report.append("=" * 80)
        report.append("")
        
        summary = results['summary']
        mode = "DRY RUN" if summary['dry_run'] else "ACTUAL FIXES"
        
        report.append(f"📊 SUMMARY ({mode}):")
        report.append(f"   Total Files Processed: {summary['total_files']}")
        report.append(f"   Files Modified: {summary['files_modified']}")
        report.append(f"   Total Changes: {summary['total_changes']}")
        report.append("")
        
        # Critical fixes
        if results['critical_fixes']:
            report.append("🚨 CRITICAL FIXES (rationale → evidence):")
            for fix in results['critical_fixes']:
                report.append(f"   ✅ {fix['file']} line {fix['line']}: {fix['fix']}")
            report.append("")
        
        # File-by-file details
        report.append("📁 FILE DETAILS:")
        for file_result in results['files']:
            if file_result['modified']:
                report.append(f"   🔧 {file_result['file']} - {len(file_result['changes'])} changes")
                for change in file_result['changes'][:3]:  # Show first 3 changes
                    report.append(f"      Line {change['line']}: {change['old']} → {change['new']}")
                if len(file_result['changes']) > 3:
                    report.append(f"      ... and {len(file_result['changes']) - 3} more changes")
            else:
                report.append(f"   ✅ {file_result['file']} - No changes needed")
        
        report.append("")
        
        if summary['dry_run']:
            report.append("💡 This was a DRY RUN. To apply fixes, run with dry_run=False")
        else:
            report.append("✅ All fixes have been applied to the files!")
            report.append("🔄 Restart the dashboard to see the changes take effect")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Run the column issue fixer"""
    fixer = ColumnIssueFixer()
    
    # First do a dry run
    print("🔍 Running dry run to preview fixes...")
    dry_results = fixer.fix_all_files(dry_run=True)
    
    # Generate and show dry run report
    dry_report = fixer.generate_fix_report(dry_results)
    print(dry_report)
    
    # Ask if user wants to apply fixes
    if dry_results['summary']['total_changes'] > 0:
        print("\n🤔 Apply these fixes? (y/n): ", end="")
        response = input().lower().strip()
        
        if response in ['y', 'yes']:
            print("\n🔧 Applying fixes...")
            actual_results = fixer.fix_all_files(dry_run=False)
            actual_report = fixer.generate_fix_report(actual_results)
            print(actual_report)
            
            # Save report
            report_file = fixer.dashboard_dir / "fix_report.txt"
            with open(report_file, 'w') as f:
                f.write(actual_report)
            print(f"\n📄 Fix report saved to: {report_file}")
        else:
            print("\n❌ Fixes not applied. Files remain unchanged.")
    else:
        print("\n✅ No fixes needed!")

if __name__ == "__main__":
    main() 