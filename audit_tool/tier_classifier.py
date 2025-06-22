"""
Tier Classification Engine
Maps URLs to content tiers based on Sopra Steria Brand Audit Methodology
"""

import re
from typing import Dict, Tuple, Optional
import yaml
from pathlib import Path

class TierClassifier:
    """Classifies pages into content tiers based on URL patterns and content analysis"""
    
    def __init__(self, methodology_path: str = "audit_tool/config/methodology.yaml"):
        self.methodology_path = Path(methodology_path)
        self.tier_config = self._load_tier_config()
        
    def _load_tier_config(self) -> Dict:
        """Load tier configuration from methodology.yaml"""
        try:
            with open(self.methodology_path, 'r') as f:
                methodology = yaml.safe_load(f)
            return methodology.get('classification', {}).get('onsite', {})
        except Exception as e:
            print(f"Warning: Could not load methodology config: {e}")
            return self._get_default_tier_config()
    
    def _get_default_tier_config(self) -> Dict:
        """Fallback tier configuration based on methodology"""
        return {
            'tier_1': {
                'name': 'Brand Positioning',
                'weight_in_onsite': 0.3,
                'brand_percentage': 80,
                'performance_percentage': 20,
                'url_patterns': [
                    r'.*/(index|home)?/?$',  # Homepage
                    r'.*/about.*',           # About pages
                    r'.*/corporate.*',       # Corporate pages
                    r'.*/history.*',         # History pages
                    r'.*/responsibility.*'   # CSR pages
                ],
                'content_triggers': [
                    'the world is how we shape it',
                    'about us',
                    'corporate responsibility',
                    'our story',
                    'our mission'
                ]
            },
            'tier_2': {
                'name': 'Value Propositions', 
                'weight_in_onsite': 0.5,
                'brand_percentage': 50,
                'performance_percentage': 50,
                'url_patterns': [
                    r'.*/services/.*',       # Service pages
                    r'.*/industries/.*',     # Industry pages
                    r'.*/solutions/.*',      # Solution pages
                    r'.*/what-we-do/.*',     # What we do pages
                    r'.*/transformation/.*', # Transformation pages
                    r'.*/consulting/.*'      # Consulting pages
                ],
                'content_triggers': [
                    'ai services',
                    'financial services', 
                    'cloud solutions',
                    'digital transformation',
                    'cybersecurity'
                ]
            },
            'tier_3': {
                'name': 'Functional Content',
                'weight_in_onsite': 0.2, 
                'brand_percentage': 30,
                'performance_percentage': 70,
                'url_patterns': [
                    r'.*/blog.*',           # Blog posts
                    r'.*/news.*',           # News/press
                    r'.*/press.*',          # Press releases
                    r'.*/events.*',         # Events
                    r'.*/insights.*',       # Insights
                    r'.*/case-stud.*',      # Case studies
                    r'.*/white-paper.*',    # White papers
                    r'.*/newsroom.*'        # Newsroom
                ],
                'content_triggers': [
                    'blog',
                    'press release',
                    'case study',
                    'white paper',
                    'thought leadership'
                ]
            }
        }
    
    def classify_url(self, url: str, content: str = "") -> Tuple[str, Dict]:
        """
        Classify a URL into a content tier
        
        Args:
            url: The URL to classify
            content: Optional page content for additional classification
            
        Returns:
            Tuple of (tier_name, tier_config)
        """
        url_lower = url.lower()
        content_lower = content.lower() if content else ""
        
        # Check each tier in priority order (1, 2, 3)
        for tier_key in ['tier_1', 'tier_2', 'tier_3']:
            tier_config = self.tier_config.get(tier_key, {})
            
            # Check URL patterns
            url_patterns = tier_config.get('url_patterns', [])
            for pattern in url_patterns:
                if re.search(pattern, url_lower):
                    return tier_key, tier_config
            
            # Check content triggers if content provided
            if content:
                content_triggers = tier_config.get('content_triggers', [])
                for trigger in content_triggers:
                    if trigger.lower() in content_lower:
                        return tier_key, tier_config
        
        # Default to tier_2 if no match found
        return 'tier_2', self.tier_config.get('tier_2', {})
    
    def get_tier_criteria_weights(self, tier_name: str) -> Dict[str, float]:
        """Get the brand/performance split for a tier"""
        tier_config = self.tier_config.get(tier_name, {})
        return {
            'brand_weight': tier_config.get('brand_percentage', 50) / 100,
            'performance_weight': tier_config.get('performance_percentage', 50) / 100,
            'tier_weight': tier_config.get('weight_in_onsite', 0.33)
        }
    
    def calculate_tier_weighted_score(self, page_scores: Dict, tier_name: str) -> float:
        """Calculate tier-weighted score for a page"""
        weights = self.get_tier_criteria_weights(tier_name)
        
        # Get brand and performance criteria scores
        brand_criteria = ['corporate_positioning_alignment', 'brand_differentiation', 
                         'emotional_resonance', 'visual_brand_integrity',
                         'regional_narrative_integration', 'brand_message_consistency']
        
        performance_criteria = ['strategic_clarity', 'trust_credibility_signals',
                              'strategic_value_clarity', 'solution_sophistication',
                              'executive_relevance', 'business_value_focus']
        
        brand_scores = [page_scores.get(c, 0) for c in brand_criteria if c in page_scores]
        performance_scores = [page_scores.get(c, 0) for c in performance_criteria if c in page_scores]
        
        brand_avg = sum(brand_scores) / len(brand_scores) if brand_scores else 0
        performance_avg = sum(performance_scores) / len(performance_scores) if performance_scores else 0
        
        # Apply tier-specific weighting
        tier_score = (brand_avg * weights['brand_weight'] + 
                     performance_avg * weights['performance_weight'])
        
        return tier_score
    
    def get_all_tier_info(self) -> Dict:
        """Get complete tier configuration information"""
        return {
            tier_key: {
                'name': config.get('name', tier_key),
                'weight': config.get('weight_in_onsite', 0.33),
                'brand_split': config.get('brand_percentage', 50),
                'performance_split': config.get('performance_percentage', 50),
                'description': f"{config.get('name', tier_key)} ({config.get('brand_percentage', 50)}% brand, {config.get('performance_percentage', 50)}% performance)"
            }
            for tier_key, config in self.tier_config.items()
        }

