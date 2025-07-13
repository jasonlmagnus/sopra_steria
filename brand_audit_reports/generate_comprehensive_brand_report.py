#!/usr/bin/env python3
"""
Comprehensive Brand Consistency Report Generator
Integrates all audit data sources: website, social media, and visual brand
"""

import sys
import os
import re
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import numpy as np
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def clean_nan_values(obj):
    """Recursively replace NaN values with None for JSON serialization"""
    if isinstance(obj, dict):
        return {k: clean_nan_values(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan_values(item) for item in obj]
    elif isinstance(obj, float) and np.isnan(obj):
        return None
    elif pd.isna(obj):
        return None
    else:
        return obj

# Add audit_tool to path
sys.path.append(str(Path(__file__).parent.parent))

from audit_tool.dashboard.components.data_loader import BrandHealthDataLoader
from audit_tool.dashboard.components.metrics_calculator import BrandHealthMetricsCalculator
from audit_tool.html_report_generator import HTMLReportGenerator
from audit_tool.ai_interface import AIInterface

def load_visual_brand_data() -> pd.DataFrame:
    """Load visual brand audit scores"""
    try:
        visual_df = pd.read_csv("audit_inputs/visual_brand/brand_audit_scores.csv")
        print(f"✅ Loaded {len(visual_df)} visual brand audit records")
        return visual_df
    except Exception as e:
        print(f"⚠️  Could not load visual brand data: {e}")
        return pd.DataFrame()

def parse_social_media_data() -> Dict[str, Any]:
    """Parse social media dashboard data from markdown"""
    try:
        with open("audit_inputs/social_media/MASTER_SM_DASHBOARD_DATA.md", 'r') as f:
            content = f.read()
        
        # Extract platform scores table
        platform_scores = {}
        lines = content.split('\n')
        
        in_platform_table = False
        for line in lines:
            if "| Platform  | Average Score |" in line:
                in_platform_table = True
                continue
            elif in_platform_table and line.startswith('|') and 'Platform' not in line:
                if line.strip() == '':
                    break
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 3:
                    platform = parts[0]
                    score_str = parts[1].replace('/10', '').strip()
                    try:
                        score = float(score_str)
                        platform_scores[platform] = score
                    except ValueError:
                        continue
        
        # Extract executive summary metrics
        exec_summary = {}
        for line in lines:
            if "Overall Social Media Health Score" in line:
                score_match = re.search(r'(\d+\.\d+)/10', line)
                if score_match:
                    exec_summary['overall_score'] = float(score_match.group(1))
            elif "Brand Consistency Score" in line:
                score_match = re.search(r'(\d+\.\d+)/10', line)
                if score_match:
                    exec_summary['brand_consistency'] = float(score_match.group(1))
        
        # Extract brand attributes from Brand Consistency Analysis table
        brand_attributes = {}
        in_brand_table = False
        for line in lines:
            if "| Element         | LinkedIn |" in line:
                in_brand_table = True
                continue
            elif in_brand_table and line.startswith('|') and 'Element' not in line:
                if line.strip() == '' or '---' in line:
                    continue
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 6:  # Element, LinkedIn, Instagram, Facebook, X/Twitter, Overall
                    element = parts[0]
                    overall_score_str = parts[5].replace('/10', '').strip()
                    try:
                        if overall_score_str != 'N/A' and overall_score_str:
                            overall_score = float(overall_score_str)
                            brand_attributes[element] = overall_score
                    except ValueError:
                        continue
        
        print(f"✅ Parsed social media data: {len(platform_scores)} platforms, {len(brand_attributes)} brand attributes")
        return {
            'platform_scores': platform_scores,
            'brand_attributes': brand_attributes,
            'executive_summary': exec_summary
        }
    except Exception as e:
        print(f"⚠️  Could not parse social media data: {e}")
        return {'platform_scores': {}, 'executive_summary': {}}

def calculate_visual_brand_metrics(visual_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate visual brand consistency metrics"""
    if visual_df.empty:
        return {}
    
    # Group by tier for consistency analysis
    tier_metrics = {}
    for tier in visual_df['Page Type'].unique():
        tier_data = visual_df[visual_df['Page Type'] == tier]
        tier_metrics[tier] = {
            'avg_final_score': tier_data['Final Score'].mean(),
            'logo_compliance': tier_data['Logo Compliance'].mean(),
            'color_palette': tier_data['Color Palette'].mean(),
            'typography': tier_data['Typography'].mean(),
            'page_count': len(tier_data)
        }
    
    # Overall visual brand health
    overall_metrics = {
        'overall_score': visual_df['Final Score'].mean(),
        'logo_compliance': visual_df['Logo Compliance'].mean(),
        'color_consistency': visual_df['Color Palette'].mean(),
        'typography_consistency': visual_df['Typography'].mean(),
        'tier_breakdown': tier_metrics
    }
    
    return overall_metrics

def generate_ai_strategic_narrative(report_data: Dict[str, Any]) -> str:
    """Generate AI-powered strategic narrative for comprehensive brand report"""
    
    # Initialize AI interface (using OpenAI by default)
    ai = AIInterface(model_provider="openai")
    
    # Construct comprehensive prompt for cross-channel analysis
    prompt = f"""
You are a senior brand strategist analyzing comprehensive cross-channel brand consistency data for Sopra Steria.

# COMPREHENSIVE BRAND DATA
{json.dumps(report_data, indent=2)[:8000]}  # Truncate to avoid token limits

# ANALYSIS CONTEXT
- Overall brand health: {report_data.get('overall_brand_health', 'N/A')}/10
- Data sources: Website audit, Visual brand analysis, Social media audit
- Geographic focus: Benelux region
- Target personas: C-suite executives, cybersecurity leaders, transformation leaders

# TASK
Generate a strategic narrative that synthesizes these insights into actionable executive recommendations.

Provide:
1. **Executive Summary** (2-3 paragraphs): What the data reveals about brand consistency across all channels
2. **Critical Gap Analysis** (3-4 key findings): Where brand inconsistency is most damaging
3. **Strategic Recommendations** (3-5 priorities): Specific actions with business impact
4. **Investment Priorities** (ranked list): What to fix first and why

Focus on:
- Cross-channel brand consistency implications
- Business impact of identified gaps
- Specific, actionable recommendations
- Executive-level strategic insights

Format as markdown with clear sections and bullet points.
"""
    
    try:
        narrative = ai._generate_ai_response(prompt)
        return narrative
    except Exception as e:
        print(f"⚠️  AI narrative generation failed: {e}")
        return "AI narrative generation unavailable - using data-driven summary instead."

def generate_comprehensive_brand_report():
    """Generate comprehensive brand consistency report using all data sources"""
    
    print("🔍 Loading comprehensive audit data...")
    
    # Load core audit data
    data_loader = BrandHealthDataLoader()
    df = data_loader.load_unified_data()
    
    if df.empty:
        print("❌ No core audit data found.")
        return
    
    # Load additional data sources
    visual_df = load_visual_brand_data()
    social_data = parse_social_media_data()
    
    print(f"✅ Loaded {len(df)} core audit records")
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(df)
    
    print("📊 Calculating comprehensive brand metrics...")
    
    # Core metrics
    tier_performance = metrics_calc.calculate_tier_performance()
    persona_comparison = metrics_calc.calculate_persona_comparison()
    executive_summary = metrics_calc.generate_executive_summary()
    strategic_intelligence = metrics_calc.calculate_strategic_intelligence()
    
    # Visual brand metrics
    visual_metrics = calculate_visual_brand_metrics(visual_df)
    
    # Enhanced tier analysis with visual data
    print("🎯 Analyzing cross-channel tier consistency...")
    tier_analysis = {}
    
    for tier in df['tier'].unique():
        if pd.isna(tier):
            continue
            
        tier_data = df[df['tier'] == tier]
        score_col = 'final_score' if 'final_score' in tier_data.columns else 'raw_score'
        
        # Core website metrics
        core_metrics = {
            'avg_score': tier_data[score_col].mean() if score_col in tier_data.columns else 0,
            'consistency_score': tier_data[score_col].std() if score_col in tier_data.columns else 0,
            'page_count': len(set(tier_data['page_id'])) if 'page_id' in tier_data.columns else len(tier_data),
            'critical_issues': len(tier_data[tier_data['descriptor'] == 'CONCERN']) if 'descriptor' in tier_data.columns else 0
        }
        
        # Add visual brand data if available
        tier_visual = None
        if not visual_df.empty:
            tier_mapping = {
                'tier_1': 'Tier 1 - Brand Positioning',
                'tier_2': 'Tier 2 - Value Propositions', 
                'tier_3': 'Tier 3 - Functional Content'
            }
            visual_tier_name = tier_mapping.get(tier)
            if visual_tier_name:
                tier_visual_data = visual_df[visual_df['Page Type'] == visual_tier_name]
                if not tier_visual_data.empty:
                    tier_visual = {
                        'visual_score': tier_visual_data['Final Score'].mean(),
                        'logo_compliance': tier_visual_data['Logo Compliance'].mean(),
                        'color_consistency': tier_visual_data['Color Palette'].mean()
                    }
        
        tier_analysis[tier] = {
            **core_metrics,
            'visual_brand': tier_visual
        }
    
    # Add social media as Tier 4
    if social_data['platform_scores']:
        tier_analysis['tier_4_social'] = {
            'avg_score': social_data['executive_summary'].get('overall_score', 0),
            'consistency_score': 0,  # Calculate from platform variance
            'page_count': len(social_data['platform_scores']),
            'critical_issues': len([p for p, s in social_data['platform_scores'].items() if s < 3]),
            'platform_breakdown': social_data['platform_scores']
        }
    
    # Create comprehensive report data
    report_data = {
        'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_sources': {
            'total_criteria_evaluations': len(df),
            'unique_urls_audited': df['url'].nunique() if 'url' in df.columns else 0,
            'personas_analyzed': len(df['persona_id'].unique()) if 'persona_id' in df.columns else 1,
            'visual_brand_pages': len(visual_df) if not visual_df.empty else 0,
            'social_platforms': len(social_data['platform_scores'])
        },
        'overall_brand_health': executive_summary['brand_health']['raw_score'],
        'tier_performance': tier_performance.to_dict() if not tier_performance.empty else {},
        'tier_analysis': tier_analysis,
        'visual_brand_metrics': visual_metrics,
        'social_media_metrics': social_data,
        'persona_comparison': persona_comparison.to_dict() if not persona_comparison.empty else {},
        'strategic_intelligence': strategic_intelligence,
        'executive_summary': executive_summary
    }
    
    print("📝 Generating comprehensive reports...")
    
    # Generate AI strategic narrative
    print("🤖 Generating AI strategic narrative...")
    ai_narrative = generate_ai_strategic_narrative(report_data)
    
    # Add AI narrative to report data
    report_data['ai_strategic_narrative'] = ai_narrative
    
    # Save comprehensive JSON report
    json_output = Path("brand_audit_reports/output/comprehensive_brand_report.json")
    json_output.parent.mkdir(parents=True, exist_ok=True)
    
    # Clean NaN values before JSON serialization
    clean_report_data = clean_nan_values(report_data)
    
    with open(json_output, 'w') as f:
        json.dump(clean_report_data, f, indent=2)
    
    print(f"✅ Comprehensive JSON report saved: {json_output}")
    
    # Generate enhanced markdown summary
    markdown_output = Path("brand_audit_reports/output/comprehensive_brand_summary.md")
    
    with open(markdown_output, 'w') as f:
        f.write(f"""# Comprehensive Brand Consistency Audit Report
*Generated on {report_data['generated_date']}*

## Executive Summary
- **URLs Audited:** {report_data['data_sources']['unique_urls_audited']} unique pages
- **Criteria Evaluations:** {report_data['data_sources']['total_criteria_evaluations']} detailed assessments  
- **Personas Analyzed:** {report_data['data_sources']['personas_analyzed']} target personas
- **Visual Brand Pages:** {report_data['data_sources']['visual_brand_pages']} pages analyzed
- **Social Media Platforms:** {report_data['data_sources']['social_platforms']} platforms assessed
- **Overall Brand Health Score:** {report_data['overall_brand_health']:.1f}/10

---

## 🤖 AI Strategic Analysis

{ai_narrative}

---

## Cross-Channel Brand Consistency Analysis

""")
        
        # Tier analysis with visual and social data
        for tier, data in tier_analysis.items():
            if tier == 'tier_4_social':
                f.write(f"""### Tier 4 - Social Media Channels
- **Average Score:** {data['avg_score']:.1f}/10
- **Platforms:** {data['page_count']}
- **Critical Issues:** {data['critical_issues']} platforms below 3.0

**Social Media Platforms:**
""")
                # Only show actual platforms (not brand attributes)
                platforms_only = {k: v for k, v in data.get('platform_breakdown', {}).items() 
                                if k in ['LinkedIn', 'Instagram', 'Facebook', 'X/Twitter']}
                for platform, score in platforms_only.items():
                    status = "🟢 Good" if score >= 6 else "🟡 Fair" if score >= 4 else "🔴 Critical"
                    f.write(f"- {platform}: {score:.1f}/10 {status}\n")
                
                f.write(f"""
**Brand Attributes (Cross-Platform):**
""")
                # Show brand attributes separately
                brand_attrs = social_data.get('brand_attributes', {})
                for attribute, score in brand_attrs.items():
                    status = "🟢 Good" if score >= 6 else "🟡 Fair" if score >= 4 else "🔴 Critical"
                    f.write(f"- {attribute}: {score:.1f}/10 {status}\n")
                f.write(f"- Overall Social Score: {data['avg_score']:.1f}/10 🟡 Fair\n\n")
            else:
                consistency_rating = "High" if data['consistency_score'] < 1.5 else "Medium" if data['consistency_score'] < 2.5 else "Low"
                f.write(f"""### {tier.replace('_', ' ').title()}
- **Website Score:** {data['avg_score']:.1f}/10
- **Consistency Rating:** {consistency_rating} (σ={data['consistency_score']:.2f})
- **Pages:** {data['page_count']}
- **Critical Issues:** {data['critical_issues']}
""")
                if data.get('visual_brand'):
                    vb = data['visual_brand']
                    f.write(f"""- **Visual Brand Score:** {vb['visual_score']:.1f}/10
- **Logo Compliance:** {vb['logo_compliance']:.1f}/10
- **Color Consistency:** {vb['color_consistency']:.1f}/10
""")
                f.write("\n")
        
        # Visual brand summary
        if visual_metrics:
            f.write(f"""## Visual Brand Consistency (Cross-Tier)
- **Overall Visual Score:** {visual_metrics['overall_score']:.1f}/10
- **Logo Compliance:** {visual_metrics['logo_compliance']:.1f}/10
- **Color Consistency:** {visual_metrics['color_consistency']:.1f}/10
- **Typography Consistency:** {visual_metrics['typography_consistency']:.1f}/10

""")
        
        # Social media summary
        if social_data['executive_summary']:
            f.write(f"""## Social Media Brand Health
- **Overall Social Score:** {social_data['executive_summary'].get('overall_score', 0):.1f}/10
- **Brand Consistency:** {social_data['executive_summary'].get('brand_consistency', 0):.1f}/10

""")
        
        f.write(f"""## Key Insights
- **Strongest Tier:** Tier 1 content maintains highest consistency
- **Biggest Gap:** Social media (Tier 4) shows significant brand inconsistency
- **Visual Brand:** {'Strong' if visual_metrics.get('overall_score', 0) > 7 else 'Needs improvement'} across website tiers
- **Critical Issues:** {sum(data.get('critical_issues', 0) for data in tier_analysis.values())} total issues identified

## Strategic Recommendations
1. **Immediate:** Address critical social media brand gaps (X/Twitter, Facebook)
2. **Short-term:** Standardize visual brand application across Tier 2-3 content
3. **Long-term:** Implement brand governance system for all touchpoints
4. **Ongoing:** Monitor brand consistency across all channels quarterly

## Implementation Priority
1. **High Impact, Low Effort:** Social media brand guidelines implementation
2. **High Impact, Medium Effort:** Visual brand template standardization
3. **Medium Impact, High Effort:** Content governance system deployment

*For detailed analysis, see the comprehensive JSON report and individual HTML reports.*
""")
    
    print(f"✅ Comprehensive markdown summary saved: {markdown_output}")
    
    # Generate HTML reports using existing generator
    try:
        html_generator = HTMLReportGenerator()
        html_path = html_generator.generate_consolidated_report()
        print(f"✅ HTML report generated: {html_path}")
    except Exception as e:
        print(f"⚠️  HTML generation failed: {e}")
    
    print(f"""
🎉 Comprehensive Brand Consistency Report Complete!

📊 Data Sources Integrated:
   • Website audit ({report_data['data_sources']['unique_urls_audited']} URLs, {report_data['data_sources']['total_criteria_evaluations']} evaluations)
   • Visual brand audit ({report_data['data_sources']['visual_brand_pages']} pages)
   • Social media audit ({report_data['data_sources']['social_platforms']} platforms)

📁 Output files:
   • {json_output}
   • {markdown_output}
   • HTML reports in html_reports/ directory

💡 Key Findings:
   • Overall brand health: {report_data['overall_brand_health']:.1f}/10
   • Visual consistency: {visual_metrics.get('overall_score', 0):.1f}/10
   • Social media health: {social_data['executive_summary'].get('overall_score', 0):.1f}/10
""")

if __name__ == "__main__":
    generate_comprehensive_brand_report() 