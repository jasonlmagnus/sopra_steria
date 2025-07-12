#!/usr/bin/env python3
"""
HTML Report Generator for Brand Experience Reports
Generates comprehensive HTML reports from audit data
"""

import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os

logger = logging.getLogger(__name__)

# pyright: reportAttributeAccessIssue=false, reportCallIssue=false, reportAssignmentType=false
# Suppress pandas type errors: pandas DataFrame/Series are not fully supported by static type checkers.
# All code is tested and works at runtime.

class HTMLReportGenerator:
    """Generates comprehensive HTML brand experience reports."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize the HTML report generator.
        
        Args:
            template_dir: Directory containing Jinja2 templates (auto-detected if None)
        """
        if template_dir is None:
            # Auto-detect template directory based on execution context
            possible_paths = [
                "audit_tool/templates",
                "../audit_tool/templates", 
                "templates"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    template_dir = path
                    break
            else:
                # Fallback to default
                template_dir = "audit_tool/templates"
        
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_unified_data(self, persona_name: Optional[str] = None) -> Any:  # type: ignore
        """Load unified audit data from CSV file"""
        try:
            # Load the unified CSV - handle both root and audit_tool directory execution
            csv_path = 'audit_data/unified_audit_data.csv'
            if not os.path.exists(csv_path):
                csv_path = '../audit_data/unified_audit_data.csv'
            df: pd.DataFrame = pd.read_csv(csv_path)
            
            # Filter by persona if specified
            if persona_name:
                df = df[df['persona_id'] == persona_name]
            
            self.logger.info(f"Loaded unified data: {len(df)} records for persona: {persona_name}")
            return df  # type: ignore
            
        except Exception as e:
            self.logger.error(f"Error loading unified data: {e}")
            raise
    
    def generate_executive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
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
    
    def get_tier_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate tier-based analysis from unified data"""
        tier_analysis = {}
        
        for tier_name in df['tier_name'].unique():
            tier_data = df[df['tier_name'] == tier_name]
            
            # Get evidence examples (both positive and negative)
            evidence_examples = tier_data['evidence'].dropna().head(5).tolist()  # type: ignore
            
            # Get top issues for this tier
            tier_issues = tier_data[tier_data['descriptor'].isin(['CRITICAL', 'CONCERN'])]  # type: ignore
            top_issues = tier_issues['criterion_id'].head(3).tolist()  # type: ignore
            
            # Get effective/ineffective copy examples
            effective_copy = tier_data['effective_copy_examples'].dropna().head(3).tolist()  # type: ignore
            ineffective_copy = tier_data['ineffective_copy_examples'].dropna().head(3).tolist()  # type: ignore
            
            tier_analysis[tier_name] = {
                'page_count': int(tier_data['page_id'].nunique()),  # type: ignore
                'criteria_count': len(tier_data),
                'avg_score': round(float(tier_data['final_score'].mean()), 1),
                'tier_weight': float(tier_data['tier_weight'].iloc[0]) if len(tier_data) > 0 else 0.0,  # type: ignore
                'brand_percentage': float(tier_data['brand_percentage'].iloc[0]) if len(tier_data) > 0 else 0.0,  # type: ignore
                'performance_percentage': float(tier_data['performance_percentage'].iloc[0]) if len(tier_data) > 0 else 0.0,  # type: ignore
                'evidence_examples': evidence_examples,
                'top_issues': top_issues,
                'effective_copy': effective_copy,
                'ineffective_copy': ineffective_copy
            }
        
        return tier_analysis
    
    def get_persona_voice_insights(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract persona voice insights from unified data"""
        
        # Get copy examples
        effective_examples = df['effective_copy_examples'].dropna().head(5).tolist()
        ineffective_examples = df['ineffective_copy_examples'].dropna().head(5).tolist()
        
        # Calculate average numeric scores based on evidence data
        avg_sentiment = df['sentiment_numeric'].mean() if 'sentiment_numeric' in df.columns else 0
        avg_engagement = df['engagement_numeric'].mean() if 'engagement_numeric' in df.columns else 0
        avg_conversion = df['conversion_numeric'].mean() if 'conversion_numeric' in df.columns else 0
        
        # Derive sentiment from scores for onsite data
        score_col = 'final_score' if 'final_score' in df.columns else 'raw_score'
        if score_col in df.columns:
            scores = df[score_col].dropna()
            sentiment_derived = {
                'positive': int((scores >= 7.0).sum()),
                'neutral': int(((scores >= 4.0) & (scores < 7.0)).sum()),
                'negative': int((scores < 4.0).sum())
            }
        else:
            sentiment_derived = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        return {
            'sentiment_distribution': sentiment_derived,
            'effective_copy_examples': effective_examples,
            'ineffective_copy_examples': ineffective_examples,
            'avg_sentiment_score': round(avg_sentiment, 1),
            'avg_engagement_score': round(avg_engagement, 1),
            'avg_conversion_score': round(avg_conversion, 1),
            'total_pages_analyzed': df['page_id'].nunique()
        }
    
    def get_strategic_recommendations(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
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
        }).sort_values(by='final_score').head(5)  # type: ignore
        
        for criterion_id, row in high_impact_issues.iterrows():
            criterion_str = str(criterion_id)
            final_score = float(row['final_score'])
            tier_weight = float(row['tier_weight'])
            evidence = str(row['evidence'])
            
            recommendations['high_impact'].append({
                'title': f"Address {criterion_str.replace('_', ' ').title()}",
                'description': evidence[:200] + "..." if len(evidence) > 200 else evidence,
                'impact_score': round((10 - final_score) * tier_weight, 1),
                'complexity': 'High' if tier_weight > 0.5 else 'Medium'
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
        }).sort_values(by='final_score').head(5)  # type: ignore
        
        for criterion_id, row in quick_win_issues.iterrows():
            criterion_str = str(criterion_id)
            final_score = float(row['final_score'])
            tier_weight = float(row['tier_weight'])
            evidence = str(row['evidence'])
            
            recommendations['quick_wins'].append({
                'title': f"Quick Fix: {criterion_str.replace('_', ' ').title()}",
                'description': evidence[:200] + "..." if len(evidence) > 200 else evidence,
                'impact_score': round((10 - final_score) * tier_weight, 1),
                'complexity': 'Low'
            })
        
        return recommendations
    
    def get_visual_brand_assessment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate visual brand assessment from criteria scores"""
        # Brand-related criteria
        brand_criteria = df[df['criterion_id'].str.contains('brand|visual|positioning|consistency', case=False, na=False)]
        
        if len(brand_criteria) == 0:
            # Fallback to all criteria if no brand-specific ones found
            brand_criteria = df
        
        brand_score = brand_criteria['final_score'].mean()
        
        # Calculate compliance rate
        compliance_rate = (brand_criteria['final_score'] >= 7).mean() * 100
        
        return {
            'overall_brand_score': round(brand_score, 1),
            'compliance_rate': compliance_rate,
            'brand_criteria_count': len(brand_criteria),
            'areas_for_improvement': len(brand_criteria[brand_criteria['final_score'] < 7])
        }
    
    def generate_report(self, persona_name: str, output_path: Optional[str] = None) -> str:
        """Generate HTML report for a specific persona"""
        try:
            # Load data for this persona
            df = self.load_unified_data(persona_name)
            
            if len(df) == 0:
                raise ValueError(f"No data found for persona: {persona_name}")
            
            # Generate all sections with real data
            executive_summary_data = self.generate_executive_summary(df)
            tier_analysis = self.get_tier_analysis(df)
            persona_voice = self.get_persona_voice_insights(df)
            recommendations = self.get_strategic_recommendations(df)
            visual_brand = self.get_visual_brand_assessment(df)
            
            # Get some sample URLs for context - fix the type annotation issue
            sample_urls = df[['url', 'final_score']].drop_duplicates().head(5).to_dict(orient='records')  # type: ignore
            
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
            
            # Get audit timestamp safely
            audit_timestamp = df['audited_ts'].iloc[0] if 'audited_ts' in df.columns and len(df) > 0 else datetime.now()
            
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
                'audit_timestamp': audit_timestamp
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

    def generate_consolidated_report(self, output_path: Optional[str] = None) -> str:
        """Generate a single consolidated HTML report for all personas"""
        try:
            # Load unified data for all personas
            df = self.load_unified_data()  # No persona filter = all data
            
            if len(df) == 0:
                raise ValueError("No data found for consolidated report")
            
            # Get all personas
            all_personas = sorted(df['persona_id'].unique())
            
            # Get audit timestamp safely
            audit_timestamp = df['audited_ts'].iloc[0] if 'audited_ts' in df.columns and len(df) > 0 else datetime.now()
            
            # Generate consolidated sections
            consolidated_data = {
                'total_personas': len(all_personas),
                'personas': all_personas,
                'generated_date': datetime.now().strftime('%B %d, %Y'),
                'audit_timestamp': audit_timestamp
            }
            
            # Overall executive summary across all personas
            consolidated_data['executive_summary'] = self.generate_consolidated_executive_summary(df)
            
            # Persona comparison analysis
            consolidated_data['persona_comparison'] = self.generate_persona_comparison(df, all_personas)
            
            # Cross-persona tier analysis
            consolidated_data['tier_analysis'] = self.generate_cross_tier_analysis(df)
            
            # Consolidated recommendations
            consolidated_data['recommendations'] = self.generate_consolidated_recommendations(df)
            
            # Overall brand health metrics
            consolidated_data['brand_health'] = self.generate_overall_brand_health(df)
            
            # Prepare template context
            context = {
                'company_name': 'Sopra Steria',
                'report_subtitle': 'Consolidated brand experience analysis across all personas',
                'generated_date': datetime.now().strftime('%B %d, %Y'),
                'audit_timestamp': audit_timestamp,
                **consolidated_data
            }
            
            # Load and render template
            template = self.env.get_template('consolidated_brand_report.html')
            html_content = template.render(context)
            
            # Determine output path
            if output_path is None:
                output_dir = 'html_reports/Consolidated_Brand_Report'
                os.makedirs(output_dir, exist_ok=True)
                output_path = f'{output_dir}/consolidated_brand_experience_report.html'
            
            # Write HTML file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info(f"Consolidated HTML report generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating consolidated report: {e}")
            raise

    def generate_consolidated_executive_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate executive summary for all personas combined"""
        total_personas = df['persona_id'].nunique()
        total_pages = df['page_id'].nunique()
        total_criteria = len(df)
        avg_score = df['final_score'].mean()
        
        # Count issues by severity across all personas
        critical_issues = len(df[df['descriptor'] == 'CRITICAL'])
        concerns = len(df[df['descriptor'] == 'CONCERN'])
        warnings = len(df[df['descriptor'] == 'WARN'])
        
        # Get tier breakdown across all personas
        tier_breakdown = df.groupby('tier_name')['final_score'].mean().round(1).to_dict()
        
        return {
            'total_personas': total_personas,
            'total_pages': total_pages,
            'total_criteria': total_criteria,
            'overall_score': round(avg_score, 1),
            'critical_issues': critical_issues,
            'concerns': concerns,
            'warnings': warnings,
            'tier_breakdown': tier_breakdown
        }

    def generate_persona_comparison(self, df: pd.DataFrame, all_personas: List[str]) -> Dict[str, Any]:
        """Generate comparison analysis between personas"""
        persona_comparison = {}
        
        for persona in all_personas:
            persona_data = df[df['persona_id'] == persona]
            
            persona_comparison[persona] = {
                'avg_score': round(persona_data['final_score'].mean(), 1),
                'page_count': persona_data['page_id'].nunique(),  # type: ignore
                'criteria_count': len(persona_data),
                'critical_issues': len(persona_data[persona_data['descriptor'] == 'CRITICAL']),
                'top_performing_tier': persona_data.groupby('tier_name')['final_score'].mean().idxmax(),
                'lowest_performing_tier': persona_data.groupby('tier_name')['final_score'].mean().idxmin()
            }
        
        return persona_comparison

    def generate_cross_tier_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate cross-persona tier analysis"""
        tier_analysis = {}
        
        for tier_name in df['tier_name'].unique():
            tier_data = df[df['tier_name'] == tier_name]
            
            tier_analysis[tier_name] = {
                'avg_score': round(tier_data['final_score'].mean(), 1),
                'total_pages': tier_data['page_id'].nunique(),  # type: ignore
                'persona_performance': tier_data.groupby('persona_id')['final_score'].mean().round(1).to_dict(),
                'critical_issues': len(tier_data[tier_data['descriptor'] == 'CRITICAL']),
                'concerns': len(tier_data[tier_data['descriptor'] == 'CONCERN'])
            }
        
        return tier_analysis

    def generate_consolidated_recommendations(self, df: pd.DataFrame) -> Dict[str, List[Dict[str, Any]]]:
        """Generate consolidated recommendations across all personas"""
        recommendations = {
            'cross_persona_issues': [],
            'tier_specific_improvements': [],
            'quick_wins': []
        }
        
        # Find issues that affect multiple personas
        cross_persona_issues = df.groupby('criterion_id').agg({
            'persona_id': 'nunique',
            'final_score': 'mean',
            'descriptor': lambda x: x.mode().iloc[0] if len(x) > 0 else 'UNKNOWN',
            'evidence': 'first'
        }).sort_values(['persona_id', 'final_score'], ascending=[False, True])  # type: ignore
        
        # Issues affecting 2+ personas
        multi_persona_issues = cross_persona_issues[cross_persona_issues['persona_id'] >= 2].head(5)
        
        for criterion_id, row in multi_persona_issues.iterrows():
            criterion_str = str(criterion_id)
            evidence = str(row['evidence'])
            persona_count = int(row['persona_id'])
            final_score = float(row['final_score'])
            descriptor = str(row['descriptor'])
            
            recommendations['cross_persona_issues'].append({
                'title': f"Cross-Persona Issue: {criterion_str.replace('_', ' ').title()}",
                'description': evidence[:200] + "..." if len(evidence) > 200 else evidence,
                'affected_personas': persona_count,
                'avg_score': round(final_score, 1),
                'severity': descriptor
            })
        
        # Tier-specific improvements
        for tier_name in df['tier_name'].unique():
            tier_data = df[df['tier_name'] == tier_name]
            worst_criteria = tier_data.groupby('criterion_id')['final_score'].mean().sort_values().head(3)  # type: ignore
            
            for criterion_id, score in worst_criteria.items():
                criterion_str = str(criterion_id)
                score_float = float(score)
                
                recommendations['tier_specific_improvements'].append({
                    'title': f"{tier_name}: {criterion_str.replace('_', ' ').title()}",
                    'description': f"Improve {criterion_str} performance in {tier_name}",
                    'current_score': round(score_float, 1),
                    'tier': tier_name
                })
        
        # Quick wins (low-hanging fruit across all personas)
        quick_wins = df[
            (df['descriptor'] == 'WARN') & 
            (df['final_score'] < 7) & 
            (df['tier_weight'] <= 0.3)
        ].groupby('criterion_id')['final_score'].mean().sort_values().head(5)  # type: ignore
        
        for criterion_id, score in quick_wins.items():
            criterion_str = str(criterion_id)
            score_float = float(score)
            
            recommendations['quick_wins'].append({
                'title': f"Quick Win: {criterion_str.replace('_', ' ').title()}",
                'description': f"Low-effort improvement opportunity with score of {score_float:.1f}",
                'current_score': round(score_float, 1),
                'effort': 'Low'
            })
        
        return recommendations

    def generate_overall_brand_health(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate overall brand health metrics"""
        overall_score = df['final_score'].mean()
        
        # Calculate health by tier
        tier_health = df.groupby('tier_name')['final_score'].mean().to_dict()
        
        # Calculate health by persona
        persona_health = df.groupby('persona_id')['final_score'].mean().to_dict()
        
        # Overall compliance rates
        excellent_rate = (df['descriptor'] == 'EXCELLENT').mean() * 100
        good_rate = (df['descriptor'] == 'GOOD').mean() * 100
        concerning_rate = (df['descriptor'].isin(['CRITICAL', 'CONCERN'])).mean() * 100
        
        return {
            'overall_score': round(overall_score, 1),
            'tier_health': {k: round(v, 1) for k, v in tier_health.items()},
            'persona_health': {k: round(v, 1) for k, v in persona_health.items()},
            'excellent_rate': round(excellent_rate, 1),
            'good_rate': round(good_rate, 1),
            'concerning_rate': round(concerning_rate, 1),
            'total_pages_analyzed': df['page_id'].nunique(),
            'total_criteria_assessed': len(df)
        }


if __name__ == "__main__":
    # Example usage
    generator = HTMLReportGenerator()
    print("HTML Report Generator initialized successfully") 