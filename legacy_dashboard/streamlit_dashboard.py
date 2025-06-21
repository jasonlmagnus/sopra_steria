#!/usr/bin/env python3
"""
Sopra Steria Website Audit - Streamlit Dashboard
Interactive dashboard for analyzing website audit results across personas
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np
from datetime import datetime
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from collections import defaultdict

# Import the strategic analyzer
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from strategic_insights import StrategicAnalyzer

# Page configuration
st.set_page_config(
    page_title="Sopra Steria Website Audit Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .critical-alert {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
        margin: 1rem 0;
    }
    .success-alert {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }
    .insight-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .priority-critical {
        border-left: 4px solid #dc3545;
    }
    .priority-high {
        border-left: 4px solid #fd7e14;
    }
    .priority-medium {
        border-left: 4px solid #ffc107;
    }
    .priority-low {
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class Example:
    category: str
    persona: str
    metric: str
    score: float
    example_text: str
    justification: str
    recommendation: str
    url: str

class ExampleExtractor:
    def __init__(self, data):
        self.data = data
    
    def extract_examples_from_text(self, text: str) -> Dict[str, Dict[str, str]]:
        """Extract examples, justifications, and recommendations from evaluation text"""
        examples = {}
        
        # Define metrics to look for
        metrics = {
            'headline': ['Headline Effectiveness', 'headline'],
            'content': ['Content Relevance', 'content'],
            'pain_points': ['Pain Point Recognition', 'pain point'],
            'value_prop': ['Value Proposition Clarity', 'value proposition'],
            'trust': ['Trust Signals', 'trust'],
            'cta': ['Call-to-Action Appropriateness', 'CTA Appropriateness', 'cta']
        }
        
        for metric_key, metric_names in metrics.items():
            for metric_name in metric_names:
                # Look for metric sections in the text - more flexible pattern
                patterns = [
                    rf'{re.escape(metric_name)}[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=(?:[A-Z][^:]*\(\d+(?:\.\d+)?/5\):|Recommendation:|Overall Score:|$))',
                    rf'{re.escape(metric_name)}[^:]*\((\d+(?:\.\d+)?)\):\s*(.*?)(?=(?:[A-Z][^:]*\(\d+(?:\.\d+)?\):|Recommendation:|Overall Score:|$))',
                    rf'{metric_name}[^:]*:\s*(\d+(?:\.\d+)?)/5[^\n]*\n(.*?)(?=(?:[A-Z][^:]*:|$))'
                ]
                
                match = None
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        break
                
                if match:
                    score = float(match.group(1))
                    content = match.group(2).strip()
                    
                    # Extract justification, examples, and recommendations more comprehensively
                    justification = ""
                    example_text = ""
                    recommendation = ""
                    
                    # Enhanced justification extraction
                    justification_patterns = [
                        r'Justification:\s*(.*?)(?=Example:|Recommendation:|$)',
                        r'Evaluation:\s*(.*?)(?=Example:|Recommendation:|$)',
                        r'(?:The|This)\s+(?:headline|content|website|page).*?(?:lacks|doesn\'t|fails|is|shows|demonstrates|highlights).*?(?=Example:|Recommendation:|$)',
                        r'(?:While|Although).*?(?:lacks|doesn\'t|fails|is|shows|demonstrates|highlights).*?(?=Example:|Recommendation:|$)'
                    ]
                    
                    for pattern in justification_patterns:
                        just_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                        if just_match and just_match.groups():
                            justification = just_match.group(1).strip()
                            break
                    
                    # If no explicit justification found, take the main content before recommendations
                    if not justification:
                        parts = content.split('Recommendation')
                        if len(parts) > 0:
                            # Clean up the justification text
                            justification = parts[0].strip()
                            # Remove common prefixes
                            justification = re.sub(r'^(?:Justification:|Evaluation:)\s*', '', justification, flags=re.IGNORECASE)
                    
                    # Enhanced example extraction
                    example_patterns = [
                        r'Example[s]?:\s*(.*?)(?=Recommendation:|$)',
                        r'For example[,:]?\s*(.*?)(?=Recommendation:|$)',
                        r'e\.g\.,?\s*(.*?)(?=Recommendation:|$)',
                        r'"([^"]+)"',  # Quoted text
                        r'such as\s+"([^"]+)"',
                        r'like\s+"([^"]+)"',
                        r'including\s+"([^"]+)"'
                    ]
                    
                    for pattern in example_patterns:
                        ex_matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
                        if ex_matches:
                            # Take the longest example found
                            example_text = max(ex_matches, key=len) if isinstance(ex_matches[0], str) else ex_matches[0]
                            example_text = example_text.strip()
                            break
                    
                    # Enhanced recommendation extraction
                    rec_patterns = [
                        r'Recommendation[s]?:\s*(.*?)$',
                        r'Improvement:\s*(.*?)$',
                        r'Suggest[s]?:\s*(.*?)$',
                        r'Should:\s*(.*?)$',
                        r'Consider:\s*(.*?)$'
                    ]
                    
                    for pattern in rec_patterns:
                        rec_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                        if rec_match and rec_match.groups():
                            recommendation = rec_match.group(1).strip()
                            break
                    
                    # Clean up extracted text
                    justification = self._clean_text(justification)
                    example_text = self._clean_text(example_text)
                    recommendation = self._clean_text(recommendation)
                    
                    examples[metric_key] = {
                        'score': score,
                        'justification': justification,
                        'example': example_text,
                        'recommendation': recommendation
                    }
                    break
        
        return examples
    
    def _clean_text(self, text: str) -> str:
        """Clean and format extracted text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common artifacts
        text = re.sub(r'^(?:Justification:|Evaluation:|Example:|Recommendation:)\s*', '', text, flags=re.IGNORECASE)
        
        # Remove trailing punctuation artifacts
        text = re.sub(r'\s*[.]{2,}$', '', text)
        
        # Limit length for display
        if len(text) > 500:
            text = text[:500] + "..."
        
        return text.strip()
    
    def get_best_and_worst_examples(self) -> Dict[str, Dict[str, List[Example]]]:
        """Get best and worst performing examples for each metric"""
        examples_by_metric = defaultdict(list)
        
        for item in self.data['raw_data']:
            text = item.get('evaluation_text', '')
            if not text:
                continue
                
            extracted = self.extract_examples_from_text(text)
            
            for metric, details in extracted.items():
                if details['score'] > 0:  # Valid score
                    example = Example(
                        category=item['category'],
                        persona=item['persona'],
                        metric=metric,
                        score=details['score'],
                        example_text=details['example'],
                        justification=details['justification'],
                        recommendation=details['recommendation'],
                        url=item['url']
                    )
                    examples_by_metric[metric].append(example)
        
        # Sort and get best/worst for each metric
        result = {}
        for metric, examples in examples_by_metric.items():
            sorted_examples = sorted(examples, key=lambda x: x.score, reverse=True)
            result[metric] = {
                'best': sorted_examples[:3],  # Top 3
                'worst': sorted_examples[-3:],  # Bottom 3
                'all': sorted_examples
            }
        
        return result

