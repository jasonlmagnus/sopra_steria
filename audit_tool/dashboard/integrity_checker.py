"""
Dashboard Integrity Checker
Validates all dashboard pages against unified CSV columns configuration to prevent column mismatch errors
"""

import ast
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardIntegrityChecker:
    """Validates dashboard code against available columns in unified dataset"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.dashboard_dir = Path(__file__).parent
        self.config_file = self.project_root / "audit_tool" / "config" / "unified_csv_columns.yaml"
        self.available_columns = self._load_available_columns()
        
    def _load_available_columns(self) -> Set[str]:
        """Load available columns from unified CSV configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            columns = set(config.get('unified_audit_data_columns', []))
            logger.info(f"Loaded {len(columns)} available columns from {self.config_file}")
            return columns
            
        except Exception as e:
            logger.error(f"Error loading column configuration: {e}")
            return set()
    
    def _extract_column_references(self, file_path: Path) -> List[Dict]:
        """Extract all column references from a Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            column_refs = []
            
            # Use regex patterns to find column references
            column_refs.extend(self._find_regex_column_refs(content, file_path))
            
            return column_refs
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []
    
    def _find_regex_column_refs(self, content: str, file_path: Path) -> List[Dict]:
        """Find column references using regex patterns"""
        column_refs = []
        lines = content.split('\n')
        
        # More specific patterns for actual DataFrame column references
        patterns = [
            # DataFrame column access for reading: df['column'].method(), data['column'].apply(), etc.
            # But NOT assignment: df['column'] = ...
            r"(?:self\.df|df|data|master_df|filtered_df|tier_data|page_data|criteria_df|experience_df|unified_df|audit_df)\s*\[\s*['\"]([^'\"]+)['\"]\s*\]\s*\.(?!fillna\(\))",
            # Column existence checks: 'column' in/not in df.columns (including self.df)
            r"['\"]([^'\"]+)['\"]\s+(?:not\s+)?in\s+(?:self\.df|df|data|master_df|filtered_df|tier_data|page_data|criteria_df|experience_df|unified_df|audit_df)\.columns",
            # groupby operations: .groupby('column') or .groupby(['col1', 'col2'])
            r"\.groupby\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\.groupby\s*\(\s*\[\s*['\"]([^'\"]+)['\"]",
            # sort_values operations: .sort_values('column') or .sort_values(['col1', 'col2'])
            r"\.sort_values\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\.sort_values\s*\(\s*\[\s*['\"]([^'\"]+)['\"]",
            # Pandas operations that use column names (but not assignment)
            r"\.drop\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\.rename\s*\([^)]*['\"]([^'\"]+)['\"]",
            # Column selection in pandas: df[['col1', 'col2']] (but not single column assignment)
            r"(?:self\.df|df|data|master_df|filtered_df|tier_data|page_data|criteria_df|experience_df|unified_df|audit_df)\s*\[\s*\[\s*['\"]([^'\"]+)['\"]",
            # Direct column references that look like our schema (in method calls, not assignments)
            r"(?:\.apply\(|\.map\(|\.fillna\(|\.str\.|\.astype\(|\.nunique\(|\.mean\(|\.sum\(|\.min\(|\.max\(|\.std\(|\.count\().*['\"]([a-z_]+(?:_score|_id|_code|_slug|_name|_weight|_percentage|_flag|_level|_likelihood|_ts|_numeric))['\"]",
            # row.get() patterns for accessing column values
            r"row\.get\s*\(\s*['\"]([^'\"]+)['\"]",
            # DataFrame nlargest/nsmallest operations
            r"\.nlargest\s*\([^,]+,\s*['\"]([^'\"]+)['\"]",
            r"\.nsmallest\s*\([^,]+,\s*['\"]([^'\"]+)['\"]"
        ]
        
        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly not DataFrame column operations
            if any(skip_pattern in line for skip_pattern in [
                'st.session_state', 'summary[', 'stats[', 'brand_health[', 'sentiment[', 
                'conversion[', 'key_metrics[', 'recommendations[', 'story[', 'opp[',
                'f"', 'f\'', '.format(', 'logging.', 'logger.', 'print(', 'st.metric(',
                'st.markdown(', 'st.success(', 'st.error(', 'st.warning(', 'st.info(',
                'st.expander(', 'st.write(', 'st.text(', 'st.title(', 'st.header(',
                'import ', 'from ', 'def ', 'class ', 'if __name__', '#'
            ]):
                continue
            
            # Skip column assignment lines (creating new columns)
            if re.search(r"df\s*\[\s*['\"][^'\"]+['\"]\s*\]\s*=", line):
                continue
                
            for pattern in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    for group in match.groups():
                        if group and self._is_likely_column_name(group):
                            column_refs.append({
                                'column': group,
                                'line': line_num,
                                'type': 'regex',
                                'file': file_path.name,
                                'context': line.strip()
                            })
        
        return column_refs
    
    def _is_likely_column_name(self, name: str) -> bool:
        """Check if a string is likely a column name"""
        # Filter out common non-column strings
        exclude_patterns = [
            'streamlit', 'pandas', 'plotly', 'numpy', 'matplotlib',
            'main', 'data', 'file', 'path', 'http', 'www',
            'title', 'label', 'width', 'height', 'size',
            # Session state and dictionary keys (but NOT potential column names)
            'master_df', 'summary', 'stats', 'brand_health', 'sentiment',
            'conversion', 'key_metrics', 'recommendations', 'story', 'opp',
            'experience_records', 'total_recommendations', 'status', 'emoji',
            'critical_issues', 'quick_wins', 'success_pages', 'net_sentiment',
            'positive', 'neutral', 'negative', 'current_score', 'effort_level',
            'key_strengths', 'avg_engagement', 'avg_score_mean'
            # Removed 'potential_impact' - this should be checked as a potential column name
        ]
        
        # Include patterns that look like our actual column names
        include_patterns = [
            '_score', '_id', '_code', '_slug', '_name', '_weight', 
            '_percentage', '_flag', '_level', '_likelihood', '_ts', '_numeric',
            'tier', 'persona', 'page', 'criterion', 'evidence',
            'sentiment', 'engagement', 'conversion', 'descriptor'
        ]
        
        name_lower = name.lower()
        
        # Exclude obvious non-columns
        if any(pattern in name_lower for pattern in exclude_patterns):
            return False
        
        # Include likely columns based on our schema
        if any(pattern in name_lower for pattern in include_patterns):
            return True
        
        # Include if it matches our exact column naming convention
        if re.match(r'^[a-z][a-z0-9_]*[a-z0-9]$', name_lower) and len(name) > 3:
            # But exclude common dictionary keys
            if name_lower in ['total_pages', 'total_personas', 'total_criteria', 
                             'has_experience_data', 'has_recommendations', 'data_shape',
                             'available_columns', 'score_column']:
                return False
            return True
        
        return False
    
    def check_file(self, file_path: Path) -> Dict:
        """Check a single file for column integrity issues"""
        logger.info(f"Checking {file_path.name}...")
        
        column_refs = self._extract_column_references(file_path)
        issues = []
        valid_refs = []
        
        for ref in column_refs:
            column = ref['column']
            if column not in self.available_columns:
                issues.append({
                    'severity': 'ERROR',
                    'column': column,
                    'line': ref['line'],
                    'type': ref['type'],
                    'message': f"Column '{column}' not found in unified dataset",
                    'context': ref.get('context', ''),
                    'suggestion': self._suggest_alternative(column)
                })
            else:
                valid_refs.append(ref)
        
        return {
            'file': file_path.name,
            'path': str(file_path),
            'total_refs': len(column_refs),
            'valid_refs': len(valid_refs),
            'issues': issues,
            'status': 'PASS' if not issues else 'FAIL'
        }
    
    def _suggest_alternative(self, column: str) -> str:
        """Suggest alternative column names for invalid columns"""
        # Common mappings for renamed columns (using unified_csv_columns.yaml as source of truth)
        mappings = {
            'rationale': 'evidence',
            'reason': 'evidence', 
            'justification': 'evidence',
            'score': 'raw_score',
            'potential_impact': 'raw_score',  # Use score as proxy for impact
            'impact': 'raw_score',
            'criterion': 'criterion_code',
            'criteria': 'criterion_code',
            'page': 'page_id',
            'persona': 'persona_id',
            'sentiment': 'overall_sentiment',
            'engagement': 'engagement_level',
            'conversion': 'conversion_likelihood'
        }
        
        if column in mappings:
            return f"Use '{mappings[column]}' instead"
        
        # Find similar column names
        similar = []
        for available_col in self.available_columns:
            if column.lower() in available_col.lower() or available_col.lower() in column.lower():
                similar.append(available_col)
        
        if similar:
            return f"Similar columns: {', '.join(similar[:3])}"
        
        return "No direct alternative found"
    
    def check_all_dashboard_files(self) -> Dict:
        """Check all dashboard files for column integrity"""
        logger.info("Starting dashboard integrity check...")
        
        # Files to skip (legacy code that doesn't affect dashboard functionality)
        skip_files = {
            'data_loader.py',  # Legacy code with known compatibility issues
            '__init__.py',
            '__pycache__'
        }
        
        # Find all Python files in dashboard directory
        python_files = []
        
        # Main dashboard file
        main_file = self.dashboard_dir / "brand_health_command_center.py"
        if main_file.exists():
            python_files.append(main_file)
        
        # Component files
        components_dir = self.dashboard_dir / "components"
        if components_dir.exists():
            for file in components_dir.glob("*.py"):
                if file.name not in skip_files:
                    python_files.append(file)
        
        # Page files
        pages_dir = self.dashboard_dir / "pages"
        if pages_dir.exists():
            for file in pages_dir.glob("*.py"):
                if file.name not in skip_files:
                    python_files.append(file)
        
        # Check each file
        results = {
            'files_checked': [],
            'total_issues': 0,
            'files_with_issues': 0,
            'summary': {}
        }
        
        for file_path in python_files:
            file_result = self.check_file(file_path)
            results['files_checked'].append(file_result)
            
            if file_result['issues']:
                results['files_with_issues'] += 1
                results['total_issues'] += len(file_result['issues'])
        
        # Generate summary
        results['summary'] = {
            'total_files': len(results['files_checked']),
            'files_with_issues': results['files_with_issues'],
            'files_clean': len(results['files_checked']) - results['files_with_issues'],
            'total_issues': results['total_issues']
        }
        
        # Add recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on check results"""
        recommendations = []
        
        if results['total_issues'] == 0:
            recommendations.append("✅ All dashboard files are using valid column references!")
            return recommendations
        
        # Common issues and recommendations
        issue_counts = {}
        for file_result in results['files_checked']:
            for issue in file_result['issues']:
                column = issue['column']
                issue_counts[column] = issue_counts.get(column, 0) + 1
        
        if issue_counts:
            recommendations.append("🔧 Most common invalid columns:")
            for column, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                recommendations.append(f"   • '{column}' ({count} occurrences)")
        
        recommendations.append("📋 Next steps:")
        recommendations.append("   1. Review the issues above")
        recommendations.append("   2. Update column references to match unified CSV schema")
        recommendations.append("   3. Test dashboard functionality after fixes")
        
        return recommendations
    
    def generate_report(self, results: Dict) -> str:
        """Generate a detailed report of the integrity check"""
        report = []
        report.append("=" * 60)
        report.append("DASHBOARD INTEGRITY CHECK REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append(f"📊 SUMMARY")
        report.append(f"   Files Checked: {summary['total_files']}")
        report.append(f"   Files with Issues: {summary['files_with_issues']}")
        report.append(f"   Clean Files: {summary['files_clean']}")
        report.append(f"   Total Issues: {summary['total_issues']}")
        report.append("")
        
        # Available columns info
        report.append(f"📋 AVAILABLE COLUMNS ({len(self.available_columns)})")
        sorted_columns = sorted(self.available_columns)
        for i in range(0, len(sorted_columns), 3):
            row = sorted_columns[i:i+3]
            report.append(f"   {' | '.join(f'{col:<25}' for col in row)}")
        report.append("")
        
        # File-by-file results
        if results['files_checked']:
            report.append("🔍 DETAILED RESULTS")
            report.append("-" * 40)
            
            for file_result in results['files_checked']:
                status_icon = "✅" if file_result['status'] == 'PASS' else "❌"
                report.append(f"{status_icon} {file_result['file']}")
                report.append(f"   Total References: {file_result['total_refs']}")
                report.append(f"   Valid References: {file_result['valid_refs']}")
                report.append(f"   Issues: {len(file_result['issues'])}")
                
                if file_result['issues']:
                    for issue in file_result['issues']:
                        report.append(f"      ⚠️  Line {issue['line']}: '{issue['column']}' - {issue['message']}")
                        if issue['suggestion']:
                            report.append(f"         💡 {issue['suggestion']}")
                        if issue['context']:
                            report.append(f"         📝 Context: {issue['context'][:80]}...")
                
                report.append("")
        
        # Recommendations
        if results.get('recommendations'):
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 40)
            for rec in results['recommendations']:
                report.append(rec)
            report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)


def main():
    """Main function to run integrity check"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check dashboard integrity against unified CSV columns')
    parser.add_argument('--output', '-o', help='Output report to file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run integrity check
    checker = DashboardIntegrityChecker()
    results = checker.check_all_dashboard_files()
    
    # Generate and display report
    report = checker.generate_report(results)
    print(report)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with error code if issues found
    if results['total_issues'] > 0:
        print(f"\n❌ Found {results['total_issues']} issues across {results['files_with_issues']} files")
        exit(1)
    else:
        print(f"\n✅ All {results['summary']['total_files']} files passed integrity check!")
        exit(0)


if __name__ == "__main__":
    main() 