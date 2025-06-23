#!/usr/bin/env python3
"""
Example Extractor for Sopra Steria Website Audit
Extracts specific examples, justifications, and recommendations from evaluation text
"""

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

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
    def __init__(self, data_file='dashboard_data.json'):
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
    
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
                # Look for metric sections in the text
                pattern = rf'{re.escape(metric_name)}[^:]*\((\d+(?:\.\d+)?)/5\):\s*(.*?)(?=(?:[A-Z][^:]*\(\d+(?:\.\d+)?/5\):|Recommendation:|Overall Score:|$))'
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                
                if match:
                    score = float(match.group(1))
                    content = match.group(2).strip()
                    
                    # Extract justification and examples
                    justification = ""
                    example_text = ""
                    recommendation = ""
                    
                    # Look for justification
                    just_match = re.search(r'Justification:\s*(.*?)(?=Example:|Recommendation:|$)', content, re.IGNORECASE | re.DOTALL)
                    if just_match:
                        justification = just_match.group(1).strip()
                    else:
                        # If no explicit justification, take first part
                        parts = content.split('Recommendation:')
                        if len(parts) > 0:
                            justification = parts[0].strip()
                    
                    # Look for examples
                    example_patterns = [
                        r'Example[s]?:\s*(.*?)(?=Recommendation:|$)',
                        r'For example[,:]?\s*(.*?)(?=Recommendation:|$)',
                        r'e\.g\.,?\s*(.*?)(?=Recommendation:|$)'
                    ]
                    
                    for pattern in example_patterns:
                        ex_match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
                        if ex_match:
                            example_text = ex_match.group(1).strip()
                            break
                    
                    # Look for recommendations
                    rec_match = re.search(r'Recommendation[s]?:\s*(.*?)$', content, re.IGNORECASE | re.DOTALL)
                    if rec_match:
                        recommendation = rec_match.group(1).strip()
                    
                    examples[metric_key] = {
                        'score': score,
                        'justification': justification,
                        'example': example_text,
                        'recommendation': recommendation
                    }
                    break
        
        return examples
    
    def get_best_and_worst_examples(self) -> Dict[str, List[Example]]:
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
    
    def get_persona_examples(self, persona: str) -> Dict[str, List[Example]]:
        """Get examples for a specific persona"""
        persona_examples = defaultdict(list)
        
        for item in self.data['raw_data']:
            if item['persona'] != persona:
                continue
                
            text = item.get('evaluation_text', '')
            if not text:
                continue
                
            extracted = self.extract_examples_from_text(text)
            
            for metric, details in extracted.items():
                if details['score'] > 0:
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
                    persona_examples[metric].append(example)
        
        # Sort by score for each metric
        for metric in persona_examples:
            persona_examples[metric].sort(key=lambda x: x.score, reverse=True)
        
        return dict(persona_examples)
    
    def get_category_examples(self, category: str) -> Dict[str, List[Example]]:
        """Get examples for a specific content category"""
        category_examples = defaultdict(list)
        
        for item in self.data['raw_data']:
            if item['category'] != category:
                continue
                
            text = item.get('evaluation_text', '')
            if not text:
                continue
                
            extracted = self.extract_examples_from_text(text)
            
            for metric, details in extracted.items():
                if details['score'] > 0:
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
                    category_examples[metric].append(example)
        
        # Sort by score for each metric
        for metric in category_examples:
            category_examples[metric].sort(key=lambda x: x.score, reverse=True)
        
        return dict(category_examples)
    
    def extract_specific_quotes(self, text: str) -> List[str]:
        """Extract specific quotes and examples from evaluation text"""
        quotes = []
        
        # Look for quoted text
        quote_patterns = [
            r'"([^"]+)"',
            r'""([^""]+)""',
            r'Example[s]?:\s*([^.]+\.)',
            r'For example[,:]?\s*([^.]+\.)',
            r'e\.g\.,?\s*([^.]+\.)'
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            quotes.extend(matches)
        
        return [q.strip() for q in quotes if len(q.strip()) > 10]
    
    def generate_actionable_insights(self) -> Dict[str, Any]:
        """Generate actionable insights with specific examples"""
        insights = {
            'best_practices': {},
            'critical_issues': {},
            'quick_wins': {},
            'persona_insights': {},
            'category_insights': {}
        }
        
        examples_by_metric = self.get_best_and_worst_examples()
        
        # Best practices (high-scoring examples)
        for metric, data in examples_by_metric.items():
            best_examples = [ex for ex in data['best'] if ex.score >= 3.5]
            if best_examples:
                insights['best_practices'][metric] = {
                    'examples': best_examples,
                    'common_patterns': self._extract_patterns(best_examples),
                    'recommendations': self._extract_recommendations(best_examples)
                }
        
        # Critical issues (low-scoring examples)
        for metric, data in examples_by_metric.items():
            worst_examples = [ex for ex in data['worst'] if ex.score <= 2.0]
            if worst_examples:
                insights['critical_issues'][metric] = {
                    'examples': worst_examples,
                    'common_problems': self._extract_patterns(worst_examples),
                    'recommendations': self._extract_recommendations(worst_examples)
                }
        
        # Quick wins (moderate scores with clear recommendations)
        for metric, data in examples_by_metric.items():
            moderate_examples = [ex for ex in data['all'] if 2.0 < ex.score < 3.5 and ex.recommendation]
            if moderate_examples:
                insights['quick_wins'][metric] = {
                    'examples': moderate_examples[:5],
                    'improvement_potential': 3.5 - sum(ex.score for ex in moderate_examples) / len(moderate_examples),
                    'recommendations': self._extract_recommendations(moderate_examples)
                }
        
        # Persona-specific insights
        personas = set(item['persona'] for item in self.data['raw_data'])
        for persona in personas:
            persona_examples = self.get_persona_examples(persona)
            if persona_examples:
                insights['persona_insights'][persona] = self._analyze_persona_examples(persona_examples)
        
        # Category-specific insights
        categories = set(item['category'] for item in self.data['raw_data'])
        for category in categories:
            category_examples = self.get_category_examples(category)
            if category_examples:
                insights['category_insights'][category] = self._analyze_category_examples(category_examples)
        
        return insights
    
    def _extract_patterns(self, examples: List[Example]) -> List[str]:
        """Extract common patterns from examples"""
        patterns = []
        
        # Analyze justifications for common themes
        justifications = [ex.justification for ex in examples if ex.justification]
        
        # Look for common keywords and phrases
        common_words = defaultdict(int)
        for just in justifications:
            words = re.findall(r'\b\w+\b', just.lower())
            for word in words:
                if len(word) > 4:  # Skip short words
                    common_words[word] += 1
        
        # Get most common themes
        sorted_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)
        patterns = [word for word, count in sorted_words[:10] if count > 1]
        
        return patterns
    
    def _extract_recommendations(self, examples: List[Example]) -> List[str]:
        """Extract unique recommendations from examples"""
        recommendations = []
        seen = set()
        
        for ex in examples:
            if ex.recommendation and ex.recommendation not in seen:
                recommendations.append(ex.recommendation)
                seen.add(ex.recommendation)
        
        return recommendations[:5]  # Top 5 unique recommendations
    
    def _analyze_persona_examples(self, persona_examples: Dict[str, List[Example]]) -> Dict[str, Any]:
        """Analyze examples for a specific persona"""
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'avg_scores': {},
            'top_recommendations': []
        }
        
        for metric, examples in persona_examples.items():
            if examples:
                avg_score = sum(ex.score for ex in examples) / len(examples)
                analysis['avg_scores'][metric] = avg_score
                
                if avg_score >= 3.0:
                    analysis['strengths'].append({
                        'metric': metric,
                        'score': avg_score,
                        'best_example': examples[0] if examples else None
                    })
                elif avg_score <= 2.0:
                    analysis['weaknesses'].append({
                        'metric': metric,
                        'score': avg_score,
                        'worst_example': examples[-1] if examples else None
                    })
                
                # Collect recommendations
                for ex in examples:
                    if ex.recommendation:
                        analysis['top_recommendations'].append(ex.recommendation)
        
        # Remove duplicate recommendations
        analysis['top_recommendations'] = list(set(analysis['top_recommendations']))[:5]
        
        return analysis
    
    def _analyze_category_examples(self, category_examples: Dict[str, List[Example]]) -> Dict[str, Any]:
        """Analyze examples for a specific content category"""
        analysis = {
            'performance_by_persona': {},
            'avg_scores': {},
            'best_practices': [],
            'improvement_areas': []
        }
        
        # Analyze by persona within category
        personas = set()
        for examples in category_examples.values():
            personas.update(ex.persona for ex in examples)
        
        for persona in personas:
            persona_scores = {}
            for metric, examples in category_examples.items():
                persona_examples = [ex for ex in examples if ex.persona == persona]
                if persona_examples:
                    avg_score = sum(ex.score for ex in persona_examples) / len(persona_examples)
                    persona_scores[metric] = avg_score
            
            if persona_scores:
                analysis['performance_by_persona'][persona] = persona_scores
        
        # Overall metric performance
        for metric, examples in category_examples.items():
            if examples:
                avg_score = sum(ex.score for ex in examples) / len(examples)
                analysis['avg_scores'][metric] = avg_score
                
                if avg_score >= 3.0:
                    analysis['best_practices'].append({
                        'metric': metric,
                        'score': avg_score,
                        'example': examples[0]
                    })
                elif avg_score <= 2.0:
                    analysis['improvement_areas'].append({
                        'metric': metric,
                        'score': avg_score,
                        'example': examples[-1]
                    })
        
        return analysis

def main():
    """Generate example-based insights"""
    extractor = ExampleExtractor()
    
    print("🔍 Extracting specific examples and insights...")
    
    # Generate actionable insights
    insights = extractor.generate_actionable_insights()
    
    # Save insights
    with open('actionable_insights.json', 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, default=str)
    
    print("✅ Actionable insights generated and saved to actionable_insights.json")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"Best Practices identified: {len(insights['best_practices'])}")
    print(f"Critical Issues identified: {len(insights['critical_issues'])}")
    print(f"Quick Wins identified: {len(insights['quick_wins'])}")
    print(f"Persona insights: {len(insights['persona_insights'])}")
    print(f"Category insights: {len(insights['category_insights'])}")

if __name__ == "__main__":
    main() 