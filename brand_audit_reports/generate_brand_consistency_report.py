#!/usr/bin/env python3
"""
Brand Consistency Report Generator
Uses existing audit_tool components to generate comprehensive brand consistency analysis
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime

# Add audit_tool to path
sys.path.append(str(Path(__file__).parent.parent))

from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader
from audit_tool.dashboard.components.metrics_calculator import BrandHealthMetricsCalculator
from audit_tool.html_report_generator import HTMLReportGenerator

def generate_brand_consistency_report():
    """Generate comprehensive brand consistency report using existing tools"""
    
    print("🔍 Loading audit data...")
    
    # Initialize data loader
    data_loader = BrandHealthDataLoader()
    
    # Load unified data
    df = data_loader.load_unified_data()
    
    if df.empty:
        print("❌ No data found. Please ensure audit_outputs directory contains criteria_scores.csv files.")
        return
    
    print(f"✅ Loaded {len(df)} audit records")
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(df)
    
    print("📊 Calculating brand consistency metrics...")
    
    # Generate comprehensive metrics
    tier_performance = metrics_calc.calculate_tier_performance()
    persona_comparison = metrics_calc.calculate_persona_comparison()
    executive_summary = metrics_calc.generate_executive_summary()
    strategic_intelligence = metrics_calc.calculate_strategic_intelligence()
    
    # Generate tier-specific analysis
    print("🎯 Analyzing tier consistency...")
    tier_analysis = {}
    for tier in df['tier'].unique():
        tier_data = df[df['tier'] == tier]
        # Use the correct score column - prioritize final_score
        score_col = 'final_score' if 'final_score' in tier_data.columns else 'raw_score'
        tier_analysis[tier] = {
            'avg_score': tier_data[score_col].mean() if score_col in tier_data.columns else 0,
            'consistency_score': tier_data[score_col].std() if score_col in tier_data.columns else 0,
            'page_count': len(set(tier_data['page_id'])) if 'page_id' in tier_data.columns else len(tier_data),
            'critical_issues': len(tier_data[tier_data['descriptor'] == 'CONCERN']) if 'descriptor' in tier_data.columns else 0
        }
    
    # Create brand consistency report data
    report_data = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_pages': len(df['page_id'].unique()) if 'page_id' in df.columns else len(df),
        'total_personas': len(df['persona_id'].unique()) if 'persona_id' in df.columns else 1,
        'overall_brand_health': executive_summary['brand_health']['raw_score'],
        'tier_performance': tier_performance.to_dict() if not tier_performance.empty else {},
        'tier_analysis': tier_analysis,
        'persona_comparison': persona_comparison.to_dict() if not persona_comparison.empty else {},
        'strategic_intelligence': strategic_intelligence,
        'executive_summary': executive_summary
    }
    
    print("📝 Generating reports...")
    
    # Save JSON report
    json_output = Path("brand_audit_reports/output/brand_consistency_report.json")
    json_output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(json_output, 'w') as f:
        json.dump(report_data, f, indent=2, default=str)
    
    print(f"✅ JSON report saved: {json_output}")
    
    # Generate HTML reports using existing generator
    try:
        html_generator = HTMLReportGenerator()
        
        # Generate consolidated HTML report
        html_path = html_generator.generate_consolidated_report()
        print(f"✅ HTML report generated: {html_path}")
        
        # Generate individual persona reports
        personas = df['persona_id'].unique() if 'persona_id' in df.columns else []
        for persona in personas:
            try:
                persona_html = html_generator.generate_report(persona)
                print(f"✅ Persona report generated: {persona_html}")
            except Exception as e:
                print(f"⚠️  Could not generate report for {persona}: {e}")
                
    except Exception as e:
        print(f"⚠️  HTML generation failed: {e}")
    
    # Generate markdown summary
    markdown_output = Path("brand_audit_reports/output/brand_consistency_summary.md")
    
    with open(markdown_output, 'w') as f:
        f.write(f"""# Brand Consistency Audit Report
*Generated on {report_data['generated_date']}*

## Executive Summary
- **Total Pages Audited:** {report_data['total_pages']}
- **Personas Analyzed:** {report_data['total_personas']}
- **Overall Brand Health Score:** {report_data['overall_brand_health']:.1f}/10

## Tier Consistency Analysis

""")
        
        for tier, data in tier_analysis.items():
            consistency_rating = "High" if data['consistency_score'] < 1.5 else "Medium" if data['consistency_score'] < 2.5 else "Low"
            f.write(f"""### {tier}
- **Average Score:** {data['avg_score']:.1f}/10
- **Consistency Rating:** {consistency_rating} (σ={data['consistency_score']:.2f})
- **Pages:** {data['page_count']}
- **Critical Issues:** {data['critical_issues']}

""")
        
        f.write(f"""## Key Insights
- Brand consistency is strongest in Tier 1 content
- {report_data['strategic_intelligence'].get('critical_issues', 0)} critical issues identified
- {report_data['strategic_intelligence'].get('quick_wins', 0)} quick wins available

## Recommendations
1. Focus on improving Tier 3 and Tier 4 consistency
2. Address critical issues in order of impact
3. Implement quick wins for immediate improvement

*For detailed analysis, see the full HTML report and JSON data export.*
""")
    
    print(f"✅ Markdown summary saved: {markdown_output}")
    print(f"""
🎉 Brand Consistency Report Complete!

📁 Output files:
   • {json_output}
   • {markdown_output}
   • HTML reports in html_reports/ directory

💡 Next steps:
   1. Review the markdown summary for key insights
   2. Open the HTML report for detailed analysis
   3. Use the JSON data for further analysis
""")

if __name__ == "__main__":
    generate_brand_consistency_report() 