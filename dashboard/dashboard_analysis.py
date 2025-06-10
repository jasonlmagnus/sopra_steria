#!/usr/bin/env python3
"""
Sopra Steria Website Audit Dashboard Analysis
Processes otto_audit.csv and creates visualizations for executive dashboard
"""

import csv
import re
import json
from collections import defaultdict, Counter

def extract_scores_from_text(text):
    """Extract numerical scores from evaluation text"""
    if not text or text.strip() == '':
        return {}
    
    scores = {}
    
    # Look for "Overall Score: X/5" or "Overall Score: X.X/5"
    overall_patterns = [
        r'Overall Score:?\s*(\d+\.?\d*)/5',
        r'Overall Score:?\s*(\d+\.?\d*)\s*/\s*5',
        r'overall_score["\']:\s*(\d+\.?\d*)'
    ]
    
    for pattern in overall_patterns:
        overall_match = re.search(pattern, text, re.IGNORECASE)
        if overall_match:
            scores['overall'] = float(overall_match.group(1))
            break
    
    # Look for individual category scores with more flexible patterns
    category_patterns = [
        # Pattern: "Category Name (X/5):" or "Category Name (/5): X/5"
        (r'Headline\s+Effectiveness[^:]*(?:\((\d+\.?\d*)/5\)|:\s*(\d+\.?\d*)/5)', 'headline'),
        (r'Content\s+Relevance[^:]*(?:\((\d+\.?\d*)/5\)|:\s*(\d+\.?\d*)/5)', 'content'),
        (r'Pain\s+Point\s+Recognition[^:]*(?:\((\d+\.?\d*)/5\)|:\s*(\d+\.?\d*)/5)', 'pain_points'),
        (r'Value\s+Proposition\s+Clarity[^:]*(?:\((\d+\.?\d*)/5\)|:\s*(\d+\.?\d*)/5)', 'value_prop'),
        (r'Trust\s+Signals[^:]*(?:\((\d+\.?\d*)/5\)|:\s*(\d+\.?\d*)/5)', 'trust'),
        (r'CTA\s+Appropriateness[^:]*(?:\((\d+\.?\d*)/5\)|:\s*(\d+\.?\d*)/5)', 'cta'),
        
        # Alternative patterns for different formats
        (r'headline_effectiveness["\']:\s*{\s*["\']score["\']:\s*(\d+\.?\d*)', 'headline'),
        (r'content_relevance["\']:\s*{\s*["\']score["\']:\s*(\d+\.?\d*)', 'content'),
        (r'pain_point_recognition["\']:\s*{\s*["\']score["\']:\s*(\d+\.?\d*)', 'pain_points'),
        (r'value_proposition_clarity["\']:\s*{\s*["\']score["\']:\s*(\d+\.?\d*)', 'value_prop'),
        (r'trust_signals["\']:\s*{\s*["\']score["\']:\s*(\d+\.?\d*)', 'trust'),
        (r'cta_appropriateness["\']:\s*{\s*["\']score["\']:\s*(\d+\.?\d*)', 'cta')
    ]
    
    for pattern, key in category_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            # Check which group captured the score
            score_value = None
            for group in match.groups():
                if group is not None:
                    score_value = group
                    break
            
            if score_value:
                try:
                    scores[key] = float(score_value)
                except ValueError:
                    continue
    
    # If we didn't find an overall score but found individual scores, calculate average
    if 'overall' not in scores and len(scores) > 0:
        scores['overall'] = sum(scores.values()) / len(scores)
    
    return scores

def process_audit_data(filename):
    """Process the audit CSV and extract structured data"""
    data = []
    
    with open(filename, 'r', encoding='utf-8-sig') as file:  # utf-8-sig handles BOM
        reader = csv.DictReader(file)
        
        for row in reader:
            # Extract scores for each persona
            personas = [
                'IT Executive (Public Sector) Evaluation',
                'Financial Services Leader Evaluation', 
                'Chief Data Officer Evaluation',
                'Operations Transformation Executive Evaluation',
                'Cross-Sector IT Director Evaluation'
            ]
            
            for persona in personas:
                if row[persona]:
                    scores = extract_scores_from_text(row[persona])
                    if scores:  # Only include rows with actual scores
                        data.append({
                            'category': row['Category'],
                            'url': row['Company URL'],
                            'region': row['Region'],
                            'persona': persona.replace(' Evaluation', ''),
                            'evaluation_text': row[persona],
                            **scores
                        })
    
    return data

def create_summary_stats(data):
    """Create summary statistics for the dashboard"""
    stats = {
        'total_evaluations': len(data),
        'unique_urls': len(set(item['url'] for item in data)),
        'unique_categories': len(set(item['category'] for item in data)),
        'personas': list(set(item['persona'] for item in data))
    }
    
    # Overall score statistics
    overall_scores = [item['overall'] for item in data if 'overall' in item]
    if overall_scores:
        stats['avg_overall_score'] = sum(overall_scores) / len(overall_scores)
        stats['min_score'] = min(overall_scores)
        stats['max_score'] = max(overall_scores)
    
    # Persona performance
    persona_scores = defaultdict(list)
    for item in data:
        if 'overall' in item:
            persona_scores[item['persona']].append(item['overall'])
    
    stats['persona_averages'] = {
        persona: sum(scores) / len(scores) 
        for persona, scores in persona_scores.items()
    }
    
    # Category performance
    category_scores = defaultdict(list)
    for item in data:
        if 'overall' in item:
            category_scores[item['category']].append(item['overall'])
    
    stats['category_averages'] = {
        category: sum(scores) / len(scores)
        for category, scores in category_scores.items()
    }
    
    return stats

