"""
Metrics Calculator for Brand Health Command Center
Handles all derived metrics and KPI calculations
"""

import pandas as pd
import numpy as np
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
            return self.df['raw_score'].mean()
        elif 'final_score' in self.df.columns:
            return self.df['final_score'].mean()
        elif 'raw_score' in self.df.columns:
            return self.df['raw_score'].mean()
        
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
            url_slug = row.get('url_slug', '')
            page_title = self._create_friendly_title(url_slug)
            
            # Calculate effort level based on current score
            current_score = row.get(score_col, 0)
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
                'potential_impact': round(row.get('opportunity_impact', 0), 1),
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
        top_success = page_success.nlargest(5, score_col)
        
        result = []
        for _, row in top_success.iterrows():
            # Create a friendly page title from URL slug
            url_slug = row.get('url_slug', '')
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
        """Convert text feedback to numeric score based on positive keywords"""
        if text_series.empty:
            return 0.0
        
        # Count positive mentions across all text entries
        total_positive = 0
        total_entries = 0
        
        for text in text_series.dropna():
            if isinstance(text, str):
                text_lower = text.lower()
                positive_count = sum(1 for keyword in positive_keywords if keyword in text_lower)
                # Score based on keyword density (0-10 scale)
                entry_score = min(positive_count * 2, 10)  # Cap at 10
                total_positive += entry_score
                total_entries += 1
        
        return total_positive / total_entries if total_entries > 0 else 0.0 