@st.cache_data
def load_data():
    """Load and cache the dashboard data"""
    try:
        with open('dashboard_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        st.error("Dashboard data file not found. Please run dashboard_analysis.py first.")
        return None

@st.cache_data
def load_strategic_insights():
    """Load and cache the strategic insights"""
    try:
        analyzer = StrategicAnalyzer()
        narrative = analyzer.generate_strategic_narrative()
        return narrative
    except Exception as e:
        st.error(f"Error loading strategic insights: {str(e)}")
        return None

def get_performance_color(score):
    """Get color based on performance score"""
    if score >= 3.5:
        return "#4CAF50"  # Green
    elif score >= 2.5:
        return "#FF9800"  # Orange
    elif score >= 1.5:
        return "#FF5722"  # Red-Orange
    else:
        return "#F44336"  # Red

def create_executive_summary(data, insights):
    """Create executive summary section"""
    st.markdown('<div class="main-header">📊 Sopra Steria Website Audit Dashboard</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Evaluations",
            value=f"{insights['executive_summary']['total_evaluations']:,}",
            help="Total number of persona-content evaluations analyzed"
        )
    
    with col2:
        avg_score = insights['executive_summary']['average_score']
        st.metric(
            label="Average Score",
            value=f"{avg_score:.2f}/5.0",
            delta=f"{avg_score - 2.5:.2f} vs. target",
            delta_color="inverse" if avg_score < 2.5 else "normal",
            help="Overall average performance score across all evaluations"
        )
    
    with col3:
        critical_issues = insights['executive_summary']['critical_issues']
        st.metric(
            label="Critical Issues",
            value=f"{critical_issues}",
            delta=f"{critical_issues - 50} vs. target",
            delta_color="inverse",
            help="Number of evaluations scoring ≤2.0 (target: <50)"
        )
    
    with col4:
        high_performers = insights['executive_summary']['high_performers']
        st.metric(
            label="High Performers",
            value=f"{high_performers}",
            delta=f"{high_performers - 100} vs. target",
            delta_color="normal" if high_performers > 50 else "inverse",
            help="Number of evaluations scoring ≥3.5 (target: >100)"
        )
    
    # Performance alerts
    if critical_issues > 100:
        st.markdown(f"""
        <div class="critical-alert">
            <strong>🚨 Critical Performance Alert</strong><br>
            {critical_issues} evaluations are performing critically (≤2.0). Immediate action required.
            <br><strong>Improvement Potential:</strong> {insights['executive_summary']['improvement_opportunity']}
        </div>
        """, unsafe_allow_html=True)
    
    if high_performers < 20:
        st.markdown(f"""
        <div class="critical-alert">
            <strong>⚠️ Low High-Performance Rate</strong><br>
            Only {high_performers} evaluations are performing well (≥3.5). Significant optimization opportunity exists.
        </div>
        """, unsafe_allow_html=True)

def create_strategic_insights_tab(insights):
    """Create strategic insights tab"""
    st.header("🎯 Strategic Insights & Narrative Analysis")
    
    # Priority Actions
    st.subheader("🚨 Critical Priority Actions")
    priority_actions = insights.get('priority_actions', [])
    
    if priority_actions:
        for action in priority_actions:
            priority_class = f"priority-{action.priority}"
            st.markdown(f"""
            <div class="insight-card {priority_class}">
                <h4>🚨 {action.title}</h4>
                <p><strong>Impact:</strong> {action.impact_potential} | <strong>Personas Affected:</strong> {', '.join(action.personas_affected)}</p>
                <p>{action.description}</p>
                <details>
                    <summary><strong>Evidence & Actions</strong></summary>
                    <p><strong>Evidence:</strong></p>
                    <ul>
                        {''.join([f'<li>{evidence}</li>' for evidence in action.evidence])}
                    </ul>
                    <p><strong>Immediate Actions:</strong></p>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in action.recommendations])}
                    </ul>
                </details>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No critical priority actions identified.")
    
    # Quick Wins
    st.subheader("⚡ Quick Wins Implementation Roadmap")
    quick_wins = insights.get('quick_wins', [])
    
    if quick_wins:
        # Create tabs for different phases
        phase1_tab, phase2_tab, phase3_tab = st.tabs(["Phase 1: Immediate (0-30 days)", "Phase 2: Strategic (30-90 days)", "Phase 3: Advanced (90+ days)"])
        
        with phase1_tab:
            st.markdown("### Immediate Fixes (High Impact, Low Effort)")
            for i, win in enumerate(quick_wins[:3], 1):
                st.markdown(f"""
                <div class="insight-card priority-medium">
                    <h5>{i}. {win.title}</h5>
                    <p><strong>Impact:</strong> {win.impact_potential} | <strong>Effort:</strong> Low-Medium</p>
                    <p><strong>Affected:</strong> {len(win.personas_affected)} personas, {len(win.content_areas)} content areas</p>
                    <p><strong>Key Action:</strong> {win.recommendations[0] if win.recommendations else 'See detailed recommendations'}</p>
                    <details>
                        <summary>View Details</summary>
                        <p><strong>Evidence:</strong></p>
                        <ul>
                            {''.join([f'<li>{evidence}</li>' for evidence in win.evidence])}
                        </ul>
                        <p><strong>All Recommendations:</strong></p>
                        <ul>
                            {''.join([f'<li>{rec}</li>' for rec in win.recommendations])}
                        </ul>
                    </details>
                </div>
                """, unsafe_allow_html=True)
        
        with phase2_tab:
            st.markdown("""
            ### Strategic Improvements (30-90 days)
            - Implement persona-specific content strategies
            - Develop comprehensive trust signal framework
            - Create standardized pain point recognition approach
            - Launch A/B testing program for optimizations
            """)
        
        with phase3_tab:
            st.markdown("""
            ### Advanced Optimization (90+ days)
            - Deploy advanced personalization
            - Implement dynamic content optimization
            - Launch comprehensive measurement and analytics framework
            - Establish continuous improvement processes
            """)
    
    # Recommendation Themes
    st.subheader("📋 Recommendation Themes Analysis")
    themes = insights.get('recommendation_themes', {})
    
    if themes:
        # Create metrics for theme frequency
        theme_cols = st.columns(len(themes))
        for i, (theme, recommendations) in enumerate(themes.items()):
            with theme_cols[i]:
                st.metric(
                    label=theme.replace('_', ' ').title(),
                    value=len(recommendations),
                    help=f"Number of mentions across evaluations"
                )
        
        # Detailed theme analysis
        selected_theme = st.selectbox(
            "Select theme for detailed analysis:",
            options=list(themes.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_theme and themes[selected_theme]:
            st.markdown(f"### {selected_theme.replace('_', ' ').title()} Analysis")
            recommendations = themes[selected_theme]
            
            # Show frequency and patterns
            st.markdown(f"**Frequency:** {len(recommendations)} mentions across evaluations")
            
            # Sample recommendations
            st.markdown("**Common Patterns:**")
            for i, rec in enumerate(recommendations[:5], 1):
                st.markdown(f"{i}. *{rec['text'][:150]}...* (Score: {rec['score']}, Persona: {rec['persona']})")
            
            st.info("This theme appears consistently across multiple personas and content areas, indicating a systematic opportunity for improvement.")

def create_persona_insights_tab(insights):
    """Create persona journey insights tab"""
    st.header("👥 Persona Journey Analysis")
    
    # Get persona journey insights
    persona_insights = [insight for insight in insights.get('strategic_insights', []) if insight.category == 'persona_journey']
    
    if persona_insights:
        st.markdown("### Journey Inconsistencies Identified")
        
        for insight in persona_insights:
            priority_class = f"priority-{insight.priority}"
            variance = float(insight.description.split('(')[1].split(' points')[0])
            
            st.markdown(f"""
            <div class="insight-card {priority_class}">
                <h4>{'⚠️' if insight.priority == 'high' else '📊'} {insight.title}</h4>
                <p><strong>Performance Variance:</strong> {variance:.1f} points across touchpoints</p>
                <p>{insight.description}</p>
                <details>
                    <summary><strong>Journey Analysis</strong></summary>
                    <ul>
                        {''.join([f'<li>{evidence}</li>' for evidence in insight.evidence])}
                    </ul>
                    <p><strong>Recommendations:</strong></p>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in insight.recommendations])}
                    </ul>
                </details>
            </div>
            """, unsafe_allow_html=True)
        
        # Journey consistency chart
        st.subheader("📊 Persona Journey Consistency Overview")
        
        # Create a summary chart of journey variances
        persona_names = [insight.title.replace(' Journey Inconsistency', '') for insight in persona_insights]
        variances = [float(insight.description.split('(')[1].split(' points')[0]) for insight in persona_insights]
        
        fig = go.Figure(data=[
            go.Bar(
                x=persona_names,
                y=variances,
                marker_color=['#dc3545' if v > 2.0 else '#fd7e14' if v > 1.5 else '#ffc107' for v in variances],
                text=[f"{v:.1f}" for v in variances],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title="Persona Journey Variance (Lower is Better)",
            xaxis_title="Persona",
            yaxis_title="Score Variance (Points)",
            height=400
        )
        
        fig.add_hline(y=1.5, line_dash="dash", line_color="orange", 
                     annotation_text="Significant Inconsistency Threshold")
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No significant persona journey inconsistencies identified.")

def create_competitive_insights_tab(insights):
    """Create competitive positioning insights tab"""
    st.header("🏆 Competitive Positioning Analysis")
    
    # Get competitive insights
    competitive_insights = [insight for insight in insights.get('strategic_insights', []) if insight.category == 'competitive_positioning']
    
    if competitive_insights:
        for insight in competitive_insights:
            st.markdown(f"""
            <div class="insight-card priority-medium">
                <h4>📊 {insight.title}</h4>
                <p>{insight.description}</p>
                <details>
                    <summary><strong>Analysis & Recommendations</strong></summary>
                    <p><strong>Evidence:</strong></p>
                    <ul>
                        {''.join([f'<li>{evidence}</li>' for evidence in insight.evidence])}
                    </ul>
                    <p><strong>Strategic Recommendations:</strong></p>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in insight.recommendations])}
                    </ul>
                </details>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No specific competitive positioning insights identified.")
    
    # Success patterns
    success_patterns = [insight for insight in insights.get('strategic_insights', []) if insight.category == 'success_patterns']
    
    if success_patterns:
        st.subheader("🌟 Success Patterns Analysis")
        for pattern in success_patterns:
            st.markdown(f"""
            <div class="success-alert">
                <h4>✅ {pattern.title}</h4>
                <p>{pattern.description}</p>
                <details>
                    <summary><strong>Success Factors</strong></summary>
                    <p><strong>Evidence:</strong></p>
                    <ul>
                        {''.join([f'<li>{evidence}</li>' for evidence in pattern.evidence])}
                    </ul>
                    <p><strong>Replication Strategy:</strong></p>
                    <ul>
                        {''.join([f'<li>{rec}</li>' for rec in pattern.recommendations])}
                    </ul>
                </details>
            </div>
            """, unsafe_allow_html=True)

