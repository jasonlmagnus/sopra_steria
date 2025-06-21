#!/usr/bin/env python3
"""
Strategic Insights Analysis for Sopra Steria Website Audit
Extracts deeper strategic narratives from quantitative scores and qualitative evaluation text
"""

import json
import re
from collections import defaultdict, Counter
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class StrategicInsight:
    category: str
    title: str
    description: str
    evidence: List[str]
    recommendations: List[str]
    priority: str
    impact_potential: str
    personas_affected: List[str]
    content_areas: List[str]

class StrategicAnalyzer:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.raw_data = self.data['raw_data']
        
    def extract_recommendation_themes(self):
        """Extract common recommendation themes from evaluation text"""
        themes = defaultdict(list)
        
        for item in self.raw_data:
            text = item.get('evaluation_text', '')
            
            # Extract recommendations using regex
            recommendations = re.findall(r'Recommendation[s]?:([^.]*(?:\.[^.]*)*)', text, re.IGNORECASE | re.DOTALL)
            
            for rec in recommendations:
                # Clean and categorize recommendations
                rec_clean = rec.strip()
                if len(rec_clean) > 50:  # Filter out very short matches
                    # Categorize by keywords
                    if any(word in rec_clean.lower() for word in ['headline', 'title']):
                        themes['headline_optimization'].append({
                            'text': rec_clean[:200] + '...' if len(rec_clean) > 200 else rec_clean,
                            'persona': item['persona'],
                            'category': item['category'],
                            'score': item.get('headline', 0)
                        })
                    elif any(word in rec_clean.lower() for word in ['content', 'section', 'case study', 'white paper']):
                        themes['content_development'].append({
                            'text': rec_clean[:200] + '...' if len(rec_clean) > 200 else rec_clean,
                            'persona': item['persona'],
                            'category': item['category'],
                            'score': item.get('content', 0)
                        })
                    elif any(word in rec_clean.lower() for word in ['trust', 'credential', 'certification', 'testimonial']):
                        themes['trust_building'].append({
                            'text': rec_clean[:200] + '...' if len(rec_clean) > 200 else rec_clean,
                            'persona': item['persona'],
                            'category': item['category'],
                            'score': item.get('trust', 0)
                        })
                    elif any(word in rec_clean.lower() for word in ['cta', 'call to action', 'contact', 'assessment']):
                        themes['cta_optimization'].append({
                            'text': rec_clean[:200] + '...' if len(rec_clean) > 200 else rec_clean,
                            'persona': item['persona'],
                            'category': item['category'],
                            'score': item.get('cta', 0)
                        })
                    elif any(word in rec_clean.lower() for word in ['pain point', 'challenge', 'acknowledge']):
                        themes['pain_point_recognition'].append({
                            'text': rec_clean[:200] + '...' if len(rec_clean) > 200 else rec_clean,
                            'persona': item['persona'],
                            'category': item['category'],
                            'score': item.get('pain_points', 0)
                        })
                    elif any(word in rec_clean.lower() for word in ['value proposition', 'roi', 'benefit', 'quantify']):
                        themes['value_proposition'].append({
                            'text': rec_clean[:200] + '...' if len(rec_clean) > 200 else rec_clean,
                            'persona': item['persona'],
                            'category': item['category'],
                            'score': item.get('value_prop', 0)
                        })
        
        return themes
    
    def identify_success_patterns(self):
        """Identify what's working well across high-performing content"""
        success_patterns = []
        
        # Find high-performing evaluations (overall score >= 3.5)
        high_performers = [item for item in self.raw_data if item.get('overall', 0) >= 3.5]
        
        if high_performers:
            # Analyze what makes them successful
            success_categories = Counter([item['category'] for item in high_performers])
            success_personas = Counter([item['persona'] for item in high_performers])
            
            # Extract positive justifications
            positive_patterns = []
            for item in high_performers:
                text = item.get('evaluation_text', '')
                # Look for positive justifications
                positive_matches = re.findall(r'Justification:([^.]*(?:\.[^.]*)*?)(?:Recommendation|$)', text, re.IGNORECASE | re.DOTALL)
                for match in positive_matches:
                    if any(word in match.lower() for word in ['strong', 'effective', 'good', 'excellent', 'demonstrates', 'showcases']):
                        positive_patterns.append({
                            'text': match.strip()[:150] + '...' if len(match.strip()) > 150 else match.strip(),
                            'persona': item['persona'],
                            'category': item['category'],
                            'overall_score': item.get('overall', 0)
                        })
            
            success_patterns.append(StrategicInsight(
                category="success_patterns",
                title="High-Performance Content Characteristics",
                description=f"Analysis of {len(high_performers)} high-performing evaluations reveals key success factors",
                evidence=[
                    f"Best performing categories: {', '.join([f'{cat} ({count} instances)' for cat, count in success_categories.most_common(3)])}",
                    f"Most successful personas: {', '.join([f'{persona} ({count} instances)' for persona, count in success_personas.most_common(3)])}",
                    f"Common positive elements: {len(positive_patterns)} instances of strong performance identified"
                ],
                recommendations=[
                    "Replicate successful elements from high-performing content across other categories",
                    "Study the specific approaches that work well for top-performing personas",
                    "Apply proven patterns to underperforming content areas"
                ],
                priority="high",
                impact_potential="high",
                personas_affected=list(success_personas.keys()),
                content_areas=list(success_categories.keys())
            ))
        
        return success_patterns
    
    def identify_critical_gaps(self):
        """Identify critical performance gaps and failure patterns"""
        critical_gaps = []
        
        # Find low-performing evaluations (overall score <= 2.0)
        low_performers = [item for item in self.raw_data if item.get('overall', 0) <= 2.0]
        
        if low_performers:
            # Analyze failure patterns
            failure_categories = Counter([item['category'] for item in low_performers])
            failure_personas = Counter([item['persona'] for item in low_performers])
            
            # Analyze category-specific weaknesses
            category_weaknesses = defaultdict(list)
            for item in low_performers:
                for metric in ['headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']:
                    score = item.get(metric, 0)
                    if score <= 1.5:  # Critical weakness
                        category_weaknesses[metric].append({
                            'category': item['category'],
                            'persona': item['persona'],
                            'score': score
                        })
            
            critical_gaps.append(StrategicInsight(
                category="critical_gaps",
                title="Critical Performance Gaps Requiring Immediate Attention",
                description=f"Analysis of {len(low_performers)} underperforming evaluations reveals systemic issues",
                evidence=[
                    f"Worst performing categories: {', '.join([f'{cat} ({count} instances)' for cat, count in failure_categories.most_common(3)])}",
                    f"Most challenged personas: {', '.join([f'{persona} ({count} instances)' for persona, count in failure_personas.most_common(3)])}",
                    f"Critical weaknesses by metric: {', '.join([f'{metric} ({len(items)} critical scores)' for metric, items in category_weaknesses.items() if len(items) >= 3])}"
                ],
                recommendations=[
                    "Prioritize immediate fixes for categories with multiple critical scores",
                    "Develop persona-specific content strategies for underperforming audiences",
                    "Address systemic issues in trust signals and pain point recognition"
                ],
                priority="critical",
                impact_potential="high",
                personas_affected=list(failure_personas.keys()),
                content_areas=list(failure_categories.keys())
            ))
        
        return critical_gaps
    
    def analyze_persona_journey_gaps(self):
        """Analyze gaps in persona-specific customer journeys"""
        persona_insights = []
        
        # Group by persona and analyze journey consistency
        persona_data = defaultdict(list)
        for item in self.raw_data:
            persona_data[item['persona']].append(item)
        
        for persona, items in persona_data.items():
            # Calculate average scores by category
            category_scores = defaultdict(list)
            for item in items:
                category_scores[item['category']].append(item.get('overall', 0))
            
            avg_scores = {cat: sum(scores)/len(scores) for cat, scores in category_scores.items()}
            
            # Identify journey inconsistencies
            score_variance = max(avg_scores.values()) - min(avg_scores.values()) if avg_scores else 0
            
            if score_variance > 1.5:  # Significant inconsistency
                best_category = max(avg_scores.items(), key=lambda x: x[1])
                worst_category = min(avg_scores.items(), key=lambda x: x[1])
                
                # Extract specific pain points for this persona
                persona_pain_points = []
                for item in items:
                    text = item.get('evaluation_text', '')
                    pain_matches = re.findall(r'pain point[s]?[^.]*\.', text, re.IGNORECASE)
                    persona_pain_points.extend(pain_matches)
                
                persona_insights.append(StrategicInsight(
                    category="persona_journey",
                    title=f"{persona} Journey Inconsistency",
                    description=f"Significant performance variance ({score_variance:.1f} points) across content touchpoints",
                    evidence=[
                        f"Best performing: {best_category[0]} (avg: {best_category[1]:.2f})",
                        f"Worst performing: {worst_category[0]} (avg: {worst_category[1]:.2f})",
                        f"Journey touchpoints analyzed: {len(avg_scores)}",
                        f"Specific pain points identified: {len(set(persona_pain_points))}"
                    ],
                    recommendations=[
                        f"Standardize successful elements from {best_category[0]} across all {persona} touchpoints",
                        f"Prioritize improvements to {worst_category[0]} content for {persona}",
                        "Develop cohesive persona journey mapping and content strategy",
                        "Address identified pain points with targeted content solutions"
                    ],
                    priority="high" if score_variance > 2.0 else "medium",
                    impact_potential="high",
                    personas_affected=[persona],
                    content_areas=list(avg_scores.keys())
                ))
        
        return persona_insights
    
    def identify_quick_wins(self):
        """Identify high-impact, low-effort optimization opportunities"""
        quick_wins = []
        
        # Find content with moderate scores that could be easily improved
        moderate_performers = [item for item in self.raw_data if 2.0 < item.get('overall', 0) < 3.5]
        
        # Analyze specific metrics that are dragging down overall scores
        improvement_opportunities = defaultdict(list)
        
        for item in moderate_performers:
            overall = item.get('overall', 0)
            for metric in ['headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']:
                score = item.get(metric, 0)
                if score < overall - 0.5:  # Metric significantly below overall
                    improvement_opportunities[metric].append({
                        'category': item['category'],
                        'persona': item['persona'],
                        'current_score': score,
                        'overall_score': overall,
                        'improvement_potential': overall - score
                    })
        
        # Identify the most common quick win opportunities
        for metric, opportunities in improvement_opportunities.items():
            if len(opportunities) >= 5:  # Significant pattern
                avg_potential = sum([opp['improvement_potential'] for opp in opportunities]) / len(opportunities)
                
                quick_wins.append(StrategicInsight(
                    category="quick_wins",
                    title=f"{metric.replace('_', ' ').title()} Optimization Opportunity",
                    description=f"Systematic underperformance in {metric} across {len(opportunities)} evaluations",
                    evidence=[
                        f"Average improvement potential: {avg_potential:.2f} points",
                        f"Affected content pieces: {len(opportunities)}",
                        f"Most affected categories: {', '.join(set([opp['category'] for opp in opportunities[:3]]))}",
                        f"Most affected personas: {', '.join(set([opp['persona'] for opp in opportunities[:3]]))}"
                    ],
                    recommendations=[
                        f"Implement standardized {metric} improvements across identified content",
                        f"Create templates and guidelines for {metric} optimization",
                        f"Prioritize {metric} fixes for highest-impact content pieces",
                        "Measure and track improvements after implementation"
                    ],
                    priority="medium",
                    impact_potential="medium",
                    personas_affected=list(set([opp['persona'] for opp in opportunities])),
                    content_areas=list(set([opp['category'] for opp in opportunities]))
                ))
        
        return quick_wins
    
    def analyze_competitive_positioning(self):
        """Analyze competitive positioning based on evaluation feedback"""
        positioning_insights = []
        
        # Extract mentions of competitive elements, partnerships, and differentiators
        competitive_mentions = []
        partnership_mentions = []
        differentiator_mentions = []
        
        for item in self.raw_data:
            text = item.get('evaluation_text', '')
            
            # Look for competitive/partnership mentions
            if any(word in text.lower() for word in ['microsoft', 'aws', 'google', 'sap', 'oracle']):
                partnership_mentions.append({
                    'text': text,
                    'persona': item['persona'],
                    'category': item['category'],
                    'trust_score': item.get('trust', 0)
                })
            
            # Look for differentiator mentions
            if any(word in text.lower() for word in ['unique', 'differentiator', 'competitive', 'advantage']):
                differentiator_mentions.append({
                    'text': text,
                    'persona': item['persona'],
                    'category': item['category'],
                    'value_prop_score': item.get('value_prop', 0)
                })
        
        if partnership_mentions:
            positioning_insights.append(StrategicInsight(
                category="competitive_positioning",
                title="Partnership Leverage Opportunity",
                description=f"Strategic partnerships mentioned in {len(partnership_mentions)} evaluations but not fully leveraged",
                evidence=[
                    f"Partnership mentions across {len(set([p['persona'] for p in partnership_mentions]))} personas",
                    f"Average trust score where partnerships mentioned: {sum([p['trust_score'] for p in partnership_mentions])/len(partnership_mentions):.2f}",
                    "Key partnerships: Microsoft, AWS, SAP identified as trust signals"
                ],
                recommendations=[
                    "Prominently feature strategic partnerships in trust signal sections",
                    "Develop partnership-specific case studies and success stories",
                    "Leverage partner certifications and credentials more effectively",
                    "Create co-branded content with key technology partners"
                ],
                priority="medium",
                impact_potential="medium",
                personas_affected=list(set([p['persona'] for p in partnership_mentions])),
                content_areas=list(set([p['category'] for p in partnership_mentions]))
            ))
        
        return positioning_insights
    
    def generate_strategic_narrative(self):
        """Generate comprehensive strategic narrative"""
        print("🔍 Analyzing strategic patterns...")
        
        # Run all analyses
        recommendation_themes = self.extract_recommendation_themes()
        success_patterns = self.identify_success_patterns()
        critical_gaps = self.identify_critical_gaps()
        persona_insights = self.analyze_persona_journey_gaps()
        quick_wins = self.identify_quick_wins()
        competitive_insights = self.analyze_competitive_positioning()
        
        # Combine all insights
        all_insights = (success_patterns + critical_gaps + persona_insights + 
                       quick_wins + competitive_insights)
        
        # Generate executive summary
        total_evaluations = len(self.raw_data)
        avg_overall = sum([item.get('overall', 0) for item in self.raw_data]) / total_evaluations
        
        critical_count = len([item for item in self.raw_data if item.get('overall', 0) <= 2.0])
        high_performing_count = len([item for item in self.raw_data if item.get('overall', 0) >= 3.5])
        
        narrative = {
            'executive_summary': {
                'total_evaluations': total_evaluations,
                'average_score': round(avg_overall, 2),
                'critical_issues': critical_count,
                'high_performers': high_performing_count,
                'improvement_opportunity': f"{((3.5 - avg_overall) / 3.5 * 100):.1f}% potential improvement to reach good performance threshold"
            },
            'recommendation_themes': recommendation_themes,
            'strategic_insights': all_insights,
            'priority_actions': [insight for insight in all_insights if insight.priority == 'critical'],
            'quick_wins': [insight for insight in all_insights if insight.category == 'quick_wins']
        }
        
        return narrative
    
    def create_strategic_report(self, narrative, output_file='strategic_insights_report.md'):
        """Create detailed strategic insights report"""
        
        report = f"""# Sopra Steria Website Audit: Strategic Insights & Narrative Analysis

## Executive Summary

### Performance Overview
- **Total Evaluations Analyzed:** {narrative['executive_summary']['total_evaluations']}
- **Current Average Score:** {narrative['executive_summary']['average_score']}/5.0
- **Critical Issues:** {narrative['executive_summary']['critical_issues']} evaluations scoring ≤2.0
- **High Performers:** {narrative['executive_summary']['high_performers']} evaluations scoring ≥3.5
- **Improvement Potential:** {narrative['executive_summary']['improvement_opportunity']}

### Strategic Situation
The audit reveals a **significant optimization opportunity** across all personas and content categories. While some content performs well, systemic issues in trust signals, pain point recognition, and calls-to-action are limiting overall effectiveness.

## Critical Priority Actions

"""
        
        for insight in narrative['priority_actions']:
            report += f"""### 🚨 {insight.title}
**Impact:** {insight.impact_potential} | **Affected Personas:** {', '.join(insight.personas_affected)}

{insight.description}

**Evidence:**
{chr(10).join([f"- {evidence}" for evidence in insight.evidence])}

**Immediate Actions:**
{chr(10).join([f"- {rec}" for rec in insight.recommendations])}

---

"""
        
        report += """## Strategic Insights by Category

"""
        
        # Group insights by category
        insights_by_category = defaultdict(list)
        for insight in narrative['strategic_insights']:
            insights_by_category[insight.category].append(insight)
        
        for category, insights in insights_by_category.items():
            report += f"""### {category.replace('_', ' ').title()}

"""
            for insight in insights:
                priority_emoji = {'critical': '🚨', 'high': '⚠️', 'medium': '📊', 'low': 'ℹ️'}
                report += f"""#### {priority_emoji.get(insight.priority, '📊')} {insight.title}
{insight.description}

**Evidence:**
{chr(10).join([f"- {evidence}" for evidence in insight.evidence])}

**Recommendations:**
{chr(10).join([f"- {rec}" for rec in insight.recommendations])}

**Affected Areas:** {', '.join(insight.content_areas)}
**Personas:** {', '.join(insight.personas_affected)}

---

"""
        
        report += """## Quick Wins Implementation Roadmap

### Phase 1: Immediate Fixes (0-30 days)
"""
        
        quick_wins = narrative['quick_wins']
        if quick_wins:
            for i, win in enumerate(quick_wins[:3], 1):
                report += f"""
{i}. **{win.title}**
   - Impact: {win.impact_potential}
   - Effort: Low-Medium
   - Affected: {len(win.personas_affected)} personas, {len(win.content_areas)} content areas
   - Key Action: {win.recommendations[0] if win.recommendations else 'See detailed recommendations above'}
"""
        
        report += """
### Phase 2: Strategic Improvements (30-90 days)
- Implement persona-specific content strategies
- Develop comprehensive trust signal framework
- Create standardized pain point recognition approach
- Launch A/B testing program for optimizations

### Phase 3: Advanced Optimization (90+ days)
- Deploy advanced personalization
- Implement dynamic content optimization
- Launch comprehensive measurement and analytics framework
- Establish continuous improvement processes

## Recommendation Themes Analysis

"""
        
        themes = narrative['recommendation_themes']
        for theme, recommendations in themes.items():
            if recommendations:
                report += f"""### {theme.replace('_', ' ').title()}
**Frequency:** {len(recommendations)} mentions across evaluations

**Common Patterns:**
{chr(10).join([f"- {rec['text'][:100]}... (Score: {rec['score']}, Persona: {rec['persona']})" for rec in recommendations[:3]])}

**Strategic Implication:** This theme appears consistently across multiple personas and content areas, indicating a systematic opportunity for improvement.

---

"""
        
        report += """## Implementation Framework

### Success Metrics
- **Overall Score Improvement:** Target 3.5+ average (currently {})
- **Critical Issues Reduction:** Reduce from {} to <5 evaluations
- **Persona Consistency:** Achieve <1.0 variance across content touchpoints
- **Trust Signal Effectiveness:** Improve trust scores to 3.5+ average

### Resource Requirements
- **Content Strategy Team:** 2-3 FTE for 90 days
- **Technical Implementation:** 1-2 FTE for optimization
- **Measurement & Analytics:** 1 FTE ongoing
- **Executive Sponsorship:** Required for cross-functional coordination

### Risk Mitigation
- **Change Management:** Phased rollout to minimize disruption
- **Quality Assurance:** A/B testing for all major changes
- **Stakeholder Alignment:** Regular review cycles with persona representatives
- **Performance Monitoring:** Real-time tracking of key metrics

---

*Report generated from comprehensive analysis of {} evaluations across {} personas and {} content categories*
""".format(
            narrative['executive_summary']['average_score'],
            narrative['executive_summary']['critical_issues'],
            narrative['executive_summary']['total_evaluations'],
            len(set([item['persona'] for item in self.raw_data])),
            len(set([item['category'] for item in self.raw_data]))
        )
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📊 Strategic insights report saved to {output_file}")
        return report

# Main execution
if __name__ == "__main__":
    print("🚀 Starting Strategic Insights Analysis...")
    
    analyzer = StrategicAnalyzer()
    narrative = analyzer.generate_strategic_narrative()
    
    # Save detailed analysis
    with open('strategic_narrative.json', 'w', encoding='utf-8') as f:
        json.dump(narrative, f, indent=2, ensure_ascii=False, default=str)
    
    # Create strategic report
    report = analyzer.create_strategic_report(narrative)
    
    print("\n✅ Strategic Analysis Complete!")
    print("Files created:")
    print("- strategic_insights_report.md (Executive strategic report)")
    print("- strategic_narrative.json (Detailed analysis data)")
    print("\nKey Findings:")
    print(f"- {len(narrative['strategic_insights'])} strategic insights identified")
    print(f"- {len(narrative['priority_actions'])} critical priority actions")
    print(f"- {len(narrative['quick_wins'])} quick win opportunities")
    print(f"- {narrative['executive_summary']['improvement_opportunity']} improvement potential") 