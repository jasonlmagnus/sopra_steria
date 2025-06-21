#!/usr/bin/env python3
"""
Concrete Findings Extractor for Sopra Steria Website Audit
Extracts specific examples, concrete issues, and detailed justifications from evaluation text
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd

@dataclass
class ConcreteFinding:
    persona: str
    category: str
    url: str
    metric: str
    score: float
    specific_issue: str
    concrete_example: str
    detailed_justification: str
    specific_recommendation: str
    quoted_content: str
    quantified_impact: str

class ConcreteFindings:
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
    def extract_concrete_findings(self) -> List[ConcreteFinding]:
        """Extract concrete, specific findings from evaluation text"""
        findings = []
        
        for item in self.data['raw_data']:
            text = item.get('evaluation_text', '')
            if not text:
                continue
            
            # Extract findings for each metric
            metrics = ['headline', 'content', 'pain_points', 'value_prop', 'trust', 'cta']
            
            for metric in metrics:
                finding = self._extract_metric_finding(item, text, metric)
                if finding:
                    findings.append(finding)
        
        return findings
    
    def _extract_metric_finding(self, item: dict, text: str, metric: str) -> Optional[ConcreteFinding]:
        """Extract concrete finding for a specific metric"""
        
        # Define metric patterns
        metric_patterns = {
            'headline': [
                r'Headline Effectiveness[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=Content Relevance|Pain Point|Value Proposition|Trust|CTA|Overall Score|$)',
                r'headline[^:]*\((\d+(?:\.\d+)?)/5\)[^:]*:\s*(.*?)(?=Content|Pain|Value|Trust|CTA|Overall|$)'
            ],
            'content': [
                r'Content Relevance[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=Pain Point|Value Proposition|Trust|CTA|Overall Score|$)',
                r'content[^:]*\((\d+(?:\.\d+)?)/5\)[^:]*:\s*(.*?)(?=Pain|Value|Trust|CTA|Overall|$)'
            ],
            'pain_points': [
                r'Pain Point Recognition[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=Value Proposition|Trust|CTA|Overall Score|$)',
                r'pain[^:]*\((\d+(?:\.\d+)?)/5\)[^:]*:\s*(.*?)(?=Value|Trust|CTA|Overall|$)'
            ],
            'value_prop': [
                r'Value Proposition Clarity[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=Trust|CTA|Overall Score|$)',
                r'value[^:]*\((\d+(?:\.\d+)?)/5\)[^:]*:\s*(.*?)(?=Trust|CTA|Overall|$)'
            ],
            'trust': [
                r'Trust Signals[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=CTA|Overall Score|$)',
                r'trust[^:]*\((\d+(?:\.\d+)?)/5\)[^:]*:\s*(.*?)(?=CTA|Overall|$)'
            ],
            'cta': [
                r'CTA Appropriateness[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=Overall Score|$)',
                r'cta[^:]*\((\d+(?:\.\d+)?)/5\)[^:]*:\s*(.*?)(?=Overall|$)'
            ]
        }
        
        patterns = metric_patterns.get(metric, [])
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                score = float(match.group(1))
                content = match.group(2).strip()
                
                # Extract specific components
                specific_issue = self._extract_specific_issue(content)
                concrete_example = self._extract_concrete_example(content)
                detailed_justification = self._extract_detailed_justification(content)
                specific_recommendation = self._extract_specific_recommendation(content)
                quoted_content = self._extract_quoted_content(content)
                quantified_impact = self._extract_quantified_impact(content)
                
                return ConcreteFinding(
                    persona=item['persona'],
                    category=item['category'],
                    url=item['url'],
                    metric=metric,
                    score=score,
                    specific_issue=specific_issue,
                    concrete_example=concrete_example,
                    detailed_justification=detailed_justification,
                    specific_recommendation=specific_recommendation,
                    quoted_content=quoted_content,
                    quantified_impact=quantified_impact
                )
        
        return None
    
    def _extract_specific_issue(self, content: str) -> str:
        """Extract the specific issue mentioned"""
        issue_patterns = [
            r'(?:lacks?|doesn\'t|missing|fails? to|no mention of|absent|limited|generic|vague|too broad)\s+([^.!?]+[.!?])',
            r'(?:The|This)\s+(?:headline|content|website|page)\s+([^.!?]*(?:lacks?|doesn\'t|missing|fails?)[^.!?]*[.!?])',
            r'(?:However|While|Although)[^,]*,\s*([^.!?]*(?:lacks?|doesn\'t|missing|limited)[^.!?]*[.!?])',
            r'(?:There\'s no|There are no|No explicit)\s+([^.!?]+[.!?])'
        ]
        
        for pattern in issue_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                return max(matches, key=len).strip()
        
        # Fallback: extract first sentence that contains negative indicators
        sentences = re.split(r'[.!?]+', content)
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['lacks', 'doesn\'t', 'missing', 'fails', 'no mention', 'limited', 'generic', 'vague']):
                return sentence.strip()
        
        return ""
    
    def _extract_concrete_example(self, content: str) -> str:
        """Extract concrete examples mentioned"""
        example_patterns = [
            r'"([^"]+)"',  # Quoted text
            r'(?:For example|Example|e\.g\.)[,:]\s*"([^"]+)"',
            r'(?:For example|Example|e\.g\.)[,:]\s*([^.!?]+[.!?])',
            r'(?:such as|like|including)\s+"([^"]+)"',
            r'(?:such as|like|including)\s+([^.!?]+[.!?])',
            r'Examples?:\s*"([^"]+)"',
            r'Examples?:\s*([^.!?]+[.!?])'
        ]
        
        examples = []
        for pattern in example_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            examples.extend(matches)
        
        if examples:
            # Return the longest, most specific example
            return max(examples, key=len).strip()
        
        return ""
    
    def _extract_detailed_justification(self, content: str) -> str:
        """Extract the detailed justification"""
        # Split content by recommendation to get justification part
        parts = re.split(r'Recommendation[s]?:', content, flags=re.IGNORECASE)
        justification_part = parts[0].strip()
        
        # Clean up common prefixes
        justification_part = re.sub(r'^(?:Justification:|Evaluation:)\s*', '', justification_part, flags=re.IGNORECASE)
        
        # Extract the main justification (usually the longest coherent explanation)
        sentences = re.split(r'[.!?]+', justification_part)
        
        # Filter out very short sentences and combine meaningful ones
        meaningful_sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if meaningful_sentences:
            # Take up to 3 most informative sentences
            return '. '.join(meaningful_sentences[:3]) + '.'
        
        return justification_part[:300] + "..." if len(justification_part) > 300 else justification_part
    
    def _extract_specific_recommendation(self, content: str) -> str:
        """Extract specific, actionable recommendations"""
        rec_patterns = [
            r'Recommendation[s]?:\s*(.*?)(?=Example|$)',
            r'Recommend[s]?:\s*(.*?)(?=Example|$)',
            r'Should:\s*(.*?)(?=Example|$)',
            r'Consider:\s*(.*?)(?=Example|$)',
            r'Suggest[s]?:\s*(.*?)(?=Example|$)'
        ]
        
        for pattern in rec_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                rec_text = match.group(1).strip()
                
                # Extract specific actionable items
                specific_actions = []
                
                # Look for bullet points or numbered items
                bullet_matches = re.findall(r'(?:•|-|\d+\.)\s*([^•\-\d][^.!?]*[.!?])', rec_text)
                if bullet_matches:
                    specific_actions.extend(bullet_matches)
                
                # Look for "Examples:" sections
                example_matches = re.findall(r'Examples?:\s*([^.!?]+[.!?])', rec_text, re.IGNORECASE)
                if example_matches:
                    specific_actions.extend(example_matches)
                
                # If no structured recommendations, take the main recommendation text
                if not specific_actions:
                    sentences = re.split(r'[.!?]+', rec_text)
                    specific_actions = [s.strip() for s in sentences if len(s.strip()) > 10][:2]
                
                return ' '.join(specific_actions).strip()
        
        return ""
    
    def _extract_quoted_content(self, content: str) -> str:
        """Extract any quoted content that shows specific examples"""
        quotes = re.findall(r'"([^"]+)"', content)
        if quotes:
            # Return the longest quote as it's likely the most specific
            return max(quotes, key=len)
        return ""
    
    def _extract_quantified_impact(self, content: str) -> str:
        """Extract any quantified impacts or statistics mentioned"""
        quantity_patterns = [
            r'(\d+%[^.!?]*[.!?])',
            r'(\d+\+[^.!?]*[.!?])',
            r'(\d+/\d+[^.!?]*[.!?])',
            r'(only \d+%[^.!?]*[.!?])',
            r'(\d+ out of \d+[^.!?]*[.!?])',
            r'(\d+:\d+[^.!?]*[.!?])'
        ]
        
        quantities = []
        for pattern in quantity_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            quantities.extend(matches)
        
        if quantities:
            return max(quantities, key=len).strip()
        
        return ""
    
    def generate_concrete_insights_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report with concrete findings"""
        findings = self.extract_concrete_findings()
        
        # Organize findings
        insights = {
            'total_concrete_findings': len(findings),
            'findings_by_persona': defaultdict(list),
            'findings_by_metric': defaultdict(list),
            'critical_issues': [],
            'best_practices': [],
            'specific_recommendations': defaultdict(list),
            'quantified_impacts': [],
            'concrete_examples': []
        }
        
        for finding in findings:
            insights['findings_by_persona'][finding.persona].append(finding)
            insights['findings_by_metric'][finding.metric].append(finding)
            
            # Categorize findings
            if finding.score <= 2.0 and finding.specific_issue:
                insights['critical_issues'].append({
                    'persona': finding.persona,
                    'category': finding.category,
                    'metric': finding.metric,
                    'score': finding.score,
                    'issue': finding.specific_issue,
                    'example': finding.concrete_example,
                    'recommendation': finding.specific_recommendation
                })
            
            if finding.score >= 3.5 and finding.detailed_justification:
                insights['best_practices'].append({
                    'persona': finding.persona,
                    'category': finding.category,
                    'metric': finding.metric,
                    'score': finding.score,
                    'what_works': finding.detailed_justification,
                    'example': finding.concrete_example
                })
            
            if finding.specific_recommendation:
                insights['specific_recommendations'][finding.metric].append({
                    'persona': finding.persona,
                    'category': finding.category,
                    'score': finding.score,
                    'recommendation': finding.specific_recommendation,
                    'context': finding.specific_issue
                })
            
            if finding.quantified_impact:
                insights['quantified_impacts'].append({
                    'persona': finding.persona,
                    'metric': finding.metric,
                    'impact': finding.quantified_impact,
                    'context': finding.detailed_justification
                })
            
            if finding.concrete_example:
                insights['concrete_examples'].append({
                    'persona': finding.persona,
                    'category': finding.category,
                    'metric': finding.metric,
                    'score': finding.score,
                    'example': finding.concrete_example,
                    'quoted_content': finding.quoted_content
                })
        
        return insights
    
    def save_concrete_findings(self):
        """Save concrete findings to JSON file"""
        findings = self.extract_concrete_findings()
        insights = self.generate_concrete_insights_report()
        
        # Convert findings to serializable format
        findings_data = []
        for finding in findings:
            findings_data.append({
                'persona': finding.persona,
                'category': finding.category,
                'url': finding.url,
                'metric': finding.metric,
                'score': finding.score,
                'specific_issue': finding.specific_issue,
                'concrete_example': finding.concrete_example,
                'detailed_justification': finding.detailed_justification,
                'specific_recommendation': finding.specific_recommendation,
                'quoted_content': finding.quoted_content,
                'quantified_impact': finding.quantified_impact
            })
        
        # Save to files
        with open('concrete_findings.json', 'w', encoding='utf-8') as f:
            json.dump(findings_data, f, indent=2, ensure_ascii=False)
        
        with open('concrete_insights.json', 'w', encoding='utf-8') as f:
            json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Extracted {len(findings)} concrete findings")
        print(f"✅ Identified {len(insights['critical_issues'])} critical issues with specific examples")
        print(f"✅ Found {len(insights['best_practices'])} best practices with concrete justifications")
        print(f"✅ Generated {len(insights['quantified_impacts'])} quantified impact statements")
        
        return insights

if __name__ == "__main__":
    extractor = ConcreteFindings()
    insights = extractor.save_concrete_findings()
    
    # Print sample findings
    print("\n🔍 Sample Critical Issues:")
    for issue in insights['critical_issues'][:3]:
        print(f"- {issue['persona']} | {issue['metric']}: {issue['issue']}")
        if issue['example']:
            print(f"  Example: {issue['example']}")
        print()
    
    print("\n✅ Sample Best Practices:")
    for practice in insights['best_practices'][:3]:
        print(f"- {practice['persona']} | {practice['metric']}: {practice['what_works'][:100]}...")
        print() 