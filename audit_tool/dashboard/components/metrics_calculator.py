"""
Metrics Calculator for Brand Health Command Center
Handles all derived metrics and KPI calculations
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class BrandHealthMetricsCalculator:
    """Calculate brand health metrics and KPIs"""
    
    def __init__(self, df: pd.DataFrame, recommendations_df: Optional[pd.DataFrame] = None):
        self.df = df
        self.recommendations_df = recommendations_df
        self.validate_data()
    
    def validate_data(self) -> None:
        """Validate that required columns exist"""
        # Check for page_id
        if 'page_id' not in self.df.columns:
            logger.warning("Missing required column: page_id")
        
        # Check for at least one score column
        score_cols = ['raw_score', 'raw_score', 'final_score']
        has_score = any(col in self.df.columns for col in score_cols)
        if not has_score:
            logger.warning(f"Missing score columns. Expected one of: {score_cols}")
    
    def calculate_brand_health_score(self) -> float:
        """Calculate overall brand health score"""
        # Use raw_score as the primary score column for unified data
        if 'raw_score' in self.df.columns:
            return float(self.df['raw_score'].mean())
        elif 'final_score' in self.df.columns:
            return float(self.df['final_score'].mean())
        elif 'avg_score' in self.df.columns:
            return float(self.df['avg_score'].mean())
        
        logger.warning("No score column found for brand health calculation")
        return 0.0
    
    def get_brand_health_status(self, score: float) -> Tuple[str, str]:
        """Get brand health status and emoji"""
        if score >= 8.0:
            return "Excellent", "🟢"
        elif score >= 6.0:
            return "Good", "🟡"
        elif score >= 4.0:
            return "Fair", "🟠"
        else:
            return "Critical", "🔴"
    
    def calculate_critical_issues(self) -> Dict:
        """Calculate critical issues metrics"""
        # Use raw_score as the primary score column for unified data
        if 'raw_score' in self.df.columns:
            critical_pages = self.df[self.df['raw_score'] < 4.0]
            score_col = 'raw_score'
        elif 'final_score' in self.df.columns:
            critical_pages = self.df[self.df['final_score'] < 4.0]
            score_col = 'final_score'
        elif 'raw_score' in self.df.columns:
            critical_pages = self.df[self.df['raw_score'] < 4.0]
            score_col = 'raw_score'
        else:
            critical_pages = pd.DataFrame()
            score_col = None
        
        return {
            'count': len(critical_pages),
            'percentage': len(critical_pages) / len(self.df) * 100 if len(self.df) > 0 else 0,
            'pages': critical_pages['page_id'].tolist() if 'page_id' in critical_pages.columns else []
        }
    
    def calculate_sentiment_metrics(self) -> Dict:
        """Calculate sentiment-related metrics"""
        # Remove overall_sentiment usage - this should only apply to offsite channels
        # For onsite data, we'll use other evidence-based metrics
        
        # Check if we have valid score data to derive sentiment from
        score_col = None
        for col in ['final_score', 'raw_score', 'avg_score']:
            if col in self.df.columns:
                score_col = col
                break
        
        if score_col is None:
            return {'positive': 0, 'neutral': 0, 'negative': 0, 'net_sentiment': 0}
        
        # Derive sentiment from score ranges for onsite data
        scores = self.df[score_col].dropna()
        if len(scores) == 0:
            return {'positive': 0, 'neutral': 0, 'negative': 0, 'net_sentiment': 0}
        
        # Convert scores to sentiment categories
        positive_pct = (scores >= 7.0).sum() / len(scores) * 100
        neutral_pct = ((scores >= 4.0) & (scores < 7.0)).sum() / len(scores) * 100
        negative_pct = (scores < 4.0).sum() / len(scores) * 100
        
        return {
            'positive': positive_pct,
            'neutral': neutral_pct,
            'negative': negative_pct,
            'net_sentiment': positive_pct - negative_pct
        }
    
    def calculate_conversion_readiness(self) -> Dict:
        """Calculate conversion readiness metrics"""
        # Remove problematic fields: conversion_likelihood, engagement, etc.
        # These should only apply to offsite channels, not onsite data (Tier 1, 2, 3)
        
        # Use evidence-based metrics for onsite conversion assessment
        evidence_cols = ['trust_credibility_assessment', 'business_impact_analysis', 'effective_copy_examples']
        
        # Check what columns are actually available from evidence
        available_cols = [col for col in evidence_cols if col in self.df.columns]
        
        # If no evidence columns, use score-based approach
        if not available_cols:
            # Use the main score column
            score_col = None
            for col in ['final_score', 'raw_score', 'avg_score']:
                if col in self.df.columns:
                    score_col = col
                    break
            
            if score_col is None:
                return {'raw_score': 0, 'status': 'Unknown', 'color': 'gray'}
            
            # Calculate average score for conversion readiness
            conversion_score = float(self.df[score_col].mean())
        else:
            # Use evidence-based assessment for conversion readiness
            # This is more appropriate for onsite data
            evidence_scores = []
            for col in available_cols:
                # Convert text evidence to numeric scores based on quality
                col_data = self.df[col].dropna()
                if len(col_data) > 0:
                    # Score based on evidence quality (length and content)
                    scores = col_data.apply(lambda x: min(len(str(x)) / 100, 10) if pd.notna(x) else 0)
                    evidence_scores.append(float(scores.mean()))
            
            if evidence_scores:
                conversion_score = sum(evidence_scores) / len(evidence_scores)
            else:
                conversion_score = 0.0
        
        if conversion_score >= 7.0:
            status, color = "High", "green"
        elif conversion_score >= 5.0:
            status, color = "Medium", "orange"
        else:
            status, color = "Low", "red"
        
        return {
            'raw_score': conversion_score,
            'status': status,
            'color': color
        }
    
    def calculate_quick_wins(self) -> Dict:
        """Calculate quick wins metrics"""
        # Use quick_win_flag from unified CSV if available
        if 'quick_win_flag' in self.df.columns:
            quick_wins = self.df[self.df['quick_win_flag'] == True]
            return {
                'count': len(quick_wins),
                'opportunities': quick_wins[['page_id', 'url_slug', 'avg_score']].to_dict('records') if len(quick_wins) > 0 else []
            }
        
        # Fallback: identify potential quick wins from score data
        # Find the correct score column - use avg_score from unified CSV
        score_col = 'avg_score' if 'avg_score' in self.df.columns else 'raw_score'
        
        if score_col in self.df.columns:
            # Quick wins are pages with moderate scores (4-7) that could be improved easily
            potential_wins = self.df[(self.df[score_col] >= 4.0) & (self.df[score_col] <= 7.0)]
            return {
                'count': len(potential_wins),
                'opportunities': potential_wins[['page_id', 'url_slug', score_col]].rename(columns={score_col: 'current_score'}).to_dict('records') if len(potential_wins) > 0 else []
            }
        
        # No data available
        return {
            'count': 0,
            'opportunities': []
        }
    
    def calculate_tier_performance(self) -> pd.DataFrame:
        """Calculate performance metrics by tier"""
        if 'tier' not in self.df.columns:
            return pd.DataFrame()
        
        # Use the correct score column from unified CSV - prioritize final_score
        score_col = None
        if 'final_score' in self.df.columns:
            score_col = 'final_score'
        elif 'raw_score' in self.df.columns:
            score_col = 'raw_score'
        elif 'avg_score' in self.df.columns:
            score_col = 'avg_score'
        
        if not score_col:
            logger.warning("No score column found for tier performance calculation")
            return pd.DataFrame()
        
        # Build aggregation dictionary using existing columns
        agg_dict = {
            score_col: ['mean', 'count']  # Use the available score column
        }
        
        # Only add numeric columns to avoid string aggregation errors
        if 'sentiment_numeric' in self.df.columns:
            agg_dict['sentiment_numeric'] = 'mean'
        if 'engagement_numeric' in self.df.columns:
            agg_dict['engagement_numeric'] = 'mean'
        if 'conversion_numeric' in self.df.columns:
            agg_dict['conversion_numeric'] = 'mean'
        
        try:
            tier_metrics = self.df.groupby('tier').agg(agg_dict).round(2)
            
            # Flatten column names and standardize to expected names
            new_columns = []
            for col in tier_metrics.columns:
                if isinstance(col, tuple):
                    base_col, agg_func = col
                    if agg_func == 'mean' and base_col in [score_col]:
                        new_columns.append('avg_score')  # Standardize score column name
                    elif agg_func == 'mean' and base_col == 'sentiment_numeric':
                        new_columns.append('avg_sentiment')
                    elif agg_func == 'mean' and base_col == 'engagement_numeric':
                        new_columns.append('avg_engagement')
                    elif agg_func == 'mean' and base_col == 'conversion_numeric':
                        new_columns.append('avg_conversion')
                    else:
                        new_columns.append('_'.join(col).strip())
                else:
                    new_columns.append(col)
            
            tier_metrics.columns = new_columns
            return tier_metrics.reset_index()
        except Exception as e:
            logger.error(f"Error calculating tier performance: {e}")
            return pd.DataFrame()
    
    def get_top_opportunities(self, limit: int = 5) -> List[Dict]:
        """Get top improvement opportunities with evidence from unified dataset"""
        # Find the correct score column
        score_col = None
        for col in ['avg_score', 'raw_score', 'final_score']:
            if col in self.df.columns:
                score_col = col
                break
        
        if score_col is None:
            return []
        
        # Get lowest scoring pages with evidence for improvement opportunities
        low_scoring = self.df[self.df[score_col] < 7.0].copy()
        
        if low_scoring.empty:
            return []
        
        # Calculate opportunity impact using tier weights
        if 'tier_weight' in low_scoring.columns:
            low_scoring['opportunity_impact'] = (10 - low_scoring[score_col]) * low_scoring['tier_weight']
        else:
            low_scoring['opportunity_impact'] = (10 - low_scoring[score_col])
        
        # AGGREGATE TO PAGE LEVEL to avoid duplicates - include richer supporting data
        page_opportunities = low_scoring.groupby('page_id').agg({
            score_col: 'mean',  # Average score across all criteria for this page
            'opportunity_impact': 'mean',  # Average impact across all criteria (keep within 1-10 scale)
            'tier': 'first',
            'tier_name': 'first',
            'url': 'first',
            'url_slug': 'first',
            'evidence': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip()])[:500],  # Combine evidence
            'business_impact_analysis': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:300],
            'descriptor': lambda x: x.mode().iloc[0] if not x.mode().empty else 'NEEDS IMPROVEMENT',  # Most common descriptor
            # Content examples for concrete evidence
            'effective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
            'ineffective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
            # Specific feedback areas
            'trust_credibility_assessment': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200],
            'information_gaps': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200]
        }).reset_index()
        
        # Sort by total opportunity impact and get top opportunities
        top_opportunities = page_opportunities.nlargest(limit, 'opportunity_impact')
        
        result = []
        for _, row in top_opportunities.iterrows():
            # Create a friendly page title from URL slug
            url_slug = row.get('url_slug') or ''
            if not isinstance(url_slug, str):
                url_slug = str(url_slug) if url_slug is not None else ''
            page_title = self._create_friendly_title(url_slug)
            
            # Calculate effort level based on current score
            current_score = row.get(score_col, 0)
            if current_score is None:
                current_score = 0
            current_score = float(current_score)
            
            if current_score < 3.0:
                effort_level = "High"
            elif current_score < 5.0:
                effort_level = "Medium"
            else:
                effort_level = "Low"
            
            # Extract evidence and create actionable recommendation
            evidence_text = row.get('evidence', '')
            business_impact = row.get('business_impact_analysis', '')
            trust_assessment = row.get('trust_credibility_assessment', '')
            
            # Create specific recommendation based on evidence
            if evidence_text and len(str(evidence_text)) > 20:
                # Extract key issues from evidence
                recommendation = self._create_recommendation_from_evidence(evidence_text, current_score)
                evidence_summary = str(evidence_text)[:200] + "..." if len(str(evidence_text)) > 200 else str(evidence_text)
            else:
                recommendation = f"Improve {row.get('tier_name', 'page')} content - current score {current_score:.1f}/10"
                evidence_summary = f"Page scoring {current_score:.1f}/10 needs improvement"
            
            # Add business context if available
            if business_impact and len(str(business_impact)) > 10:
                evidence_summary += f" | Business Impact: {str(business_impact)[:100]}"
            
            result.append({
                'page_id': row.get('page_id', 'Unknown'),
                'page_title': page_title,
                'url': row.get('url', ''),
                'current_score': current_score,
                'potential_impact': round(float(row.get('opportunity_impact') or 0), 1),
                'effort_level': effort_level,
                'tier': row.get('tier', 'Unknown'),
                'recommendation': recommendation,
                'evidence': evidence_summary,
                'criterion': row.get('criterion_code', 'General'),
                'descriptor': row.get('descriptor', 'NEEDS IMPROVEMENT'),
                # Rich supporting data - evidence-based fields only
                'business_impact_analysis': row.get('business_impact_analysis', ''),
                'effective_copy_examples': row.get('effective_copy_examples', ''),
                'ineffective_copy_examples': row.get('ineffective_copy_examples', ''),
                'trust_credibility_assessment': row.get('trust_credibility_assessment', ''),
                'information_gaps': row.get('information_gaps', '')
            })
        
        return result
    
    def _create_recommendation_from_evidence(self, evidence: str, score: float) -> str:
        """Create actionable recommendation from evidence text"""
        evidence_str = str(evidence).lower()
        
        # Common improvement patterns based on evidence keywords
        if 'brand' in evidence_str and 'generic' in evidence_str:
            return "Strengthen brand differentiation and unique value proposition"
        elif 'navigation' in evidence_str or 'menu' in evidence_str:
            return "Improve site navigation and information architecture"
        elif 'content' in evidence_str and ('unclear' in evidence_str or 'confusing' in evidence_str):
            return "Clarify content messaging and improve readability"
        elif 'trust' in evidence_str or 'credibility' in evidence_str:
            return "Add trust signals and credibility indicators"
        elif 'engagement' in evidence_str or 'boring' in evidence_str:
            return "Enhance content engagement and visual appeal"
        elif 'conversion' in evidence_str or 'action' in evidence_str:
            return "Optimize calls-to-action and conversion pathways"
        elif score < 3.0:
            return "Critical content overhaul required - multiple issues identified"
        elif score < 5.0:
            return "Moderate content improvements needed based on audit findings"
        else:
            return "Fine-tune content based on specific audit feedback"
    
    def calculate_success_stories(self, min_score: float = 7.7) -> List[Dict]:
        """Get success stories (high-performing pages) aggregated to page level"""
        # Use avg_score as the primary score column for unified data
        if 'avg_score' in self.df.columns:
            score_col = 'avg_score'
        elif 'raw_score' in self.df.columns:
            score_col = 'raw_score'
        elif 'final_score' in self.df.columns:
            score_col = 'final_score'
        else:
            return []
        
        success_pages = self.df[self.df[score_col] >= min_score]
        
        if success_pages.empty:
            return []
        
        # AGGREGATE TO PAGE LEVEL to avoid duplicates
        page_success = success_pages.groupby('page_id').agg({
            score_col: 'mean',  # Average score across all criteria for this page
            'tier': 'first',
            'url': 'first',
            'url_slug': 'first',
            'evidence': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e).strip()) > 10])[:500]  # Combine meaningful evidence
        }).reset_index()
        
        # Filter to keep only pages that still meet the min_score after aggregation
        page_success = page_success[page_success[score_col] >= min_score]
        
        # Sort by score (highest first) and limit to top 5
        column_name = str(score_col)  # Explicit type conversion for type checker
        top_success = page_success.sort_values(by=column_name, ascending=False).head(5)
        
        result = []
        for _, row in top_success.iterrows():
            # Create a friendly page title from URL slug
            url_slug = row.get('url_slug') or ''
            if not isinstance(url_slug, str):
                url_slug = str(url_slug) if url_slug is not None else ''
            page_title = self._create_friendly_title(url_slug)
            
            story = {
                'page_id': row.get('page_id', 'Unknown'),
                'page_title': page_title,
                'url': row.get('url', ''),
                'raw_score': row.get(score_col, 0),
                'tier': row.get('tier', 'Unknown'),
                'key_strengths': self._extract_page_level_strengths(row),
                'evidence': row.get('evidence', '')  # Include aggregated evidence
            }
            
            result.append(story)
        
        return result

    def calculate_success_library(
        self,
        success_threshold: float = 7.5,
        persona: str = "All",
        tier: str = "All",
        max_stories: int = 10,
        evidence_type: str = "All",
        search_term: str = "",
    ) -> Dict[str, Any]:
        """Comprehensive success library metrics"""

        filtered_df = self.df.copy()
        if persona != "All" and 'persona_id' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['persona_id'] == persona]
        if tier != "All" and 'tier' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['tier'] == tier]

        if 'avg_score' in filtered_df.columns:
            success_df = filtered_df[filtered_df['avg_score'] >= success_threshold]
        else:
            success_df = pd.DataFrame()

        if success_df.empty:
            return {
                "successStories": [],
                "overview": {
                    "totalPages": 0,
                    "successPages": 0,
                    "successRate": 0,
                    "avgScore": 0,
                    "excellent": 0,
                    "veryGood": 0,
                    "good": 0,
                },
                "patternData": [],
                "evidenceItems": [],
                "replicationTemplates": [],
                "personas": [],
                "tiers": [],
            }

        page_success = success_df.groupby('page_id').agg({
            'avg_score': 'mean',
            'tier': 'first',
            'url': 'first',
            'url_slug': 'first',
            'persona_id': 'first',
            'effective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
            'ineffective_copy_examples': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 20])[:400],
            'evidence': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip()])[:500],
            'business_impact_analysis': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:300],
            'trust_credibility_assessment': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200],
            'information_gaps': lambda x: ' | '.join([str(e) for e in x.dropna() if str(e).strip() and len(str(e)) > 10])[:200],
        }).reset_index()

        page_success = page_success[page_success['avg_score'] >= success_threshold]
        page_success = page_success.sort_values('avg_score', ascending=False).head(max_stories)

        all_scores = self.df['avg_score'].dropna() if 'avg_score' in self.df.columns else pd.Series([])

        success_stories: List[Dict[str, Any]] = []
        for _, story in page_success.iterrows():
            page_id = story.get('page_id', 'Unknown')
            score = story.get('avg_score', 0)
            url = story.get('url', '')
            title = self._create_friendly_page_title(page_id, url)
            percentile = (all_scores < score).mean() * 100 if len(all_scores) > 0 else 0
            effective_examples = story.get('effective_copy_examples', '')
            persona_quotes = self.extract_persona_quotes_success(effective_examples)
            story_data = {
                'pageId': page_id,
                'pageTitle': title,
                'url': url,
                'score': round(score, 1),
                'percentile': round(percentile, 1),
                'tier': story.get('tier', 'Unknown'),
                'personaId': story.get('persona_id', 'Unknown'),
                'effectiveCopy': story.get('effective_copy_examples', ''),
                'ineffectiveCopy': story.get('ineffective_copy_examples', ''),
                'informationGaps': story.get('information_gaps', ''),
                'trustAssessment': story.get('trust_credibility_assessment', ''),
                'businessImpact': story.get('business_impact_analysis', ''),
                'evidence': story.get('evidence', ''),
                'personaQuotes': persona_quotes,
            }
            success_stories.append(story_data)

        total_pages = len(filtered_df['page_id'].unique()) if 'page_id' in filtered_df.columns else len(filtered_df)
        success_pages = len(page_success)
        success_rate = (success_pages / total_pages * 100) if total_pages > 0 else 0
        avg_success_score = page_success['avg_score'].mean() if success_pages > 0 else 0

        excellent = len(page_success[page_success['avg_score'] >= 9.0])
        very_good = len(page_success[(page_success['avg_score'] >= 8.0) & (page_success['avg_score'] < 9.0)])
        good = len(page_success[(page_success['avg_score'] >= 7.5) & (page_success['avg_score'] < 8.0)])

        pattern_data: List[Dict[str, Any]] = []
        if 'tier' in success_df.columns:
            tier_patterns = success_df.groupby('tier').agg({'avg_score': 'mean', 'page_id': 'nunique'}).reset_index()
            for _, row in tier_patterns.iterrows():
                pattern_data.append({
                    'tier': row['tier'],
                    'avgScore': round(row['avg_score'], 1),
                    'count': int(row['page_id']),
                })

        evidence_items: List[Dict[str, Any]] = []
        for _, story in page_success.iterrows():
            page_title = self._create_friendly_page_title(story.get('page_id', 'Unknown'), story.get('url', ''))
            score = story.get('avg_score', 0)
            evidence_sources = {
                'Copy Examples': story.get('effective_copy_examples', ''),
                'Performance Data': story.get('business_impact_analysis', ''),
                'User Feedback': story.get('evidence', ''),
                'Trust Assessment': story.get('trust_credibility_assessment', ''),
            }
            for evidence_key, content in evidence_sources.items():
                if content and len(str(content).strip()) > 20:
                    content_str = str(content).strip()
                    if evidence_type != "All" and evidence_key != evidence_type:
                        continue
                    if search_term and search_term.lower() not in content_str.lower():
                        continue
                    evidence_items.append({
                        'type': evidence_key,
                        'content': content_str[:300] + '...' if len(content_str) > 300 else content_str,
                        'pageTitle': page_title,
                        'score': round(score, 1),
                    })

        replication_templates = [
            {
                'tier': pattern['tier'],
                'avgScore': pattern['avgScore'],
                'keyElements': [
                    'Focus on high-performing criteria patterns',
                    'Maintain consistent messaging tone',
                    'Implement proven design elements',
                    'Apply successful content structure',
                ],
            }
            for pattern in pattern_data
        ]

        personas = ['All'] + sorted(self.df['persona_id'].unique().tolist()) if 'persona_id' in self.df.columns else ['All']
        tiers = ['All'] + sorted([t for t in self.df['tier'].unique() if pd.notna(t)]) if 'tier' in self.df.columns else ['All']

        return {
            "successStories": success_stories,
            "overview": {
                "totalPages": total_pages,
                "successPages": success_pages,
                "successRate": round(success_rate, 1),
                "avgScore": round(avg_success_score, 1),
                "excellent": excellent,
                "veryGood": very_good,
                "good": good,
            },
            "patternData": pattern_data,
            "evidenceItems": evidence_items,
            "replicationTemplates": replication_templates,
            "personas": personas,
            "tiers": tiers,
        }

    def _extract_key_strengths(self, row: Any) -> List[str]:
        """Extract key strengths from a high-performing page"""
        strengths = []
        
        # Base strengths on evidence data and score, not on problematic fields
        score = row.get('raw_score', 0) or row.get('avg_score', 0) or row.get('final_score', 0)
        
        if score >= 9.0:
            strengths.append("Exceptional performance across all criteria")
        elif score >= 8.0:
            strengths.append("Strong performance with minor optimization opportunities")
        elif score >= 7.5:
            strengths.append("Good performance with room for improvement")
        
        # Check for evidence-based strengths
        evidence = row.get('evidence', '')
        if evidence and len(str(evidence)) > 50:
            strengths.append("Clear evidence of effective implementation")
        
        # If we have trust or business impact evidence, highlight those
        if row.get('trust_credibility_assessment') and len(str(row.get('trust_credibility_assessment', ''))) > 20:
            strengths.append("Strong trust and credibility indicators")
        
        if row.get('business_impact_analysis') and len(str(row.get('business_impact_analysis', ''))) > 20:
            strengths.append("Clear business impact and value proposition")
        
        if row.get('effective_copy_examples') and len(str(row.get('effective_copy_examples', ''))) > 20:
            strengths.append("Effective copy and messaging examples")
        
        return strengths[:3]  # Limit to top 3 strengths
    
    def _extract_page_level_strengths(self, row: Any) -> List[str]:
        """Extract key strengths from a page-level row"""
        strengths = []
        
        # Base strengths on evidence and score data, not on problematic fields
        score_val = row.get('raw_score', 0) or row.get('avg_score', 0)
        if score_val >= 9.0:
            strengths.append("Exceptional performance score")
        elif score_val >= 8.5:
            strengths.append("Strong performance score")
        
        # Check evidence for additional strengths
        evidence = str(row.get('evidence', '')).lower()
        if 'clear' in evidence and 'messaging' in evidence:
            strengths.append("Clear messaging and communication")
        if 'professional' in evidence or 'polished' in evidence:
            strengths.append("Professional presentation")
        if 'trust' in evidence and 'credible' in evidence:
            strengths.append("Strong trust and credibility")
        
        return strengths if strengths else ["High-performing page"]
    
    def _create_friendly_title(self, url_slug: str) -> str:
        """Create a user-friendly title from URL slug"""
        if not url_slug:
            return "Unknown Page"
        
        # Remove common prefixes
        title = url_slug.replace('www', '').replace('https', '').replace('http', '')
        
        # Handle specific patterns
        if 'soprasteria' in title:
            if 'newsroom' in title and 'blog' in title:
                if 'details' in title:
                    # Extract blog post title
                    parts = title.split('details')
                    if len(parts) > 1:
                        blog_title = parts[1].replace('-', ' ').title()
                        return f"Blog: {blog_title[:50]}..."
                return "Sopra Steria Blog"
            elif 'newsroom' in title and 'press-releases' in title:
                return "Press Release"
            elif 'industries' in title:
                if 'financial-services' in title:
                    return "Financial Services Industry Page"
                elif 'retail-logistics-telecom' in title:
                    return "Retail & Logistics Industry Page"
                return "Industry Page"
            elif 'whatwedo' in title:
                if 'data-ai' in title:
                    return "Data & AI Services"
                elif 'digital-themes' in title:
                    return "Digital Transformation Services"
                elif 'management-digital-transformation' in title:
                    return "Management Consulting"
                return "Services Page"
            elif 'about-us' in title:
                if 'history' in title:
                    return "Company History"
                elif 'corporate-responsibility' in title:
                    return "Corporate Responsibility"
                return "About Us"
            elif title.endswith('be'):
                return "Sopra Steria Belgium Homepage"
            elif title.endswith('nl'):
                return "Sopra Steria Netherlands Homepage"
            elif title.endswith('com'):
                return "Sopra Steria Global Homepage"
        elif 'linkedin' in title:
            return "LinkedIn Company Page"
        elif 'youtube' in title:
            return "YouTube Channel"
        elif 'nldigital' in title:
            return "NL Digital Directory"
        
        # Fallback: clean up the slug
        clean_title = title.replace('-', ' ').replace('_', ' ').title()
        return clean_title[:60] + "..." if len(clean_title) > 60 else clean_title

    @staticmethod
    def extract_persona_quotes_success(text: str) -> List[str]:
        """Extract persona voice quotes from success text"""
        if not text or pd.isna(text):
            return []

        quotes: List[str] = []
        text_str = str(text)

        quote_patterns = [
            r'"([^"]{20,200})"',
            r"'([^']{20,200})'",
            r'—([^—]{20,200})—',
            r'–([^–]{20,200})–',
        ]

        for pattern in quote_patterns:
            matches = re.findall(pattern, text_str)
            quotes.extend(matches[:2])

        return quotes[:5]
    
    def calculate_persona_comparison(self) -> pd.DataFrame:
        """Calculate metrics for persona comparison"""
        if 'persona_id' not in self.df.columns:
            return pd.DataFrame()
        
        # Find the correct score column - prioritize final_score for our data
        score_col = None
        for col in ['final_score', 'raw_score', 'raw_score']:
            if col in self.df.columns:
                score_col = col
                break
        
        if score_col is None:
            return pd.DataFrame()
        
        # Build aggregation dictionary dynamically based on available columns
        agg_dict = {
            score_col: ['mean', 'count']
        }
        
        # Add optional columns only if they exist and are numeric
        optional_cols = {
            'sentiment_numeric': 'mean'
        }
        
        for col, func in optional_cols.items():
            if col in self.df.columns:
                try:
                    # Check if column can be converted to numeric
                    pd.to_numeric(self.df[col], errors='coerce')
                    agg_dict[col] = func
                except:
                    pass
        
        # Calculate persona metrics
        persona_metrics = self.df.groupby('persona_id').agg(agg_dict).round(2)
        
        # Flatten multi-level columns if they exist
        if isinstance(persona_metrics.columns, pd.MultiIndex):
            persona_metrics.columns = ['_'.join(col).strip() for col in persona_metrics.columns.values]
        
        return persona_metrics
    
    def generate_executive_summary(self) -> Dict:
        """Generate executive summary metrics"""
        brand_health = self.calculate_brand_health_score()
        status, emoji = self.get_brand_health_status(brand_health)
        critical_issues = self.calculate_critical_issues()
        sentiment = self.calculate_sentiment_metrics()
        conversion = self.calculate_conversion_readiness()
        quick_wins = self.calculate_quick_wins()
        
        return {
            'brand_health': {
                'raw_score': round(brand_health, 1),
                'status': status,
                'emoji': emoji
            },
            'key_metrics': {
                'total_pages': len(self.df['page_id'].unique()) if 'page_id' in self.df.columns else len(self.df),
                'critical_issues': critical_issues['count'],
                'quick_wins': quick_wins['count'],
                'success_pages': self._calculate_success_pages()
            },
            'sentiment': sentiment,
            'conversion': conversion,
            'recommendations': self._generate_top_recommendations()
        }
    
    def _generate_top_recommendations(self) -> List[str]:
        """Generate top strategic recommendations"""
        recommendations = []
        
        # Use our dataset column names - prioritize final_score
        score_col = 'final_score' if 'final_score' in self.df.columns else 'raw_score'
        
        # Critical issues recommendation
        if score_col in self.df.columns:
            critical_count = len(self.df[self.df[score_col] < 4.0])
            if critical_count > 0:
                recommendations.append(f"Address {critical_count} critical pages scoring below 4.0")
        
        # Quick wins recommendation using quick_win_flag from unified dataset
        if 'quick_win_flag' in self.df.columns and score_col in self.df.columns:
            quick_wins = len(self.df[self.df['quick_win_flag'] == True])
            if quick_wins > 0:
                recommendations.append(f"Implement {quick_wins} quick wins for immediate impact")
            else:
                # Fallback: identify potential quick wins from score range
                potential_wins = len(self.df[(self.df[score_col] >= 4.0) & (self.df[score_col] < 7.0)])
                if potential_wins > 0:
                    recommendations.append(f"Focus on {potential_wins} moderate-scoring pages for quick improvements")
        elif score_col in self.df.columns:
            # Fallback: identify potential quick wins
            potential_wins = len(self.df[(self.df[score_col] >= 4.0) & (self.df[score_col] < 7.0)])
            if potential_wins > 0:
                recommendations.append(f"Focus on {potential_wins} moderate-scoring pages for quick improvements")
        
        # Persona-specific recommendation
        if 'persona_id' in self.df.columns and score_col in self.df.columns:
            persona_scores = self.df.groupby('persona_id')[score_col].mean()
            if len(persona_scores) > 1:
                worst_persona = persona_scores.idxmin()
                recommendations.append(f"Prioritize improvements for {worst_persona} persona (lowest scoring)")
        
        return recommendations[:3]  # Top 3 recommendations
    
    def _calculate_success_pages(self) -> int:
        """Calculate number of success pages (score >= 7.7)"""
        # Find the correct score column - prioritize final_score for our data
        score_col = None
        for col in ['final_score', 'raw_score', 'raw_score']:
            if col in self.df.columns:
                score_col = col
                break
        
        if score_col is None:
            return 0
        
        return len(self.df[self.df[score_col] >= 7.7])
    
    def calculate_distinctiveness_score(self) -> Dict:
        """Calculate distinctiveness using first_impression + brand_percentage + language_tone_feedback"""
        # Columns that contribute to distinctiveness
        distinctiveness_cols = ['first_impression', 'brand_percentage', 'language_tone_feedback']
        
        # Check which columns are available and have non-null data
        available_cols = []
        for col in distinctiveness_cols:
            if col in self.df.columns and not self.df[col].isna().all():
                available_cols.append(col)
        
        if not available_cols:
            # Fallback to overall score
            score_col = 'avg_score' if 'avg_score' in self.df.columns else 'raw_score'
            if score_col in self.df.columns:
                score = self.df[score_col].mean()
            else:
                score = 0.0
        else:
            # Calculate weighted average based on available columns
            scores = []
            
            # First impression (40% weight) - how unique/memorable is the first impression
            if 'first_impression' in available_cols:
                # Convert text to numeric if needed, otherwise use as-is
                if self.df['first_impression'].dtype == 'object':
                    # For text data, count positive keywords
                    first_impression_score = self._text_to_score(self.df['first_impression'], 
                                                               positive_keywords=['unique', 'distinct', 'memorable', 'standout', 'different'])
                else:
                    first_impression_score = self.df['first_impression'].dropna().mean()
                
                if not pd.isna(first_impression_score):
                    scores.append(('first_impression', first_impression_score, 0.4))
            
            # Brand percentage (30% weight) - how strongly branded is the content
            if 'brand_percentage' in available_cols:
                brand_score = self.df['brand_percentage'].dropna().mean()
                if not pd.isna(brand_score):
                    # Convert to 0-10 scale if it's a percentage
                    if brand_score > 10:
                        brand_score = brand_score / 10
                    scores.append(('brand_percentage', brand_score, 0.3))
            
            # Language tone feedback (30% weight) - is the tone distinctive
            if 'language_tone_feedback' in available_cols:
                if self.df['language_tone_feedback'].dtype == 'object':
                    tone_score = self._text_to_score(self.df['language_tone_feedback'],
                                                   positive_keywords=['distinctive', 'unique', 'compelling', 'engaging', 'memorable'])
                else:
                    tone_score = self.df['language_tone_feedback'].dropna().mean()
                
                if not pd.isna(tone_score):
                    scores.append(('language_tone_feedback', tone_score, 0.3))
            
            # Calculate weighted average
            if scores:
                total_weight = sum(weight for _, _, weight in scores)
                weighted_sum = sum(score * weight for _, score, weight in scores)
                score = weighted_sum / total_weight if total_weight > 0 else 0.0
            else:
                # Fallback to overall score if no valid components
                score_col = 'avg_score' if 'avg_score' in self.df.columns else 'raw_score'
                if score_col in self.df.columns:
                    score = self.df[score_col].mean()
                else:
                    score = 0.0
        
        # Determine status
        if score >= 7.0:
            status = "Strong"
        elif score >= 4.0:
            status = "Moderate"
        else:
            status = "Weak"
        
        return {
            'score': score,
            'status': status,
            'components': available_cols
        }
    
    def calculate_resonance_score(self) -> Dict:
        """Calculate resonance using sentiment_numeric + engagement_numeric + success_flag"""
        # Columns that contribute to resonance
        resonance_cols = ['sentiment_numeric', 'engagement_numeric', 'success_flag']
        
        # Check which columns are available
        available_cols = [col for col in resonance_cols if col in self.df.columns]
        
        if not available_cols:
            # Fallback to sentiment calculation
            return self.calculate_sentiment_metrics()
        
        scores = []
        
        # Sentiment numeric (50% weight) - how positive is the sentiment
        if 'sentiment_numeric' in self.df.columns:
            sentiment_score = self.df['sentiment_numeric'].mean()
            scores.append(('sentiment_numeric', sentiment_score, 0.5))
        
        # Engagement numeric (30% weight) - how engaging is the content
        if 'engagement_numeric' in self.df.columns:
            engagement_score = self.df['engagement_numeric'].mean()
            scores.append(('engagement_numeric', engagement_score, 0.3))
        
        # Success flag (20% weight) - proportion of successful pages
        if 'success_flag' in self.df.columns:
            success_rate = self.df['success_flag'].mean() * 10  # Convert to 0-10 scale
            scores.append(('success_flag', success_rate, 0.2))
        
        # Calculate weighted average
        if scores:
            total_weight = sum(weight for _, _, weight in scores)
            weighted_sum = sum(score * weight for _, score, weight in scores)
            score = weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            score = 0.0
        
        # Convert to percentage for net sentiment
        net_sentiment = (score / 10) * 100 if score > 0 else 0.0
        
        # Determine status
        if net_sentiment >= 60:
            status = "Positive"
        elif net_sentiment >= 40:
            status = "Neutral"
        else:
            status = "Negative"
        
        return {
            'net_sentiment': net_sentiment,
            'status': status,
            'components': available_cols
        }
    
    def calculate_conversion_score(self) -> Dict:
        """Calculate conversion using conversion_numeric + trust_credibility + performance_percentage"""
        # Columns that contribute to conversion
        conversion_cols = ['conversion_numeric', 'trust_credibility_assessment', 'performance_percentage']
        
        # Check which columns are available and have non-null data
        available_cols = []
        for col in conversion_cols:
            if col in self.df.columns and not self.df[col].isna().all():
                available_cols.append(col)
        
        if not available_cols:
            # Fallback to existing conversion readiness calculation
            return self.calculate_conversion_readiness()
        
        scores = []
        
        # Conversion numeric (50% weight) - direct conversion likelihood
        if 'conversion_numeric' in available_cols:
            conversion_score = self.df['conversion_numeric'].dropna().mean()
            if not pd.isna(conversion_score):
                scores.append(('conversion_numeric', conversion_score, 0.5))
        
        # Trust credibility assessment (30% weight) - how trustworthy/credible
        if 'trust_credibility_assessment' in available_cols:
            if self.df['trust_credibility_assessment'].dtype == 'object':
                trust_score = self._text_to_score(self.df['trust_credibility_assessment'],
                                                positive_keywords=['trustworthy', 'credible', 'reliable', 'authoritative', 'professional'])
            else:
                trust_score = self.df['trust_credibility_assessment'].dropna().mean()
            
            if not pd.isna(trust_score):
                scores.append(('trust_credibility_assessment', trust_score, 0.3))
        
        # Performance percentage (20% weight) - overall performance
        if 'performance_percentage' in available_cols:
            performance_score = self.df['performance_percentage'].dropna().mean()
            if not pd.isna(performance_score):
                # Convert to 0-10 scale if it's a percentage
                if performance_score > 10:
                    performance_score = performance_score / 10
                scores.append(('performance_percentage', performance_score, 0.2))
        
        # Calculate weighted average
        if scores:
            total_weight = sum(weight for _, _, weight in scores)
            weighted_sum = sum(score * weight for _, score, weight in scores)
            score = weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            # Fallback to existing conversion readiness calculation
            fallback = self.calculate_conversion_readiness()
            score = fallback.get('raw_score', 0.0)
        
        # Determine status
        if score >= 7.0:
            status = "High"
        elif score >= 5.0:
            status = "Medium"
        else:
            status = "Low"
        
        return {
            'score': score,
            'status': status,
            'components': available_cols
        }
    
    def _text_to_score(self, text_series: pd.Series, positive_keywords: List[str]) -> float:
        """Convert text series to numerical score based on positive keywords"""
        if text_series.empty:
            return 0.0
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text_series.str.lower()
        
        # Count positive keyword matches
        positive_count = 0
        for keyword in positive_keywords:
            positive_count += text_lower.str.contains(keyword, na=False).sum()
        
        # Calculate score (normalize by text length and keyword count)
        total_texts = len(text_series)
        if total_texts == 0:
            return 0.0
        
        # Score between 0-10 based on keyword density
        score = min(10, (positive_count / total_texts) * 10)
        return float(score)

    def calculate_strategic_themes(self) -> List[Dict]:
        """Generate strategic themes from real research data patterns"""
        themes = []
        
        # Brand & Messaging Strategy (based on real criterion patterns)
        if 'criterion_id' in self.df.columns and 'raw_score' in self.df.columns:
            branding_criteria = ['corporate_positioning_alignment', 'brand_differentiation', 'value_proposition_clarity']
            branding_mask = self.df['criterion_id'].isin(branding_criteria)
            branding_data = self.df[branding_mask]
            
            if len(branding_data) > 0:
                avg_score = float(branding_data['raw_score'].mean()) if pd.notna(branding_data['raw_score'].mean()) else 0
                # Extract real insights from business_impact_analysis field
                branding_insights = []
                if 'business_impact_analysis' in branding_data.columns:
                    impact_text = ' '.join(branding_data['business_impact_analysis'].dropna().astype(str))
                    if 'value proposition' in impact_text.lower():
                        branding_insights.append('Value proposition clarity gaps identified in research')
                    if 'brand' in impact_text.lower() and 'positioning' in impact_text.lower():
                        branding_insights.append('Brand positioning inconsistencies found across touchpoints')
                    if 'differentiation' in impact_text.lower():
                        branding_insights.append('Competitive differentiation opportunities identified')
                
                if not branding_insights:
                    branding_insights = ['Research shows brand messaging gaps across customer journey']
                    
                themes.append({
                    'id': 'brand_messaging',
                    'title': 'Brand & Messaging Strategy',
                    'description': 'Strengthen brand positioning and value proposition clarity',
                    'currentScore': round(avg_score, 1),
                    'targetScore': round(min(10, avg_score + 2.5), 1),
                    'businessImpact': 'High' if avg_score < 6 else 'Medium',
                    'affectedPages': len(branding_data),
                    'competitiveRisk': 'High' if avg_score < 6 else 'Medium' if avg_score < 7.5 else 'Low',
                    'keyInsights': branding_insights[:3],
                    'soWhat': f'Brand messaging gaps identified across {len(branding_data)} pages in research analysis.'
                })
        
        # User Experience & Trust (based on real criterion patterns)  
        if 'criterion_id' in self.df.columns and 'raw_score' in self.df.columns:
            trust_criteria = ['trust_credibility_signals', 'calltoaction_effectiveness']
            trust_mask = self.df['criterion_id'].isin(trust_criteria)
            trust_data = self.df[trust_mask]
            
            if len(trust_data) > 0:
                avg_score = float(trust_data['raw_score'].mean()) if pd.notna(trust_data['raw_score'].mean()) else 0
                # Extract real insights from research
                trust_insights = []
                if 'business_impact_analysis' in trust_data.columns:
                    impact_text = ' '.join(trust_data['business_impact_analysis'].dropna().astype(str))
                    if 'trust' in impact_text.lower():
                        trust_insights.append('Trust signal deficiencies identified in audit')
                    if 'credibility' in impact_text.lower():
                        trust_insights.append('Credibility markers need enhancement per research')
                    if 'call' in impact_text.lower() and 'action' in impact_text.lower():
                        trust_insights.append('Call-to-action effectiveness gaps found')
                        
                if not trust_insights:
                    trust_insights = ['Research identifies trust and credibility optimization opportunities']
                    
                themes.append({
                    'id': 'ux_trust',
                    'title': 'User Experience & Trust',
                    'description': 'Improve credibility and ease of use across all touchpoints',
                    'currentScore': round(avg_score, 1),
                    'targetScore': round(min(10, avg_score + 2), 1),
                    'businessImpact': 'High' if avg_score < 5 else 'Medium',
                    'affectedPages': len(trust_data),
                    'competitiveRisk': 'High' if avg_score < 5 else 'Medium' if avg_score < 7 else 'Low',
                    'keyInsights': trust_insights[:3],
                    'soWhat': f'Trust and UX issues found on {len(trust_data)} pages through systematic research.'
                })
        
        # Low Performance Pattern (based on real avg_score data)
        if 'avg_score' in self.df.columns:
            low_performing = self.df[self.df['avg_score'] < 6]
            if len(low_performing) > 0:
                avg_score = float(low_performing['avg_score'].mean()) if pd.notna(low_performing['avg_score'].mean()) else 0
                # Use real performance insights
                performance_insights = []
                if 'ineffective_copy_examples' in low_performing.columns:
                    ineffective_examples = low_performing['ineffective_copy_examples'].dropna()
                    if len(ineffective_examples) > 0:
                        performance_insights.append('Content performance gaps documented in research evidence')
                        
                if 'engagement_numeric' in low_performing.columns:
                    low_engagement = low_performing[low_performing['engagement_numeric'] < 5]
                    if len(low_engagement) > 0:
                        performance_insights.append('Low engagement patterns identified across multiple pages')
                        
                if not performance_insights:
                    performance_insights = ['Performance optimization opportunities identified in research']
                    
                themes.append({
                    'id': 'content_performance',
                    'title': 'Content Performance Optimization',
                    'description': 'Improve content effectiveness based on research findings',
                    'currentScore': round(avg_score, 1),
                    'targetScore': round(min(10, avg_score + 3), 1),
                    'businessImpact': 'Medium',
                    'affectedPages': len(low_performing),
                    'competitiveRisk': 'Medium',
                    'keyInsights': performance_insights[:3],
                    'soWhat': f'Research identifies performance improvement opportunities on {len(low_performing)} pages.'
                })
        
        return themes

    def calculate_business_recommendations(self, tier_filter: Optional[str] = None, 
                                         business_impact_filter: Optional[str] = None, 
                                         timeline_filter: Optional[str] = None) -> List[Dict]:
        """Generate business recommendations from real research data"""
        recommendations = []
        
        # Use real quick wins from research data
        if 'quick_win_flag' in self.df.columns:
            quick_wins = self.df[self.df['quick_win_flag'] == True]
            for _, row in quick_wins.head(10).iterrows():
                recommendations.append({
                    'id': f"qw_{row.get('page_id', 'unknown')}",
                    'title': f"Quick Win: {self._create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))}",
                    'description': row.get('effective_copy_examples', row.get('evidence', 'Research-based optimization opportunity')),
                    'businessImpact': 'Medium',
                    'implementationEffort': 'Low',  
                    'timeline': '0-30 days',
                    'tier': row.get('tier_name', row.get('tier', 'Unknown')),
                    'persona': row.get('persona_id', 'Multi-Persona'),
                    'currentScore': float(row.get('avg_score', 0)) if pd.notna(row.get('avg_score', 0)) else 0,
                    'targetScore': min(10, float(row.get('avg_score', 0)) + 2) if pd.notna(row.get('avg_score', 0)) else 8,
                    'evidence': row.get('evidence', 'Research findings available'),
                    'soWhat': row.get('business_impact_analysis', 'Improve brand performance and user engagement'),
                    'implementationSteps': [
                        'Apply effective copy examples from research',
                        'Implement trust signals identified in analysis', 
                        'Test and measure performance improvement'
                    ],
                    'success_metrics': ['Engagement Level', 'Conversion Likelihood', 'Brand Performance']
                })
        
        # Use real critical issues from research data  
        if 'critical_issue_flag' in self.df.columns:
            critical_issues = self.df[self.df['critical_issue_flag'] == True]
            for _, row in critical_issues.head(10).iterrows():
                recommendations.append({
                    'id': f"ci_{row.get('page_id', 'unknown')}",
                    'title': f"Critical Issue: {self._create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))}",
                    'description': row.get('ineffective_copy_examples', row.get('evidence', 'Critical performance gap identified')),
                    'businessImpact': 'High',
                    'implementationEffort': 'High',
                    'timeline': '30-90 days',
                    'tier': row.get('tier_name', row.get('tier', 'Unknown')),
                    'persona': row.get('persona_id', 'Multi-Persona'),
                    'currentScore': float(row.get('avg_score', 0)) if pd.notna(row.get('avg_score', 0)) else 0,
                    'targetScore': min(10, float(row.get('avg_score', 0)) + 4) if pd.notna(row.get('avg_score', 0)) else 8,
                    'evidence': row.get('evidence', 'Research findings available'),
                    'soWhat': row.get('business_impact_analysis', 'Address critical performance barriers'),
                    'implementationSteps': [
                        'Address ineffective copy patterns',
                        'Rebuild trust and credibility elements',
                        'Enhance value proposition clarity'
                    ],
                    'success_metrics': ['Brand Perception', 'Trust Indicators', 'Performance Score']
                })
        
        return recommendations

    def calculate_competitive_context(self) -> Dict:
        """Calculate competitive context and benchmarking"""
        if self.df.empty:
            return {'advantages': [], 'gaps': [], 'industryBenchmark': 7.2, 'overallPosition': 'At Market'}
        
        avg_score = self.df['avg_score'].mean() if 'avg_score' in self.df.columns else 0
        industry_benchmark = 7.2  # Industry average
        
        advantages = []
        gaps = []
        
        if avg_score > industry_benchmark + 0.5:
            advantages.append('Above-market brand health performance')
            position = 'Market Leader'
        elif avg_score > industry_benchmark:
            advantages.append('Competitive brand positioning')
            position = 'Above Market'
        elif avg_score > industry_benchmark - 0.5:
            gaps.append('Minor performance gaps vs. industry leaders')
            position = 'At Market'
        else:
            gaps.append('Significant competitive disadvantage')
            gaps.append('Risk of market share erosion')
            position = 'Below Market'
        
        # Identify specific competitive advantages
        if 'success_flag' in self.df.columns:
            success_count = len(self.df[self.df['success_flag'] == True])
            if success_count > len(self.df) * 0.3:
                advantages.append('Strong success story portfolio')
        
        # Identify specific gaps
        if 'critical_issue_flag' in self.df.columns:
            critical_count = len(self.df[self.df['critical_issue_flag'] == True])
            if critical_count > len(self.df) * 0.2:
                gaps.append('High number of critical brand issues')
        
        # Map position to what React expects
        if position in ['Market Leader', 'Above Market']:
            overall_position = 'Above Average'
        else:
            overall_position = 'Below Average'
        
        # Generate market opportunity message
        if avg_score > industry_benchmark:
            market_opportunity = f"Strong market position with {round(avg_score - industry_benchmark, 1)} point advantage"
        else:
            market_opportunity = f"Opportunity to close {round(industry_benchmark - avg_score, 1)} point gap with market leaders"
        
        return {
            'overallPosition': overall_position,
            'benchmarkScore': industry_benchmark,
            'currentScore': round(avg_score, 1),
            'competitiveGap': round(avg_score - industry_benchmark, 1),
            'advantages': advantages,
            'vulnerabilities': gaps,
            'marketOpportunity': market_opportunity
        }

    def calculate_strategic_tier_analysis(self) -> Dict:
        """Calculate tier-level performance analysis"""
        tier_analysis = {}
        
        if 'tier' in self.df.columns and 'avg_score' in self.df.columns:
            tier_mapping = {
                'tier_1': {'name': 'Strategic (Tier 1)', 'priority': 'Highest', 'impact': 'Board-level content, highest impact'},
                'tier_2': {'name': 'Tactical (Tier 2)', 'priority': 'High', 'impact': 'Campaign-level, medium impact'},
                'tier_3': {'name': 'Operational (Tier 3)', 'priority': 'Medium', 'impact': 'Conversion optimization, immediate fixes'}
            }
            
            for tier_key, tier_info in tier_mapping.items():
                tier_data = self.df[self.df['tier'] == tier_key]
                
                if len(tier_data) > 0:
                    avg_score = tier_data['avg_score'].mean()
                    critical_issues = len(tier_data[tier_data['critical_issue_flag'] == True]) if 'critical_issue_flag' in tier_data.columns else 0
                    quick_wins = len(tier_data[tier_data['quick_win_flag'] == True]) if 'quick_win_flag' in tier_data.columns else 0
                    
                    tier_analysis[tier_key] = {
                        'name': tier_info['name'],
                        'avgScore': round(avg_score, 1),
                        'pageCount': len(tier_data),
                        'criticalIssues': critical_issues,
                        'quickWins': quick_wins,
                        'priority': tier_info['priority'],
                        'businessContext': tier_info['impact']
                    }
        
        return tier_analysis

    def generate_implementation_roadmap(self, recommendations: List[Dict]) -> List[Dict]:
        """Generate phased implementation roadmap"""
        roadmap = []
        
        # Phase 1: 0-30 days (Quick Wins)
        phase_1_recs = [r for r in recommendations if r.get('timeline') == '0-30 days']
        if phase_1_recs:
            roadmap.append({
                'phase': '0-30 Days',
                'focus': 'Quick Wins & Critical Fixes',
                'recommendations': [r.get('title', 'Improvement') for r in phase_1_recs[:5]],
                'expectedImpact': 8.5,
                'keyMilestones': [
                    'Content optimization deployed',
                    'Quick wins implemented',
                    'Initial performance boost'
                ]
            })
        
        # Phase 2: 30-90 days (Strategic Improvements)
        phase_2_recs = [r for r in recommendations if r.get('timeline') == '30-90 days']
        if phase_2_recs:
            roadmap.append({
                'phase': '30-90 Days',
                'focus': 'Strategic Improvements',
                'recommendations': [r.get('title', 'Strategic improvement') for r in phase_2_recs[:5]],
                'expectedImpact': 7.2,
                'keyMilestones': [
                    'Brand messaging alignment',
                    'Tier 1 content enhanced',
                    'Competitive positioning strengthened'
                ]
            })
        
        # Phase 3: 90+ days (Long-term Transformation)
        phase_3_recs = [r for r in recommendations if r.get('timeline', '').startswith('90+')]
        high_impact_recs = [r for r in recommendations if r.get('businessImpact') == 'High']
        roadmap.append({
            'phase': '90+ Days',
            'focus': 'Long-term Transformation',
            'recommendations': [r.get('title', 'Strategic initiative') for r in (phase_3_recs or high_impact_recs)[:5]],
            'expectedImpact': 6.8,
            'keyMilestones': [
                'Full brand health optimization',
                'Market leadership position',
                'Sustainable competitive advantage'
            ]
        })
        
        return roadmap

    def _create_friendly_page_title(self, page_id: str, url: str) -> str:
        """Create user-friendly page title from page_id and URL"""
        if not page_id:
            return "Unknown Page"
        
        # Remove common prefixes and clean up
        title = page_id.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())
        
        # Add URL context if available
        if url and 'www.' in url:
            domain_part = url.split('www.')[1].split('/')[0] if 'www.' in url else ''
            if domain_part:
                title = f"{title} ({domain_part})"
        
        return title

    def calculate_strategic_intelligence(self, tier_filter: Optional[str] = None,
                                       business_impact_filter: Optional[str] = None,
                                       timeline_filter: Optional[str] = None) -> Dict:
        """Calculate comprehensive strategic intelligence metrics"""
        
        # Calculate basic metrics
        avg_score = self.df['avg_score'].mean() if 'avg_score' in self.df.columns else 0
        if pd.isna(avg_score):
            avg_score = 0
        
        critical_issues = len(self.df[self.df['critical_issue_flag'] == True]) if 'critical_issue_flag' in self.df.columns else 0
        quick_wins = len(self.df[self.df['quick_win_flag'] == True]) if 'quick_win_flag' in self.df.columns else 0
        success_stories = len(self.df[self.df['success_flag'] == True]) if 'success_flag' in self.df.columns else 0
        
        # Calculate research-based performance metrics
        performance_gap = round(max(0, 7.5 - avg_score), 1) if not pd.isna(avg_score) else 0
        optimization_potential = quick_wins  # Number of quick wins available
        improvement_areas = critical_issues  # Number of critical issues to address
        
        # Generate strategic insights
        strategic_themes = self.calculate_strategic_themes()
        business_recommendations = self.calculate_business_recommendations(tier_filter, business_impact_filter, timeline_filter)
        competitive_context = self.calculate_competitive_context()
        tier_analysis = self.calculate_strategic_tier_analysis()
        implementation_roadmap = self.generate_implementation_roadmap(business_recommendations)
        
        return {
            "executiveSummary": {
                "totalRecommendations": len(business_recommendations),
                "highImpactOpportunities": len([r for r in business_recommendations if r.get('businessImpact') == 'High']),
                "quickWinOpportunities": quick_wins,
                "criticalIssues": critical_issues,
                "overallScore": round(avg_score, 2)
            },
            "strategicThemes": strategic_themes,
            "businessImpact": {
                "optimizationPotential": optimization_potential,
                "improvementAreas": improvement_areas,
                "competitiveAdvantage": competitive_context.get('advantages', []),
                "successStories": [f"Pages with success flag: {success_stories}", f"Average score: {avg_score:.1f}/10"]
            },
            "recommendations": business_recommendations,
            "tierAnalysis": tier_analysis,
            "competitiveContext": competitive_context,
            "implementationRoadmap": implementation_roadmap
        }

    # ------------------------------------------------------------------
    # Report Generation Methods (moved from fastapi_service.main)
    # ------------------------------------------------------------------

    def generate_executive_summary_report(self) -> Dict[str, Any]:
        """Generate executive summary report"""
        df = self.df
        if df.empty:
            return {"error": "No data available for executive summary"}

        try:
            total_records = len(df)
            unique_pages = df['page_id'].nunique() if 'page_id' in df.columns else 0
            avg_score = df['final_score'].mean() if 'final_score' in df.columns else 0

            critical_issues = len(df[df['descriptor'] == 'CRITICAL']) if 'descriptor' in df.columns else 0
            concerns = len(df[df['descriptor'] == 'CONCERN']) if 'descriptor' in df.columns else 0
            warnings = len(df[df['descriptor'] == 'WARN']) if 'descriptor' in df.columns else 0
            good_scores = len(df[df['descriptor'] == 'GOOD']) if 'descriptor' in df.columns else 0

            top_issues: List[Dict[str, Any]] = []
            if 'criterion_id' in df.columns and 'final_score' in df.columns:
                low_scoring = df[df['final_score'] < 6].groupby('criterion_id')['final_score'].mean().sort_values().head(5)
                for criterion, score in low_scoring.items():
                    top_issues.append({
                        'criterion': criterion.replace('_', ' ').title(),
                        'score': round(score, 1)
                    })

            return {
                'type': 'Executive Summary Report',
                'generated_date': datetime.now().isoformat(),
                'metrics': {
                    'total_records': total_records,
                    'unique_pages': unique_pages,
                    'average_score': round(avg_score, 1),
                    'critical_issues': critical_issues,
                    'concerns': concerns,
                    'warnings': warnings,
                    'good_scores': good_scores
                },
                'top_issues': top_issues,
                'summary': (
                    f"Analyzed {total_records:,} records across {unique_pages:,} pages "
                    f"with an average score of {avg_score:.1f}/10. Found {critical_issues} critical issues "
                    f"and {concerns} concerns."
                )
            }
        except Exception as e:  # pragma: no cover - safeguard
            return {'error': f'Error generating executive summary: {str(e)}'}

    def generate_persona_performance_report(self) -> Dict[str, Any]:
        """Generate persona performance report"""
        df = self.df
        if df.empty or 'persona_id' not in df.columns:
            return {'error': 'No persona data available'}

        try:
            persona_perf = df.groupby('persona_id').agg({
                'avg_score': ['mean', 'count'],
                'final_score': 'mean'
            }).round(2)

            persona_perf.columns = ['avg_score_mean', 'page_count', 'final_score_mean']
            persona_perf = persona_perf.sort_values('avg_score_mean', ascending=False)

            personas: List[Dict[str, Any]] = []
            for persona_id, row in persona_perf.iterrows():
                personas.append({
                    'persona_id': persona_id,
                    'average_score': row['avg_score_mean'],
                    'page_count': row['page_count'],
                    'final_score': row['final_score_mean']
                })

            best_persona = personas[0]['persona_id'] if personas else 'Unknown'
            worst_persona = personas[-1]['persona_id'] if personas else 'Unknown'

            return {
                'type': 'Persona Performance Report',
                'generated_date': datetime.now().isoformat(),
                'personas': personas,
                'insights': {
                    'best_performing': best_persona,
                    'needs_attention': worst_persona,
                    'total_personas': len(personas)
                }
            }
        except Exception as e:  # pragma: no cover - safeguard
            return {'error': f'Error generating persona performance report: {str(e)}'}

    def generate_content_tier_report(self) -> Dict[str, Any]:
        """Generate content tier analysis report"""
        df = self.df
        if df.empty or 'tier' not in df.columns:
            return {'error': 'No tier data available'}

        try:
            tier_perf = df.groupby('tier').agg({
                'avg_score': ['mean', 'count', 'std'],
                'final_score': 'mean'
            }).round(2)
            tier_perf.columns = ['avg_score_mean', 'page_count', 'score_variation', 'final_score_mean']
            tier_perf = tier_perf.sort_values('avg_score_mean', ascending=False)

            tiers: List[Dict[str, Any]] = []
            for tier_name, row in tier_perf.iterrows():
                tiers.append({
                    'tier_name': tier_name,
                    'average_score': row['avg_score_mean'],
                    'page_count': row['page_count'],
                    'score_variation': row['score_variation'],
                    'final_score': row['final_score_mean']
                })

            return {
                'type': 'Content Tier Analysis Report',
                'generated_date': datetime.now().isoformat(),
                'tiers': tiers,
                'insights': {
                    'total_tiers': len(tiers),
                    'best_performing_tier': tiers[0]['tier_name'] if tiers else 'Unknown',
                    'most_variable_tier': max(tiers, key=lambda x: x['score_variation'])['tier_name'] if tiers else 'Unknown'
                }
            }
        except Exception as e:  # pragma: no cover - safeguard
            return {'error': f'Error generating content tier report: {str(e)}'}

    def generate_success_stories_report(self) -> Dict[str, Any]:
        """Generate success stories report"""
        df = self.df
        if df.empty or 'final_score' not in df.columns:
            return {'error': 'No score data available for success stories'}

        try:
            success_threshold = 7.5
            success_stories = df[df['final_score'] >= success_threshold]

            if success_stories.empty:
                max_score = df['final_score'].max()
                return {
                    'type': 'Success Stories Report',
                    'generated_date': datetime.now().isoformat(),
                    'success_stories': [],
                    'message': f'No pages found with score ≥ {success_threshold}. Highest score: {max_score:.1f}'
                }

            if 'page_id' in success_stories.columns and 'url' in success_stories.columns:
                page_scores = success_stories.groupby(['page_id', 'url'])['final_score'].mean().sort_values(ascending=False).head(10)

                stories = []
                for i, ((page_id, url), score) in enumerate(page_scores.items(), 1):
                    page_data = success_stories[success_stories['page_id'] == page_id].iloc[0]
                    tier = page_data.get('tier_name', 'Unknown') if 'tier_name' in page_data else 'Unknown'
                    stories.append({
                        'rank': i,
                        'page_id': page_id,
                        'url': url[:100] + '...' if len(url) > 100 else url,
                        'score': round(score, 1),
                        'tier': tier
                    })
            else:
                stories = []
                for i, (_, story) in enumerate(success_stories.head(5).iterrows(), 1):
                    stories.append({
                        'rank': i,
                        'page_id': story.get('page_id', 'Unknown'),
                        'score': round(story['final_score'], 1),
                        'tier': story.get('tier_name', 'Unknown')
                    })

            return {
                'type': 'Success Stories Report',
                'generated_date': datetime.now().isoformat(),
                'success_stories': stories,
                'summary': f'Found {len(success_stories)} success stories with score ≥ {success_threshold}',
                'threshold': success_threshold
            }
        except Exception as e:  # pragma: no cover - safeguard
            return {'error': f'Error generating success stories report: {str(e)}'}

    # ------------------------------------------------------------------
    # Persona Voice & Copy Analysis Methods
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_segments(text: str) -> str:
        """Advanced content deduplication"""
        if not text or pd.isna(text):
            return ""

        segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
        unique_segments: List[str] = []
        seen: set[str] = set()

        for segment in segments:
            simplified = re.sub(r'"[^"]*"', '[QUOTE]', segment.lower())
            if simplified not in seen:
                seen.add(simplified)
                unique_segments.append(segment)

        return ' | '.join(unique_segments)

    @staticmethod
    def _deduplicate_business_analysis(text: str) -> str:
        """Less aggressive deduplication for business analysis"""
        if not text or pd.isna(text):
            return ""

        segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]
        unique_segments: List[str] = []
        seen: set[str] = set()

        for segment in segments:
            comparison_key = segment[:100].lower().strip()
            if comparison_key not in seen and len(segment) > 30:
                seen.add(comparison_key)
                unique_segments.append(segment)

        return ' | '.join(unique_segments)

    @staticmethod
    def _create_friendly_page_title(page_id: str, url: str) -> str:
        """Create user-friendly page title"""
        if not page_id:
            return "Unknown Page"

        title = page_id.replace('_', ' ').replace('-', ' ')
        title = ' '.join(word.capitalize() for word in title.split())

        if url:
            lower_url = url.lower()
            if 'newsroom' in lower_url:
                title = f"Newsroom > {title}"
            elif 'blog' in lower_url:
                title = f"Blog > {title}"
            elif 'about' in lower_url:
                title = f"About > {title}"
            elif 'services' in lower_url:
                title = f"Services > {title}"
            elif 'industries' in lower_url:
                title = f"Industries > {title}"
            elif 'company' in lower_url:
                title = f"Company > {title}"

        return title

    @staticmethod
    def calculate_voice_stats(persona_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate voice data completeness statistics"""
        if persona_data.empty:
            return {
                "total_entries": 0,
                "effective_copy_examples": {"populated": 0, "total": 0, "percentage": 0},
                "ineffective_copy_examples": {"populated": 0, "total": 0, "percentage": 0},
                "business_impact_analysis": {"populated": 0, "total": 0, "percentage": 0}
            }

        total_entries = len(persona_data)
        effective_populated = persona_data['effective_copy_examples'].notna().sum() if 'effective_copy_examples' in persona_data.columns else 0
        ineffective_populated = persona_data['ineffective_copy_examples'].notna().sum() if 'ineffective_copy_examples' in persona_data.columns else 0
        business_populated = persona_data['business_impact_analysis'].notna().sum() if 'business_impact_analysis' in persona_data.columns else 0

        return {
            "total_entries": int(total_entries),
            "effective_copy_examples": {
                "populated": int(effective_populated),
                "total": int(total_entries),
                "percentage": float((effective_populated / total_entries) * 100) if total_entries > 0 else 0
            },
            "ineffective_copy_examples": {
                "populated": int(ineffective_populated),
                "total": int(total_entries),
                "percentage": float((ineffective_populated / total_entries) * 100) if total_entries > 0 else 0
            },
            "business_impact_analysis": {
                "populated": int(business_populated),
                "total": int(total_entries),
                "percentage": float((business_populated / total_entries) * 100) if total_entries > 0 else 0
            }
        }

    @classmethod
    def process_effective_copy_examples(cls, persona_data: pd.DataFrame) -> Dict[str, Any]:
        """Process and analyze effective copy examples"""
        if 'effective_copy_examples' not in persona_data.columns:
            return {"pages": [], "total_examples": 0}

        data_with_examples = persona_data[
            persona_data['effective_copy_examples'].notna() &
            (persona_data['effective_copy_examples'].str.len() > 10)
        ].copy()

        if data_with_examples.empty:
            return {"pages": [], "total_examples": 0}

        page_aggregated = data_with_examples.groupby(['url']).agg({
            'effective_copy_examples': lambda x: ' | '.join(x.drop_duplicates().dropna().astype(str)),
            'avg_score': 'mean',
            'page_id': 'first',
            'tier_name': 'first'
        }).reset_index()

        page_aggregated['effective_copy_examples'] = page_aggregated['effective_copy_examples'].apply(cls._deduplicate_segments)
        page_aggregated = page_aggregated[page_aggregated['effective_copy_examples'].str.len() > 20]

        processed_pages: List[Dict[str, Any]] = []
        for _, row in page_aggregated.iterrows():
            page_title = cls._create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))
            examples = cls.process_voice_examples(row.get('effective_copy_examples', ''))

            processed_pages.append({
                "page_title": page_title,
                "url": row.get('url', ''),
                "tier_name": row.get('tier_name', 'Unknown'),
                "avg_score": float(row.get('avg_score', 0)),
                "examples": examples
            })

        return {
            "pages": processed_pages,
            "total_examples": len(processed_pages)
        }

    @classmethod
    def process_ineffective_copy_examples(cls, persona_data: pd.DataFrame) -> Dict[str, Any]:
        """Process and analyze ineffective copy examples"""
        if 'ineffective_copy_examples' not in persona_data.columns:
            return {"pages": [], "total_examples": 0}

        data_with_issues = persona_data[
            persona_data['ineffective_copy_examples'].notna() &
            (persona_data['ineffective_copy_examples'].str.len() > 10)
        ].copy()

        if data_with_issues.empty:
            return {"pages": [], "total_examples": 0}

        page_aggregated = data_with_issues.groupby(['url']).agg({
            'ineffective_copy_examples': lambda x: ' | '.join(x.drop_duplicates().dropna().astype(str)),
            'avg_score': 'mean',
            'page_id': 'first',
            'tier_name': 'first'
        }).reset_index()

        page_aggregated['ineffective_copy_examples'] = page_aggregated['ineffective_copy_examples'].apply(cls._deduplicate_segments)
        page_aggregated = page_aggregated[page_aggregated['ineffective_copy_examples'].str.len() > 20]

        processed_pages: List[Dict[str, Any]] = []
        for _, row in page_aggregated.iterrows():
            page_title = cls._create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))
            examples = cls.process_voice_examples(row.get('ineffective_copy_examples', ''))

            processed_pages.append({
                "page_title": page_title,
                "url": row.get('url', ''),
                "tier_name": row.get('tier_name', 'Unknown'),
                "avg_score": float(row.get('avg_score', 0)),
                "examples": examples
            })

        return {
            "pages": processed_pages,
            "total_examples": len(processed_pages)
        }

    @classmethod
    def process_business_impact_analysis(cls, persona_data: pd.DataFrame) -> Dict[str, Any]:
        """Process strategic business impact analysis"""
        if 'business_impact_analysis' not in persona_data.columns:
            return {"pages": [], "total_insights": 0}

        data_with_analysis = persona_data[
            persona_data['business_impact_analysis'].notna() &
            (persona_data['business_impact_analysis'].astype(str).str.len() > 5)
        ].copy()

        if data_with_analysis.empty:
            return {"pages": [], "total_insights": 0}

        page_aggregated = data_with_analysis.groupby(['url']).agg({
            'business_impact_analysis': lambda x: ' | '.join(x.dropna().astype(str)),
            'avg_score': 'mean',
            'page_id': 'first',
            'tier_name': 'first'
        }).reset_index()

        page_aggregated['business_impact_analysis'] = page_aggregated['business_impact_analysis'].apply(cls._deduplicate_business_analysis)

        page_aggregated = page_aggregated[
            (page_aggregated['business_impact_analysis'].astype(str).str.len() > 5) &
            (page_aggregated['business_impact_analysis'] != '') &
            (page_aggregated['business_impact_analysis'] != 'nan')
        ]

        processed_pages: List[Dict[str, Any]] = []
        for _, row in page_aggregated.iterrows():
            page_title = cls._create_friendly_page_title(row.get('page_id', ''), row.get('url', ''))
            insights = cls.process_business_insights(row.get('business_impact_analysis', ''))

            processed_pages.append({
                "page_title": page_title,
                "url": row.get('url', ''),
                "tier_name": row.get('tier_name', 'Unknown'),
                "avg_score": float(row.get('avg_score', 0)),
                "insights": insights
            })

        return {
            "pages": processed_pages,
            "total_insights": len(processed_pages)
        }

    @staticmethod
    def process_voice_examples(text: str) -> List[Dict[str, str]]:
        """Process voice examples and extract quotes with analysis"""
        if not text or pd.isna(text):
            return []

        examples: List[Dict[str, str]] = []
        segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]

        for segment in segments:
            quoted_copy = re.findall(r'"([^"]{10,})"', segment)
            if quoted_copy:
                for quote in quoted_copy:
                    analysis_parts = segment.split(f'"{quote}"')
                    analysis_text = ""
                    if len(analysis_parts) > 1:
                        analysis_text = analysis_parts[1].strip()
                        if analysis_text.startswith(':'):
                            analysis_text = analysis_text[1:].strip()

                    examples.append({
                        "type": "quoted_copy",
                        "quote": quote,
                        "analysis": analysis_text or "Analysis not available"
                    })
            else:
                examples.append({
                    "type": "persona_insight",
                    "quote": "",
                    "analysis": segment
                })

        return examples

    @staticmethod
    def process_business_insights(text: str) -> List[Dict[str, str]]:
        """Process business impact insights"""
        if not text or pd.isna(text):
            return []

        insights: List[Dict[str, str]] = []
        segments = [seg.strip() for seg in str(text).split(' | ') if seg.strip()]

        for segment in segments:
            insights.append({
                "type": "strategic_insight",
                "content": segment
            })

        return insights

    @staticmethod
    def generate_copy_ready_quotes(persona_data: pd.DataFrame) -> Dict[str, List[str]]:
        """Generate copy-ready persona quotes categorized by type"""
        quotes: Dict[str, List[str]] = {'positive': [], 'negative': [], 'strategic': []}

        # Extract from effective examples
        if 'effective_copy_examples' in persona_data.columns:
            for text in persona_data['effective_copy_examples'].dropna():
                if text and not pd.isna(text):
                    text_str = str(text)
                    persona_statements = re.findall(r'As a[^.]*\.', text_str, re.IGNORECASE)
                    quotes['positive'].extend(persona_statements)

        if 'ineffective_copy_examples' in persona_data.columns:
            for text in persona_data['ineffective_copy_examples'].dropna():
                if text and not pd.isna(text):
                    text_str = str(text)
                    persona_statements = re.findall(r'As a[^.]*\.', text_str, re.IGNORECASE)
                    quotes['negative'].extend(persona_statements)

        if 'business_impact_analysis' in persona_data.columns:
            for text in persona_data['business_impact_analysis'].dropna():
                if text and not pd.isna(text):
                    text_str = str(text)
                    strategic_statements = re.findall(r'[^.]*recommend[^.]*\.', text_str, re.IGNORECASE)
                    quotes['strategic'].extend(strategic_statements)

        for category in quotes:
            quotes[category] = list(set([q.strip() for q in quotes[category] if len(q.strip()) > 30]))[:5]

        return quotes

    # ------------------------------------------------------------------
    # Social Media Calculation Methods
    # ------------------------------------------------------------------

    @staticmethod
    def calculate_platform_metrics(social_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate comprehensive platform metrics"""
        platform_stats: List[Dict[str, Any]] = []

        for platform in social_df['platform_display'].unique():
            platform_data = social_df[social_df['platform_display'] == platform]
            if len(platform_data) == 0:
                continue

            avg_score = platform_data['avg_score'].mean()
            score_range = f"{platform_data['avg_score'].min():.1f} - {platform_data['avg_score'].max():.1f}"

            if avg_score >= 7:
                status = "✅ Strong"
                status_color = "success"
            elif avg_score >= 5:
                status = "⚠️ Moderate"
                status_color = "warning"
            elif avg_score >= 3:
                status = "🟠 At Risk"
                status_color = "warning"
            else:
                status = "🔴 Critical"
                status_color = "error"

            high_performers = len(platform_data[platform_data['avg_score'] >= 7])
            moderate_performers = len(platform_data[(platform_data['avg_score'] >= 5) & (platform_data['avg_score'] < 7)])
            low_performers = len(platform_data[platform_data['avg_score'] < 5])

            avg_engagement = platform_data['engagement_numeric'].mean()
            avg_sentiment = platform_data['sentiment_numeric'].mean()

            platform_stats.append({
                'Platform': platform,
                'Platform_Code': platform_data['platform'].iloc[0],
                'Average_Score': float(avg_score),
                'Score_Range': score_range,
                'Status': status,
                'Status_Color': status_color,
                'Total_Entries': len(platform_data),
                'High_Performers': int(high_performers),
                'Moderate_Performers': int(moderate_performers),
                'Low_Performers': int(low_performers),
                'Avg_Engagement': float(avg_engagement),
                'Avg_Sentiment': float(avg_sentiment),
                'Critical_Issues': int(len(platform_data[platform_data['critical_issue_flag'] == True])),
                'Success_Cases': int(len(platform_data[platform_data['success_flag'] == True])),
                'Quick_Wins': int(len(platform_data[platform_data['quick_win_flag'] == True]))
            })

        return platform_stats

    @staticmethod
    def generate_social_media_insights(social_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate key insights from social media data"""
        insights: List[Dict[str, Any]] = []

        overall_avg = social_df['avg_score'].mean()
        insights.append({
            'Category': 'Overall Performance',
            'Insight': f'Average social media score across all platforms and personas is {overall_avg:.1f}/10',
            'Type': 'metric'
        })

        platform_avgs = social_df.groupby('platform_display')['avg_score'].mean().sort_values(ascending=False)
        if len(platform_avgs) > 0:
            best_platform = platform_avgs.index[0]
            best_score = float(platform_avgs.iloc[0])
            insights.append({
                'Category': 'Top Performer',
                'Insight': f'{best_platform} is the strongest platform with {best_score:.1f}/10 average score',
                'Type': 'success'
            })

            worst_platform = platform_avgs.index[-1]
            worst_score = float(platform_avgs.iloc[-1])
            insights.append({
                'Category': 'Needs Attention',
                'Insight': f'{worst_platform} requires review with {worst_score:.1f}/10 average score',
                'Type': 'warning'
            })

        critical_count = len(social_df[social_df['critical_issue_flag'] == True])
        if critical_count > 0:
            insights.append({
                'Category': 'Critical Issues',
                'Insight': f'{critical_count} entries flagged as critical issues requiring immediate action',
                'Type': 'warning'
            })

        quick_wins = len(social_df[social_df['quick_win_flag'] == True])
        if quick_wins > 0:
            insights.append({
                'Category': 'Quick Wins',
                'Insight': f'{quick_wins} opportunities identified for quick improvement',
                'Type': 'opportunity'
            })

        if len(social_df) > 1:
            correlation = social_df['engagement_numeric'].corr(social_df['avg_score'])
            if pd.notna(correlation):
                strength = 'Strong' if abs(correlation) > 0.7 else 'Moderate' if abs(correlation) > 0.4 else 'Weak'
                insights.append({
                    'Category': 'Engagement Correlation',
                    'Insight': f'Engagement and performance correlation: {correlation:.2f} ({strength})',
                    'Type': 'metric'
                })

        return insights

    @staticmethod
    def generate_social_media_recommendations(social_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate actionable recommendations from social media data"""
        recommendations: List[Dict[str, Any]] = []

        for platform in social_df['platform_display'].unique():
            platform_data = social_df[social_df['platform_display'] == platform]
            avg_score = platform_data['avg_score'].mean()

            if avg_score < 3:
                priority = 'High'
                recommendations.append({
                    'Platform': platform,
                    'Priority': priority,
                    'Category': 'Critical Revival',
                    'Recommendation': f'Immediate reactivation required for {platform}. Current score of {avg_score:.1f}/10 indicates platform abandonment.',
                    'Impact': 'High',
                    'Timeline': '0-30 days'
                })
            elif avg_score < 5:
                priority = 'High'
                recommendations.append({
                    'Platform': platform,
                    'Priority': priority,
                    'Category': 'Strategic Improvement',
                    'Recommendation': f'Comprehensive content strategy needed for {platform}. Score of {avg_score:.1f}/10 shows underperformance.',
                    'Impact': 'Medium',
                    'Timeline': '1-3 months'
                })
            elif avg_score < 7:
                priority = 'Medium'
                recommendations.append({
                    'Platform': platform,
                    'Priority': priority,
                    'Category': 'Optimization',
                    'Recommendation': f'Enhance content quality and persona targeting for {platform}. Current score: {avg_score:.1f}/10.',
                    'Impact': 'Medium',
                    'Timeline': '1-3 months'
                })

        persona_performance = social_df.groupby('persona_clean')['avg_score'].mean().sort_values()
        if len(persona_performance) > 0:
            worst_persona = persona_performance.index[0]
            worst_persona_score = float(persona_performance.iloc[0])
            recommendations.append({
                'Platform': 'Cross-Platform',
                'Priority': 'High',
                'Category': 'Persona Strategy',
                'Recommendation': f'Develop targeted content strategy for {worst_persona} (avg score: {worst_persona_score:.1f}/10)',
                'Impact': 'High',
                'Timeline': '1-2 months'
            })

        quick_wins = social_df[social_df['quick_win_flag'] == True]
        if len(quick_wins) > 0:
            recommendations.append({
                'Platform': 'Cross-Platform',
                'Priority': 'Medium',
                'Category': 'Quick Wins',
                'Recommendation': f'Focus on {len(quick_wins)} identified quick win opportunities for immediate improvement',
                'Impact': 'Medium',
                'Timeline': '0-30 days'
            })

        return recommendations

    @staticmethod
    def calculate_persona_platform_matrix(social_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate persona-platform performance matrix for heatmap"""
        try:
            matrix = social_df.pivot_table(
                values='avg_score',
                index='persona_clean',
                columns='platform_display',
                aggfunc='mean'
            ).fillna(0)

            matrix_data: List[Dict[str, Any]] = []
            for persona in matrix.index:
                for platform in matrix.columns:
                    score = matrix.loc[persona, platform]
                    if score > 0:
                        matrix_data.append({
                            'persona': persona,
                            'platform': platform,
                            'score': float(score)
                        })

            return matrix_data
        except Exception:
            return []
