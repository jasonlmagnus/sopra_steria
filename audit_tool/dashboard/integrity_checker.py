"""
Dashboard Integrity Checker
Validates all dashboard pages against unified CSV columns configuration to prevent column mismatch errors
Enhanced with data type validation and API compatibility checking
"""

import ast
import re
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DashboardIntegrityChecker:
    """Validates dashboard code against available columns in unified dataset with type checking"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.dashboard_dir = Path(__file__).parent
        self.config_file = self.project_root / "audit_tool" / "config" / "unified_csv_columns.yaml"
        self.column_config = self._load_column_configuration()
        self.available_columns = set(self.column_config.get('column_names_only', []))
        
    def _load_column_configuration(self) -> Dict[str, Any]:
        """Load complete column configuration with types and validation rules"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded column configuration with {len(config.get('column_names_only', []))} columns")
            return config
            
        except Exception as e:
            logger.error(f"Error loading column configuration: {e}")
            return {}
    
    def _get_column_type(self, column_name: str) -> str:
        """Get the expected data type for a column"""
        column_details = self.column_config.get('unified_audit_data_columns', {})
        if isinstance(column_details, dict) and column_name in column_details:
            return column_details[column_name].get('type', 'unknown')
        return 'unknown'
    
    def _get_numeric_columns(self) -> Set[str]:
        """Get all columns that should contain numeric data"""
        numeric_config = self.column_config.get('numeric_columns', {})
        numeric_cols = set()
        for category, columns in numeric_config.items():
            numeric_cols.update(columns)
        return numeric_cols
    
    def _get_empty_columns(self) -> Set[str]:
        """Get columns that are known to be empty in current data"""
        return set(self.column_config.get('data_quality_notes', {}).get('empty_columns', []))
    
    def _extract_column_references(self, file_path: Path) -> List[Dict]:
        """Extract all column references from a Python file with enhanced detection"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            column_refs = []
            
            # Use regex patterns to find column references
            column_refs.extend(self._find_regex_column_refs(content, file_path))
            
            # Check for API compatibility issues
            column_refs.extend(self._find_api_compatibility_issues(content, file_path))
            
            return column_refs
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
            return []
    
    def _find_api_compatibility_issues(self, content: str, file_path: Path) -> List[Dict]:
        """Find API compatibility issues like deprecated methods"""
        issues = []
        lines = content.split('\n')
        
        # Known API compatibility issues
        api_issues = [
            {
                'pattern': r'\.update_xaxis\(',
                'issue': 'Plotly API error',
                'message': "Use 'update_xaxes()' instead of 'update_xaxis()'",
                'severity': 'ERROR'
            },
            {
                'pattern': r'\.applymap\(',
                'issue': 'Deprecated Pandas API',
                'message': "Use '.map()' instead of '.applymap()' (deprecated in pandas 2.1+)",
                'severity': 'WARNING'
            },
            {
                'pattern': r'st\.session_state\[[\'"]\w+[\'"]\]\s*=',
                'issue': 'Streamlit session state conflict',
                'message': "Avoid setting session_state after widget creation - causes StreamlitAPIException",
                'severity': 'ERROR'
            },
            {
                'pattern': r'\.calculate_tier_performance\(',
                'issue': 'Method not found',
                'message': "Method 'calculate_tier_performance()' doesn't exist, use 'get_tier_summary()' instead",
                'severity': 'ERROR'
            },
            # NEW: Streamlit version compatibility issues
            {
                'pattern': r'st\.metric\([^)]*key\s*=',
                'issue': 'Streamlit version compatibility',
                'message': "st.metric() 'key' parameter not supported in Streamlit 1.46.0. Remove key parameter or upgrade Streamlit.",
                'severity': 'ERROR'
            },
            {
                'pattern': r'st\.selectbox\([^)]*key\s*=.*\)\s*\n.*st\.session_state\[',
                'issue': 'Streamlit session state conflict',
                'message': "Setting session_state after widget with key causes StreamlitAPIException",
                'severity': 'ERROR'
            },
            # NEW: Data structure assumption errors
            {
                'pattern': r'dataset_info\[[\'"]\w+[\'"]\]',
                'issue': 'Data structure assumption',
                'message': "Assuming dataset_info is dict, but it might be list. Check data structure before accessing.",
                'severity': 'ERROR'
            },
            {
                'pattern': r'story\.get\([^)]*\).*sorted\(',
                'issue': 'Data type assumption',
                'message': "Mixing string and numeric types in sorted() comparison. Filter to numeric values first.",
                'severity': 'ERROR'
            },
            # NEW: Numeric operations on text data
            {
                'pattern': r'\.mean\(\)(?!\s*\(.*numeric_only\s*=\s*True)',
                'issue': 'Numeric operation on mixed data',
                'message': "Use .mean(numeric_only=True) to avoid TypeError with text columns",
                'severity': 'ERROR'
            },
            {
                'pattern': r'\.corr\(\)(?!\s*\(.*numeric_only\s*=\s*True)',
                'issue': 'Numeric operation on mixed data', 
                'message': "Use .corr(numeric_only=True) to avoid TypeError with text columns",
                'severity': 'ERROR'
            }
        ]
        
        # Check for Streamlit duplicate element ID issues
        streamlit_elements = {}
        for line_num, line in enumerate(lines, 1):
            # Look for Streamlit elements that can cause duplicate ID issues
            streamlit_patterns = [
                (r'st\.plotly_chart\([^)]*\)', 'plotly_chart'),
                (r'st\.metric\([^)]*\)', 'metric'),
                (r'st\.dataframe\([^)]*\)', 'dataframe'),
                (r'st\.data_editor\([^)]*\)', 'data_editor'),
                (r'st\.selectbox\([^)]*\)', 'selectbox'),
                (r'st\.multiselect\([^)]*\)', 'multiselect'),
                (r'st\.slider\([^)]*\)', 'slider'),
                (r'st\.text_input\([^)]*\)', 'text_input'),
                (r'st\.number_input\([^)]*\)', 'number_input'),
                (r'st\.radio\([^)]*\)', 'radio'),
                (r'st\.checkbox\([^)]*\)', 'checkbox')
            ]
            
            for pattern, element_type in streamlit_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    element_call = match.group(0)
                    # Check if it has a key parameter
                    has_key = 'key=' in element_call
                    
                    if not has_key:
                        # Track elements without keys
                        if element_type not in streamlit_elements:
                            streamlit_elements[element_type] = []
                        streamlit_elements[element_type].append({
                            'line': line_num,
                            'call': element_call,
                            'context': line.strip()
                        })
        
        # Report potential duplicate ID issues
        for element_type, occurrences in streamlit_elements.items():
            if len(occurrences) > 1:
                for occurrence in occurrences:
                    issues.append({
                        'column': 'API_COMPATIBILITY',
                        'line': occurrence['line'],
                        'type': 'api_compatibility',
                        'file': file_path.name,
                        'context': occurrence['context'],
                        'issue_type': 'Streamlit duplicate element ID risk',
                        'message': f"Multiple {element_type} elements without unique keys may cause StreamlitDuplicateElementId error. Add key='unique_name' parameter.",
                        'severity': 'WARNING'
                    })
        
        # Check for existing API issues
        for line_num, line in enumerate(lines, 1):
            for api_issue in api_issues:
                if re.search(api_issue['pattern'], line):
                    issues.append({
                        'column': 'API_COMPATIBILITY',
                        'line': line_num,
                        'type': 'api_compatibility',
                        'file': file_path.name,
                        'context': line.strip(),
                        'issue_type': api_issue['issue'],
                        'message': api_issue['message'],
                        'severity': api_issue['severity']
                    })
        
        return issues
    
    def _find_regex_column_refs(self, content: str, file_path: Path) -> List[Dict]:
        """Find column references using regex patterns with enhanced type checking"""
        column_refs = []
        lines = content.split('\n')
        
        # Enhanced patterns for actual DataFrame column references
        patterns = [
            # DataFrame column access for reading: df['column'].method(), data['column'].apply(), etc.
            r"(?:self\.df|df|data|master_df|filtered_df|tier_data|page_data|criteria_df|experience_df|unified_df|audit_df)\s*\[\s*['\"]([^'\"]+)['\"]\s*\]\s*\.(?!fillna\(\))",
            # Column existence checks: 'column' in/not in df.columns
            r"['\"]([^'\"]+)['\"]\s+(?:not\s+)?in\s+(?:self\.df|df|data|master_df|filtered_df|tier_data|page_data|criteria_df|experience_df|unified_df|audit_df)\.columns",
            # groupby operations: .groupby('column') or .groupby(['col1', 'col2'])
            r"\.groupby\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\.groupby\s*\(\s*\[\s*['\"]([^'\"]+)['\"]",
            # sort_values operations: .sort_values('column') or .sort_values(['col1', 'col2'])
            r"\.sort_values\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\.sort_values\s*\(\s*\[\s*['\"]([^'\"]+)['\"]",
            # Pandas operations that use column names
            r"\.drop\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",
            r"\.rename\s*\([^)]*['\"]([^'\"]+)['\"]",
            # Column selection: df[['col1', 'col2']]
            r"(?:self\.df|df|data|master_df|filtered_df|tier_data|page_data|criteria_df|experience_df|unified_df|audit_df)\s*\[\s*\[\s*['\"]([^'\"]+)['\"]",
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
        """Check if a string is likely a column name with enhanced filtering"""
        # Filter out common non-column strings
        exclude_patterns = [
            'streamlit', 'pandas', 'plotly', 'numpy', 'matplotlib',
            'main', 'data', 'file', 'path', 'http', 'www',
            'title', 'label', 'width', 'height', 'size',
            # Session state and dictionary keys
            'master_df', 'summary', 'stats', 'brand_health', 'sentiment',
            'conversion', 'key_metrics', 'recommendations', 'story', 'opp',
            'experience_records', 'total_recommendations', 'status', 'emoji',
            'critical_issues', 'quick_wins', 'success_pages', 'net_sentiment',
            'positive', 'neutral', 'negative', 'current_score', 'effort_level',
            'key_strengths', 'avg_engagement', 'avg_score_mean'
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
        """Check a single file for column integrity and API compatibility issues"""
        logger.info(f"Checking {file_path.name}...")
        
        column_refs = self._extract_column_references(file_path)
        issues = []
        valid_refs = []
        warnings = []
        
        for ref in column_refs:
            column = ref['column']
            
            # Handle API compatibility issues
            if ref.get('type') == 'api_compatibility':
                issues.append({
                    'severity': ref.get('severity', 'ERROR'),
                    'column': column,
                    'line': ref['line'],
                    'type': ref['type'],
                    'message': ref['message'],
                    'context': ref.get('context', ''),
                    'issue_type': ref.get('issue_type', 'API Compatibility')
                })
                continue
            
            # Handle column references
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
                # Check for data type compatibility issues
                column_type = self._get_column_type(column)
                numeric_columns = self._get_numeric_columns()
                empty_columns = self._get_empty_columns()
                
                # Warn about using empty columns for calculations
                if column in empty_columns and any(calc_pattern in ref.get('context', '') for calc_pattern in ['.mean()', '.sum()', '.std()', '.count()']):
                    warnings.append({
                        'severity': 'WARNING',
                        'column': column,
                        'line': ref['line'],
                        'type': 'empty_column_calculation',
                        'message': f"Column '{column}' is empty in current dataset - calculations will fail",
                        'context': ref.get('context', ''),
                        'suggestion': f"Use numeric columns like: {', '.join(list(numeric_columns)[:5])}"
                    })
                
                # Warn about using text columns for numeric operations
                if column_type in ['string'] and column not in numeric_columns and any(calc_pattern in ref.get('context', '') for calc_pattern in ['.mean()', '.sum()', '.std()']):
                    warnings.append({
                        'severity': 'WARNING',
                        'column': column,
                        'line': ref['line'],
                        'type': 'type_mismatch',
                        'message': f"Column '{column}' is text type but used in numeric calculation",
                        'context': ref.get('context', ''),
                        'suggestion': f"Use numeric columns: {', '.join(list(numeric_columns)[:5])}"
                    })
                
                valid_refs.append(ref)
        
        # Combine issues and warnings
        all_issues = issues + warnings
        
        return {
            'file': file_path.name,
            'path': str(file_path),
            'total_refs': len(column_refs),
            'valid_refs': len(valid_refs),
            'issues': all_issues,
            'status': 'PASS' if not issues else 'FAIL',  # Only errors fail, warnings are OK
            'warnings': len(warnings),
            'errors': len(issues)
        }
    
    def _suggest_alternative(self, column: str) -> str:
        """Suggest alternative column names for invalid columns with type awareness"""
        # Enhanced mappings using the new typed configuration
        numeric_columns = self._get_numeric_columns()
        
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
        
        # Suggest numeric alternatives if this looks like a numeric operation
        if any(calc_hint in column.lower() for calc_hint in ['score', 'rating', 'value', 'performance']):
            return f"For calculations, use numeric columns: {', '.join(list(numeric_columns)[:3])}"
        
        return "No direct alternative found"
    
    def check_all_dashboard_files(self) -> Dict:
        """Check all dashboard files for column integrity and API compatibility"""
        logger.info("Starting comprehensive dashboard integrity check...")
        
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
            'total_warnings': 0,
            'files_with_errors': 0,
            'files_with_warnings': 0,
            'summary': {}
        }
        
        for file_path in python_files:
            file_result = self.check_file(file_path)
            results['files_checked'].append(file_result)
            
            if file_result['errors'] > 0:
                results['files_with_errors'] += 1
                results['total_issues'] += file_result['errors']
            
            if file_result['warnings'] > 0:
                results['files_with_warnings'] += 1
                results['total_warnings'] += file_result['warnings']
        
        # Generate summary
        results['summary'] = {
            'total_files': len(results['files_checked']),
            'files_with_errors': results['files_with_errors'],
            'files_with_warnings': results['files_with_warnings'],
            'files_clean': len(results['files_checked']) - results['files_with_errors'] - results['files_with_warnings'],
            'total_errors': results['total_issues'],
            'total_warnings': results['total_warnings']
        }
        
        # Add recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        return results
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate recommendations based on check results with enhanced guidance"""
        recommendations = []
        
        if results['total_issues'] == 0 and results['total_warnings'] == 0:
            recommendations.append("✅ All dashboard files passed integrity check with no issues!")
            return recommendations
        
        # Error analysis
        if results['total_issues'] > 0:
            recommendations.append(f"🚨 Found {results['total_issues']} errors that will prevent dashboard from running:")
            
            # Collect error types
            error_types = {}
            for file_result in results['files_checked']:
                for issue in file_result['issues']:
                    if issue['severity'] == 'ERROR':
                        error_type = issue.get('issue_type', issue.get('type', 'Unknown'))
                        error_types[error_type] = error_types.get(error_type, 0) + 1
            
            for error_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
                recommendations.append(f"   • {error_type}: {count} occurrences")
        
        # Warning analysis
        if results['total_warnings'] > 0:
            recommendations.append(f"⚠️  Found {results['total_warnings']} warnings (won't break dashboard but may cause issues):")
            
            warning_types = {}
            for file_result in results['files_checked']:
                for issue in file_result['issues']:
                    if issue['severity'] == 'WARNING':
                        warning_type = issue.get('issue_type', issue.get('type', 'Unknown'))
                        warning_types[warning_type] = warning_types.get(warning_type, 0) + 1
            
            for warning_type, count in sorted(warning_types.items(), key=lambda x: x[1], reverse=True):
                recommendations.append(f"   • {warning_type}: {count} occurrences")
        
        recommendations.append("")
        recommendations.append("🔧 Priority fixes:")
        recommendations.append("   1. Fix ERROR-level issues first (these break the dashboard)")
        recommendations.append("   2. Address API compatibility issues (update_xaxis → update_xaxes)")
        recommendations.append("   3. Fix Streamlit session state conflicts")
        recommendations.append("   4. Use correct method names (calculate_tier_performance → get_tier_summary)")
        recommendations.append("   5. Replace deprecated pandas methods (applymap → map)")
        
        recommendations.append("")
        recommendations.append("💡 Data type recommendations:")
        numeric_cols = self._get_numeric_columns()
        empty_cols = self._get_empty_columns()
        recommendations.append(f"   • Use numeric columns for calculations: {', '.join(list(numeric_cols)[:5])}")
        if empty_cols:
            recommendations.append(f"   • Avoid empty columns: {', '.join(list(empty_cols)[:3])}")
        
        return recommendations
    
    def generate_report(self, results: Dict) -> str:
        """Generate a comprehensive report of the integrity check"""
        report = []
        report.append("=" * 70)
        report.append("ENHANCED DASHBOARD INTEGRITY CHECK REPORT")
        report.append("Column References + API Compatibility + Data Types")
        report.append("=" * 70)
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append(f"📊 SUMMARY")
        report.append(f"   Files Checked: {summary['total_files']}")
        report.append(f"   Files with Errors: {summary['files_with_errors']} (will break dashboard)")
        report.append(f"   Files with Warnings: {summary['files_with_warnings']} (may cause issues)")
        report.append(f"   Clean Files: {summary['files_clean']}")
        report.append(f"   Total Errors: {summary['total_errors']}")
        report.append(f"   Total Warnings: {summary['total_warnings']}")
        report.append("")
        
        # Available columns info with types
        report.append(f"📋 AVAILABLE COLUMNS ({len(self.available_columns)})")
        numeric_cols = self._get_numeric_columns()
        empty_cols = self._get_empty_columns()
        
        report.append(f"   Numeric columns ({len(numeric_cols)}): {', '.join(sorted(numeric_cols))}")
        report.append(f"   Empty columns ({len(empty_cols)}): {', '.join(sorted(empty_cols))}")
        report.append("")
        
        # File-by-file results
        if results['files_checked']:
            report.append("🔍 DETAILED RESULTS")
            report.append("-" * 50)
            
            for file_result in results['files_checked']:
                if file_result['errors'] > 0:
                    status_icon = "❌"
                elif file_result['warnings'] > 0:
                    status_icon = "⚠️ "
                else:
                    status_icon = "✅"
                    
                report.append(f"{status_icon} {file_result['file']}")
                report.append(f"   Total References: {file_result['total_refs']}")
                report.append(f"   Valid References: {file_result['valid_refs']}")
                report.append(f"   Errors: {file_result['errors']}")
                report.append(f"   Warnings: {file_result['warnings']}")
                
                if file_result['issues']:
                    for issue in file_result['issues']:
                        severity_icon = "🚨" if issue['severity'] == 'ERROR' else "⚠️ "
                        report.append(f"      {severity_icon} Line {issue['line']}: {issue.get('issue_type', issue['type'])}")
                        report.append(f"         Column: '{issue['column']}'")
                        report.append(f"         Message: {issue['message']}")
                        if issue.get('suggestion'):
                            report.append(f"         💡 {issue['suggestion']}")
                        if issue.get('context'):
                            report.append(f"         📝 Context: {issue['context'][:80]}...")
                
                report.append("")
        
        # Recommendations
        if results.get('recommendations'):
            report.append("💡 RECOMMENDATIONS")
            report.append("-" * 50)
            for rec in results['recommendations']:
                report.append(rec)
            report.append("")
        
        report.append("=" * 70)
        return "\n".join(report)


def main():
    """Main function to run enhanced integrity check"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced dashboard integrity check with type validation')
    parser.add_argument('--output', '-o', help='Output report to file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--errors-only', action='store_true', help='Show only errors, skip warnings')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run integrity check
    checker = DashboardIntegrityChecker()
    results = checker.check_all_dashboard_files()
    
    # Filter results if errors-only requested
    if args.errors_only:
        for file_result in results['files_checked']:
            file_result['issues'] = [issue for issue in file_result['issues'] if issue['severity'] == 'ERROR']
    
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
        print(f"\n❌ Found {results['total_issues']} errors across {results['files_with_errors']} files")
        if results['total_warnings'] > 0:
            print(f"⚠️  Also found {results['total_warnings']} warnings across {results['files_with_warnings']} files")
        exit(1)
    elif results['total_warnings'] > 0:
        print(f"\n⚠️  Found {results['total_warnings']} warnings across {results['files_with_warnings']} files (no errors)")
        exit(0)
    else:
        print(f"\n✅ All {results['summary']['total_files']} files passed integrity check!")
        exit(0)


if __name__ == "__main__":
    main() 