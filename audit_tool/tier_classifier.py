"""
Tier Classifier for Brand Audit Tool

STATUS: ACTIVE

This module provides URL classification functionality that:
1. Determines the appropriate tier (Tier 1, 2, 3) for onsite content
2. Classifies offsite content into channel types (Owned, Influenced, Independent)
3. Applies pattern matching and rule-based classification
4. Supports the methodology-driven evaluation approach
5. Enables consistent scoring across different content types

The classifier uses URL patterns, content indicators, and predefined rules
to ensure appropriate evaluation criteria are applied to each digital touchpoint.
"""

import re
import logging
from typing import Tuple, Dict, Any, List, Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class TierClassifier:
    """Classifies URLs into appropriate tiers and channel types."""
    
    def __init__(self, methodology_config: Dict[str, Any] = None):
        """
        Initialize with optional methodology configuration.
        
        Args:
            methodology_config: Dictionary containing classification rules
        """
        self.config = methodology_config or {}
        
        # Default classification patterns if not provided in config
        self.tier_patterns = self.config.get('tier_patterns', {
            'tier_1': [
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/?$',  # Homepage
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/about-us/?$',  # About pages
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/industries/?$',  # Industry overview
            ],
            'tier_2': [
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/industries/[^/]+/?$',  # Industry pages
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/what-we-do/[^/]+/?$',  # Service pages
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/about-us/[^/]+/?$',  # About subpages
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/newsroom/[^/]+/?$',  # News section
            ],
            'tier_3': [
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/industries/[^/]+/[^/]+/?',  # Deep industry pages
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/what-we-do/[^/]+/[^/]+/?',  # Deep service pages
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/newsroom/[^/]+/details/[^/]+/?$',  # News articles
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)/contact-us/?',  # Contact pages
            ]
        })
        
        # Default channel patterns
        self.channel_patterns = self.config.get('channel_patterns', {
            'owned': [
                r'^https?://(?:www\.)?soprasteria\.(?:com|be|nl)',  # Main websites
                r'^https?://(?:www\.)?youtube\.com/SopraSteria',  # YouTube channel
            ],
            'influenced': [
                r'^https?://(?:www\.)?linkedin\.com/company/soprasteria',  # LinkedIn
                r'^https?://(?:www\.)?twitter\.com/soprasteria',  # Twitter
                r'^https?://(?:www\.)?facebook\.com/soprasteria',  # Facebook
            ],
            'independent': [
                r'^https?://(?:www\.)?nl\.digital\.nl',  # Industry sites
                r'^https?://(?:www\.)?(?!soprasteria)[^/]+\.[^/]+/.*sopra.*steria',  # Mentions on other sites
            ]
        })
        
        # Default fallback tiers
        self.default_tier = 'tier_2'
        self.default_channel = 'owned'
    
    def classify_url(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify a URL into the appropriate tier or channel.
        
        Args:
            url: The URL to classify
            
        Returns:
            Tuple of (tier_name, tier_config)
        """
        logger.debug(f"Classifying URL: {url}")
        
        # Check if this is an onsite or offsite URL
        if self._is_onsite(url):
            return self._classify_onsite(url)
        else:
            return self._classify_offsite(url)
    
    def _is_onsite(self, url: str) -> bool:
        """
        Determine if a URL is onsite or offsite.
        
        Args:
            url: The URL to check
            
        Returns:
            True if onsite, False if offsite
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Check if domain is a Sopra Steria domain
        onsite_domains = [
            'soprasteria.com',
            'soprasteria.be',
            'soprasteria.nl',
            'www.soprasteria.com',
            'www.soprasteria.be',
            'www.soprasteria.nl'
        ]
        
        return any(domain == d or domain.endswith('.' + d) for d in onsite_domains)
    
    def _classify_onsite(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify an onsite URL into the appropriate tier.
        
        Args:
            url: The URL to classify
            
        Returns:
            Tuple of (tier_name, tier_config)
        """
        # Check each tier pattern
        for tier_name, patterns in self.tier_patterns.items():
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    logger.debug(f"URL {url} classified as {tier_name}")
                    return tier_name, self._get_tier_config(tier_name)
        
        # If no match, use default tier
        logger.debug(f"URL {url} defaulted to {self.default_tier}")
        return self.default_tier, self._get_tier_config(self.default_tier)
    
    def _classify_offsite(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify an offsite URL into the appropriate channel.
        
        Args:
            url: The URL to classify
            
        Returns:
            Tuple of (channel_name, channel_config)
        """
        # Check each channel pattern
        for channel_name, patterns in self.channel_patterns.items():
            for pattern in patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    logger.debug(f"URL {url} classified as {channel_name}")
                    return channel_name, self._get_channel_config(channel_name)
        
        # If no match, use default channel
        logger.debug(f"URL {url} defaulted to {self.default_channel}")
        return self.default_channel, self._get_channel_config(self.default_channel)
    
    def _get_tier_config(self, tier_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a tier.
        
        Args:
            tier_name: The name of the tier
            
        Returns:
            Dictionary of tier configuration
        """
        # Get tier configuration from methodology config
        if self.config and 'classification' in self.config:
            tier_config = self.config.get('classification', {}).get('onsite', {}).get(tier_name, {})
            if tier_config:
                return tier_config
        
        # Default tier configurations
        default_configs = {
            'tier_1': {
                'name': 'TIER 1 - BRAND POSITIONING',
                'weight_in_onsite': 0.3,
                'brand_percentage': 80,
                'performance_percentage': 20
            },
            'tier_2': {
                'name': 'TIER 2 - VALUE PROPOSITIONS',
                'weight_in_onsite': 0.5,
                'brand_percentage': 50,
                'performance_percentage': 50
            },
            'tier_3': {
                'name': 'TIER 3 - FUNCTIONAL CONTENT',
                'weight_in_onsite': 0.2,
                'brand_percentage': 30,
                'performance_percentage': 70
            }
        }
        
        return default_configs.get(tier_name, default_configs['tier_2'])
    
    def _get_channel_config(self, channel_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a channel.
        
        Args:
            channel_name: The name of the channel
            
        Returns:
            Dictionary of channel configuration
        """
        # Get channel configuration from methodology config
        if self.config and 'classification' in self.config:
            channel_config = self.config.get('classification', {}).get('offsite', {}).get(channel_name, {})
            if channel_config:
                return channel_config
        
        # Default channel configurations
        default_configs = {
            'owned': {
                'name': 'Owned Channels',
                'weight_in_offsite': 0.4,
                'brand_percentage': 60,
                'performance_percentage': 40
            },
            'influenced': {
                'name': 'Influenced Channels',
                'weight_in_offsite': 0.35,
                'brand_percentage': 40,
                'authenticity_percentage': 60
            },
            'independent': {
                'name': 'Independent Channels',
                'weight_in_offsite': 0.25,
                'brand_percentage': 20,
                'sentiment_percentage': 80
            }
        }
        
        return default_configs.get(channel_name, default_configs['owned'])
    
    def get_tier_examples(self, tier_name: str) -> List[str]:
        """
        Get example URLs for a specific tier.
        
        Args:
            tier_name: The name of the tier
            
        Returns:
            List of example URLs
        """
        # Get examples from methodology config
        if self.config and 'classification' in self.config:
            examples = self.config.get('classification', {}).get('onsite', {}).get(tier_name, {}).get('examples', [])
            if examples:
                return examples
        
        # Default examples
        default_examples = {
            'tier_1': [
                'https://www.soprasteria.com',
                'https://www.soprasteria.be',
                'https://www.soprasteria.nl'
            ],
            'tier_2': [
                'https://www.soprasteria.be/industries/financial-services',
                'https://www.soprasteria.be/what-we-do/data-ai',
                'https://www.soprasteria.nl/newsroom/blog'
            ],
            'tier_3': [
                'https://www.soprasteria.be/what-we-do/data-ai/data-science-and-ai/the-future-of-generative-ai',
                'https://www.soprasteria.nl/newsroom/blog/details/interacting-with-large-language-models',
                'https://www.soprasteria.be/contact-us'
            ]
        }
        
        return default_examples.get(tier_name, [])
    
    def get_channel_examples(self, channel_name: str) -> List[str]:
        """
        Get example URLs for a specific channel.
        
        Args:
            channel_name: The name of the channel
            
        Returns:
            List of example URLs
        """
        # Get examples from methodology config
        if self.config and 'classification' in self.config:
            examples = self.config.get('classification', {}).get('offsite', {}).get(channel_name, {}).get('examples', [])
            if examples:
                return examples
        
        # Default examples
        default_examples = {
            'owned': [
                'https://www.youtube.com/SopraSteria_Benelux',
                'https://www.soprasteria.be/newsroom/press-releases'
            ],
            'influenced': [
                'https://www.linkedin.com/company/soprasteria-benelux',
                'https://twitter.com/soprasteria'
            ],
            'independent': [
                'https://www.nl.digital.nl/leden/sopra-steria-nederland-b-v',
                'https://www.techzine.be/nieuws/devops/30183/sopra-steria-helpt-bedrijven-met-ai-implementatie/'
            ]
        }
        
        return default_examples.get(channel_name, [])