# URL Classification Helper based on audit_urls.md
URL_TIER_MAPPING = {
    # Tier 1 - Brand Positioning
    'soprasteria.nl': 'tier_1',
    'soprasteria.be': 'tier_1', 
    'soprasteria.com': 'tier_1',
    'corporate-responsibility': 'tier_1',
    'history': 'tier_1',
    
    # Tier 2 - Value Propositions  
    'generative-ai': 'tier_2',
    'microsoft-azure': 'tier_2',
    'operations-automation': 'tier_2',
    'financial-services': 'tier_2',
    'retail-logistics': 'tier_2',
    
    # Tier 3 - Functional Content
    'press-releases': 'tier_3',
    'blog': 'tier_3',
    'newsroom': 'tier_3'
}

def quick_classify_from_url_list(url: str) -> str:
    """Quick classification based on known URL patterns from audit_urls.md"""
    url_lower = url.lower()
    
    for pattern, tier in URL_TIER_MAPPING.items():
        if pattern in url_lower:
            return tier
    
    # Default classification logic
    if any(x in url_lower for x in ['/', 'about', 'corporate', 'history']):
        return 'tier_1'
    elif any(x in url_lower for x in ['services', 'industries', 'solutions', 'what-we-do']):
        return 'tier_2'
    elif any(x in url_lower for x in ['blog', 'news', 'press', 'insights']):
        return 'tier_3'
    else:
        return 'tier_2'  # Default to value propositions 