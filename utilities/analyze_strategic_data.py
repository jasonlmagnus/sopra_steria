#!/usr/bin/env python3
"""
Strategic Data Analysis Script
Analyzes StrategicRecommendations.tsx data requirements vs actual data sources
"""

import pandas as pd
import json
import re
from typing import Dict, List, Set, Any
from pathlib import Path

def extract_tsx_data_fields() -> Dict[str, List[str]]:
    """Extract all data fields actually used in StrategicRecommendations.tsx"""
    
    # Read the actual TSX file and extract field references
    tsx_file_path = "web/src/pages/StrategicRecommendations.tsx"
    
    try:
        with open(tsx_file_path, 'r') as f:
            tsx_content = f.read()
    except Exception as e:
        print(f"Could not read TSX file: {e}")
        return {}
    
    # Extract field references from the TSX content
    import re
    
    # Find all references like strategicData.section.field or data.field
    patterns = {
        "executiveSummary": r'strategicData\.executiveSummary\.(\w+)',
        "strategicThemes": r'theme\.(\w+)',
        "recommendations": r'rec\.(\w+)',
        "competitiveContext": r'strategicData\.competitiveContext\.(\w+)',
        "tierAnalysis": r'data\.(\w+)',
        "implementationRoadmap": r'phase\.(\w+)',
        "businessImpact": r'strategicData\.businessImpact\.(\w+)'
    }
    
    extracted_fields = {}
    
    for section, pattern in patterns.items():
        matches = re.findall(pattern, tsx_content)
        # Remove duplicates and sort
        unique_fields = sorted(list(set(matches)))
        extracted_fields[section] = unique_fields
    
    # Also get interface fields from the file
    interface_match = re.search(r'interface StrategicIntelligence \{(.*?)\}', tsx_content, re.DOTALL)
    if interface_match:
        interface_content = interface_match.group(1)
        
        # Parse each section in the interface
        section_patterns = {
            "executiveSummary": r'executiveSummary:\s*\{([^}]+)\}',
            "strategicThemes": r'strategicThemes:\s*Array<\{([^}]+)\}>',
            "recommendations": r'recommendations:\s*Array<\{([^}]+)\}>',
            "competitiveContext": r'competitiveContext:\s*\{([^}]+)\}',
            "tierAnalysis": r'tierAnalysis:\s*\{[^{]*\{([^}]+)\}',
            "implementationRoadmap": r'implementationRoadmap:\s*Array<\{([^}]+)\}>',
            "businessImpact": r'businessImpact:\s*\{([^}]+)\}'
        }
        
        for section, section_pattern in section_patterns.items():
            section_match = re.search(section_pattern, interface_content)
            if section_match:
                section_content = section_match.group(1)
                # Extract field names
                field_matches = re.findall(r'(\w+):', section_content)
                if section not in extracted_fields:
                    extracted_fields[section] = []
                # Merge interface fields with usage fields
                all_fields = set(extracted_fields[section] + field_matches)
                extracted_fields[section] = sorted(list(all_fields))
    
    return extracted_fields

def analyze_csv_data() -> Dict[str, Any]:
    """Analyze unified_audit_data.csv structure"""
    try:
        # Read first few rows to understand structure
        df = pd.read_csv('audit_data/unified_audit_data.csv', nrows=5)
        
        return {
            "available_columns": list(df.columns),
            "numeric_columns": list(df.select_dtypes(include=['number']).columns),
            "text_columns": list(df.select_dtypes(include=['object']).columns),
            "boolean_columns": [col for col in df.columns if col.endswith('_flag')],
            "score_columns": [col for col in df.columns if 'score' in col.lower()],
            "sample_row": df.iloc[0].to_dict() if len(df) > 0 else {}
        }
    except Exception as e:
        return {"error": f"Could not analyze CSV: {str(e)}"}

