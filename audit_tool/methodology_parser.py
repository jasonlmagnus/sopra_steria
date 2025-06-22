"""
Methodology Parser for Brand Audit Tool

STATUS: ACTIVE

This module provides functionality to parse and apply the brand audit methodology:
1. Loads and parses methodology configuration from YAML files
2. Classifies URLs into appropriate tiers and channels
3. Retrieves evaluation criteria for different content types
4. Supports the consistent application of evaluation frameworks
5. Enables methodology-driven scoring and analysis

The parser ensures that all audit evaluations follow a consistent methodology,
with appropriate criteria applied based on content type and tier classification.
"""

import os
import yaml
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

from .tier_classifier import TierClassifier

logger = logging.getLogger(__name__)

class MethodologyParser:
    """Parses and applies the brand audit methodology."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize with optional configuration path.
        
        Args:
            config_path: Path to methodology configuration file
        """
        self.config_path = config_path or os.path.join("audit_tool", "config", "methodology.yaml")
        self.config = self._load_config()
        self.tier_classifier = TierClassifier(self.config)
        
        logger.info(f"Methodology parser initialized with config: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load methodology configuration from YAML.
        
        Returns:
            Dictionary of configuration
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded methodology configuration from {self.config_path}")
                return config
        except Exception as e:
            logger.warning(f"Error loading methodology configuration: {str(e)}")
            logger.info("Using default methodology configuration")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default methodology configuration.
        
        Returns:
            Dictionary of default configuration
        """
        return {
            "version": "1.0",
            "name": "Brand Audit Methodology",
            "classification": {
                "onsite": {
                    "tier_1": {
                        "name": "TIER 1 - BRAND POSITIONING",
                        "weight_in_onsite": 0.3,
                        "brand_percentage": 80,
                        "performance_percentage": 20,
                        "criteria": [
                            {
                                "code": "BP1",
                                "name": "Brand Clarity",
                                "description": "Clear communication of brand purpose, values, and positioning",
                                "weight": 0.2
                            },
                            {
                                "code": "BP2",
                                "name": "Value Proposition",
                                "description": "Clear articulation of unique value and benefits",
                                "weight": 0.2
                            },
                            {
                                "code": "BP3",
                                "name": "Visual Identity",
                                "description": "Consistent and effective use of visual brand elements",
                                "weight": 0.15
                            },
                            {
                                "code": "BP4",
                                "name": "Messaging Consistency",
                                "description": "Consistent tone, voice, and key messages",
                                "weight": 0.15
                            },
                            {
                                "code": "BP5",
                                "name": "Audience Relevance",
                                "description": "Content tailored to target audience needs and interests",
                                "weight": 0.2
                            },
                            {
                                "code": "PP1",
                                "name": "User Experience",
                                "description": "Intuitive navigation and positive user experience",
                                "weight": 0.1
                            }
                        ]
                    },
                    "tier_2": {
                        "name": "TIER 2 - VALUE PROPOSITIONS",
                        "weight_in_onsite": 0.5,
                        "brand_percentage": 50,
                        "performance_percentage": 50,
                        "criteria": [
                            {
                                "code": "BP1",
                                "name": "Brand Consistency",
                                "description": "Consistent with overall brand positioning",
                                "weight": 0.1
                            },
                            {
                                "code": "BP2",
                                "name": "Value Articulation",
                                "description": "Clear articulation of specific value proposition",
                                "weight": 0.15
                            },
                            {
                                "code": "BP3",
                                "name": "Differentiation",
                                "description": "Clear differentiation from competitors",
                                "weight": 0.15
                            },
                            {
                                "code": "BP4",
                                "name": "Credibility",
                                "description": "Evidence and proof points supporting claims",
                                "weight": 0.1
                            },
                            {
                                "code": "PP1",
                                "name": "Content Quality",
                                "description": "Well-structured, clear, and engaging content",
                                "weight": 0.15
                            },
                            {
                                "code": "PP2",
                                "name": "Call to Action",
                                "description": "Clear and compelling next steps for the user",
                                "weight": 0.1
                            },
                            {
                                "code": "PP3",
                                "name": "User Experience",
                                "description": "Intuitive navigation and positive user experience",
                                "weight": 0.15
                            },
                            {
                                "code": "PP4",
                                "name": "Mobile Optimization",
                                "description": "Effective display and functionality on mobile devices",
                                "weight": 0.1
                            }
                        ]
                    },
                    "tier_3": {
                        "name": "TIER 3 - FUNCTIONAL CONTENT",
                        "weight_in_onsite": 0.2,
                        "brand_percentage": 30,
                        "performance_percentage": 70,
                        "criteria": [
                            {
                                "code": "BP1",
                                "name": "Brand Consistency",
                                "description": "Consistent with overall brand positioning",
                                "weight": 0.1
                            },
                            {
                                "code": "BP2",
                                "name": "Tone and Voice",
                                "description": "Appropriate tone and voice for the brand",
                                "weight": 0.1
                            },
                            {
                                "code": "BP3",
                                "name": "Visual Consistency",
                                "description": "Consistent use of visual brand elements",
                                "weight": 0.1
                            },
                            {
                                "code": "PP1",
                                "name": "Content Quality",
                                "description": "Clear, accurate, and helpful content",
                                "weight": 0.2
                            },
                            {
                                "code": "PP2",
                                "name": "Functionality",
                                "description": "Effective functionality for intended purpose",
                                "weight": 0.2
                            },
                            {
                                "code": "PP3",
                                "name": "User Experience",
                                "description": "Intuitive navigation and positive user experience",
                                "weight": 0.15
                            },
                            {
                                "code": "PP4",
                                "name": "Mobile Optimization",
                                "description": "Effective display and functionality on mobile devices",
                                "weight": 0.15
                            }
                        ]
                    }
                },
                "offsite": {
                    "owned": {
                        "name": "Owned Channels",
                        "weight_in_offsite": 0.4,
                        "brand_percentage": 60,
                        "performance_percentage": 40,
                        "criteria": [
                            {
                                "code": "OC1",
                                "name": "Brand Consistency",
                                "description": "Consistent with overall brand positioning",
                                "weight": 0.2
                            },
                            {
                                "code": "OC2",
                                "name": "Content Quality",
                                "description": "High-quality, relevant content",
                                "weight": 0.2
                            },
                            {
                                "code": "OC3",
                                "name": "Visual Identity",
                                "description": "Consistent and effective use of visual brand elements",
                                "weight": 0.2
                            },
                            {
                                "code": "OC4",
                                "name": "Engagement",
                                "description": "Effective engagement with audience",
                                "weight": 0.2
                            },
                            {
                                "code": "OC5",
                                "name": "Call to Action",
                                "description": "Clear and compelling next steps for the user",
                                "weight": 0.2
                            }
                        ]
                    },
                    "influenced": {
                        "name": "Influenced Channels",
                        "weight_in_offsite": 0.35,
                        "brand_percentage": 40,
                        "authenticity_percentage": 60,
                        "criteria": [
                            {
                                "code": "IC1",
                                "name": "Brand Representation",
                                "description": "Accurate representation of the brand",
                                "weight": 0.2
                            },
                            {
                                "code": "IC2",
                                "name": "Engagement",
                                "description": "Effective engagement with audience",
                                "weight": 0.2
                            },
                            {
                                "code": "IC3",
                                "name": "Authenticity",
                                "description": "Authentic and genuine communication",
                                "weight": 0.2
                            },
                            {
                                "code": "IC4",
                                "name": "Community Building",
                                "description": "Building and nurturing community",
                                "weight": 0.2
                            },
                            {
                                "code": "IC5",
                                "name": "Content Value",
                                "description": "Providing value through content",
                                "weight": 0.2
                            }
                        ]
                    },
                    "independent": {
                        "name": "Independent Channels",
                        "weight_in_offsite": 0.25,
                        "brand_percentage": 20,
                        "sentiment_percentage": 80,
                        "criteria": [
                            {
                                "code": "INC1",
                                "name": "Brand Perception",
                                "description": "How the brand is perceived by others",
                                "weight": 0.2
                            },
                            {
                                "code": "INC2",
                                "name": "Sentiment",
                                "description": "Overall sentiment towards the brand",
                                "weight": 0.3
                            },
                            {
                                "code": "INC3",
                                "name": "Accuracy",
                                "description": "Accuracy of information about the brand",
                                "weight": 0.2
                            },
                            {
                                "code": "INC4",
                                "name": "Prominence",
                                "description": "Prominence and visibility of the brand",
                                "weight": 0.15
                            },
                            {
                                "code": "INC5",
                                "name": "Context",
                                "description": "Context in which the brand appears",
                                "weight": 0.15
                            }
                        ]
                    }
                }
            }
        }
    
    def classify_url(self, url: str) -> Tuple[str, Dict[str, Any]]:
        """
        Classify a URL into the appropriate tier or channel.
        
        Args:
            url: The URL to classify
            
        Returns:
            Tuple of (tier_name, tier_config)
        """
        return self.tier_classifier.classify_url(url)
    
    def get_criteria_for_tier(self, tier_name: str) -> List[Dict[str, Any]]:
        """
        Get the evaluation criteria for a specific tier.
        
        Args:
            tier_name: The name of the tier
            
        Returns:
            List of criteria dictionaries
        """
        # Check if this is an onsite tier
        if tier_name.startswith('tier_'):
            return self.config.get('classification', {}).get('onsite', {}).get(tier_name, {}).get('criteria', [])
        
        # Otherwise, it's an offsite channel
        return self.config.get('classification', {}).get('offsite', {}).get(tier_name, {}).get('criteria', [])
    
    def get_tier_names(self) -> List[str]:
        """
        Get all tier names.
        
        Returns:
            List of tier names
        """
        return list(self.config.get('classification', {}).get('onsite', {}).keys())
    
    def get_channel_names(self) -> List[str]:
        """
        Get all channel names.
        
        Returns:
            List of channel names
        """
        return list(self.config.get('classification', {}).get('offsite', {}).keys())
    
    def get_tier_config(self, tier_name: str) -> Dict[str, Any]:
        """
        Get the configuration for a specific tier.
        
        Args:
            tier_name: The name of the tier
            
        Returns:
            Dictionary of tier configuration
        """
        if tier_name.startswith('tier_'):
            return self.config.get('classification', {}).get('onsite', {}).get(tier_name, {})
        
        return self.config.get('classification', {}).get('offsite', {}).get(tier_name, {})
    
    def get_all_criteria(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all criteria across all tiers and channels.
        
        Returns:
            Dictionary of criteria by code
        """
        all_criteria = {}
        
        # Get onsite criteria
        for tier_name in self.get_tier_names():
            criteria = self.get_criteria_for_tier(tier_name)
            for criterion in criteria:
                code = criterion.get('code')
                if code and code not in all_criteria:
                    all_criteria[code] = criterion
        
        # Get offsite criteria
        for channel_name in self.get_channel_names():
            criteria = self.get_criteria_for_tier(channel_name)
            for criterion in criteria:
                code = criterion.get('code')
                if code and code not in all_criteria:
                    all_criteria[code] = criterion
        
        return all_criteria
    
    def get_criterion_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get a criterion by its code.
        
        Args:
            code: The criterion code
            
        Returns:
            Dictionary of criterion details or None if not found
        """
        all_criteria = self.get_all_criteria()
        return all_criteria.get(code)
