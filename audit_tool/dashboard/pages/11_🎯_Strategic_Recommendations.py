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
    
    def __init__(self, master_df: pd.DataFrame):
        self.master_df = master_df
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
                # Single recommendation for this page
                aggregated_recs.append(page_recs.iloc[0].to_dict())
            else:
                # Multiple recommendations for same page - aggregate them
                first_rec = page_recs.iloc[0]
                categories = page_recs['category'].unique()
                sources = page_recs['source'].unique()
                
                # Combine and deduplicate evidence from all recommendations for this page
                all_evidence = []
                unique_evidence = set()
                
                for _, rec in page_recs.iterrows():
                    if rec['evidence'] and len(rec['evidence']) > 20:
                        # Split evidence by common delimiters and clean
                        evidence_parts = rec['evidence'].replace(' | ', '|').split('|')
                        for part in evidence_parts:
                            clean_part = part.strip()
                            if len(clean_part) > 20 and clean_part not in unique_evidence:
                                unique_evidence.add(clean_part)
                                all_evidence.append(clean_part)
                
                # Create concise, non-redundant description
                category_list = list(set(categories))  # Remove duplicates
                
                # Create more concise description
                base_description = f"Multiple improvement opportunities identified across {len(category_list)} categories: {', '.join(category_list)}."
                
                # Add the most relevant evidence (max 1 piece)
                if all_evidence:
                    best_evidence = max(all_evidence, key=len)  # Use longest/most detailed evidence
                    if len(best_evidence) > 100:
                        best_evidence = best_evidence[:200] + "..."
                    base_description += f" Key insight: {best_evidence}"
                
                # Create aggregated recommendation
                aggregated_rec = {
                    'id': f"aggregated_{page_id}",
                    'title': first_rec['title'].replace('⚡ Quick Win: ', '').replace('🔴 CRITICAL: ', ''),
                    'description': base_description,
                    'category': categories[0] if len(categories) == 1 else 'Multiple Categories',
                    'impact_score': page_recs['impact_score'].max(),  # Use highest impact
                    'urgency_score': page_recs['urgency_score'].max(),  # Use highest urgency
                    'timeline': page_recs['timeline'].iloc[0],  # Use first timeline
                    'page_id': page_id,
                    'persona': first_rec['persona'],
                    'url': first_rec['url'],
                    'evidence': ' | '.join(all_evidence[:3]) if all_evidence else 'Multiple issues identified',  # Limit to 3 pieces
                    'source': ', '.join(set(sources))  # Remove duplicate sources
                }
                
                # Add priority indicators to title
                if aggregated_rec['impact_score'] >= 8:
                    aggregated_rec['title'] = f"🔴 CRITICAL: {aggregated_rec['title']}"
                elif 'Quick Win' in ', '.join(categories):
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
        
        if master_df.empty:
            st.error("No data available for recommendations analysis.")
            return
            
        # Initialize recommendation engine
        rec_engine = StrategicRecommendationEngine(master_df)
        recommendations = rec_engine.aggregate_all_recommendations()
        
        if recommendations.empty:
            st.warning("No recommendations could be generated from current data.")
            return
            
        # Executive Summary Cards
        st.markdown("## 📊 Executive Summary")
        
        # Calculate metrics
        critical_count = len(recommendations[recommendations['impact_score'] >= 9])
        quick_win_count = len(recommendations[recommendations['timeline'].str.contains('0-30', na=False)])
        strategic_count = len(recommendations[recommendations['timeline'].str.contains('30-90|90+', na=False)])
        avg_priority = recommendations['priority_score'].mean()
        
        # Use consistent metric cards
        col1, col2, col3, col4 = create_four_column_layout()
        
        with col1:
            create_metric_card(str(critical_count), "🔴 Critical Issues", status="error")
        with col2:
            create_metric_card(str(quick_win_count), "⚡ Quick Wins", status="success")
        with col3:
            create_metric_card(str(strategic_count), "🎯 Strategic", status="info")
        with col4:
            create_metric_card(f"{avg_priority:.1f}", "📈 Avg Priority", status="info")
        
        # Action Roadmap Timeline
        st.markdown("## 🗓️ Action Roadmap")
        
        timeline_tabs = st.tabs(["🚨 Immediate (0-30 days)", "📅 Short-term (30-90 days)", "🎯 Long-term (90+ days)"])
        
        with timeline_tabs[0]:
            immediate = recommendations[recommendations['timeline'].str.contains('0-30|0-7', na=False)]
            display_recommendation_list(immediate, "Immediate action items for maximum impact")
        
        with timeline_tabs[1]:
            short_term = recommendations[recommendations['timeline'].str.contains('30-90', na=False)]
            display_recommendation_list(short_term, "Strategic improvements for sustainable growth")
        
        with timeline_tabs[2]:
            long_term = recommendations[~recommendations['timeline'].str.contains('0-30|30-90|0-7', na=False)]
            display_recommendation_list(long_term, "Transformational initiatives for competitive advantage")
        
        # Impact vs Timeline Analysis
        st.markdown("## 📊 Priority Analysis")
        
        if not recommendations.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Impact vs Timeline bubble chart
                fig1 = create_category_priority_chart(recommendations)
                st.plotly_chart(fig1, use_container_width=True, key="impact_timeline_chart")
            
            with col2:
                # Category breakdown chart
                fig2 = create_category_breakdown_chart(recommendations)
                st.plotly_chart(fig2, use_container_width=True, key="category_breakdown_chart")
        
        # Detailed Recommendations Feed
        st.markdown("## 📋 Detailed Recommendations")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + sorted(recommendations['category'].unique().tolist()),
                key="category_filter"
            )
        
        with col2:
            persona_filter = st.selectbox(
                "Filter by Persona", 
                ["All"] + sorted(recommendations['persona'].unique().tolist()),
                key="persona_filter"
            )
        
        with col3:
            timeline_filter = st.selectbox(
                "Filter by Timeline",
                ["All"] + sorted(recommendations['timeline'].unique().tolist()),
                key="timeline_filter"
            )
        
        # Apply filters
        filtered_recs = recommendations.copy()
        if category_filter != "All":
            filtered_recs = filtered_recs[filtered_recs['category'] == category_filter]
        if persona_filter != "All":
            filtered_recs = filtered_recs[filtered_recs['persona'] == persona_filter]
        if timeline_filter != "All":
            filtered_recs = filtered_recs[filtered_recs['timeline'] == timeline_filter]
        
        # Display filtered recommendations
        display_recommendation_cards(filtered_recs)
        
        # Resource Planning Section
        st.markdown("## 📊 Resource Planning")
        
        if not recommendations.empty:
            display_resource_planning(recommendations)
        
    except Exception as e:
        st.error(f"Error loading recommendations: {str(e)}")
        st.exception(e)