def generate_dashboard_data(filename):
    """Generate all data needed for dashboard"""
    print("Processing audit data...")
    data = process_audit_data(filename)
    
    print("Creating summary statistics...")
    stats = create_summary_stats(data)
    
    print("Generating insights...")
    insights = generate_insights(data, stats)
    
    return {
        'raw_data': data,
        'summary_stats': stats,
        'insights': insights
    }

def generate_insights(data, stats):
    """Generate key insights for executive summary"""
    insights = []
    
    # Best and worst performing personas
    persona_avgs = stats['persona_averages']
    best_persona = max(persona_avgs.items(), key=lambda x: x[1])
    worst_persona = min(persona_avgs.items(), key=lambda x: x[1])
    
    insights.append({
        'type': 'persona_performance',
        'title': 'Persona Performance Gap',
        'description': f"{best_persona[0]} performs best (avg: {best_persona[1]:.2f}/5) while {worst_persona[0]} needs attention (avg: {worst_persona[1]:.2f}/5)",
        'priority': 'high' if best_persona[1] - worst_persona[1] > 1.0 else 'medium'
    })
    
    # Category insights
    category_avgs = stats['category_averages']
    best_category = max(category_avgs.items(), key=lambda x: x[1])
    worst_category = min(category_avgs.items(), key=lambda x: x[1])
    
    insights.append({
        'type': 'category_performance',
        'title': 'Content Category Gaps',
        'description': f"{best_category[0]} content performs well (avg: {best_category[1]:.2f}/5) but {worst_category[0]} needs improvement (avg: {worst_category[1]:.2f}/5)",
        'priority': 'high' if best_category[1] - worst_category[1] > 1.5 else 'medium'
    })
    
    # Overall performance insight
    avg_score = stats.get('avg_overall_score', 0)
    if avg_score < 2.0:
        insights.append({
            'type': 'overall_performance',
            'title': 'Critical Performance Issues',
            'description': f"Overall average score of {avg_score:.2f}/5 indicates significant optimization opportunities across all personas",
            'priority': 'critical'
        })
    elif avg_score < 3.0:
        insights.append({
            'type': 'overall_performance', 
            'title': 'Moderate Performance',
            'description': f"Overall average score of {avg_score:.2f}/5 shows room for improvement with targeted optimizations",
            'priority': 'medium'
        })
    
    return insights

def create_dashboard_report(dashboard_data, output_file='dashboard_report.md'):
    """Create a markdown report for the dashboard"""
    data = dashboard_data['raw_data']
    stats = dashboard_data['summary_stats']
    insights = dashboard_data['insights']
    
    report = f"""# Sopra Steria Website Audit Dashboard Report

## Executive Summary

### Key Metrics
- **Total Evaluations:** {stats['total_evaluations']}
- **URLs Analyzed:** {stats['unique_urls']}
- **Content Categories:** {stats['unique_categories']}
- **Average Overall Score:** {stats.get('avg_overall_score', 'N/A'):.2f}/5
- **Score Range:** {stats.get('min_score', 'N/A'):.1f} - {stats.get('max_score', 'N/A'):.1f}

### Critical Insights
"""
    
    for insight in insights:
        priority_emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '📊', 'low': 'ℹ️'}
        report += f"\n{priority_emoji.get(insight['priority'], '📊')} **{insight['title']}**\n"
        report += f"{insight['description']}\n"
    
    report += f"""
## Persona Performance Analysis

### Average Scores by Persona
"""
    
    for persona, avg_score in sorted(stats['persona_averages'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{persona}:** {avg_score:.2f}/5\n"
    
    report += f"""
## Content Category Performance

### Average Scores by Category
"""
    
    for category, avg_score in sorted(stats['category_averages'].items(), key=lambda x: x[1], reverse=True):
        report += f"- **{category}:** {avg_score:.2f}/5\n"
    
    report += f"""
## Recommendations

### Immediate Actions (Quick Wins)
1. **Focus on {min(stats['persona_averages'].items(), key=lambda x: x[1])[0]}** - Lowest performing persona needs targeted content optimization
2. **Improve {min(stats['category_averages'].items(), key=lambda x: x[1])[0]}** - Category with biggest improvement opportunity
3. **Standardize high-performing elements** from {max(stats['category_averages'].items(), key=lambda x: x[1])[0]} across other categories

### Strategic Initiatives
1. **Persona-Specific Content Strategy** - Develop tailored messaging for each persona
2. **BENELUX Localization** - Add region-specific case studies and regulatory content
3. **Trust Signal Enhancement** - Strengthen credibility indicators across all content

### Dashboard Implementation
1. **Power BI Dashboard** - For executive reporting and monitoring
2. **Monthly Score Tracking** - Implement regular audit cycles
3. **A/B Testing Framework** - Test optimizations and measure impact

---
*Report generated from {stats['total_evaluations']} evaluations across {len(stats['personas'])} personas*
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Dashboard report saved to {output_file}")
    return report

# Main execution
if __name__ == "__main__":
    # Check if pandas is available, if not use basic processing
    try:
        import pandas as pd
        pd_available = True
    except ImportError:
        pd_available = False
        print("Note: pandas not available, using basic processing")
    
    # Process the data
    dashboard_data = generate_dashboard_data('otto_audit.csv')
    
    # Create the report
    report = create_dashboard_report(dashboard_data)
    
    # Save processed data as JSON for dashboard tools
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(dashboard_data, f, indent=2, ensure_ascii=False)
    
    print("\nDashboard data processing complete!")
    print("Files created:")
    print("- dashboard_report.md (Executive summary)")
    print("- dashboard_data.json (Structured data for dashboard tools)")
    print("\nNext steps:")
    print("1. Import dashboard_data.json into Power BI or Tableau")
    print("2. Use dashboard_report.md for executive presentation")
    print("3. Consider implementing real-time dashboard with Streamlit/Dash") 