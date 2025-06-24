import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path to fix import issues
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


import streamlit as st
from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_main_header,
    create_section_header,
    create_subsection_header,
    create_metric_card,
    create_status_indicator,
    create_success_alert,
    create_warning_alert,
    create_error_alert,
    create_info_alert,
    get_perfect_chart_config,
    create_data_table,
    create_two_column_layout,
    create_three_column_layout,
    create_four_column_layout,
    create_content_card,
    create_brand_card,
    create_persona_card,
    create_primary_button,
    create_secondary_button,
    create_badge,
    create_spacer,
    create_divider
)


import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
from typing import Dict, List, Tuple, Optional

# Import dashboard components
from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

class StrategicRecommendationEngine:
    """Advanced recommendation aggregation and prioritization engine"""
    
    def __init__(self, master_df: pd.DataFrame, visual_audit_path: Path, sm_audit_path: Path):
        self.master_df = master_df
        self.visual_audit_path = visual_audit_path
        self.sm_audit_path = sm_audit_path
        self.recommendations = self.aggregate_all_recommendations()
        
    def aggregate_all_recommendations(self) -> pd.DataFrame:
        """Aggregate recommendations from all available sources and group by page to avoid repetition"""
        all_recs = []
        
        # Source 1: Quick win flags from unified dataset
        quick_wins = self.extract_quick_wins()
        all_recs.extend(quick_wins)
        
        # Source 2: Critical issues from unified dataset  
        critical_issues = self.extract_critical_issues()
        all_recs.extend(critical_issues)
        
        # Source 3: Success patterns for replication
        success_patterns = self.extract_success_patterns()
        all_recs.extend(success_patterns)
        
        # Source 4: Persona-specific improvements
        persona_recs = self.extract_persona_recommendations()
        all_recs.extend(persona_recs)
        
        # Source 5: Content and UX improvements
        content_recs = self.extract_content_recommendations()
        all_recs.extend(content_recs)
        
        # NEW Source 6: Visual Brand Audit Fix List
        visual_brand_recs = self.extract_visual_brand_recommendations()
        all_recs.extend(visual_brand_recs)
        
        # NEW Source 7: Social Media Audit
        social_media_recs = self.extract_social_media_recommendations()
        all_recs.extend(social_media_recs)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_recs)
        if df.empty:
            return df
            
        # Group by page_id and URL to avoid repetition
        aggregated_recs = []
        
        # Group recommendations by page_id
        for page_id in df['page_id'].unique():
            page_recs = df[df['page_id'] == page_id]
            
            if len(page_recs) == 1:
                # Single recommendation for this page, ensure consistent data structure
                rec_dict = page_recs.iloc[0].to_dict()
                rec_dict['all_categories'] = [rec_dict['category']]
                raw_evidence = [rec_dict['evidence']] if isinstance(rec_dict.get('evidence'), str) and len(rec_dict['evidence'].strip()) > 20 else []
                rec_dict['all_evidence'] = raw_evidence
                rec_dict['synthesized_findings'] = self.synthesize_findings(raw_evidence)
                aggregated_recs.append(rec_dict)

            else:
                # Multiple recommendations for same page - aggregate them
                first_rec = page_recs.iloc[0]
                
                # Collect all unique, non-trivial evidence and categories
                all_evidence = sorted(list(set([
                    ev.strip() for ev in page_recs['evidence'] if isinstance(ev, str) and len(ev.strip()) > 20
                ])))
                all_categories = sorted(list(set(page_recs['category'])))
                
                # Create a simple, high-level description. The details will be in the evidence list.
                description = f"Multiple improvement opportunities identified across {len(all_categories)} categories, requiring a coordinated effort to resolve."
                
                # THE CRITICAL ADDITION: Synthesize findings from the raw evidence
                synthesized_findings = self.synthesize_findings(all_evidence)
                
                # Create aggregated recommendation
                aggregated_rec = {
                    'id': f"aggregated_{page_id}",
                    'title': first_rec['title'].replace('⚡ Quick Win: ', '').replace('🔴 CRITICAL: ', ''),
                    'description': description,
                    'category': 'Multiple Categories',
                    'all_categories': all_categories,
                    'all_evidence': all_evidence,
                    'synthesized_findings': synthesized_findings,
                    'impact_score': page_recs['impact_score'].max(),
                    'urgency_score': page_recs['urgency_score'].max(),
                    'timeline': first_rec['timeline'],
                    'page_id': page_id,
                    'persona': first_rec['persona'],
                    'url': first_rec['url'],
                    'source': ', '.join(set(page_recs['source']))
                }
                
                # Add priority indicators to title
                if aggregated_rec['impact_score'] >= 8:
                    aggregated_rec['title'] = f"🔴 CRITICAL: {aggregated_rec['title']}"
                elif 'Quick Win' in ', '.join(all_categories):
                    aggregated_rec['title'] = f"⚡ Quick Win: {aggregated_rec['title']}"
                
                aggregated_recs.append(aggregated_rec)
        
        # Convert back to DataFrame and calculate priority scores
        final_df = pd.DataFrame(aggregated_recs)
        if not final_df.empty:
            final_df['priority_score'] = self.calculate_priority_score(final_df)
            final_df = final_df.sort_values('priority_score', ascending=False)
        
        return final_df
    
    def extract_quick_wins(self) -> List[Dict]:
        """Extract quick win opportunities from unified dataset"""
        if 'quick_win_flag' not in self.master_df.columns:
            return []
            
        quick_wins = self.master_df[self.master_df['quick_win_flag'] == True]
        recommendations = []
        
        for _, row in quick_wins.iterrows():
            page_title = self.get_friendly_page_title(row.get('url_slug', ''))
            score = row.get('raw_score', row.get('final_score', 0))
            url = row.get('url', '')
            evidence = row.get('evidence', 'Quick win opportunity identified')
            criterion = row.get('criterion_id', 'general')
            
            # Determine category based on criterion
            category = self.get_category_from_criterion(criterion)
            
            # Create comprehensive description
            full_description = f"Quick win opportunity for {page_title} (score: {score:.1f}/10). "
            if evidence and len(evidence) > 20:
                # Clean and truncate evidence to avoid repetition
                clean_evidence = evidence.strip()
                if len(clean_evidence) > 150:
                    clean_evidence = clean_evidence[:150] + "..."
                full_description += f"Key insight: {clean_evidence}"
            else:
                full_description += "Easy-to-implement improvements that will deliver immediate value."
            
            recommendations.append({
                'id': f"qw_{row.get('page_id', 'unknown')}_{criterion}",
                'title': f"⚡ Quick Win: Optimize {page_title}",
                'description': full_description,
                'category': category,
                'impact_score': min(10, 10 - score + 2),  # Higher impact for lower scores
                'urgency_score': 7,  # High urgency for quick wins
                'timeline': '0-30 days',
                'page_id': row.get('page_id'),
                'persona': row.get('persona_id', 'All'),
                'url': url,
                'evidence': evidence,
                'criterion': criterion,
                'source': 'Unified Dataset - Quick Win Flags'
            })
        
        return recommendations
    
    def extract_critical_issues(self) -> List[Dict]:
        """Extract critical issues requiring immediate attention"""
        if 'critical_issue_flag' not in self.master_df.columns:
            return []
            
        critical = self.master_df[self.master_df['critical_issue_flag'] == True]
        recommendations = []
        
        for _, row in critical.iterrows():
            page_title = self.get_friendly_page_title(row.get('url_slug', ''))
            score = row.get('raw_score', row.get('final_score', 0))
            url = row.get('url', '')
            evidence = row.get('evidence', 'Critical issue identified')
            criterion = row.get('criterion_id', 'general')
            
            # Determine category based on criterion
            category = self.get_category_from_criterion(criterion)
            
            # Create comprehensive description
            full_description = f"Critical issue requiring immediate attention (score: {score:.1f}/10). "
            if evidence and len(evidence) > 20:
                # Clean and truncate evidence to avoid repetition
                clean_evidence = evidence.strip()
                if len(clean_evidence) > 150:
                    clean_evidence = clean_evidence[:150] + "..."
                full_description += f"Issue: {clean_evidence}"
            else:
                full_description += "Urgent fixes needed to improve brand consistency and user experience."
            
            recommendations.append({
                'id': f"critical_{row.get('page_id', 'unknown')}_{criterion}",
                'title': f"🔴 CRITICAL: Fix {page_title}",
                'description': full_description,
                'category': category,
                'impact_score': 10,  # Maximum impact
                'urgency_score': 10, # Maximum urgency
                'timeline': '0-7 days',
                'page_id': row.get('page_id'),
                'persona': row.get('persona_id', 'All'),
                'url': url,
                'evidence': evidence,
                'criterion': criterion,
                'source': 'Unified Dataset - Critical Issue Flags'
            })
        
        return recommendations
    
    def extract_success_patterns(self) -> List[Dict]:
        """Extract success patterns for replication"""
        if 'success_flag' not in self.master_df.columns:
            return []
            
        successes = self.master_df[self.master_df['success_flag'] == True]
        recommendations = []
        
        # Group by similar pages/patterns
        success_patterns = {}
        for _, row in successes.iterrows():
            pattern_key = row.get('criterion_id', 'general')
            if pattern_key not in success_patterns:
                success_patterns[pattern_key] = []
            success_patterns[pattern_key].append(row)
        
        for pattern, rows in success_patterns.items():
            if len(rows) > 1:  # Only create replication recs if pattern appears multiple times
                avg_score = np.mean([r.get('raw_score', r.get('final_score', 0)) for r in rows])
                page_examples = [self.get_friendly_page_title(r.get('url_slug', '')) for r in rows[:3]]
                example_urls = [r.get('url', '') for r in rows[:3] if r.get('url', '')]
                
                # Create comprehensive description with URLs
                full_description = f"Apply successful pattern from {', '.join(page_examples)} to underperforming pages. Pattern achieves {avg_score:.1f}/10 average score. "
                if example_urls:
                    full_description += f"Reference successful implementations for replication guidance."
                
                recommendations.append({
                    'id': f"replicate_{pattern}",
                    'title': f"🔄 Replicate Success Pattern: {pattern.replace('_', ' ').title()}",
                    'description': full_description,
                    'category': f'🔄 Success Replication - {self.get_category_from_criterion(pattern)}',
                    'impact_score': min(10, avg_score),
                    'urgency_score': 5, # Medium urgency
                    'timeline': '30-90 days',
                    'page_id': 'multiple',
                    'persona': 'All',
                    'url': example_urls[0] if example_urls else '',  # First example URL
                    'evidence': f"Pattern identified across {len(rows)} high-performing pages: {', '.join(page_examples)}",
                    'criterion': pattern,
                    'source': 'Unified Dataset - Success Pattern Analysis'
                })
        
        return recommendations
    
    def extract_persona_recommendations(self) -> List[Dict]:
        """Extract persona-specific improvement opportunities"""
        recommendations = []
        
        if 'persona_id' in self.master_df.columns:
            # Analyze persona performance gaps
            persona_scores = self.master_df.groupby('persona_id').agg({
                'raw_score': 'mean',
                'final_score': 'mean'
            }).fillna(0)
            
            score_col = 'raw_score' if 'raw_score' in persona_scores.columns else 'final_score'
            worst_personas = persona_scores.nsmallest(2, score_col)
            
            for persona_id, scores in worst_personas.iterrows():
                avg_score = scores[score_col]
                if avg_score < 7.0:  # Only recommend if below good threshold
                    recommendations.append({
                        'id': f"persona_{persona_id.replace(' ', '_')}",
                        'title': f"🎭 Improve {persona_id} Experience",
                        'description': f"Persona showing lower engagement (avg score: {avg_score:.1f}/10). Requires targeted content and UX improvements.",
                        'category': '🎭 Persona Optimization',
                        'impact_score': 8,
                        'urgency_score': 6,
                        'timeline': '30-90 days',
                        'page_id': 'multiple',
                        'persona': persona_id,
                        'url': '',
                        'evidence': f"Persona performance analysis shows {avg_score:.1f}/10 average score",
                        'source': 'Unified Dataset - Persona Performance Analysis'
                    })
        
        return recommendations
    
    def extract_content_recommendations(self) -> List[Dict]:
        """Extract content and messaging improvement opportunities"""
        recommendations = []
        
        # Analyze pages with poor evidence/content quality
        if 'evidence' in self.master_df.columns:
            poor_content = self.master_df[
                (self.master_df['evidence'].str.len() < 50) |  # Very short evidence
                (self.master_df['evidence'].str.contains('generic|unclear|confusing', case=False, na=False))
            ]
            
            if not poor_content.empty:
                recommendations.append({
                    'id': 'content_quality_improvement',
                    'title': '📝 Improve Content Quality & Messaging',
                    'description': f"Content quality issues identified across {len(poor_content)} page assessments. Focus on clarity, specificity, and persona relevance.",
                    'category': '📝 Content & Copy',
                    'impact_score': 7,
                    'urgency_score': 5,
                    'timeline': '30-90 days',
                    'page_id': 'multiple',
                    'persona': 'All',
                    'url': '',
                    'evidence': f"Content analysis across {len(poor_content)} assessments",
                    'source': 'Unified Dataset - Content Quality Analysis'
                })
        
        # Analyze conversion-related issues
        if 'conversion_likelihood' in self.master_df.columns:
            low_conversion = self.master_df[self.master_df['conversion_likelihood'] == 'Low']
            if not low_conversion.empty:
                recommendations.append({
                    'id': 'conversion_optimization',
                    'title': '🎯 Optimize Conversion Paths',
                    'description': f"Low conversion likelihood identified on {len(low_conversion)} page assessments. Focus on CTAs, trust signals, and user journey optimization.",
                    'category': '🎯 Conversion Optimization',
                    'impact_score': 9,
                    'urgency_score': 8,
                    'timeline': '0-30 days',
                    'page_id': 'multiple',
                    'persona': 'All',
                    'url': '',
                    'evidence': f"Conversion analysis across {len(low_conversion)} assessments",
                    'source': 'Unified Dataset - Conversion Analysis'
                })
        
        return recommendations
    
    def extract_visual_brand_recommendations(self) -> List[Dict]:
        """Parse the visual_audit.md file and extract actionable recommendations from the Fix List."""
        recommendations = []
        if not self.visual_audit_path.exists():
            return recommendations

        with open(self.visual_audit_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Use regex to find all priority sections and their content
        priority_sections = re.findall(r"####\s(.*?)\sPriority Fixes\s.*?\n(.*?)(?=\n####|\Z)", content, re.S)
        
        priority_map = {
            "Critical": {"urgency": 10, "impact": 9},
            "High": {"urgency": 8, "impact": 8},
            "Medium": {"urgency": 6, "impact": 6},
            "Low": {"urgency": 4, "impact": 4},
        }

        for title, section_content in priority_sections:
            priority = title.strip()
            # Find individual fix items within the section
            fix_items = re.findall(r"\*\*Issue:\*\*\s(.*?)\n\*\*Impact:\*\*\s(.*?)\n.*?Recommended Action:\*\*\s(.*?)\n\s \*\*Timeline:\*\*\s(.*?)\n", section_content, re.S)
            
            for item in fix_items:
                issue, impact_desc, action, timeline = [i.strip().replace('\n', ' ') for i in item]
                
                rec = {
                    'id': f"visual_audit_{priority.lower()}_{len(recommendations)}",
                    'title': f"🎨 Visual Brand: {issue}",
                    'description': f"**Issue:** {issue}. **Impact:** {impact_desc}. **Recommended Action:** {action}",
                    'category': '🎨 Visual & Design',
                    'impact_score': priority_map.get(priority, {}).get("impact", 5),
                    'urgency_score': priority_map.get(priority, {}).get("urgency", 5),
                    'timeline': timeline,
                    'page_id': 'multiple',
                    'persona': 'All',
                    'url': '',
                    'evidence': f"From Visual Audit Report: {priority} Priority.",
                    'source': 'Visual Audit Report'
                }
                recommendations.append(rec)
                
        return recommendations
    
    def extract_social_media_recommendations(self) -> List[Dict]:
        """Parse the sm_audit_1.md file and extract strategic recommendations."""
        recommendations = []
        if not self.sm_audit_path.exists():
            return recommendations

        with open(self.sm_audit_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to capture each platform's section
        platform_sections = re.findall(r"LinkedIn \((.*?)\)\n(.*?)(?=LinkedIn \(|\Z)", content, re.S)
        
        for platform_name, section_content in platform_sections:
            platform_name = platform_name.strip()
            
            # Check for low engagement
            engagement_match = re.search(r"Engagement:\s(.*?)\.", section_content)
            if engagement_match:
                engagement_text = engagement_match.group(1).lower()
                if "low" in engagement_text or "limited" in engagement_text or "modest" in engagement_text:
                    rec = {
                        'id': f"sm_engagement_{platform_name.replace(' ', '_')}",
                        'title': f"📱 Social Media: Boost Engagement on {platform_name}",
                        'description': f"Develop a targeted content strategy to increase audience engagement for {platform_name}, which is currently low. Focus on interactive content and community management.",
                        'category': '👥 Social & Engagement',
                        'impact_score': 6,
                        'urgency_score': 6,
                        'timeline': '30-90 days',
                        'page_id': platform_name,
                        'persona': 'All',
                        'url': '',
                        'evidence': f"Social media audit identified low engagement for the {platform_name} LinkedIn account.",
                        'source': 'Social Media Audit'
                    }
                    recommendations.append(rec)

        return recommendations
    
    def calculate_priority_score(self, df: pd.DataFrame) -> pd.Series:
        """Calculate priority score using weighted algorithm (without effort)"""
        if df.empty:
            return pd.Series([], dtype=float)
            
        # Normalize scores to 0-1 range
        impact_norm = df['impact_score'] / 10
        urgency_norm = df['urgency_score'] / 10
        
        # Weighted priority calculation (impact 60%, urgency 40%)
        priority = (impact_norm * 0.6) + (urgency_norm * 0.4)
        
        # Scale to 1-10 range
        return priority * 10
    
    def get_friendly_page_title(self, url_slug: str) -> str:
        """Convert URL slug to friendly page title"""
        if not url_slug:
            return "Unknown Page"
            
        # Remove common prefixes
        title = url_slug.replace('www', '').replace('soprasteria', '').replace('com', '').replace('be', '').replace('nl', '')
        
        # Handle specific patterns
        if 'linkedin' in title:
            return "LinkedIn Company Page"
        elif 'youtube' in title:
            return "YouTube Channel"
        elif 'homepage' in title.lower() or title.strip() == '':
            return "Homepage"
        elif 'about' in title:
            return "About Us Page"
        elif 'newsroom' in title:
            return "Newsroom"
        elif 'blog' in title:
            return "Blog"
        elif 'services' in title or 'whatwedo' in title:
            return "Services Page"
        elif 'industries' in title:
            return "Industry Solutions"
        
        # Clean up and format
        title = title.replace('-', ' ').replace('_', ' ').strip()
        title = ' '.join(word.capitalize() for word in title.split() if word)
        
        return title if title else "Page"

    def get_category_from_criterion(self, criterion_id: str) -> str:
        """Map criterion IDs to meaningful categories"""
        if not criterion_id:
            return 'General'
            
        criterion_lower = criterion_id.lower()
        
        # Brand and messaging
        if any(term in criterion_lower for term in ['brand', 'message', 'value_prop', 'positioning']):
            return '🏢 Brand & Messaging'
        
        # Visual and design
        elif any(term in criterion_lower for term in ['visual', 'design', 'layout', 'ui', 'ux']):
            return '🎨 Visual & Design'
        
        # Content and copy
        elif any(term in criterion_lower for term in ['content', 'copy', 'text', 'headline']):
            return '📝 Content & Copy'
        
        # Navigation and UX
        elif any(term in criterion_lower for term in ['navigation', 'menu', 'cta', 'button', 'link']):
            return '🧭 Navigation & UX'
        
        # Trust and credibility
        elif any(term in criterion_lower for term in ['trust', 'credibility', 'testimonial', 'proof']):
            return '🛡️ Trust & Credibility'
        
        # Technical and performance
        elif any(term in criterion_lower for term in ['technical', 'performance', 'speed', 'mobile']):
            return '⚙️ Technical & Performance'
        
        # Social proof and engagement
        elif any(term in criterion_lower for term in ['social', 'engagement', 'community']):
            return '👥 Social & Engagement'
        
        else:
            return f'📋 {criterion_id.replace("_", " ").title()}'

    def synthesize_findings(self, evidence_list: List[str]) -> List[str]:
        """
        Analyzes a list of raw evidence strings and synthesizes them into
        actionable, human-readable themes. This is the core of providing
        a true summary for leadership.
        """
        if not evidence_list:
            return []

        themes = {
            "Missing clear calls to action or navigation": ['cta', 'call to action', 'button', 'next step', 'conversion', 'navigation', 'menu', 'find', 'path', 'journey'],
            "Lacks trust signals (testimonials, logos, case studies)": ['trust', 'testimonial', 'logo', 'certification', 'case stud', 'proof', 'indicator'],
            "Inconsistent or weak brand messaging": ['messaging', 'tagline', 'value prop', 'tone', 'voice', 'brand'],
            "Generic, unclear, or confusing content": ['generic', 'unclear', 'confusing', 'vague', 'content', 'copy', 'text'],
            "Visual clutter or poor layout design": ['layout', 'design', 'visual', 'spacing', 'clutter', 'ui']
        }

        identified_themes = set()
        for evidence in evidence_list:
            evidence_lower = evidence.lower()
            theme_found = False
            for theme, keywords in themes.items():
                if any(keyword in evidence_lower for keyword in keywords):
                    identified_themes.add(theme)
                    theme_found = True
                    break # Move to next piece of evidence once a theme is found
            if not theme_found:
                # Add the original evidence if no theme matches, ensuring nothing is lost
                summary = evidence[:120] + '...' if len(evidence) > 120 else evidence
                identified_themes.add(f"Specific Issue: {summary}")


        # If no specific themes were found at all, return a generic summary
        if not identified_themes:
            return ["General improvements needed across multiple areas."]

        return sorted(list(identified_themes))

    def get_thematic_recommendations(self) -> Dict[str, List[Dict]]:
        """
        Groups all raw recommendations into the real, data-driven thematic buckets.
        This is the final, correct implementation of the new engine.
        """
        themed_recommendations = {
            "Brand & Messaging Strategy": [],
            "Visual Identity & Design": [],
            "User Experience & Trust": [],
            "Social Media Performance": [],
        }
        
        # This mapping is now based on the actual data sources and criteria
        category_to_theme_map = {
            '🏢 Brand & Messaging': "Brand & Messaging Strategy",
            '📝 Content & Copy': "Brand & Messaging Strategy",
            '🎨 Visual & Design': "Visual Identity & Design",
            '🧭 Navigation & UX': "User Experience & Trust",
            '🛡️ Trust & Credibility': "User Experience & Trust",
            '🎯 Conversion Optimization': "User Experience & Trust",
            '👥 Social & Engagement': "Social Media Performance",
        }

        for index, rec in self.recommendations.iterrows():
            # Handle list of categories for aggregated recommendations
            categories = rec.get('all_categories', [rec.get('category')])
            
            assigned = False
            for cat in categories:
                theme = category_to_theme_map.get(cat)
                if theme:
                    themed_recommendations[theme].append(rec)
                    assigned = True
                    break 
            
            if not assigned:
                # Fallback logic based on the recommendation's origin
                source = rec.get('source', '').lower()
                if 'social media' in source:
                    themed_recommendations['Social Media Performance'].append(rec)
                elif 'visual audit' in source:
                    themed_recommendations['Visual Identity & Design'].append(rec)
                else: # Default for data-driven findings without a clear home
                    themed_recommendations['Brand & Messaging Strategy'].append(rec)
        
        return themed_recommendations

def main():
    # Configure page layout for consistency with other pages
    st.set_page_config(
        page_title="Strategic Recommendations",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

def main():
    # Create standardized page header
    create_main_header("🎯 Strategic Recommendations", "Prioritized action plan for brand improvement")
    
    # Load data
    try:
        loader = BrandHealthDataLoader()
        datasets, master_df = loader.load_all_data()
        
        # Define paths for the markdown-based audits
        visual_audit_path = project_root / "audit_inputs" / "visual_brand" / "visual_audit.md"
        sm_audit_path = project_root / "audit_inputs" / "social_media" / "sm_audit_1.md"
        
        if master_df.empty:
            st.error("No data available for recommendations analysis.")
            return
            
        # Initialize recommendation engine with all data sources
        rec_engine = StrategicRecommendationEngine(master_df, visual_audit_path, sm_audit_path)
        
        # Get the new, theme-based recommendations
        themed_recs = rec_engine.get_thematic_recommendations()

        # --- NEW PAGE LAYOUT BASED ON USER STORIES ---

        # 1. The 10-Second Summary
        create_section_header("Executive Summary")
        critical_count = sum(1 for _, r in rec_engine.recommendations.iterrows() if r.get('impact_score', 0) >= 9)
        quick_win_count = sum(1 for _, r in rec_engine.recommendations.iterrows() if 'quick win' in r.get('title', '').lower())
        strategic_count = len(rec_engine.recommendations) - critical_count - quick_win_count
        avg_priority = rec_engine.recommendations['priority_score'].mean() if not rec_engine.recommendations.empty else 0.0
        
        col1, col2, col3, col4 = create_four_column_layout()
        with col1:
            create_metric_card(str(critical_count), "🔴 Critical Issues")
        with col2:
            create_metric_card(str(quick_win_count), "⚡ Quick Wins")
        with col3:
            create_metric_card(str(strategic_count), "🎯 Strategic Moves")
        with col4:
            create_metric_card(f"{avg_priority:.1f}", "📈 Avg Priority")
            
        create_divider()

        # 2. The Top Priorities
        create_section_header("Top 3 Strategic Priorities")
        st.info("Based on a combined analysis of impact, urgency, and data quality, these are the most critical, high-level actions to take.")
        
        top_priorities_df = rec_engine.recommendations.sort_values(by='priority_score', ascending=False).head(3)
        for i, (index, priority) in enumerate(top_priorities_df.iterrows()):
            st.success(f"**Priority #{i+1}:** {priority['title']}")
        
        create_divider()

        # 3. The "What To Do" Plan
        create_section_header("Thematic Action Plan")
        
        for theme, rec_list in themed_recs.items():
            if rec_list:
                with st.expander(f"### {theme} ({len(rec_list)} recommendations)"):
                    st.markdown(f"**Synthesized Summary of Key Issues for {theme}:**")
                    
                    # Create a summarized list of unique findings within the theme
                    findings = set()
                    for rec in rec_list:
                        for finding in rec.get('synthesized_findings', []):
                            findings.add(finding)
                    
                    if findings:
                        # Use markdown lists for better formatting
                        findings_list_str = "\n".join([f"- {finding}" for finding in sorted(list(findings))[:5]])
                        st.markdown(findings_list_str)
                    else:
                        st.write("No specific sub-themes identified, general improvements needed.")
                        
                    st.markdown("**Affected Pages/Platforms:**")
                    affected_pages = set()
                    for rec in rec_list:
                        url = rec.get('url')
                        if url:
                            affected_pages.add(f"[{url.replace('https://www.','')}]({url})")
                        else:
                            # Use a more descriptive fallback
                            source_text = rec.get('source', 'General Recommendation')
                            if 'Visual' in source_text:
                                affected_pages.add("Multiple Pages (Visual Audit)")
                            elif 'Social' in source_text:
                                affected_pages.add(rec.get('page_id', "Multiple Platforms"))
                            else:
                                affected_pages.add(rec.get('page_id', 'General'))

                    # Display pages in a more compact way
                    st.markdown(" | ".join(sorted(list(affected_pages))[:10]))
                    
                    with st.expander("View All Underlying Recommendations for this Theme"):
                        display_recommendation_cards(rec_list)
        
    except Exception as e:
        st.error(f"Error loading recommendations: {str(e)}")
        st.exception(e)

def display_recommendation_cards(recommendations: List[Dict]):
    """Display detailed recommendation cards from a list of recommendation dicts."""
    
    if not recommendations:
        st.info("No recommendations match the selected filters.")
        return
    
    st.markdown(f"**Showing {len(recommendations)} recommendations**")
    
    for rec in recommendations:
        # Determine priority level
        priority_score = rec.get('priority_score', 0)
        if priority_score >= 8:
            priority_icon = "🔴"
        elif priority_score >= 6:
            priority_icon = "🟡"
        else:
            priority_icon = "🟢"
        
        # Get URL if available
        url = rec.get('url', '')
        evidence = rec.get('evidence', '')
        
        # Create expandable card for full details
        with st.expander(f"{priority_icon} {rec.get('title', 'N/A')} (Priority: {priority_score:.1f})", expanded=False):
            
            # URL section
            if url and url != '':
                st.markdown(f"**🔗 Page URL:** [{url}]({url})")
                st.divider()
            
            # Full description
            st.markdown("**📋 Description:**")
            st.write(rec.get('description', 'No description available.'))
            
            # Evidence/Details section
            if evidence and len(str(evidence)) > 20:
                st.markdown("**🔍 Evidence & Details:**")
                st.write(evidence)
            
            # Metrics in columns
            col1, col2, col3, col4 = create_four_column_layout()
            with col1:
                create_metric_card(f"{priority_score:.1f}/10", "Priority Score", status="warning" if priority_score >= 8 else "info")
            with col2:
                create_metric_card(f"{rec.get('impact_score', 0)}/10", "Impact", status="success" if rec.get('impact_score', 0) >= 7 else "info")
            with col3:
                create_metric_card(rec.get('timeline', 'N/A'), "Timeline", status="info")
            with col4:
                create_metric_card(rec.get('category', 'N/A'), "Category", status="info")
            
            # Additional details
            st.markdown("**📊 Additional Details:**")
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.write(f"**Persona:** {rec.get('persona', 'N/A')}")
            with detail_col2:
                st.write(f"**Source:** {rec.get('source', 'N/A')}")
            with detail_col3:
                st.write(f"**🆔 Page ID:** `{rec.get('page_id', 'N/A')}`")
        
        # Quick summary below expander
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.write(f"**Impact:** {rec.get('impact_score', 0)}/10")
        with summary_col2:
            st.write(f"**Timeline:** {rec.get('timeline', 'N/A')}")
        with summary_col3:
            st.write(f"**Category:** {rec.get('category', 'N/A')}")
        
        st.markdown("---")  # Separator between recommendations

def display_resource_planning(recommendations: pd.DataFrame):
    """Display resource planning insights"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Category Distribution")
        category_counts = recommendations['category'].value_counts()
        fig_cat = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Recommendations by Category"
        )
        st.plotly_chart(fig_cat, use_container_width=True, key="category_pie")
    
    with col2:
        st.markdown("### ⏰ Timeline Distribution")
        timeline_counts = recommendations['timeline'].value_counts()
        fig_timeline = px.bar(
            x=timeline_counts.index,
            y=timeline_counts.values,
            title="Recommendations by Timeline"
        )
        fig_timeline.update_layout(xaxis_title="Timeline", yaxis_title="Count")
        st.plotly_chart(fig_timeline, use_container_width=True, key="timeline_bar")
    
    # Resource estimates
    st.markdown("### 💼 Priority Analysis")
    
    total_recs = len(recommendations)
    high_priority = len(recommendations[recommendations['priority_score'] >= 8])
    avg_impact = recommendations['impact_score'].mean()
    
    col1, col2, col3 = create_three_column_layout()
    
    with col1:
        create_metric_card(str(total_recs), "Total Recommendations", status="info")
    
    with col2:
        create_metric_card(str(high_priority), "High Priority Items", status="warning" if high_priority > 0 else "success")
    
    with col3:
        create_metric_card(f"{avg_impact:.1f}/10", "Average Impact Level", status="success" if avg_impact >= 7 else "info")
    
    # Priority distribution
    priority_ranges = pd.cut(recommendations['priority_score'], 
                           bins=[0, 4, 6, 8, 10], 
                           labels=['Low (1-4)', 'Medium (4-6)', 'High (6-8)', 'Critical (8-10)'])
    priority_dist = priority_ranges.value_counts()
    st.markdown("### 🎯 Priority Distribution")
    st.bar_chart(priority_dist)

if __name__ == "__main__":
    main() 