def display_recommendation_list(recommendations: pd.DataFrame, description: str):
    """Display a simple list of recommendations for timeline tabs"""
    st.markdown(f"*{description}*")
    
    if recommendations.empty:
        st.info("No recommendations in this timeline category.")
        return
    
    for _, rec in recommendations.head(10).iterrows():  # Limit to top 10 for each timeline
        priority_color = "🔴" if rec['priority_score'] >= 8 else "🟡" if rec['priority_score'] >= 6 else "🟢"
        
        # Show URL if available
        url_text = ""
        if rec.get('url') and rec['url'] != '':
            url_text = f"  \n🔗 [{rec['url']}]({rec['url']})"
        
        st.markdown(f"""
        **{priority_color} {rec['title']}**  
        *Priority: {rec['priority_score']:.1f} | Impact: {rec['impact_score']}/10 | Timeline: {rec['timeline']}*  
        {rec['description']}{url_text}
        """)

def create_category_priority_chart(recommendations: pd.DataFrame) -> go.Figure:
    """Create interactive impact vs effort scatter plot with priority bubbles"""
    
    # Create a more useful visualization - Impact vs Timeline with Priority as bubble size
    fig = go.Figure()
    
    # Define timeline order for x-axis
    timeline_order = {'0-7 days': 1, '0-30 days': 2, '30-90 days': 3, '90+ days': 4}
    
    # Map timelines to numeric values
    recommendations['timeline_numeric'] = recommendations['timeline'].map(
        lambda x: timeline_order.get(x, 2.5)  # Default to middle if not found
    )
    
    # Create color mapping for categories (excluding "Multiple Categories")
    categories = [cat for cat in recommendations['category'].unique() if cat != 'Multiple Categories']
    colors = px.colors.qualitative.Set3[:len(categories)]
    color_map = dict(zip(categories, colors))
    
    # Add scatter plot for each category
    for category in recommendations['category'].unique():
        cat_data = recommendations[recommendations['category'] == category]
        
        fig.add_trace(go.Scatter(
            x=cat_data['timeline_numeric'],
            y=cat_data['impact_score'],
            mode='markers',
            name=category,
            marker=dict(
                size=cat_data['priority_score'] * 3,  # Scale bubble size
                opacity=0.7,
                line=dict(width=1, color='white')
            ),
            text=cat_data['title'].str[:50] + '...',  # Truncate long titles
            hovertemplate='<b>%{text}</b><br>' +
                         'Impact: %{y}/10<br>' +
                         'Timeline: %{customdata}<br>' +
                         'Priority: %{marker.size:.1f}<br>' +
                         '<extra></extra>',
            customdata=cat_data['timeline']
        ))
    
    # Update layout
    fig.update_layout(
        title="Impact vs Timeline Analysis (Bubble size = Priority)",
        xaxis_title="Implementation Timeline",
        yaxis_title="Impact Score (1-10)",
        xaxis=dict(
            tickmode='array',
            tickvals=[1, 2, 3, 4],
            ticktext=['0-7 days', '0-30 days', '30-90 days', '90+ days']
        ),
        yaxis=dict(range=[0, 11]),
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_category_breakdown_chart(recommendations: pd.DataFrame) -> go.Figure:
    """Create a useful category breakdown chart showing average priority by category"""
    
    # Calculate average priority and count by category
    category_stats = recommendations.groupby('category').agg({
        'priority_score': ['mean', 'count'],
        'impact_score': 'mean'
    }).round(1)
    
    # Flatten column names
    category_stats.columns = ['avg_priority', 'count', 'avg_impact']
    category_stats = category_stats.reset_index()
    
    # Create a horizontal bar chart
    fig = go.Figure()
    
    # Add bars colored by average impact
    fig.add_trace(go.Bar(
        y=category_stats['category'],
        x=category_stats['avg_priority'],
        orientation='h',
        marker=dict(
            color=category_stats['avg_impact'],
            colorscale='RdYlGn',
            colorbar=dict(title="Avg Impact"),
            cmin=0,
            cmax=10
        ),
        text=[f"{count} items" for count in category_stats['count']],
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>' +
                     'Avg Priority: %{x:.1f}<br>' +
                     'Count: %{text}<br>' +
                     'Avg Impact: %{marker.color:.1f}<br>' +
                     '<extra></extra>'
    ))
    
    fig.update_layout(
        title="Average Priority by Category",
        xaxis_title="Average Priority Score",
        yaxis_title="Category",
        height=400,
        showlegend=False
    )
    
    return fig

def display_recommendation_cards(recommendations: pd.DataFrame):
    """Display detailed recommendation cards with URLs and full descriptions"""
    
    if recommendations.empty:
        st.info("No recommendations match the selected filters.")
        return
    
    st.markdown(f"**Showing {len(recommendations)} recommendations**")
    
    for _, rec in recommendations.iterrows():
        # Determine priority level
        if rec['priority_score'] >= 8:
            priority_icon = "🔴"
            priority_level = "HIGH"
        elif rec['priority_score'] >= 6:
            priority_icon = "🟡"
            priority_level = "MEDIUM"
        else:
            priority_icon = "🟢"
            priority_level = "LOW"
        
        # Get URL if available
        url = rec.get('url', '')
        evidence = rec.get('evidence', '')
        
        # Create expandable card for full details
        with st.expander(f"{priority_icon} {rec['title']} (Priority: {rec['priority_score']:.1f})", expanded=False):
            
            # URL section
            if url and url != '':
                st.markdown(f"**🔗 Page URL:** [{url}]({url})")
                st.divider()
            
            # Full description
            st.markdown("**📋 Description:**")
            st.write(rec['description'])
            
            # Evidence/Details section
            if evidence and len(evidence) > 20:
                st.markdown("**🔍 Evidence & Details:**")
                st.write(evidence)
            
            # Metrics in columns
            col1, col2, col3, col4 = create_four_column_layout()
            with col1:
                create_metric_card(f"{rec['priority_score']:.1f}/10", "Priority Score", status="warning" if rec['priority_score'] >= 8 else "info")
            with col2:
                create_metric_card(f"{rec['impact_score']}/10", "Impact", status="success" if rec['impact_score'] >= 7 else "info")
            with col3:
                create_metric_card(rec['timeline'], "Timeline", status="info")
            with col4:
                create_metric_card(rec['category'], "Category", status="info")
            
            # Additional details
            st.markdown("**📊 Additional Details:**")
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.write(f"**Persona:** {rec['persona']}")
            with detail_col2:
                st.write(f"**Source:** {rec['source']}")
            with detail_col3:
                st.write(f"**🆔 Page ID:** `{rec['page_id']}`")
        
        # Quick summary below expander
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        with summary_col1:
            st.write(f"**Impact:** {rec['impact_score']}/10")
        with summary_col2:
            st.write(f"**Timeline:** {rec['timeline']}")
        with summary_col3:
            st.write(f"**Category:** {rec['category']}")
        
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