def analyze_metrics_calculator() -> Dict[str, Any]:
    """Analyze what metrics_calculator.py can actually provide"""
    
    # From the metrics_calculator.py file, extract what calculate_strategic_intelligence returns
    actual_calculator_output = {
        "executiveSummary": [
            "totalRecommendations",
            "highImpactOpportunities", 
            "quickWinOpportunities",  # NEW: replaced pipelineRisk
            "criticalIssues",         # NEW: replaced competitiveGaps
            "overallScore"            # NEW: replaced strategicInvestmentROI
        ],
        "strategicThemes": [
            "id", "title", "description", "currentScore", "targetScore",
            "businessImpact", "affectedPages", "competitiveRisk", 
            "keyInsights", "soWhat"
        ],
        "recommendations": [
            "id", "title", "description", "businessImpact", "implementationEffort",
            "timeline", "tier", "persona", "currentScore", "targetScore",
            "evidence", "soWhat", "implementationSteps", "success_metrics"
        ],
        "competitiveContext": [
            "currentScore", "benchmarkScore", "marketOpportunity", 
            "vulnerabilities", "overallPosition"
        ],
        "tierAnalysis": [
            "count", "averageScore", "criticalIssues", "quickWins", "keyInsights"
        ],
        "implementationRoadmap": [
            "phase", "focus", "recommendations", "expectedImpact"
        ],
        "businessImpact": [
            "optimizationPotential", "improvementAreas", 
            "competitiveAdvantage", "successStories"
        ]
    }
    
    return actual_calculator_output

def analyze_social_media_data() -> Dict[str, Any]:
    """Extract available data from social media dashboard"""
    
    # Based on MASTER_SM_DASHBOARD_DATA_ENHANCED.md
    social_media_fields = {
        "platform_metrics": [
            "average_score", "followers", "engagement_level", "posting_frequency",
            "content_quality", "brand_consistency", "health_status"
        ],
        "content_performance": [
            "engagement_rate", "content_types", "performance_metrics",
            "visual_quality", "tone_consistency"
        ],
        "strategic_data": [
            "overall_social_media_health_score", "platform_coverage", 
            "total_reach", "critical_issues", "brand_consistency_score"
        ]
    }
    
    return social_media_fields

def analyze_journey_data() -> Dict[str, Any]:
    """Extract available data from journey analysis"""
    
    # Based on unified_journey_analysis.md
    journey_fields = {
        "journey_steps": [
            "homepage_reactions", "service_page_reactions", "proof_points",
            "thought_leadership", "contact_conversion"
        ],
        "persona_insights": [
            "persona_reactions", "gap_severity", "common_pain_points",
            "shared_opportunities", "persona_specific_needs"
        ],
        "recommendations": [
            "quick_wins", "strategic_improvements", "persona_optimizations",
            "immediate_actions", "medium_term_improvements"
        ]
    }
    
    return journey_fields

def cross_reference_data(tsx_fields: Dict[str, List[str]], 
                        csv_data: Dict[str, Any],
                        calculator_output: Dict[str, Any],
                        social_data: Dict[str, Any],
                        journey_data: Dict[str, Any]) -> Dict[str, Any]:
    """Cross-reference TSX requirements with actual data sources"""
    
    results = {
        "real_fields": {},
        "fake_fields": {},
        "missing_fields": {},
        "data_source_mapping": {}
    }
    
    csv_columns = set(csv_data.get("available_columns", []))
    
    for section, fields in tsx_fields.items():
        results["real_fields"][section] = []
        results["fake_fields"][section] = []
        results["missing_fields"][section] = []
        results["data_source_mapping"][section] = {}
        
        calculator_fields = set(calculator_output.get(section, []))
        
        for field in fields:
            field_sources = []
            is_real = False
            
            # Check if field is in calculator output (primary source)
            if field in calculator_fields:
                field_sources.append("metrics_calculator")
                is_real = True
            
            # Check if field maps to CSV data
            csv_mappings = {
                "totalRecommendations": "page_id",  # count of records
                "criticalIssues": "critical_issue_flag",
                "quickWinOpportunities": "quick_win_flag", 
                "overallScore": "final_score",
                "currentScore": "final_score",
                "targetScore": "final_score",  # derived
                "tier": "tier",
                "persona": "persona_id",
                "evidence": "evidence",
                "businessImpact": "business_impact_analysis",
                "implementationSteps": "effective_copy_examples",
                "title": "business_impact_analysis",  # derived
                "description": "evidence"
            }
            
            if field in csv_mappings and csv_mappings[field] in csv_columns:
                field_sources.append(f"CSV:{csv_mappings[field]}")
                is_real = True
            
            # Check direct CSV column match
            if field in csv_columns:
                field_sources.append("CSV:direct")
                is_real = True
            
            # Check for score-related fields
            if "score" in field.lower() and any("score" in col for col in csv_columns):
                field_sources.append("CSV:score_columns")
                is_real = True
            
            # If field is not found in any real data source, it's fake
            if is_real:
                results["real_fields"][section].append(field)
                results["data_source_mapping"][section][field] = " | ".join(field_sources)
            else:
                results["fake_fields"][section].append(field)
                results["data_source_mapping"][section][field] = "FAKE - No real data source"
    
    return results

