"""
Metrics Calculator for Brand Health Command Center
Handles all derived metrics and KPI calculations
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class BrandHealthMetricsCalculator:
    """Calculate brand health metrics and KPIs"""
    
    def __init__(self, df: pd.DataFrame, recommendations_df: pd.DataFrame = None):
        self.df = df
        self.recommendations_df = recommendations_df
        self.validate_data()
    
    def validate_data(self):
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
        # Use the correct column name from our data structure
        sentiment_col = 'overall_sentiment' if 'overall_sentiment' in self.df.columns else 'sentiment'
        
        if sentiment_col not in self.df.columns:
            return {'positive': 0, 'neutral': 0, 'negative': 0, 'net_sentiment': 0}
        
        sentiment_counts = self.df[sentiment_col].value_counts(normalize=True) * 100
        
        return {
            'positive': sentiment_counts.get('Positive', 0),
            'neutral': sentiment_counts.get('Neutral', 0),
            'negative': sentiment_counts.get('Negative', 0),
            'net_sentiment': sentiment_counts.get('Positive', 0) - sentiment_counts.get('Negative', 0)
        }
    
    def calculate_conversion_readiness(self) -> Dict:
        """Calculate conversion readiness metrics"""
        # Define conversion-related columns and their priorities
        conversion_cols = ['conversion_likelihood', 'engagement', 'trust_credibility_signals', 'calltoaction_effectiveness']
        
        # Check what columns are actually available
        available_cols = [col for col in conversion_cols if col in self.df.columns]
        
        # If no specific conversion columns, use score-based approach
        if not available_cols:
            # Use the main score column (either 'final_score', 'raw_score', or 'raw_score')
            score_col = None
            for col in ['final_score', 'raw_score', 'raw_score']:
                if col in self.df.columns:
                    score_col = col
                    break
            
            if score_col is None:
                return {'raw_score': 0, 'status': 'Unknown', 'color': 'gray'}
            
            # Calculate average score for conversion readiness
            conversion_score = self.df[score_col].mean()
        else:
            # Calculate average of available conversion-related metrics
            # Ensure we only work with numeric columns
            numeric_cols = []
            for col in available_cols:
                if self.df[col].dtype in ['int64', 'float64'] or pd.api.types.is_numeric_dtype(self.df[col]):
                    numeric_cols.append(col)
            
            if not numeric_cols:
                # Fallback to score column
                score_col = None
                for col in ['final_score', 'raw_score', 'raw_score']:
                    if col in self.df.columns:
                        score_col = col
                        break
                
                if score_col is None:
                    return {'raw_score': 0, 'status': 'Unknown', 'color': 'gray'}
                
                conversion_score = self.df[score_col].mean()
            else:
                conversion_score = self.df[numeric_cols].mean().mean()
        
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
        """Get top improvement opportunities based on score gaps and tier importance"""
        # Find the correct score column
        score_col = None
        for col in ['avg_score', 'raw_score', 'final_score']:
            if col in self.df.columns:
                score_col = col
                break
        
        if score_col is None or 'tier_weight' not in self.df.columns:
            return []
        
        # Aggregate by page to avoid duplicates (unified dataset has multiple rows per page)
        page_agg = self.df.groupby('page_id').agg({
            score_col: 'mean',  # Use avg_score which should be consistent per page
            'tier_weight': 'first',  # Tier weight should be same for all criteria of a page
            'tier': 'first',
            'tier_name': 'first', 
            'url': 'first',
            'url_slug': 'first'
        }).reset_index()
        
        # Calculate opportunity score: (10 - current_score) * tier_weight
        # Higher opportunity score = bigger gap in more important pages
        page_agg['opportunity_score'] = (10 - page_agg[score_col]) * page_agg['tier_weight']
        
        # Filter to pages with meaningful improvement potential (score < 7.5)
        improvement_candidates = page_agg[page_agg[score_col] < 7.5]
        
        if improvement_candidates.empty:
            return []
        
        # Get top opportunities by opportunity score
        opportunities = improvement_candidates.nlargest(limit, 'opportunity_score')
        
        result = []
        for _, row in opportunities.iterrows():
            # Calculate effort level based on current score
            current_score = row.get(score_col, 0)
            if current_score < 3.0:
                effort_level = "High"
            elif current_score < 5.0:
                effort_level = "Medium"
            else:
                effort_level = "Low"
            
            result.append({
                'page_id': row.get('page_id', 'Unknown'),
                'url': row.get('url', ''),
                'current_score': current_score,
                'potential_impact': round(row.get('opportunity_score', 0), 1),
                'effort_level': effort_level,
                'tier': row.get('tier', 'Unknown'),
                'recommendation': f"Improve {row.get('tier_name', 'page')} content - current score {current_score:.1f}/10"
            })
        
        return result
    
    def calculate_success_stories(self, min_score: float = 7.7) -> List[Dict]:
        """Get success stories (high-performing pages)"""
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
        
        result = []
        for _, row in success_pages.iterrows():
            story = {
                'page_id': row.get('page_id', 'Unknown'),
                'url': row.get('url', ''),
                'raw_score': row.get(score_col, 0),
                'tier': row.get('tier', 'Unknown'),
                'key_strengths': self._extract_key_strengths(row)
            }
            
            # Add sentiment if available (string-based)
            if 'overall_sentiment' in row:
                story['sentiment'] = row['overall_sentiment']
            
            result.append(story)
        
        return result[:5]  # Return top 5
    
    def _extract_key_strengths(self, row) -> List[str]:
        """Extract key strengths from a high-performing page"""
        strengths = []
        
        # Check various criteria for strengths - use correct column names
        if row.get('overall_sentiment') == 'Positive' or row.get('sentiment') == 'Positive':
            strengths.append("Positive user sentiment")
        
        # Safely handle conversion_likelihood (string-based)
        conversion_val = row.get('conversion_likelihood', '')
        if isinstance(conversion_val, str) and conversion_val.lower() in ['high', 'excellent']:
            strengths.append("High conversion potential")
        
        # Check engagement level (string-based)
        engagement_val = row.get('engagement_level', '')
        if isinstance(engagement_val, str) and engagement_val.lower() in ['high', 'excellent']:
            strengths.append("High user engagement")
        
        # Check for score-based strengths - prioritize avg_score from unified data
        score_val = row.get('avg_score', 0) or row.get('raw_score', 0) or row.get('final_score', 0)
        if score_val >= 9.0:
            strengths.append("Exceptional performance score")
        elif score_val >= 8.5:
            strengths.append("Strong performance score")
        
        return strengths if strengths else ["High-performing page"]
    
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
            'sentiment_numeric': 'mean',
            'conversion_likelihood': 'mean',
            'overall_sentiment': 'mean'
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