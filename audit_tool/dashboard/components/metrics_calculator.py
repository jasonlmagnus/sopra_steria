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
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.validate_data()
    
    def validate_data(self):
        """Validate that required columns exist"""
        required_cols = ['page_id', 'final_score']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            logger.warning(f"Missing required columns: {missing_cols}")
    
    def calculate_brand_health_score(self) -> float:
        """Calculate overall brand health score"""
        if 'final_score' not in self.df.columns:
            return 0.0
        return self.df['final_score'].mean()
    
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
        critical_pages = self.df[self.df['final_score'] < 4.0] if 'final_score' in self.df.columns else pd.DataFrame()
        
        return {
            'count': len(critical_pages),
            'percentage': len(critical_pages) / len(self.df) * 100 if len(self.df) > 0 else 0,
            'pages': critical_pages['page_id'].tolist() if 'page_id' in critical_pages.columns else []
        }
    
    def calculate_sentiment_metrics(self) -> Dict:
        """Calculate sentiment-related metrics"""
        if 'sentiment' not in self.df.columns:
            return {'positive': 0, 'neutral': 0, 'negative': 0, 'net_sentiment': 0}
        
        sentiment_counts = self.df['sentiment'].value_counts(normalize=True) * 100
        
        return {
            'positive': sentiment_counts.get('Positive', 0),
            'neutral': sentiment_counts.get('Neutral', 0),
            'negative': sentiment_counts.get('Negative', 0),
            'net_sentiment': sentiment_counts.get('Positive', 0) - sentiment_counts.get('Negative', 0)
        }
    
    def calculate_conversion_readiness(self) -> Dict:
        """Calculate conversion readiness proxy metrics"""
        conversion_cols = ['conversion_likelihood', 'cta_effectiveness', 'trust_credibility_signals']
        available_cols = [col for col in conversion_cols if col in self.df.columns]
        
        if not available_cols:
            return {'score': 0, 'status': 'Unknown', 'color': 'gray'}
        
        # Calculate average of available conversion-related metrics
        conversion_score = self.df[available_cols].mean().mean()
        
        if conversion_score >= 7.0:
            status, color = "High", "green"
        elif conversion_score >= 5.0:
            status, color = "Medium", "orange"
        else:
            status, color = "Low", "red"
        
        return {
            'score': conversion_score,
            'status': status,
            'color': color
        }
    
    def calculate_quick_wins(self) -> Dict:
        """Calculate quick wins metrics"""
        if 'quick_win_flag' not in self.df.columns:
            # Fallback calculation
            if 'potential_impact' in self.df.columns and 'effort_level' in self.df.columns:
                quick_wins = self.df[(self.df['potential_impact'] >= 1.5) & (self.df['effort_level'] == 'Low')]
            else:
                quick_wins = pd.DataFrame()
        else:
            quick_wins = self.df[self.df['quick_win_flag'] == True]
        
        return {
            'count': len(quick_wins),
            'opportunities': quick_wins[['page_id', 'potential_impact']].to_dict('records') if len(quick_wins) > 0 else []
        }
    
    def calculate_tier_performance(self) -> pd.DataFrame:
        """Calculate performance metrics by tier"""
        if 'tier' not in self.df.columns:
            return pd.DataFrame()
        
        # Build aggregation dictionary dynamically based on available columns
        agg_dict = {
            'final_score': ['mean', 'count']
        }
        
        # Add optional columns only if they exist
        if 'sentiment_numeric' in self.df.columns:
            agg_dict['sentiment_numeric'] = 'mean'
        if 'conversion_likelihood' in self.df.columns:
            agg_dict['conversion_likelihood'] = 'mean'
        if 'critical_issue_flag' in self.df.columns:
            agg_dict['critical_issue_flag'] = 'sum'
        if 'success_page_flag' in self.df.columns:
            agg_dict['success_page_flag'] = 'sum'
        
        tier_metrics = self.df.groupby('tier_clean' if 'tier_clean' in self.df.columns else 'tier').agg(agg_dict).round(2)
        
        # Flatten column names dynamically
        new_columns = ['avg_score', 'page_count']
        if 'sentiment_numeric' in self.df.columns:
            new_columns.append('avg_sentiment')
        if 'conversion_likelihood' in self.df.columns:
            new_columns.append('avg_conversion')
        if 'critical_issue_flag' in self.df.columns:
            new_columns.append('critical_issues')
        if 'success_page_flag' in self.df.columns:
            new_columns.append('success_pages')
        
        tier_metrics.columns = new_columns
        
        # Add performance indicators
        tier_metrics['performance_status'] = tier_metrics['avg_score'].apply(
            lambda x: 'Excellent' if x >= 8 else 'Good' if x >= 6 else 'Fair' if x >= 4 else 'Critical'
        )
        
        return tier_metrics.reset_index()
    
    def get_top_opportunities(self, limit: int = 5) -> List[Dict]:
        """Get top improvement opportunities"""
        if 'potential_impact' not in self.df.columns:
            return []
        
        # Sort by potential impact and get top opportunities
        opportunities = self.df.nlargest(limit, 'potential_impact')
        
        result = []
        for _, row in opportunities.iterrows():
            result.append({
                'page_id': row.get('page_id', 'Unknown'),
                'url': row.get('url', ''),
                'current_score': row.get('final_score', 0),
                'potential_impact': row.get('potential_impact', 0),
                'effort_level': row.get('effort_level', 'Unknown'),
                'tier': row.get('tier', 'Unknown'),
                'gap': row.get('criterion_gap', 0)
            })
        
        return result
    
    def calculate_success_stories(self, min_score: float = 8.0) -> List[Dict]:
        """Get success stories (high-performing pages)"""
        if 'final_score' not in self.df.columns:
            return []
        
        success_pages = self.df[self.df['final_score'] >= min_score]
        
        result = []
        for _, row in success_pages.iterrows():
            result.append({
                'page_id': row.get('page_id', 'Unknown'),
                'url': row.get('url', ''),
                'score': row.get('final_score', 0),
                'tier': row.get('tier', 'Unknown'),
                'sentiment': row.get('sentiment', 'Unknown'),
                'key_strengths': self._extract_key_strengths(row)
            })
        
        return result
    
    def _extract_key_strengths(self, row) -> List[str]:
        """Extract key strengths from a high-performing page"""
        strengths = []
        
        # Check various criteria for strengths
        if row.get('sentiment') == 'Positive':
            strengths.append("Positive user sentiment")
        
        if row.get('conversion_likelihood', 0) > 7:
            strengths.append("High conversion potential")
        
        if row.get('engagement', 0) > 7:
            strengths.append("Strong user engagement")
        
        # Add more strength detection logic as needed
        return strengths[:3]  # Limit to top 3 strengths
    
    def calculate_persona_comparison(self) -> pd.DataFrame:
        """Calculate metrics for persona comparison"""
        if 'persona_id' not in self.df.columns:
            return pd.DataFrame()
        
        # Build aggregation dictionary dynamically based on available columns
        agg_dict = {
            'final_score': ['mean', 'count']
        }
        
        # Add optional columns only if they exist
        if 'sentiment_numeric' in self.df.columns:
            agg_dict['sentiment_numeric'] = 'mean'
        if 'conversion_likelihood' in self.df.columns:
            agg_dict['conversion_likelihood'] = 'mean'
        if 'engagement' in self.df.columns:
            agg_dict['engagement'] = 'mean'
        
        persona_metrics = self.df.groupby('persona_id').agg(agg_dict).round(2)
        
        # Flatten column names dynamically
        new_columns = ['avg_score', 'page_count']
        if 'sentiment_numeric' in self.df.columns:
            new_columns.append('avg_sentiment')
        if 'conversion_likelihood' in self.df.columns:
            new_columns.append('avg_conversion')
        if 'engagement' in self.df.columns:
            new_columns.append('avg_engagement')
        
        persona_metrics.columns = new_columns
        
        return persona_metrics.reset_index()
    
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
                'score': round(brand_health, 1),
                'status': status,
                'emoji': emoji
            },
            'key_metrics': {
                'total_pages': len(self.df['page_id'].unique()) if 'page_id' in self.df.columns else 0,
                'critical_issues': critical_issues['count'],
                'quick_wins': quick_wins['count'],
                'success_pages': len(self.df[self.df['final_score'] >= 8.0]) if 'final_score' in self.df.columns else 0
            },
            'sentiment': sentiment,
            'conversion': conversion,
            'recommendations': self._generate_top_recommendations()
        }
    
    def _generate_top_recommendations(self) -> List[str]:
        """Generate top strategic recommendations"""
        recommendations = []
        
        # Critical issues recommendation
        critical_count = len(self.df[self.df['final_score'] < 4.0]) if 'final_score' in self.df.columns else 0
        if critical_count > 0:
            recommendations.append(f"Address {critical_count} critical pages scoring below 4.0")
        
        # Quick wins recommendation
        quick_wins = len(self.df[self.df.get('quick_win_flag', False) == True])
        if quick_wins > 0:
            recommendations.append(f"Implement {quick_wins} quick wins for immediate impact")
        
        # Sentiment recommendation
        if 'sentiment' in self.df.columns:
            negative_pct = (self.df['sentiment'] == 'Negative').mean() * 100
            if negative_pct > 20:
                recommendations.append("Focus on improving negative sentiment experiences")
        
        return recommendations[:3]  # Top 3 recommendations 