#!/usr/bin/env python3
"""
Gap Analysis Tool - Dynamic Development Quality Assurance
Validates React component functionality and detects missing features.
"""

import os
import json
import yaml
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

@dataclass
class Gap:
    component: str
    feature: str
    description: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    detected_at: str
    fix_suggestion: str = ""
    
@dataclass
class GapReport:
    timestamp: str
    total_gaps: int
    critical_gaps: int
    high_gaps: int
    medium_gaps: int
    low_gaps: int
    gaps: List[Gap] = field(default_factory=list)
    
    def add_gap(self, gap: Gap):
        self.gaps.append(gap)
        self.total_gaps += 1
        if gap.severity == 'critical':
            self.critical_gaps += 1
        elif gap.severity == 'high':
            self.high_gaps += 1
        elif gap.severity == 'medium':
            self.medium_gaps += 1
        elif gap.severity == 'low':
            self.low_gaps += 1

class GapAnalyzer:
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.web_dir = self.project_root / "web"
        self.api_dir = self.project_root / "api"
        self.audit_tool_dir = self.project_root / "audit_tool"
        
        # API base URL for testing
        self.api_base = "http://localhost:3000"
        
        # Expected components and their features
        self.expected_features = {
            "ExecutiveDashboard": {
                "filters": ["tierFilter"],
                "metrics": ["brand_health", "key_metrics", "sentiment", "conversion"],
                "charts": ["sparklines", "trend_analysis"],
                "api_endpoints": ["/api/summary", "/api/opportunities", "/api/strategic-assessment"]
            },
            "PersonaInsights": {
                "filters": ["persona_selector", "comparison_mode"],
                "metrics": ["avg_score", "page_count", "critical_issues"],
                "charts": ["comparison_charts", "performance_charts"],
                "api_endpoints": ["/api/persona-insights", "/api/persona-comparison"]
            },
            "ContentMatrix": {
                "filters": ["persona", "tier", "score", "performance_level"],
                "metrics": ["content_performance", "tier_analysis"],
                "charts": ["heatmap", "performance_charts"],
                "api_endpoints": ["/api/content-matrix"]
            },
            "Recommendations": {
                "filters": ["category", "timeline", "impact", "urgency"],
                "metrics": ["priority_score", "impact_score", "urgency_score"],
                "charts": ["distribution_charts", "scatter_plots"],
                "api_endpoints": ["/api/recommendations", "/api/full-recommendations"]
            },
            "SuccessLibrary": {
                "filters": ["score_filter", "category_filter"],
                "metrics": ["success_count", "pattern_analysis"],
                "charts": ["distribution_charts"],
                "api_endpoints": ["/api/success-stories"]
            }
        }
        
    def analyze_gaps(self) -> GapReport:
        """Main gap analysis function"""
        report = GapReport(
            timestamp=datetime.now().isoformat(),
            total_gaps=0,
            critical_gaps=0,
            high_gaps=0,
            medium_gaps=0,
            low_gaps=0
        )
        
        print("🔍 Starting Gap Analysis...")
        print(f"Project Root: {self.project_root}")
        
        # Check component structure
        self._check_component_structure(report)
        
        # Check API endpoints
        self._check_api_endpoints(report)
        
        # Check routing integration
        self._check_routing_integration(report)
        
        # Check filter implementations
        self._check_filter_implementations(report)
        
        # Check data consistency
        self._check_data_consistency(report)
        
        return report
        
    def _check_component_structure(self, report: GapReport):
        """Check if expected components exist with required features"""
        print("\n📁 Checking Component Structure...")
        
        pages_dir = self.web_dir / "src" / "pages"
        if not pages_dir.exists():
            report.add_gap(Gap(
                component="Project Structure",
                feature="pages_directory",
                description="Missing pages directory",
                severity="critical",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Create web/src/pages directory"
            ))
            return
            
        for component_name, expected_features in self.expected_features.items():
            component_file = pages_dir / f"{component_name}.tsx"
            
            if not component_file.exists():
                report.add_gap(Gap(
                    component=component_name,
                    feature="component_file",
                    description=f"Missing {component_name}.tsx file",
                    severity="high",
                    detected_at=datetime.now().isoformat(),
                    fix_suggestion=f"Create {component_name}.tsx component"
                ))
                continue
                
            # Check component content
            self._analyze_component_content(component_file, component_name, expected_features, report)
            
    def _analyze_component_content(self, component_file: Path, component_name: str, 
                                 expected_features: Dict, report: GapReport):
        """Analyze component file content for missing features"""
        try:
            content = component_file.read_text()
            
            # Check for filter implementation
            if "filters" in expected_features:
                for filter_name in expected_features["filters"]:
                    if filter_name not in content:
                        report.add_gap(Gap(
                            component=component_name,
                            feature=f"filter_{filter_name}",
                            description=f"Missing {filter_name} filter implementation",
                            severity="medium",
                            detected_at=datetime.now().isoformat(),
                            fix_suggestion=f"Implement {filter_name} filter in {component_name}"
                        ))
                        
            # Check for API endpoint usage
            if "api_endpoints" in expected_features:
                for endpoint in expected_features["api_endpoints"]:
                    if endpoint not in content:
                        report.add_gap(Gap(
                            component=component_name,
                            feature=f"api_{endpoint.replace('/', '_')}",
                            description=f"Missing API endpoint {endpoint}",
                            severity="medium",
                            detected_at=datetime.now().isoformat(),
                            fix_suggestion=f"Add {endpoint} API call to {component_name}"
                        ))
                        
            # Check for chart implementations
            if "charts" in expected_features:
                for chart_type in expected_features["charts"]:
                    if "PlotlyChart" not in content and "BarChart" not in content:
                        report.add_gap(Gap(
                            component=component_name,
                            feature=f"chart_{chart_type}",
                            description=f"Missing chart implementation for {chart_type}",
                            severity="low",
                            detected_at=datetime.now().isoformat(),
                            fix_suggestion=f"Add {chart_type} visualization to {component_name}"
                        ))
                        
        except Exception as e:
            report.add_gap(Gap(
                component=component_name,
                feature="file_analysis",
                description=f"Error analyzing component file: {str(e)}",
                severity="medium",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Check file permissions and syntax"
            ))
            
    def _check_api_endpoints(self, report: GapReport):
        """Check if API endpoints are accessible"""
        print("\n🌐 Checking API Endpoints...")
        
        # First check if API server is running
        try:
            response = requests.get(f"{self.api_base}/health", timeout=5)
            if response.status_code != 200:
                report.add_gap(Gap(
                    component="API Server",
                    feature="health_check",
                    description="API server health check failed",
                    severity="critical",
                    detected_at=datetime.now().isoformat(),
                    fix_suggestion="Start API server: npm run dev (in api directory)"
                ))
        except requests.exceptions.ConnectionError:
            report.add_gap(Gap(
                component="API Server",
                feature="connection",
                description="Cannot connect to API server",
                severity="critical",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Start API server: npm run dev (in api directory)"
            ))
            return
        except Exception as e:
            report.add_gap(Gap(
                component="API Server",
                feature="connection",
                description=f"API connection error: {str(e)}",
                severity="high",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Check API server status and network connectivity"
            ))
            return
            
        # Check individual endpoints
        all_endpoints = set()
        for component_features in self.expected_features.values():
            if "api_endpoints" in component_features:
                all_endpoints.update(component_features["api_endpoints"])
                
        for endpoint in all_endpoints:
            try:
                response = requests.get(f"{self.api_base}{endpoint}", timeout=10)
                if response.status_code != 200:
                    report.add_gap(Gap(
                        component="API",
                        feature=f"endpoint_{endpoint.replace('/', '_')}",
                        description=f"API endpoint {endpoint} returned {response.status_code}",
                        severity="high",
                        detected_at=datetime.now().isoformat(),
                        fix_suggestion=f"Fix API endpoint {endpoint} implementation"
                    ))
            except Exception as e:
                report.add_gap(Gap(
                    component="API",
                    feature=f"endpoint_{endpoint.replace('/', '_')}",
                    description=f"Error calling {endpoint}: {str(e)}",
                    severity="medium",
                    detected_at=datetime.now().isoformat(),
                    fix_suggestion=f"Debug API endpoint {endpoint}"
                ))
                
    def _check_routing_integration(self, report: GapReport):
        """Check if components are properly integrated in routing"""
        print("\n🗺️ Checking Routing Integration...")
        
        app_file = self.web_dir / "src" / "App.tsx"
        if not app_file.exists():
            report.add_gap(Gap(
                component="Routing",
                feature="app_file",
                description="Missing App.tsx file",
                severity="critical",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Create App.tsx with routing configuration"
            ))
            return
            
        try:
            app_content = app_file.read_text()
            
            for component_name in self.expected_features.keys():
                # Check if component is imported
                if f"import {component_name}" not in app_content:
                    report.add_gap(Gap(
                        component="Routing",
                        feature=f"import_{component_name}",
                        description=f"{component_name} not imported in App.tsx",
                        severity="medium",
                        detected_at=datetime.now().isoformat(),
                        fix_suggestion=f"Add import for {component_name} in App.tsx"
                    ))
                    
                # Check if component has a route
                if f"<Route" in app_content and f"element={{{component_name}}}" not in app_content:
                    report.add_gap(Gap(
                        component="Routing",
                        feature=f"route_{component_name}",
                        description=f"{component_name} not configured in routing",
                        severity="medium",
                        detected_at=datetime.now().isoformat(),
                        fix_suggestion=f"Add route for {component_name} in App.tsx"
                    ))
                    
        except Exception as e:
            report.add_gap(Gap(
                component="Routing",
                feature="analysis",
                description=f"Error analyzing routing: {str(e)}",
                severity="medium",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Check App.tsx file syntax"
            ))
            
    def _check_filter_implementations(self, report: GapReport):
        """Check if filters are properly implemented"""
        print("\n🎛️ Checking Filter Implementations...")
        
        # Check if FilterContext exists
        filter_context_file = self.web_dir / "src" / "context" / "FilterContext.tsx"
        if not filter_context_file.exists():
            report.add_gap(Gap(
                component="Filters",
                feature="filter_context",
                description="Missing FilterContext implementation",
                severity="high",
                detected_at=datetime.now().isoformat(),
                fix_suggestion="Create FilterContext for global state management"
            ))
            
    def _check_data_consistency(self, report: GapReport):
        """Check for data consistency issues"""
        print("\n📊 Checking Data Consistency...")
        
        # Check if required data files exist
        required_files = [
            "audit_data/unified_audit_data.csv",
            "audit_data/unified_audit_data.parquet",
            "api/data/gap_analysis.json",
            "api/data/implementation_tracking.json"
        ]
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                report.add_gap(Gap(
                    component="Data",
                    feature=f"data_file_{file_path.replace('/', '_')}",
                    description=f"Missing required data file: {file_path}",
                    severity="medium",
                    detected_at=datetime.now().isoformat(),
                    fix_suggestion=f"Generate or restore {file_path}"
                ))
                
    def generate_report(self, report: GapReport, output_file: Optional[str] = None):
        """Generate detailed gap analysis report"""
        if output_file is None:
            output_path = self.project_root / "gap_analysis_report.json"
        else:
            output_path = Path(output_file)
            
        # Convert to JSON-serializable format
        report_dict = {
            "timestamp": report.timestamp,
            "summary": {
                "total_gaps": report.total_gaps,
                "critical_gaps": report.critical_gaps,
                "high_gaps": report.high_gaps,
                "medium_gaps": report.medium_gaps,
                "low_gaps": report.low_gaps
            },
            "gaps": [
                {
                    "component": gap.component,
                    "feature": gap.feature,
                    "description": gap.description,
                    "severity": gap.severity,
                    "detected_at": gap.detected_at,
                    "fix_suggestion": gap.fix_suggestion
                }
                for gap in report.gaps
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2)
            
        print(f"\n📋 Report saved to: {output_path}")
        return output_path
        
    def print_summary(self, report: GapReport):
        """Print a summary of the gap analysis"""
        print("\n" + "="*60)
        print("🎯 GAP ANALYSIS SUMMARY")
        print("="*60)
        print(f"Timestamp: {report.timestamp}")
        print(f"Total Gaps: {report.total_gaps}")
        print(f"  🔴 Critical: {report.critical_gaps}")
        print(f"  🟡 High: {report.high_gaps}")
        print(f"  🟠 Medium: {report.medium_gaps}")
        print(f"  🟢 Low: {report.low_gaps}")
        
        if report.critical_gaps > 0:
            print("\n🚨 CRITICAL GAPS (Fix Immediately):")
            for gap in report.gaps:
                if gap.severity == 'critical':
                    print(f"  • {gap.component}: {gap.description}")
                    print(f"    💡 Fix: {gap.fix_suggestion}")
                    
        if report.high_gaps > 0:
            print("\n⚠️ HIGH PRIORITY GAPS:")
            for gap in report.gaps:
                if gap.severity == 'high':
                    print(f"  • {gap.component}: {gap.description}")
                    
        print("\n" + "="*60)
        
        # Health score
        total_possible = len(self.expected_features) * 4  # Rough estimate
        health_score = max(0, 100 - (report.total_gaps * 5))
        print(f"🏥 Overall Health Score: {health_score:.1f}%")
        
        if health_score >= 90:
            print("✅ Excellent! Dashboard is in great shape.")
        elif health_score >= 70:
            print("👍 Good! Minor improvements needed.")
        elif health_score >= 50:
            print("⚠️ Fair. Several issues need attention.")
        else:
            print("🚨 Poor. Significant issues require immediate attention.")

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Gap Analysis Tool for Brand Health Dashboard")
    parser.add_argument("--project-root", help="Project root directory", default=None)
    parser.add_argument("--output", help="Output file for detailed report", default=None)
    parser.add_argument("--api-base", help="API base URL", default="http://localhost:3000")
    
    args = parser.parse_args()
    
    analyzer = GapAnalyzer(project_root=args.project_root)
    if args.api_base:
        analyzer.api_base = args.api_base
        
    # Run analysis
    report = analyzer.analyze_gaps()
    
    # Generate outputs
    analyzer.print_summary(report)
    analyzer.generate_report(report, args.output)
    
    # Exit with error code if critical gaps found
    if report.critical_gaps > 0:
        print("\n❌ Analysis failed due to critical gaps.")
        return 1
    else:
        print("\n✅ Analysis completed successfully.")
        return 0

if __name__ == "__main__":
    exit(main()) 