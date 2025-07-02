#!/usr/bin/env python3
"""
HTML Report Generator for Brand Experience Reports
Generates comprehensive HTML reports from audit data
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

logger = logging.getLogger(__name__)


class HTMLReportGenerator:
    """Generates comprehensive HTML brand experience reports."""
    
    def __init__(self, template_dir="audit_tool/templates"):
        """
        Initialize the HTML report generator.
        
        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_unified_data(self, persona_name=None):
        """Load unified audit data from CSV file"""
        try:
            # Load the unified CSV
            df = pd.read_csv('audit_data/unified_audit_data.csv')
            
            # Filter by persona if specified
            if persona_name:
                df = df[df['persona_id'] == persona_name]
            
            self.logger.info(f"Loaded unified data: {len(df)} records for persona: {persona_name}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading unified data: {e}")
            raise
    
    def generate_executive_summary(self, df):
        """Generate executive summary from unified data"""
        # Calculate key metrics
        total_pages = df['page_id'].nunique()
        avg_score = df['final_score'].mean()
        
        # Count issues by severity
        critical_issues = len(df[df['descriptor'] == 'CRITICAL'])
        concerns = len(df[df['descriptor'] == 'CONCERN'])
        warnings = len(df[df['descriptor'] == 'WARN'])
        good_scores = len(df[df['descriptor'] == 'GOOD'])
        excellent_scores = len(df[df['descriptor'] == 'EXCELLENT'])
        
        # Get tier breakdown
        tier_scores = df.groupby('tier_name')['final_score'].mean().round(1).to_dict()
        
        return {
            'total_pages_audited': total_pages,
            'overall_score': round(avg_score, 1),
            'total_criteria_assessed': len(df),
            'critical_issues': critical_issues,
            'concerns': concerns,
            'warnings': warnings,
            'good_scores': good_scores,
            'excellent_scores': excellent_scores,
            'tier_breakdown': tier_scores
        }
    
    def get_tier_analysis(self, df):
        """Generate tier-based analysis from unified data"""
        tier_analysis = {}
        
        for tier_name in df['tier_name'].unique():
            tier_data = df[df['tier_name'] == tier_name]
            
            # Get evidence examples (both positive and negative)
            evidence_examples = tier_data['evidence'].dropna().head(5).tolist()
            
            # Get top issues for this tier
            tier_issues = tier_data[tier_data['descriptor'].isin(['CRITICAL', 'CONCERN'])]
            top_issues = tier_issues['criterion_id'].head(3).tolist()
            
            # Get effective/ineffective copy examples
            effective_copy = tier_data['effective_copy_examples'].dropna().head(3).tolist()
            ineffective_copy = tier_data['ineffective_copy_examples'].dropna().head(3).tolist()
            
            tier_analysis[tier_name] = {
                'page_count': tier_data['page_id'].nunique(),
                'criteria_count': len(tier_data),
                'avg_score': round(tier_data['final_score'].mean(), 1),
                'tier_weight': tier_data['tier_weight'].iloc[0] if len(tier_data) > 0 else 0,
                'brand_percentage': tier_data['brand_percentage'].iloc[0] if len(tier_data) > 0 else 0,
                'performance_percentage': tier_data['performance_percentage'].iloc[0] if len(tier_data) > 0 else 0,
                'evidence_examples': evidence_examples,
                'top_issues': top_issues,
                'effective_copy': effective_copy,
                'ineffective_copy': ineffective_copy,
                'sentiment_distribution': tier_data['overall_sentiment'].value_counts().to_dict(),
                'engagement_distribution': tier_data['engagement_level'].value_counts().to_dict()
            }
        
        return tier_analysis
    
    def get_persona_voice_insights(self, df):
        """Extract persona voice insights from unified data"""
        # Get sentiment and engagement distributions
        sentiment_dist = df['overall_sentiment'].value_counts().to_dict()
        engagement_dist = df['engagement_level'].value_counts().to_dict()
        conversion_dist = df['conversion_likelihood'].value_counts().to_dict()
        
        # Get copy examples
        effective_examples = df['effective_copy_examples'].dropna().head(5).tolist()
        ineffective_examples = df['ineffective_copy_examples'].dropna().head(5).tolist()
        
        # Calculate average numeric scores
        avg_sentiment = df['sentiment_numeric'].mean() if 'sentiment_numeric' in df.columns else 0
        avg_engagement = df['engagement_numeric'].mean() if 'engagement_numeric' in df.columns else 0
        avg_conversion = df['conversion_numeric'].mean() if 'conversion_numeric' in df.columns else 0
        
        return {
            'sentiment_distribution': sentiment_dist,
            'engagement_distribution': engagement_dist,
            'conversion_distribution': conversion_dist,
            'effective_copy_examples': effective_examples,
            'ineffective_copy_examples': ineffective_examples,
            'avg_sentiment_score': round(avg_sentiment, 1),
            'avg_engagement_score': round(avg_engagement, 1),
            'avg_conversion_score': round(avg_conversion, 1),
            'total_pages_analyzed': df['page_id'].nunique()
        }
    
    def get_strategic_recommendations(self, df):
        """Generate strategic recommendations based on audit findings"""
        recommendations = {
            'high_impact': [],
            'quick_wins': []
        }
        
        # Identify high-impact issues (critical and concerns with high tier weights)
        high_impact_issues = df[
            (df['descriptor'].isin(['CRITICAL', 'CONCERN'])) & 
            (df['tier_weight'] >= 0.4)
        ].groupby('criterion_id').agg({
            'final_score': 'mean',
            'evidence': 'first',
            'tier_weight': 'first'
        }).sort_values('final_score').head(5)
        
        for criterion_id, row in high_impact_issues.iterrows():
            recommendations['high_impact'].append({
                'title': f"Address {criterion_id.replace('_', ' ').title()}",
                'description': row['evidence'][:200] + "..." if len(row['evidence']) > 200 else row['evidence'],
                'impact_score': round((10 - row['final_score']) * row['tier_weight'], 1),
                'complexity': 'High' if row['tier_weight'] > 0.5 else 'Medium'
            })
        
        # Identify quick wins (issues with low scores but lower complexity)
        quick_win_issues = df[
            (df['descriptor'].isin(['WARN', 'CONCERN'])) & 
            (df['tier_weight'] <= 0.3) &
            (df['final_score'] < 7)
        ].groupby('criterion_id').agg({
            'final_score': 'mean',
            'evidence': 'first',
            'tier_weight': 'first'
        }).sort_values('final_score').head(5)
        
        for criterion_id, row in quick_win_issues.iterrows():
            recommendations['quick_wins'].append({
                'title': f"Quick Fix: {criterion_id.replace('_', ' ').title()}",
                'description': row['evidence'][:200] + "..." if len(row['evidence']) > 200 else row['evidence'],
                'impact_score': round((10 - row['final_score']) * row['tier_weight'], 1),
                'complexity': 'Low'
            })
        
        return recommendations
    
    def get_visual_brand_assessment(self, df):
        """Generate visual brand assessment from criteria scores"""
        # Brand-related criteria
        brand_criteria = df[df['criterion_id'].str.contains('brand|visual|positioning|consistency', case=False, na=False)]
        
        if len(brand_criteria) == 0:
            # Fallback to all criteria if no brand-specific ones found
            brand_criteria = df
        
        brand_score = brand_criteria['final_score'].mean()
        compliance_rate = len(brand_criteria[brand_criteria['final_score'] >= 7]) / len(brand_criteria) * 100
        
        return {
            'overall_brand_score': round(brand_score, 1),
            'compliance_rate': round(compliance_rate, 1),
            'total_criteria_assessed': len(brand_criteria),
            'areas_of_concern': brand_criteria[brand_criteria['final_score'] < 6]['criterion_id'].head(5).tolist(),
            'top_performing_areas': brand_criteria[brand_criteria['final_score'] >= 8]['criterion_id'].head(5).tolist()
        }
    
    def generate_report(self, persona_name, output_path=None):
        """Generate HTML report for a persona using unified data"""
        try:
            # Load unified data
            df = self.load_unified_data(persona_name)
            
            if len(df) == 0:
                raise ValueError(f"No data found for persona: {persona_name}")
            
            # Generate all sections with real data
            executive_summary_data = self.generate_executive_summary(df)
            tier_analysis = self.get_tier_analysis(df)
            persona_voice = self.get_persona_voice_insights(df)
            recommendations = self.get_strategic_recommendations(df)
            visual_brand = self.get_visual_brand_assessment(df)
            
            # Get some sample URLs for context
            sample_urls = df[['url', 'final_score']].drop_duplicates().head(5).to_dict('records')
            
            # Format executive summary properly for template
            executive_summary_text = f"""
            This comprehensive brand audit analyzed {executive_summary_data['total_pages_audited']} pages 
            across {len(tier_analysis)} content tiers, evaluating {executive_summary_data['total_criteria_assessed']} 
            criteria. The overall brand experience score is {executive_summary_data['overall_score']}/10, 
            with {executive_summary_data['critical_issues']} critical issues, {executive_summary_data['concerns']} concerns, 
            and {executive_summary_data['warnings']} warnings identified.
            """
            
            # Format summary stats for template
            summary_stats = [
                {"value": f"{executive_summary_data['total_pages_audited']}", "label": "Pages Analyzed"},
                {"value": f"{executive_summary_data['overall_score']}/10", "label": "Overall Score"},
                {"value": f"{executive_summary_data['critical_issues']}", "label": "Critical Issues"},
                {"value": f"{executive_summary_data['concerns'] + executive_summary_data['warnings']}", "label": "Areas for Improvement"}
            ]
            
            # Format tiers for template
            formatted_tiers = []
            for tier_name, tier_data in tier_analysis.items():
                working_evidence = []
                not_working_evidence = []
                
                # Split evidence into working/not working based on effective/ineffective copy
                for i, evidence in enumerate(tier_data['evidence_examples'][:3]):
                    if i < len(tier_data['effective_copy'][:2]):
                        working_evidence.append({
                            "title": f"Effective Element {i+1}",
                            "description": evidence[:200] + "..." if len(evidence) > 200 else evidence
                        })
                    else:
                        not_working_evidence.append({
                            "title": f"Improvement Area {i+1}",
                            "description": evidence[:200] + "..." if len(evidence) > 200 else evidence
                        })
                
                # Ensure we have at least one item in each category
                if not working_evidence:
                    working_evidence.append({
                        "title": "Brand Alignment",
                        "description": f"Pages in this tier maintain basic brand consistency with an average score of {tier_data['avg_score']}/10"
                    })
                
                if not not_working_evidence:
                    not_working_evidence.append({
                        "title": "Optimization Opportunity",
                        "description": f"Further optimization can improve the current {tier_data['avg_score']}/10 score in this tier"
                    })
                
                formatted_tiers.append({
                    "number": len(formatted_tiers) + 1,
                    "title": tier_name,
                    "subtitle": f"Analysis of {tier_data['page_count']} pages with {tier_data['criteria_count']} criteria evaluated",
                    "analysis_title": f"{tier_name} Performance Analysis",
                    "score": tier_data['avg_score'],
                    "brand_weight": int(tier_data['brand_percentage']),
                    "performance_weight": int(tier_data['performance_percentage']),
                    "working_evidence": working_evidence,
                    "not_working_evidence": not_working_evidence,
                    "persona_voices": []  # Can be populated if needed
                })
            
            # Format brand metrics for template
            brand_metrics = {
                "title": "Brand Health Metrics",
                "subtitle": f"Key performance indicators for {persona_name}",
                "metrics": [
                    {
                        "value": f"{visual_brand['overall_brand_score']}/10",
                        "label": "Brand Consistency",
                        "description": "Overall brand alignment across all touchpoints"
                    },
                    {
                        "value": f"{visual_brand['compliance_rate']:.1f}%",
                        "label": "Compliance Rate",
                        "description": "Percentage of criteria meeting brand standards"
                    },
                    {
                        "value": f"{persona_voice['avg_sentiment_score']}/10",
                        "label": "Sentiment Score",
                        "description": "Average sentiment rating across content"
                    },
                    {
                        "value": f"{persona_voice['avg_engagement_score']}/10",
                        "label": "Engagement Score",
                        "description": "Predicted engagement level for this persona"
                    }
                ]
            }
            
            # Format recommendations for template
            formatted_recommendations = {
                "subtitle": f"Prioritized action plan for {persona_name}",
                "sections": [
                    {
                        "title": "🔴 High Impact Improvements",
                        "color": "#dc3545",
                        "cards": [
                            {
                                "title": rec['title'],
                                "actions": [
                                    rec['description'],
                                    f"Impact Score: {rec['impact_score']}/10",
                                    f"Complexity: {rec['complexity']}"
                                ]
                            } for rec in recommendations['high_impact'][:3]
                        ]
                    },
                    {
                        "title": "⚡ Quick Wins",
                        "color": "#28a745", 
                        "cards": [
                            {
                                "title": rec['title'],
                                "actions": [
                                    rec['description'],
                                    f"Impact Score: {rec['impact_score']}/10",
                                    f"Complexity: {rec['complexity']}"
                                ]
                            } for rec in recommendations['quick_wins'][:3]
                        ]
                    }
                ]
            }
            
            # Prepare template context with properly formatted data
            context = {
                'company_name': 'Sopra Steria',
                'report_subtitle': f'Persona-specific brand experience analysis for {persona_name}',
                'persona_name': persona_name,
                'generated_date': datetime.now().strftime('%B %d, %Y'),
                'executive_summary': executive_summary_text.strip(),
                'summary_stats': summary_stats,
                'tiers': formatted_tiers,
                'brand_metrics': brand_metrics,
                'recommendations': formatted_recommendations,
                'footer_description': f'Generated on {datetime.now().strftime("%B %d, %Y")} using unified audit data',
                'footer_methodology': 'Based on multi-criteria brand experience assessment methodology',
                'audit_timestamp': df['audited_ts'].iloc[0] if 'audited_ts' in df.columns and len(df) > 0 else datetime.now()
            }
            
            # Load and render template
            template = self.env.get_template('brand_experience_report.html')
            html_content = template.render(context)
            
            # Determine output path
            if output_path is None:
                safe_persona_name = persona_name.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
                output_dir = f'html_reports/{safe_persona_name}'
                os.makedirs(output_dir, exist_ok=True)
                output_path = f'{output_dir}/brand_experience_report.html'
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise

    def generate_consolidated_report(self, output_path=None):
        """Generate a single consolidated HTML report for all personas"""
        try:
            # Load unified data for all personas
            df = self.load_unified_data()  # No persona filter = all data
            
            if len(df) == 0:
                raise ValueError("No data found for consolidated report")
            
            # Get all personas
            all_personas = sorted(df['persona_id'].unique())
            
            # Generate consolidated sections
            consolidated_data = {
                'total_personas': len(all_personas),
                'personas': all_personas,
                'generated_date': datetime.now().strftime('%B %d, %Y'),
                'audit_timestamp': df['audited_ts'].iloc[0] if 'audited_ts' in df.columns and len(df) > 0 else datetime.now()
            }
            
            # Overall executive summary across all personas
            consolidated_data['executive_summary'] = self.generate_consolidated_executive_summary(df)
            
            # Persona comparison analysis
            consolidated_data['persona_comparison'] = self.generate_persona_comparison(df, all_personas)
            
            # Cross-persona tier analysis
            consolidated_data['cross_tier_analysis'] = self.generate_cross_tier_analysis(df)
            
            # Consolidated recommendations
            consolidated_data['consolidated_recommendations'] = self.generate_consolidated_recommendations(df)
            
            # Overall brand health
            consolidated_data['overall_brand_health'] = self.generate_overall_brand_health(df)
            
            # Sample URLs across all personas
            consolidated_data['sample_urls'] = df[['url', 'final_score', 'persona_id']].drop_duplicates().head(10).to_dict('records')
            
            # Load and render consolidated template
            template = self.env.get_template('consolidated_brand_report.html')
            html_content = template.render(consolidated_data)
            
            # Determine output path
            if output_path is None:
                output_path = 'audit_outputs/Consolidated_Brand_Report/consolidated_brand_experience_report.html'
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Consolidated HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating consolidated report: {e}")
            raise
    
    def generate_consolidated_executive_summary(self, df):
        """Generate executive summary across all personas"""
        total_personas = df['persona_id'].nunique()
        total_pages = df['page_id'].nunique()
        total_criteria = len(df)
        avg_score = df['final_score'].mean()
        
        # Issues across all personas
        critical_issues = len(df[df['descriptor'] == 'CRITICAL'])
        concerns = len(df[df['descriptor'] == 'CONCERN'])
        warnings = len(df[df['descriptor'] == 'WARN'])
        good_scores = len(df[df['descriptor'] == 'GOOD'])
        excellent_scores = len(df[df['descriptor'] == 'EXCELLENT'])
        
        # Tier performance across all personas
        tier_performance = df.groupby('tier_name')['final_score'].mean().round(1).to_dict()
        
        return {
            'total_personas': total_personas,
            'total_pages': total_pages,
            'total_criteria': total_criteria,
            'overall_score': round(avg_score, 1),
            'critical_issues': critical_issues,
            'concerns': concerns,
            'warnings': warnings,
            'good_scores': good_scores,
            'excellent_scores': excellent_scores,
            'tier_performance': tier_performance
        }
    
    def generate_persona_comparison(self, df, all_personas):
        """Generate comparison analysis between personas"""
        persona_comparison = {}
        
        for persona in all_personas:
            persona_data = df[df['persona_id'] == persona]
            
            persona_comparison[persona] = {
                'total_records': len(persona_data),
                'unique_pages': persona_data['page_id'].nunique(),
                'avg_score': round(persona_data['final_score'].mean(), 1),
                'critical_issues': len(persona_data[persona_data['descriptor'] == 'CRITICAL']),
                'concerns': len(persona_data[persona_data['descriptor'] == 'CONCERN']),
                'warnings': len(persona_data[persona_data['descriptor'] == 'WARN']),
                'sentiment_positive': len(persona_data[persona_data['overall_sentiment'] == 'Positive']),
                'sentiment_neutral': len(persona_data[persona_data['overall_sentiment'] == 'Neutral']),
                'sentiment_negative': len(persona_data[persona_data['overall_sentiment'] == 'Negative']),
                'engagement_high': len(persona_data[persona_data['engagement_level'] == 'High']),
                'engagement_medium': len(persona_data[persona_data['engagement_level'] == 'Medium']),
                'engagement_low': len(persona_data[persona_data['engagement_level'] == 'Low'])
            }
        
        return persona_comparison
    
    def generate_cross_tier_analysis(self, df):
        """Generate tier analysis across all personas"""
        cross_tier = {}
        
        for tier_name in df['tier_name'].unique():
            tier_data = df[df['tier_name'] == tier_name]
            
            cross_tier[tier_name] = {
                'total_records': len(tier_data),
                'unique_pages': tier_data['page_id'].nunique(),
                'personas_affected': tier_data['persona_id'].nunique(),
                'avg_score': round(tier_data['final_score'].mean(), 1),
                'score_range': f"{tier_data['final_score'].min():.1f} - {tier_data['final_score'].max():.1f}",
                'top_issues': tier_data[tier_data['descriptor'].isin(['CRITICAL', 'CONCERN'])]['criterion_id'].value_counts().head(3).to_dict(),
                'persona_performance': tier_data.groupby('persona_id')['final_score'].mean().round(1).to_dict()
            }
        
        return cross_tier
    
    def generate_consolidated_recommendations(self, df):
        """Generate consolidated strategic recommendations across all personas"""
        recommendations = {
            'cross_persona_issues': [],
            'tier_specific_improvements': [],
            'quick_wins': []
        }
        
        # Cross-persona issues (affecting multiple personas)
        criterion_persona_counts = df.groupby('criterion_id')['persona_id'].nunique()
        cross_persona_criteria = criterion_persona_counts[criterion_persona_counts >= 3].index
        
        for criterion in cross_persona_criteria[:5]:
            criterion_data = df[df['criterion_id'] == criterion]
            avg_score = criterion_data['final_score'].mean()
            affected_personas = criterion_data['persona_id'].nunique()
            
            recommendations['cross_persona_issues'].append({
                'title': f"Address {criterion.replace('_', ' ').title()}",
                'description': f"Affects {affected_personas} personas with average score {avg_score:.1f}/10",
                'impact_score': round((10 - avg_score) * (affected_personas / len(df['persona_id'].unique())), 1),
                'affected_personas': affected_personas
            })
        
        # Tier-specific improvements
        for tier_name in df['tier_name'].unique():
            tier_data = df[df['tier_name'] == tier_name]
            if tier_data['final_score'].mean() < 6:
                recommendations['tier_specific_improvements'].append({
                    'tier': tier_name,
                    'avg_score': round(tier_data['final_score'].mean(), 1),
                    'pages_affected': tier_data['page_id'].nunique(),
                    'priority': 'High' if tier_data['final_score'].mean() < 5 else 'Medium'
                })
        
        # Quick wins (low complexity, high impact)
        quick_win_criteria = df[
            (df['final_score'] < 7) & 
            (df['tier_weight'] <= 0.3)
        ].groupby('criterion_id')['final_score'].mean().sort_values().head(5)
        
        for criterion, score in quick_win_criteria.items():
            recommendations['quick_wins'].append({
                'title': f"Quick Fix: {criterion.replace('_', ' ').title()}",
                'current_score': round(score, 1),
                'potential_impact': round((7 - score) * 0.3, 1),
                'complexity': 'Low'
            })
        
        return recommendations
    
    def generate_overall_brand_health(self, df):
        """Generate overall brand health assessment"""
        brand_criteria = df[df['criterion_id'].str.contains('brand|visual|positioning|consistency', case=False, na=False)]
        
        if len(brand_criteria) == 0:
            brand_criteria = df
        
        overall_score = brand_criteria['final_score'].mean()
        compliance_rate = len(brand_criteria[brand_criteria['final_score'] >= 7]) / len(brand_criteria) * 100
        
        # Brand health by persona
        persona_brand_health = {}
        for persona in df['persona_id'].unique():
            persona_brand = brand_criteria[brand_criteria['persona_id'] == persona]
            if len(persona_brand) > 0:
                persona_brand_health[persona] = round(persona_brand['final_score'].mean(), 1)
        
        return {
            'overall_score': round(overall_score, 1),
            'compliance_rate': round(compliance_rate, 1),
            'total_criteria_assessed': len(brand_criteria),
            'persona_brand_health': persona_brand_health,
            'critical_brand_issues': brand_criteria[brand_criteria['final_score'] < 5]['criterion_id'].head(5).tolist(),
            'brand_strengths': brand_criteria[brand_criteria['final_score'] >= 8]['criterion_id'].head(5).tolist()
        }


if __name__ == "__main__":
    # Example usage
    generator = HTMLReportGenerator()
    print("HTML Report Generator initialized successfully") 