def create_actionable_examples_tab(data):
    """Create actionable examples tab with specific concrete findings"""
    st.header("💡 Concrete Findings: Specific Issues & Examples")
    
    # Load concrete findings
    try:
        with open('concrete_findings.json', 'r', encoding='utf-8') as f:
            concrete_findings = json.load(f)
        
        with open('concrete_insights.json', 'r', encoding='utf-8') as f:
            concrete_insights = json.load(f)
    except FileNotFoundError:
        st.error("Concrete findings not found. Please run concrete_findings_extractor.py first.")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Concrete Findings", len(concrete_findings))
    
    with col2:
        st.metric("Critical Issues", len(concrete_insights['critical_issues']))
    
    with col3:
        st.metric("Best Practices", len(concrete_insights['best_practices']))
    
    with col4:
        st.metric("Quantified Impacts", len(concrete_insights['quantified_impacts']))
    
    # Metric selector
    metric_options = {
        'headline': 'Headline Effectiveness',
        'content': 'Content Relevance', 
        'pain_points': 'Pain Point Recognition',
        'value_prop': 'Value Proposition Clarity',
        'trust': 'Trust Signals',
        'cta': 'Call-to-Action Appropriateness'
    }
    
    selected_metric = st.selectbox(
        "Select metric to see concrete findings:",
        options=list(metric_options.keys()),
        format_func=lambda x: metric_options[x],
        help="Choose a metric to see specific issues, examples, and recommendations"
    )
    
    # Filter findings by metric
    metric_findings = [f for f in concrete_findings if f['metric'] == selected_metric]
    
    if not metric_findings:
        st.warning(f"No concrete findings found for {metric_options[selected_metric]}")
        return
    
    # Organize findings by score
    critical_findings = [f for f in metric_findings if f['score'] <= 2.0 and f['specific_issue']]
    good_findings = [f for f in metric_findings if f['score'] >= 3.5 and f['detailed_justification']]
    moderate_findings = [f for f in metric_findings if 2.0 < f['score'] < 3.5 and (f['specific_issue'] or f['concrete_example'])]
    
    # Create tabs for different types of findings
    critical_tab, good_tab, moderate_tab, insights_tab = st.tabs([
        f"🚨 Critical Issues ({len(critical_findings)})",
        f"✅ What Works ({len(good_findings)})", 
        f"⚡ Quick Wins ({len(moderate_findings)})",
        "📊 Insights"
    ])
    
    with critical_tab:
        st.subheader("🚨 Critical Issues with Specific Examples")
        
        if critical_findings:
            for i, finding in enumerate(critical_findings[:10], 1):  # Show top 10
                with st.expander(f"Issue {i}: {finding['persona']} - {finding['category']} ({finding['score']}/5)"):
                    
                    # URL
                    st.markdown(f"**🔗 URL:** {finding['url']}")
                    
                    # Specific Issue
                    if finding['specific_issue']:
                        st.markdown("**❌ Specific Issue:**")
                        st.error(finding['specific_issue'])
                    
                    # Concrete Example
                    if finding['concrete_example']:
                        st.markdown("**📝 Concrete Example:**")
                        st.info(f'"{finding["concrete_example"]}"')
                    
                    # Quoted Content
                    if finding['quoted_content']:
                        st.markdown("**💬 Quoted from Content:**")
                        st.code(f'"{finding["quoted_content"]}"')
                    
                    # Detailed Justification
                    if finding['detailed_justification']:
                        st.markdown("**🔍 Why This is a Problem:**")
                        st.write(finding['detailed_justification'])
                    
                    # Specific Recommendation
                    if finding['specific_recommendation']:
                        st.markdown("**🎯 Specific Recommendation:**")
                        st.success(finding['specific_recommendation'])
                    
                    # Quantified Impact
                    if finding['quantified_impact']:
                        st.markdown("**📊 Quantified Impact:**")
                        st.warning(finding['quantified_impact'])
        else:
            st.info("No critical issues found for this metric")
    
    with good_tab:
        st.subheader("✅ What's Working Well - Concrete Examples")
        
        if good_findings:
            for i, finding in enumerate(good_findings[:10], 1):  # Show top 10
                with st.expander(f"Success {i}: {finding['persona']} - {finding['category']} ({finding['score']}/5)"):
                    
                    # URL
                    st.markdown(f"**🔗 URL:** {finding['url']}")
                    
                    # What Works
                    if finding['detailed_justification']:
                        st.markdown("**✅ Why This Works:**")
                        st.success(finding['detailed_justification'])
                    
                    # Concrete Example
                    if finding['concrete_example']:
                        st.markdown("**📝 Concrete Example:**")
                        st.info(f'"{finding["concrete_example"]}"')
                    
                    # Quoted Content
                    if finding['quoted_content']:
                        st.markdown("**💬 Quoted from Content:**")
                        st.code(f'"{finding["quoted_content"]}"')
                    
                    # How to Replicate
                    if finding['specific_recommendation']:
                        st.markdown("**🔄 How to Replicate:**")
                        st.write(finding['specific_recommendation'])
        else:
            st.info("No high-performing examples found for this metric")
    
    with moderate_tab:
        st.subheader("⚡ Quick Wins - Specific Improvement Opportunities")
        
        if moderate_findings:
            for i, finding in enumerate(moderate_findings[:10], 1):  # Show top 10
                improvement_potential = 3.5 - finding['score']
                
                with st.expander(f"Opportunity {i}: {finding['persona']} - {finding['category']} ({finding['score']}/5, +{improvement_potential:.1f} potential)"):
                    
                    # URL
                    st.markdown(f"**🔗 URL:** {finding['url']}")
                    
                    # Current Issue
                    if finding['specific_issue']:
                        st.markdown("**⚠️ Current Issue:**")
                        st.warning(finding['specific_issue'])
                    
                    # Concrete Example
                    if finding['concrete_example']:
                        st.markdown("**📝 Specific Example:**")
                        st.info(f'"{finding["concrete_example"]}"')
                    
                    # Context
                    if finding['detailed_justification']:
                        st.markdown("**📋 Context:**")
                        st.write(finding['detailed_justification'])
                    
                    # Quick Fix
                    if finding['specific_recommendation']:
                        st.markdown("**🚀 Quick Fix:**")
                        st.success(finding['specific_recommendation'])
                    
                    # Impact Potential
                    st.markdown("**📈 Impact Potential:**")
                    st.metric("Score Improvement", f"+{improvement_potential:.1f} points", f"From {finding['score']:.1f} to 3.5+")
        else:
            st.info("No moderate-scoring opportunities found for this metric")
    
    with insights_tab:
        st.subheader("📊 Metric Insights & Patterns")
        
        # Persona breakdown
        persona_breakdown = {}
        for finding in metric_findings:
            persona = finding['persona']
            if persona not in persona_breakdown:
                persona_breakdown[persona] = {'total': 0, 'critical': 0, 'good': 0, 'avg_score': 0}
            
            persona_breakdown[persona]['total'] += 1
            persona_breakdown[persona]['avg_score'] += finding['score']
            
            if finding['score'] <= 2.0:
                persona_breakdown[persona]['critical'] += 1
            elif finding['score'] >= 3.5:
                persona_breakdown[persona]['good'] += 1
        
        # Calculate averages
        for persona in persona_breakdown:
            persona_breakdown[persona]['avg_score'] /= persona_breakdown[persona]['total']
        
        # Display persona breakdown
        st.markdown("### 👥 Performance by Persona")
        
        persona_df = pd.DataFrame([
            {
                'Persona': persona,
                'Avg Score': f"{data['avg_score']:.2f}",
                'Total Evaluations': data['total'],
                'Critical Issues': data['critical'],
                'Good Performance': data['good'],
                'Critical Rate': f"{data['critical']/data['total']*100:.1f}%"
            }
            for persona, data in persona_breakdown.items()
        ])
        
        st.dataframe(persona_df, use_container_width=True)
        
        # Common issues
        st.markdown("### 🔍 Most Common Issues")
        
        issue_patterns = {}
        for finding in critical_findings:
            if finding['specific_issue']:
                # Extract key phrases from issues
                issue_text = finding['specific_issue'].lower()
                key_phrases = []
                
                # Look for common patterns
                if 'lacks' in issue_text or 'missing' in issue_text:
                    key_phrases.append('Missing/Lacking Content')
                if 'generic' in issue_text or 'vague' in issue_text:
                    key_phrases.append('Generic/Vague Messaging')
                if 'no mention' in issue_text or 'doesn\'t address' in issue_text:
                    key_phrases.append('Missing Key Topics')
                if 'regulation' in issue_text or 'compliance' in issue_text:
                    key_phrases.append('Regulatory/Compliance Gaps')
                if 'specific' in issue_text and 'lack' in issue_text:
                    key_phrases.append('Lack of Specificity')
                
                for phrase in key_phrases:
                    if phrase not in issue_patterns:
                        issue_patterns[phrase] = 0
                    issue_patterns[phrase] += 1
        
        if issue_patterns:
            issue_df = pd.DataFrame([
                {'Issue Pattern': pattern, 'Frequency': count}
                for pattern, count in sorted(issue_patterns.items(), key=lambda x: x[1], reverse=True)
            ])
            
            fig = px.bar(
                issue_df,
                x='Frequency',
                y='Issue Pattern',
                orientation='h',
                title=f"Most Common Issue Patterns - {metric_options[selected_metric]}",
                color='Frequency',
                color_continuous_scale='Reds'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Quantified impacts for this metric
        metric_impacts = [imp for imp in concrete_insights['quantified_impacts'] if imp['metric'] == selected_metric]
        
        if metric_impacts:
            st.markdown("### 📊 Quantified Impacts")
            
            for impact in metric_impacts:
                st.markdown(f"""
                <div class="insight-card priority-high">
                    <strong>📈 {impact['persona']}</strong><br>
                    <strong>Impact:</strong> {impact['impact']}<br>
                    <strong>Context:</strong> {impact['context'][:200]}...
                </div>
                """, unsafe_allow_html=True)
        
        # Recommendations summary
        metric_recs = concrete_insights['specific_recommendations'].get(selected_metric, [])
        
        if metric_recs:
            st.markdown("### 🎯 Top Recommendations")
            
            # Group recommendations by similarity
            rec_groups = {}
            for rec in metric_recs:
                rec_text = rec['recommendation']
                # Simple grouping by first few words
                key_words = ' '.join(rec_text.split()[:3]).lower()
                
                if key_words not in rec_groups:
                    rec_groups[key_words] = []
                rec_groups[key_words].append(rec)
            
            # Show top recommendation groups
            for group_key, group_recs in list(rec_groups.items())[:5]:
                st.markdown(f"**{group_key.title()}** ({len(group_recs)} mentions)")
                st.write(f"• {group_recs[0]['recommendation']}")
                st.caption(f"Affects: {', '.join(set([r['persona'] for r in group_recs]))}")
                st.markdown("---")

def main():
    """Main dashboard function"""
    # Load data
    data = load_data()
    insights = load_strategic_insights()
    
    if data is None or insights is None:
        st.stop()
    
    # Create executive summary
    create_executive_summary(data, insights)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Convert raw data to DataFrame for easier filtering
    df = pd.DataFrame(data['raw_data'])
    
    # Persona filter
    personas = st.sidebar.multiselect(
        "Select Personas",
        options=df['persona'].unique(),
        default=df['persona'].unique(),
        help="Filter by target personas"
    )
    
    # Category filter
    categories = st.sidebar.multiselect(
        "Select Content Categories",
        options=df['category'].unique(),
        default=df['category'].unique(),
        help="Filter by content categories"
    )
    
    # Score range filter
    score_range = st.sidebar.slider(
        "Score Range",
        min_value=0.0,
        max_value=5.0,
        value=(0.0, 5.0),
        step=0.1,
        help="Filter by overall score range"
    )
    
    # Apply filters
    filtered_df = df[
        (df['persona'].isin(personas)) &
        (df['category'].isin(categories)) &
        (df['overall'] >= score_range[0]) &
        (df['overall'] <= score_range[1])
    ]
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📖 Methodology",
        "📊 Performance Overview", 
        "💡 Actionable Examples",
        "🎯 Strategic Insights", 
        "👥 Persona Journeys",
        "🏆 Competitive Analysis",
        "📈 Detailed Analytics", 
        "📋 Raw Data",
        "⚠️ Audit Methodology Issues"
    ])
    
    with tab1:
        # Methodology Tab
        st.header("📖 Audit Methodology & Framework")
        
        # Overview
        st.subheader("🎯 Audit Overview")
        st.markdown("""
        This comprehensive website audit evaluates Sopra Steria's digital presence across **5 key personas** and **10 content categories** 
        using a structured **6-dimensional scoring framework**. The analysis provides actionable insights for optimizing 
        website performance and user experience across different target audiences.
        """)
        
        # Key Statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Evaluations", f"{insights['executive_summary']['total_evaluations']:,}")
        with col2:
            st.metric("Target Personas", "5")
        with col3:
            st.metric("Content Categories", len(df['category'].unique()))
        with col4:
            st.metric("Scoring Dimensions", "6")
        
        # Personas Section
        st.subheader("👥 Target Personas")
        st.markdown("""
        The audit evaluates content effectiveness across five key decision-maker personas in the BENELUX region:
        """)
        
        persona_info = {
            "IT Executive (Public Sector)": {
                "focus": "Digital transformation, compliance, citizen service improvement",
                "priorities": "NIS2, DORA, GDPR compliance; legacy system modernization; cybersecurity",
                "pain_points": "Regulatory complexity, IT skills gaps, budget constraints"
            },
            "Financial Services Leader": {
                "focus": "Secure growth, regulatory compliance, operational resilience",
                "priorities": "DORA, MiCA, AI Act compliance; core banking modernization; risk management",
                "pain_points": "Legacy system disruptions, cybersecurity confidence gaps, data governance"
            },
            "Chief Data Officer": {
                "focus": "Trust, governance, ethical data practices",
                "priorities": "AI Act compliance, data quality frameworks, privacy-enhancing technologies",
                "pain_points": "GenAI readiness gaps, data silos, demonstrating governance ROI"
            },
            "Operations Transformation Executive": {
                "focus": "Operational excellence, system modernization, efficiency gains",
                "priorities": "ERP modernization, supply chain optimization, asset performance",
                "pain_points": "SAP 2027 deadline, migration risks, resource constraints"
            },
            "Cross-Sector IT Director": {
                "focus": "Business agility, innovation, employee empowerment",
                "priorities": "AI integration, cybersecurity for hybrid environments, digital employee experience",
                "pain_points": "Tech change vs. organizational capacity, IT skills shortage, innovation vs. stability"
            }
        }
        
        for persona, details in persona_info.items():
            with st.expander(f"🎭 {persona}"):
                st.markdown(f"""
                **Focus:** {details['focus']}
                
                **Key Priorities:**
                - {details['priorities']}
                
                **Main Pain Points:**
                - {details['pain_points']}
                """)
        
        # Content Categories
        st.subheader("📂 Content Categories Analyzed")
        
        # Get actual categories from data
        categories = df['category'].unique()
        category_counts = df['category'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Primary Content Types:**")
            for category in sorted(categories):
                count = category_counts[category]
                st.markdown(f"• **{category}** ({count} evaluations)")
        
        with col2:
            # Category distribution chart
            fig = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Evaluation Distribution by Content Category"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Scoring Framework
        st.subheader("📊 6-Dimensional Scoring Framework")
        st.markdown("""
        Each persona-content combination is evaluated across six critical dimensions using a **1-5 scale**:
        """)
        
        scoring_framework = {
            "Headline Effectiveness": {
                "description": "How well headlines capture attention and communicate value to the target persona",
                "criteria": "Relevance, clarity, persona-specific language, value proposition alignment"
            },
            "Content Relevance": {
                "description": "Alignment of content with persona priorities, challenges, and information needs",
                "criteria": "Topic coverage, depth, regulatory focus, solution specificity"
            },
            "Pain Point Recognition": {
                "description": "Explicit acknowledgment and understanding of persona-specific challenges",
                "criteria": "Problem identification, empathy demonstration, challenge quantification"
            },
            "Value Proposition Clarity": {
                "description": "Clear articulation of benefits and outcomes for the target persona",
                "criteria": "Benefit specificity, ROI demonstration, outcome quantification"
            },
            "Trust Signals": {
                "description": "Evidence of credibility, expertise, and reliability for the target audience",
                "criteria": "Certifications, case studies, testimonials, industry expertise"
            },
            "Call-to-Action Appropriateness": {
                "description": "Relevance and effectiveness of next-step options for the persona",
                "criteria": "Action specificity, persona alignment, engagement facilitation"
            }
        }
        
        for dimension, details in scoring_framework.items():
            with st.expander(f"📋 {dimension}"):
                st.markdown(f"""
                **Description:** {details['description']}
                
                **Evaluation Criteria:**
                - {details['criteria']}
                """)
        
        # Scoring Scale
        st.subheader("🎯 Scoring Scale & Interpretation")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("""
            **Score Ranges:**
            - **5.0:** Excellent
            - **4.0-4.9:** Good
            - **3.0-3.9:** Moderate
            - **2.0-2.9:** Poor
            - **1.0-1.9:** Critical
            """)
        
        with col2:
            # Create scoring scale visualization
            scores = [1, 2, 3, 4, 5]
            labels = ['Critical', 'Poor', 'Moderate', 'Good', 'Excellent']
            colors = ['#F44336', '#FF5722', '#FF9800', '#4CAF50', '#2E7D32']
            
            fig = go.Figure(data=[
                go.Bar(
                    x=scores,
                    y=[1]*5,
                    marker_color=colors,
                    text=labels,
                    textposition='auto',
                    showlegend=False
                )
            ])
            
            fig.update_layout(
                title="Scoring Scale",
                xaxis_title="Score",
                yaxis_title="",
                height=200,
                yaxis=dict(showticklabels=False),
                xaxis=dict(tickmode='array', tickvals=scores)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Performance Thresholds
        st.subheader("🚨 Performance Thresholds")
        
        threshold_col1, threshold_col2, threshold_col3 = st.columns(3)
        
        with threshold_col1:
            st.markdown("""
            <div class="critical-alert">
                <strong>🔴 Critical Issues</strong><br>
                Score ≤ 2.0<br>
                <small>Immediate action required</small>
            </div>
            """, unsafe_allow_html=True)
        
        with threshold_col2:
            st.markdown("""
            <div style="background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #ffc107; margin: 1rem 0;">
                <strong>🟡 Optimization Opportunity</strong><br>
                Score 2.0 - 3.5<br>
                <small>Improvement potential identified</small>
            </div>
            """, unsafe_allow_html=True)
        
        with threshold_col3:
            st.markdown("""
            <div class="success-alert">
                <strong>🟢 Good Performance</strong><br>
                Score ≥ 3.5<br>
                <small>Meeting expectations</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Data Collection Process
        st.subheader("🔍 Data Collection Process")
        st.markdown("""
        **1. Content Identification**
        - Systematic mapping of Sopra Steria's digital touchpoints
        - Categorization by content type and regional focus
        - URL validation and accessibility verification
        
        **2. Persona-Based Evaluation**
        - Each content piece evaluated from each persona's perspective
        - Structured assessment using the 6-dimensional framework
        - Qualitative insights captured alongside quantitative scores
        
        **3. Quality Assurance**
        - Consistent evaluation criteria applied across all assessments
        - Regular calibration to ensure scoring consistency
        - Comprehensive documentation of rationale and recommendations
        """)
        
        # How to Use This Dashboard
        st.subheader("📱 How to Use This Dashboard")
        st.markdown("""
        **Navigation Guide:**
        
        1. **📊 Performance Overview** - Start here for high-level insights and key metrics
        2. **🎯 Strategic Insights** - Review critical priority actions and quick wins
        3. **👥 Persona Journeys** - Analyze consistency across touchpoints for each persona
        4. **🏆 Competitive Analysis** - Understand success patterns and positioning opportunities
        5. **📈 Detailed Analytics** - Dive deep into score distributions and correlations
        6. **📋 Raw Data** - Explore individual metrics and export data for further analysis
        
        **Using Filters:**
        - Use the sidebar filters to focus on specific personas or content categories
        - Adjust score ranges to isolate high-performers or areas needing attention
        - Filters apply across all tabs for consistent analysis
        
        **Interpreting Results:**
        - Focus on patterns rather than individual scores
        - Look for consistency gaps between personas and content types
        - Prioritize improvements based on impact potential and effort required
        """)
        
        # Key Definitions
        st.subheader("📚 Key Definitions")
        
        definitions = {
            "Overall Score": "Average of all six dimensional scores for a persona-content evaluation",
            "Performance Variance": "Difference between highest and lowest scores across content touchpoints for a persona",
            "Improvement Potential": "Gap between current score and good performance threshold (3.5)",
            "Quick Wins": "High-impact, low-effort optimization opportunities identified through systematic analysis",
            "Critical Issues": "Evaluations scoring ≤2.0 requiring immediate attention",
            "Journey Inconsistency": "Significant variance (>1.5 points) in persona experience across touchpoints"
        }
        
        for term, definition in definitions.items():
            st.markdown(f"**{term}:** {definition}")
    
    with tab2:
        # Performance Overview (existing functionality)
        st.header("📊 Performance Overview")
        
        if len(filtered_df) == 0:
            st.warning("No data matches the selected filters.")
            return
        
        # Key metrics for filtered data
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_score = filtered_df['overall'].mean()
            st.metric(
                "Filtered Avg Score",
                f"{avg_score:.2f}/5.0",
                delta=f"{avg_score - insights['executive_summary']['average_score']:.2f} vs. overall"
            )
        
        with col2:
            critical_count = len(filtered_df[filtered_df['overall'] <= 2.0])
            st.metric(
                "Critical Issues",
                critical_count,
                help="Evaluations scoring ≤2.0 in filtered data"
            )
        
        with col3:
            high_perf_count = len(filtered_df[filtered_df['overall'] >= 3.5])
            st.metric(
                "High Performers",
                high_perf_count,
                help="Evaluations scoring ≥3.5 in filtered data"
            )
        
        with col4:
            st.metric(
                "Filtered Records",
                len(filtered_df),
                help="Number of records matching filters"
            )
        
        # Persona performance radar chart
        st.subheader("🎯 Persona Performance Radar")
        
        persona_metrics = filtered_df.groupby('persona')[['headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']].mean()
        
        if len(persona_metrics) > 0:
            fig = go.Figure()
            
            metrics = ['headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']
            metric_labels = ['Headline', 'Content', 'Pain Points', 'Value Prop', 'Trust', 'CTA']
            
            for persona in persona_metrics.index:
                values = persona_metrics.loc[persona, metrics].tolist()
                values.append(values[0])  # Close the radar chart
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=metric_labels + [metric_labels[0]],
                    fill='toself',
                    name=persona,
                    line=dict(width=2)
                ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                showlegend=True,
                title="Persona Performance Across Key Metrics",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Category performance
        st.subheader("📂 Category Performance")
        
        category_scores = filtered_df.groupby('category')['overall'].agg(['mean', 'count']).reset_index()
        category_scores = category_scores.sort_values('mean', ascending=True)
        
        fig = px.bar(
            category_scores,
            x='mean',
            y='category',
            orientation='h',
            color='mean',
            color_continuous_scale=['#F44336', '#FF9800', '#4CAF50'],
            title="Average Score by Content Category",
            labels={'mean': 'Average Score', 'category': 'Content Category'},
            text='count'
        )
        
        fig.update_traces(texttemplate='%{text} evals', textposition='inside')
        fig.update_layout(height=400)
        fig.update_coloraxes(cmin=0, cmax=5)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        create_actionable_examples_tab(data)
    
    with tab4:
        create_strategic_insights_tab(insights)
    
    with tab5:
        create_persona_insights_tab(insights)
    
    with tab6:
        create_competitive_insights_tab(insights)
    
    with tab7:
        # Detailed Analytics (existing functionality)
        st.header("📈 Detailed Analytics")
        
        # Score distribution
        st.subheader("📊 Score Distribution")
        
        fig = px.histogram(
            filtered_df,
            x='overall',
            nbins=20,
            title="Distribution of Overall Scores",
            labels={'overall': 'Overall Score', 'count': 'Number of Evaluations'},
            color_discrete_sequence=['#1f77b4']
        )
        
        fig.add_vline(x=2.0, line_dash="dash", line_color="red", annotation_text="Critical Threshold")
        fig.add_vline(x=3.5, line_dash="dash", line_color="green", annotation_text="Good Performance")
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Persona vs Category heatmap
        st.subheader("🔥 Persona vs Category Performance Heatmap")
        
        heatmap_data = filtered_df.pivot_table(
            values='overall',
            index='persona',
            columns='category',
            aggfunc='mean'
        )
        
        fig = px.imshow(
            heatmap_data,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title="Average Scores: Persona vs Content Category",
            labels={'color': 'Average Score'}
        )
        
        fig.update_layout(height=500)
        fig.update_coloraxes(cmin=0, cmax=5)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab8:
        # Raw Data (existing functionality)
        st.header("📋 Raw Data Analysis & Export")
        
        # Column Analysis Section
        st.subheader("🔍 Column-by-Column Analysis")
        
        # Select metric for detailed analysis
        metric_options = {
            'overall': 'Overall Score',
            'headline': 'Headline Effectiveness',
            'content': 'Content Relevance', 
            'pain_points': 'Pain Point Recognition',
            'value_prop': 'Value Proposition Clarity',
            'trust': 'Trust Signals',
            'cta': 'Call-to-Action Appropriateness'
        }
        
        selected_metric = st.selectbox(
            "Select metric for detailed analysis:",
            options=list(metric_options.keys()),
            format_func=lambda x: metric_options[x],
            help="Choose a specific metric to analyze in detail"
        )
        
        # Metric Analysis
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Distribution by persona
            metric_by_persona = filtered_df.groupby('persona')[selected_metric].agg(['mean', 'std', 'count']).round(2)
            metric_by_persona.columns = ['Average', 'Std Dev', 'Count']
            metric_by_persona = metric_by_persona.sort_values('Average', ascending=False)
            
            # Create bar chart
            fig = px.bar(
                x=metric_by_persona.index,
                y=metric_by_persona['Average'],
                title=f"{metric_options[selected_metric]} by Persona",
                labels={'x': 'Persona', 'y': 'Average Score'},
                color=metric_by_persona['Average'],
                color_continuous_scale=['#F44336', '#FF9800', '#4CAF50'],
                text=metric_by_persona['Average']
            )
            
            fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            fig.add_hline(y=2.0, line_dash="dash", line_color="red", annotation_text="Critical")
            fig.add_hline(y=3.5, line_dash="dash", line_color="green", annotation_text="Good")
            fig.update_coloraxes(cmin=0, cmax=5)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Performance Summary")
            st.dataframe(metric_by_persona, use_container_width=True)
            
            # Performance insights
            best_persona = metric_by_persona.index[0]
            worst_persona = metric_by_persona.index[-1]
            best_score = metric_by_persona.loc[best_persona, 'Average']
            worst_score = metric_by_persona.loc[worst_persona, 'Average']
            
            st.success(f"**Best:** {best_persona} ({best_score:.2f})")
            st.error(f"**Worst:** {worst_persona} ({worst_score:.2f})")
            st.info(f"**Gap:** {best_score - worst_score:.2f} points")
        
        # Persona Narrative Analysis
        st.subheader("👥 Persona-Specific Narratives")
        
        # Select persona for narrative
        selected_persona = st.selectbox(
            "Select persona for detailed narrative:",
            options=filtered_df['persona'].unique(),
            help="Choose a persona to see detailed good/bad analysis"
        )
        
        # Generate persona narrative
        persona_data = filtered_df[filtered_df['persona'] == selected_persona]
        
        if len(persona_data) > 0:
            # Calculate persona metrics
            persona_metrics = {
                'overall': persona_data['overall'].mean(),
                'headline': persona_data['headline'].mean(),
                'content': persona_data['content'].mean(),
                'pain_points': persona_data['pain_points'].mean(),
                'value_prop': persona_data['value_prop'].mean(),
                'trust': persona_data['trust'].mean(),
                'cta': persona_data['cta'].mean()
            }
            
            # Identify strengths and weaknesses
            strengths = {k: v for k, v in persona_metrics.items() if v >= 3.0}
            weaknesses = {k: v for k, v in persona_metrics.items() if v <= 2.0}
            moderate = {k: v for k, v in persona_metrics.items() if 2.0 < v < 3.0}
            
            # Create narrative cards
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### ✅ What's Working Well")
                if strengths:
                    for metric, score in sorted(strengths.items(), key=lambda x: x[1], reverse=True):
                        metric_name = metric_options.get(metric, metric.replace('_', ' ').title())
                        
                        # Get best performing content for this metric
                        best_content = persona_data.nlargest(1, metric)
                        if not best_content.empty:
                            best_category = best_content.iloc[0]['category']
                            best_score = best_content.iloc[0][metric]
                            
                            st.markdown(f"""
                            <div class="success-alert">
                                <strong>{metric_name}</strong> ({score:.2f}/5.0)<br>
                                <small>Best example: {best_category} ({best_score:.1f}/5)</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No strong performance areas identified (≥3.0)")
            
            with col2:
                st.markdown("### ⚠️ Areas Needing Attention")
                if weaknesses:
                    for metric, score in sorted(weaknesses.items(), key=lambda x: x[1]):
                        metric_name = metric_options.get(metric, metric.replace('_', ' ').title())
                        
                        # Get worst performing content for this metric
                        worst_content = persona_data.nsmallest(1, metric)
                        if not worst_content.empty:
                            worst_category = worst_content.iloc[0]['category']
                            worst_score = worst_content.iloc[0][metric]
                            
                            st.markdown(f"""
                            <div class="critical-alert">
                                <strong>{metric_name}</strong> ({score:.2f}/5.0)<br>
                                <small>Worst example: {worst_category} ({worst_score:.1f}/5)</small>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("No critical performance areas identified (≤2.0)")
            
            # Moderate performance areas
            if moderate:
                st.markdown("### 📊 Moderate Performance (Optimization Opportunities)")
                moderate_cols = st.columns(len(moderate))
                for i, (metric, score) in enumerate(sorted(moderate.items(), key=lambda x: x[1], reverse=True)):
                    with moderate_cols[i]:
                        metric_name = metric_options.get(metric, metric.replace('_', ' ').title())
                        improvement_potential = 3.5 - score
                        st.metric(
                            label=metric_name,
                            value=f"{score:.2f}/5.0",
                            delta=f"+{improvement_potential:.1f} potential",
                            help=f"Improvement potential to reach good performance (3.5)"
                        )
            
            # Detailed content breakdown
            st.markdown("### 📊 Content Category Breakdown")
            
            # Category performance for this persona
            category_breakdown = persona_data.groupby('category')[list(metric_options.keys())].mean().round(2)
            
            # Create heatmap for this persona
            fig = px.imshow(
                category_breakdown.T,
                labels=dict(x="Content Category", y="Metric", color="Score"),
                x=category_breakdown.index,
                y=[metric_options[col] for col in category_breakdown.columns],
                color_continuous_scale='RdYlGn',
                aspect="auto",
                title=f"{selected_persona} - Performance Across Content Categories"
            )
            
            fig.update_layout(height=400)
            fig.update_coloraxes(cmin=0, cmax=5)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Extract qualitative insights from evaluation text
            st.markdown("### 📝 Key Insights from Evaluations")
            
            # Sample some evaluation text for insights
            sample_evaluations = persona_data.sample(min(3, len(persona_data)))
            
            for idx, row in sample_evaluations.iterrows():
                with st.expander(f"{row['category']} - Score: {row['overall']:.1f}/5"):
                    # Extract key phrases from evaluation text
                    eval_text = row['evaluation_text']
                    
                    # Look for positive patterns
                    positive_patterns = []
                    negative_patterns = []
                    
                    if 'strong' in eval_text.lower() or 'effective' in eval_text.lower() or 'good' in eval_text.lower():
                        positive_patterns.append("Contains positive language indicators")
                    
                    if 'lacks' in eval_text.lower() or 'missing' in eval_text.lower() or 'poor' in eval_text.lower():
                        negative_patterns.append("Contains improvement opportunity indicators")
                    
                    # Show first 500 characters
                    st.markdown(f"**Evaluation Summary:** {eval_text[:500]}...")
                    
                    if positive_patterns:
                        st.success(f"✅ {', '.join(positive_patterns)}")
                    if negative_patterns:
                        st.warning(f"⚠️ {', '.join(negative_patterns)}")
        
        # Raw Data Export Section
        st.subheader("📥 Data Export")
        
        st.markdown("### 🔍 Filtered Data Preview")
        
        # Show data with better formatting
        display_df = filtered_df[['persona', 'category', 'overall', 'headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']].copy()
        
        # Add performance indicators
        display_df['Performance'] = display_df['overall'].apply(
            lambda x: '🟢 Good' if x >= 3.5 else '🟡 Moderate' if x >= 2.0 else '🔴 Critical'
        )
        
        # Reorder columns
        display_df = display_df[['persona', 'category', 'Performance', 'overall', 'headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']]
        
        st.dataframe(display_df, use_container_width=True)
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = filtered_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv_data,
                file_name=f"sopra_audit_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = filtered_df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Download Filtered Data (JSON)",
                data=json_data,
                file_name=f"sopra_audit_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col3:
            # Create summary report
            summary_data = {
                'persona': [],
                'avg_overall': [],
                'best_metric': [],
                'worst_metric': [],
                'improvement_potential': []
            }
            
            for persona in filtered_df['persona'].unique():
                persona_subset = filtered_df[filtered_df['persona'] == persona]
                metrics = ['headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']
                metric_scores = {m: persona_subset[m].mean() for m in metrics}
                
                summary_data['persona'].append(persona)
                summary_data['avg_overall'].append(persona_subset['overall'].mean())
                summary_data['best_metric'].append(max(metric_scores, key=metric_scores.get))
                summary_data['worst_metric'].append(min(metric_scores, key=metric_scores.get))
                summary_data['improvement_potential'].append(3.5 - persona_subset['overall'].mean())
            
            summary_df = pd.DataFrame(summary_data)
            summary_csv = summary_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Summary Report (CSV)",
                data=summary_csv,
                file_name=f"sopra_audit_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    with tab9:
        # Audit Methodology Issues Tab
        st.header("⚠️ Audit Methodology Issues & Improvements")
        
        st.markdown("""
        This tab identifies where the current audit methodology may be inappropriately evaluating 
        **brand positioning and aspirational content** through narrow persona lenses, and provides 
        guidance for improvement.
        """)
        
        # Load concrete findings to analyze
        try:
            with open('concrete_findings.json', 'r', encoding='utf-8') as f:
                concrete_findings = json.load(f)
        except FileNotFoundError:
            st.error("Concrete findings not found. Please run concrete_findings_extractor.py first.")
            return
        
        # Identify brand positioning issues
        st.subheader("🎯 Brand Positioning vs. Functional Content Issues")
        
        # Define brand positioning indicators
        brand_positioning_indicators = [
            "The world is how we shape it",
            "Drive meaningful impact",
            "Delivering digital transformation that makes life better",
            "Shaping the Future",
            "Empowering",
            "Building a better world"
        ]
        
        # Find problematic evaluations
        brand_positioning_issues = []
        
        for finding in concrete_findings:
            if finding['metric'] == 'headline':
                # Check if this is evaluating brand positioning inappropriately
                quoted_content = finding.get('quoted_content', '')
                detailed_justification = finding.get('detailed_justification', '')
                specific_issue = finding.get('specific_issue', '')
                
                # Look for brand positioning being criticized for lack of persona specificity
                is_brand_positioning = any(indicator in quoted_content or indicator in detailed_justification 
                                         for indicator in brand_positioning_indicators)
                
                is_inappropriate_criticism = any(phrase in specific_issue.lower() or phrase in detailed_justification.lower()
                                               for phrase in [
                                                   'too vague', 'too generic', 'lacks specific', 
                                                   'doesn\'t directly address', 'not specific',
                                                   'lacks the specific language', 'doesn\'t resonate with'
                                               ])
                
                if is_brand_positioning and is_inappropriate_criticism and finding['score'] <= 3.0:
                    brand_positioning_issues.append(finding)
        
        if brand_positioning_issues:
            st.warning(f"Found {len(brand_positioning_issues)} instances where brand positioning may be inappropriately evaluated through persona lenses.")
            
            # Show examples
            st.markdown("### 📋 Problematic Evaluations")
            
            for i, issue in enumerate(brand_positioning_issues[:10], 1):
                with st.expander(f"Issue {i}: {issue['persona']} evaluating '{issue.get('quoted_content', 'Brand positioning')}' ({issue['score']}/5)"):
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**❌ Current Evaluation:**")
                        st.error(f"**Score:** {issue['score']}/5")
                        st.write(f"**Issue:** {issue['specific_issue']}")
                        st.write(f"**Justification:** {issue['detailed_justification']}")
                    
                    with col2:
                        st.markdown("**✅ Recommended Approach:**")
                        st.success("**Should NOT be evaluated by persona specificity**")
                        st.info("""
                        **Brand positioning should be evaluated for:**
                        - Inspirational quality
                        - Memorability
                        - Differentiation from competitors
                        - Emotional resonance
                        - Brand consistency
                        
                        **NOT for:**
                        - Persona-specific relevance
                        - Technical specificity
                        - Functional benefits
                        """)
        else:
            st.success("No obvious brand positioning evaluation issues found.")
        
        # Content hierarchy guidance
        st.subheader("📊 Recommended Content Hierarchy Framework")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="insight-card priority-high">
                <h4>🎯 Tier 1: Brand Positioning</h4>
                <p><strong>Content Type:</strong></p>
                <ul>
                    <li>Main headlines/taglines</li>
                    <li>Mission/vision statements</li>
                    <li>Brand promises</li>
                </ul>
                <p><strong>Evaluation Criteria:</strong></p>
                <ul>
                    <li>Inspirational quality</li>
                    <li>Memorability</li>
                    <li>Differentiation</li>
                    <li>Emotional resonance</li>
                </ul>
                <p><strong>❌ Don't Evaluate:</strong> Persona specificity</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="insight-card priority-medium">
                <h4>🎯 Tier 2: Value Propositions</h4>
                <p><strong>Content Type:</strong></p>
                <ul>
                    <li>Service category descriptions</li>
                    <li>Solution overviews</li>
                    <li>Company positioning</li>
                </ul>
                <p><strong>Evaluation Criteria:</strong></p>
                <ul>
                    <li>Clarity for broad audience</li>
                    <li>Competitive differentiation</li>
                    <li>Strategic relevance</li>
                </ul>
                <p><strong>⚠️ Limited Persona Evaluation</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="insight-card priority-low">
                <h4>🎯 Tier 3: Functional Content</h4>
                <p><strong>Content Type:</strong></p>
                <ul>
                    <li>Specific service descriptions</li>
                    <li>Case studies</li>
                    <li>Technical content</li>
                    <li>Industry solutions</li>
                </ul>
                <p><strong>Evaluation Criteria:</strong></p>
                <ul>
                    <li>Persona-specific relevance</li>
                    <li>Technical accuracy</li>
                    <li>Actionability</li>
                </ul>
                <p><strong>✅ Full Persona Evaluation</strong></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Specific recommendations
        st.subheader("🔧 Methodology Improvement Recommendations")
        
        recommendations = [
            {
                "title": "1. Implement Content Classification",
                "description": "Before evaluation, classify content into Brand Positioning, Value Proposition, or Functional Content tiers.",
                "action": "Add content type field to evaluation framework",
                "impact": "Prevents inappropriate evaluation of aspirational content"
            },
            {
                "title": "2. Separate Evaluation Criteria",
                "description": "Use different scoring criteria for each content tier.",
                "action": "Create tier-specific evaluation rubrics",
                "impact": "More accurate and fair content assessment"
            },
            {
                "title": "3. Brand Positioning Evaluation",
                "description": "Evaluate brand positioning holistically, not through persona lenses.",
                "action": "Create brand-level evaluation separate from persona evaluation",
                "impact": "Better understanding of brand effectiveness"
            },
            {
                "title": "4. Context-Aware Scoring",
                "description": "Weight scores differently based on content type and placement.",
                "action": "Implement weighted scoring system",
                "impact": "More meaningful overall performance metrics"
            }
        ]
        
        for rec in recommendations:
            st.markdown(f"""
            <div class="insight-card priority-medium">
                <h4>{rec['title']}</h4>
                <p><strong>Description:</strong> {rec['description']}</p>
                <p><strong>Action Required:</strong> {rec['action']}</p>
                <p><strong>Expected Impact:</strong> {rec['impact']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Analysis of current issues
        st.subheader("📈 Current Impact Analysis")
        
        # Calculate impact of brand positioning issues
        total_headline_evaluations = len([f for f in concrete_findings if f['metric'] == 'headline'])
        brand_positioning_affected = len(brand_positioning_issues)
        
        if total_headline_evaluations > 0:
            impact_percentage = (brand_positioning_affected / total_headline_evaluations) * 100
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Headline Evaluations", 
                    total_headline_evaluations
                )
            
            with col2:
                st.metric(
                    "Potentially Problematic", 
                    brand_positioning_affected,
                    f"{impact_percentage:.1f}% of headlines"
                )
            
            with col3:
                avg_score_affected = sum(issue['score'] for issue in brand_positioning_issues) / len(brand_positioning_issues) if brand_positioning_issues else 0
                st.metric(
                    "Avg Score (Affected)", 
                    f"{avg_score_affected:.2f}/5.0",
                    "May be artificially low"
                )
        
        # Export recommendations
        st.subheader("📥 Export Methodology Improvements")
        
        methodology_report = {
            "audit_methodology_issues": {
                "total_brand_positioning_issues": len(brand_positioning_issues),
                "affected_evaluations": [
                    {
                        "persona": issue['persona'],
                        "url": issue['url'],
                        "quoted_content": issue.get('quoted_content', ''),
                        "score": issue['score'],
                        "issue": issue['specific_issue']
                    }
                    for issue in brand_positioning_issues
                ],
                "recommendations": recommendations,
                "content_hierarchy_framework": {
                    "tier_1_brand_positioning": {
                        "evaluation_criteria": ["Inspirational quality", "Memorability", "Differentiation", "Emotional resonance"],
                        "avoid_evaluating": ["Persona specificity", "Technical specificity"]
                    },
                    "tier_2_value_propositions": {
                        "evaluation_criteria": ["Clarity for broad audience", "Competitive differentiation", "Strategic relevance"],
                        "limited_persona_evaluation": True
                    },
                    "tier_3_functional_content": {
                        "evaluation_criteria": ["Persona-specific relevance", "Technical accuracy", "Actionability"],
                        "full_persona_evaluation": True
                    }
                }
            }
        }
        
        methodology_json = json.dumps(methodology_report, indent=2)
        
        st.download_button(
            label="📥 Download Methodology Improvement Report (JSON)",
            data=methodology_json,
            file_name=f"audit_methodology_improvements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main() 