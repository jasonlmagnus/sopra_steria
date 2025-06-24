"""
Tier Analysis Component for Brand Health Dashboard
Provides tier-based analysis and weighted scoring as per methodology
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TierAnalyzer:
    """Analyzes brand performance across content tiers with methodology-based weighting"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        # Use actual tier data from unified CSV instead of hardcoded config
        self.tier_config = self._load_tier_config_from_data()
    
    def _load_tier_config_from_data(self) -> Dict:
        """Load tier configuration from unified CSV data instead of hardcoded values"""
        tier_config = {}
        
        if self.data.empty:
            # Fallback to default config if no data
            return {
                'tier_1': {'name': 'Brand Positioning', 'weight': 0.3, 'brand_percentage': 80, 'performance_percentage': 20},
                'tier_2': {'name': 'Value Propositions', 'weight': 0.5, 'brand_percentage': 50, 'performance_percentage': 50}, 
                'tier_3': {'name': 'Functional Content', 'weight': 0.2, 'brand_percentage': 30, 'performance_percentage': 70}
            }
        
        # Extract tier configuration from unified CSV data
        for tier_id in self.data['tier'].unique():
            if pd.isna(tier_id):
                continue
                
            tier_data = self.data[self.data['tier'] == tier_id].iloc[0]
            
            tier_config[tier_id] = {
                'name': tier_data.get('tier_name', tier_id.replace('_', ' ').title()),
                'weight': tier_data.get('tier_weight', 0.33),
                'brand_percentage': tier_data.get('brand_percentage', 50),
                'performance_percentage': tier_data.get('performance_percentage', 50)
            }
        
        return tier_config
    
    def get_tier_summary(self) -> Dict:
        """Get high-level tier performance summary"""
        if self.data.empty:
            return {}
            
        tier_summary = {}
        
        for tier_id, config in self.tier_config.items():
            tier_data = self.data[self.data['tier'] == tier_id]
            
            if not tier_data.empty:
                avg_score = tier_data['raw_score'].mean()
                page_count = tier_data['page_id'].nunique()
                persona_count = tier_data['persona_id'].nunique()
                
                # Calculate brand health status
                if avg_score >= 7:
                    status = "STRONG"
                    status_color = "green"
                elif avg_score >= 5:
                    status = "MODERATE"
                    status_color = "orange"
                else:
                    status = "WEAK"
                    status_color = "red"
                
                tier_summary[tier_id] = {
                    'name': config['name'],
                    'weight': config['weight'],
                    'avg_score': avg_score,
                    'page_count': page_count,
                    'persona_count': persona_count,
                    'status': status,
                    'status_color': status_color,
                    'brand_percentage': config['brand_percentage'],
                    'performance_percentage': config['performance_percentage'],
                    'weighted_contribution': avg_score * config['weight']
                }
        
        return tier_summary
    
    def calculate_overall_brand_health(self) -> Dict:
        """Calculate overall brand health using tier-weighted methodology"""
        tier_summary = self.get_tier_summary()
        
        if not tier_summary:
            return {'score': 0, 'status': 'NO DATA', 'breakdown': {}}
        
        # Calculate weighted average
        total_weighted_score = sum(tier['weighted_contribution'] for tier in tier_summary.values())
        total_weight = sum(tier['weight'] for tier in tier_summary.values())
        
        if total_weight == 0:
            overall_score = 0
        else:
            overall_score = total_weighted_score / total_weight
        
        # Determine overall status
        if overall_score >= 7:
            overall_status = "EXCELLENT"
            status_color = "green"
        elif overall_score >= 5:
            overall_status = "GOOD"
            status_color = "orange"
        elif overall_score >= 3:
            overall_status = "NEEDS IMPROVEMENT"
            status_color = "orange"
        else:
            overall_status = "CRITICAL"
            status_color = "red"
        
        return {
            'raw_score': overall_score,
            'status': overall_status,
            'status_color': status_color,
            'breakdown': tier_summary,
            'methodology_note': "Weighted by tier importance: Brand Positioning (30%), Value Propositions (50%), Functional Content (20%)"
        }
    
    def get_tier_performance_matrix(self) -> pd.DataFrame:
        """Create tier x persona performance matrix"""
        if self.data.empty:
            return pd.DataFrame()
        
        # Group by tier and persona, calculate average scores
        matrix_data = self.data.groupby(['tier', 'persona_id'])['raw_score'].mean().reset_index()
        matrix_pivot = matrix_data.pivot(index='tier', columns='persona_id', values='raw_score')
        
        # Reorder tiers
        tier_order = ['tier_1', 'tier_2', 'tier_3']
        matrix_pivot = matrix_pivot.reindex(tier_order)
        
        # Add tier names
        tier_names = {tier: config['name'] for tier, config in self.tier_config.items()}
        matrix_pivot.index = [f"{tier} - {tier_names.get(tier, tier)}" for tier in matrix_pivot.index]
        
        return matrix_pivot
    
    def create_tier_performance_chart(self) -> go.Figure:
        """Create tier performance visualization"""
        tier_summary = self.get_tier_summary()
        
        if not tier_summary:
            return go.Figure()
        
        tiers = list(tier_summary.keys())
        tier_names = [tier_summary[tier]['name'] for tier in tiers]
        scores = [tier_summary[tier]['avg_score'] for tier in tiers]
        weights = [tier_summary[tier]['weight'] * 100 for tier in tiers]  # Convert to percentage
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Tier Performance Scores', 'Tier Weights in Overall Score'),
            specs=[[{"secondary_y": False}, {"type": "pie"}]]
        )
        
        # Bar chart for scores
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        fig.add_trace(
            go.Bar(
                x=tier_names,
                y=scores,
                marker_color=colors,
                text=[f"{score:.1f}/10" for score in scores],
                textposition='auto',
                name="Average Score"
            ),
            row=1, col=1
        )
        
        # Pie chart for weights
        fig.add_trace(
            go.Pie(
                labels=tier_names,
                values=weights,
                marker_colors=colors,
                textinfo='label+percent',
                name="Tier Weights"
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Tier-Based Brand Performance Analysis",
            showlegend=False,
            height=400
        )
        
        fig.update_xaxes(title_text="Content Tiers", row=1, col=1)
        fig.update_yaxes(title_text="Average Score (0-10)", row=1, col=1, range=[0, 10])
        
        return fig
    
    def create_brand_performance_split_chart(self) -> go.Figure:
        """Create brand vs performance criteria split visualization"""
        tier_summary = self.get_tier_summary()
        
        if not tier_summary:
            return go.Figure()
        
        tiers = list(tier_summary.keys())
        tier_names = [tier_summary[tier]['name'] for tier in tiers]
        brand_percentages = [tier_summary[tier]['brand_percentage'] for tier in tiers]
        performance_percentages = [tier_summary[tier]['performance_percentage'] for tier in tiers]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Brand Criteria',
            x=tier_names,
            y=brand_percentages,
            marker_color='#2E86AB',
            text=[f"{percentage}%" for percentage in brand_percentages],
            textposition='inside'
        ))
        
        fig.add_trace(go.Bar(
            name='Performance Criteria',
            x=tier_names,
            y=performance_percentages,
            marker_color='#A23B72',
            text=[f"{percentage}%" for percentage in performance_percentages],
            textposition='inside'
        ))
        
        fig.update_layout(
            title="Brand vs Performance Criteria Split by Tier",
            xaxis_title="Content Tiers",
            yaxis_title="Percentage (%)",
            barmode='stack',
            height=400,
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def get_tier_improvement_opportunities(self) -> List[Dict]:
        """Identify top improvement opportunities by tier"""
        opportunities = []
        
        for tier_id, config in self.tier_config.items():
            tier_data = self.data[self.data['tier'] == tier_id]
            
            if tier_data.empty:
                continue
            
            # Find lowest scoring pages in this tier
            page_scores = tier_data.groupby(['page_id', 'url_slug'])['raw_score'].mean().reset_index()
            lowest_pages = page_scores.nsmallest(3, 'raw_score')
            
            for _, page in lowest_pages.iterrows():
                page_detail = tier_data[tier_data['page_id'] == page['page_id']].iloc[0]
                
                # Calculate potential impact (tier weight * score gap)
                score_gap = 8 - page['raw_score']  # Target score of 8
                potential_impact = config['weight'] * score_gap
                
                opportunities.append({
                    'tier': config['name'],
                    'tier_weight': config['weight'],
                    'page_id': page['page_id'],
                    'url_slug': page['url_slug'],
                    'current_score': page['raw_score'],
                    'score_gap': score_gap,
                    'potential_impact': potential_impact,
                    'url': page_detail.get('url', ''),
                    'priority': 'HIGH' if potential_impact > 1.0 else 'MEDIUM' if potential_impact > 0.5 else 'LOW'
                })
        
        # Sort by potential impact
        opportunities.sort(key=lambda x: x['potential_impact'], reverse=True)
        return opportunities[:10]  # Top 10 opportunities
    
    def get_tier_success_stories(self) -> List[Dict]:
        """Identify success stories by tier"""
        success_stories = []
        
        for tier_id, config in self.tier_config.items():
            tier_data = self.data[self.data['tier'] == tier_id]
            
            if tier_data.empty:
                continue
            
            # Find highest scoring pages in this tier
            page_scores = tier_data.groupby(['page_id', 'url_slug'])['raw_score'].mean().reset_index()
            top_pages = page_scores.nlargest(3, 'raw_score')
            
            for _, page in top_pages.iterrows():
                if page['raw_score'] >= 7:  # Only include genuinely good performers
                    page_detail = tier_data[tier_data['page_id'] == page['page_id']].iloc[0]
                    
                    success_stories.append({
                        'tier': config['name'],
                        'page_id': page['page_id'],
                        'url_slug': page['url_slug'],
                        'score': page['raw_score'],
                        'url': page_detail.get('url', ''),
                        'evidence': page_detail.get('evidence', 'Strong performance across criteria')
                    })
        
        # Sort by score
        success_stories.sort(key=lambda x: x['score'], reverse=True)
        return success_stories[:5]  # Top 5 success stories
    
    def render_tier_dashboard(self):
        """Render complete tier analysis dashboard"""
        st.header("🏗️ Tier-Based Brand Analysis")
        st.markdown("*Analysis based on Sopra Steria Brand Audit Methodology*")
        
        # Overall brand health
        brand_health = self.calculate_overall_brand_health()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Overall Brand Health",
                f"{brand_health['raw_score']:.1f}/10",
                delta=None,
                help=brand_health['methodology_note']
            )
        
        with col2:
            st.metric(
                "Brand Status",
                brand_health['status'],
                delta=None
            )
        
        with col3:
            total_pages = self.data['page_id'].nunique() if not self.data.empty else 0
            st.metric("Pages Analyzed", total_pages)
        
        # Tier performance charts
        st.subheader("Tier Performance Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig1 = self.create_tier_performance_chart()
            st.plotly_chart(fig1)
        
        with col2:
            fig2 = self.create_brand_performance_split_chart()
            st.plotly_chart(fig2)
        
        # Performance matrix
        st.subheader("Tier × Persona Performance Matrix")
        matrix = self.get_tier_performance_matrix()
        
        if not matrix.empty:
            # Create heatmap
            fig = px.imshow(
                matrix.values,
                x=matrix.columns,
                y=matrix.index,
                color_continuous_scale='RdYlGn',
                aspect='auto',
                text_auto='.1f'
            )
            fig.update_layout(
                title="Performance Heatmap (Higher is Better)",
                xaxis_title="Personas",
                yaxis_title="Content Tiers"
            )
            st.plotly_chart(fig)
        else:
            st.warning("No data available for performance matrix")
        
        # Improvement opportunities
        st.subheader("🎯 Top Improvement Opportunities")
        opportunities = self.get_tier_improvement_opportunities()
        
        if opportunities:
            opp_df = pd.DataFrame(opportunities)
            st.dataframe(
                opp_df[['tier', 'url_slug', 'current_score', 'potential_impact', 'priority']],
                
            )
        else:
            st.info("No improvement opportunities identified")
        
        # Success stories
        st.subheader("🏆 Success Stories")
        success_stories = self.get_tier_success_stories()
        
        if success_stories:
            for story in success_stories:
                with st.expander(f"{story['tier']}: {story['url_slug']} ({story['score']:.1f}/10)"):
                    st.write(f"**URL:** {story['url']}")
                    st.write(f"**Evidence:** {story['evidence']}")
        else:
            st.info("No success stories identified") 