def generate_report(analysis_results: Dict[str, Any]) -> str:
    """Generate a comprehensive report"""
    
    report = []
    report.append("=" * 80)
    report.append("STRATEGIC RECOMMENDATIONS DATA ANALYSIS REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Summary statistics
    total_real = sum(len(fields) for fields in analysis_results["real_fields"].values())
    total_fake = sum(len(fields) for fields in analysis_results["fake_fields"].values())
    total_missing = sum(len(fields) for fields in analysis_results["missing_fields"].values())
    total_fields = total_real + total_fake + total_missing
    
    report.append(f"📊 SUMMARY:")
    report.append(f"   Total Fields Analyzed: {total_fields}")
    report.append(f"   ✅ Real Fields: {total_real} ({total_real/total_fields*100:.1f}%)")
    report.append(f"   ❌ Fake Fields: {total_fake} ({total_fake/total_fields*100:.1f}%)")
    report.append(f"   ❓ Missing Fields: {total_missing} ({total_missing/total_fields*100:.1f}%)")
    report.append("")
    
    # Section-by-section analysis
    for section in analysis_results["real_fields"].keys():
        report.append(f"📋 {section.upper()}:")
        report.append("-" * 40)
        
        # Real fields
        real_fields = analysis_results["real_fields"][section]
        if real_fields:
            report.append(f"   ✅ REAL FIELDS ({len(real_fields)}):")
            for field in sorted(real_fields):
                source = analysis_results["data_source_mapping"][section][field]
                report.append(f"      • {field} → {source}")
        
        # Fake fields
        fake_fields = analysis_results["fake_fields"][section]
        if fake_fields:
            report.append(f"   ❌ FAKE FIELDS ({len(fake_fields)}):")
            for field in sorted(fake_fields):
                report.append(f"      • {field} → NO REAL DATA SOURCE")
        
        # Missing fields
        missing_fields = analysis_results["missing_fields"][section]
        if missing_fields:
            report.append(f"   ❓ MISSING FIELDS ({len(missing_fields)}):")
            for field in sorted(missing_fields):
                report.append(f"      • {field} → NEED TO IMPLEMENT")
        
        report.append("")
    
    # Critical actions needed
    report.append("🚨 CRITICAL ACTIONS NEEDED:")
    report.append("-" * 40)
    
    all_fake_fields = []
    for section, fields in analysis_results["fake_fields"].items():
        for field in fields:
            all_fake_fields.append(f"{section}.{field}")
    
    if all_fake_fields:
        report.append("   1. REMOVE FAKE FIELDS FROM TSX:")
        for field in sorted(all_fake_fields):
            report.append(f"      • {field}")
        report.append("")
    
    report.append("   2. UPDATE metrics_calculator.py to match TSX interface")
    report.append("   3. Restart FastAPI server after changes")
    report.append("   4. Fix TypeScript linter errors")
    report.append("")
    
    # Data source analysis
    report.append("📊 DATA SOURCE ANALYSIS:")
    report.append("-" * 40)
    
    return "\n".join(report)

def main():
    """Main analysis function"""
    
    print("🔍 Analyzing Strategic Recommendations data requirements...")
    print("")
    
    # Extract TSX data requirements
    tsx_fields = extract_tsx_data_fields()
    
    # Analyze actual data sources
    csv_data = analyze_csv_data()
    calculator_output = analyze_metrics_calculator()
    social_data = analyze_social_media_data()
    journey_data = analyze_journey_data()
    
    # Cross-reference everything
    analysis_results = cross_reference_data(
        tsx_fields, csv_data, calculator_output, social_data, journey_data
    )
    
    # Generate report
    report = generate_report(analysis_results)
    
    # Print to console
    print(report)
    
    # Save to file
    with open("strategic_data_analysis_report.txt", "w") as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: strategic_data_analysis_report.txt")
    
    # Return structured data for further processing
    return {
        "tsx_requirements": tsx_fields,
        "csv_data": csv_data,
        "calculator_output": calculator_output,
        "analysis_results": analysis_results
    }

if __name__ == "__main__":
    main() 