"""
This module is responsible for parsing the methodology.yaml configuration file
and converting it into structured Python objects for the audit tool.
"""
import logging
import yaml
from pathlib import Path
from typing import Dict, List, Any
from .models import Methodology, Tier, Criterion, OffsiteChannel

class MethodologyParser:
    """
    Parses the methodology.yaml configuration file and builds structured objects.
    """
    
    def __init__(self, yaml_filepath: str = None):
        """Initialize with path to methodology.yaml file."""
        if yaml_filepath is None:
            # Default to config/methodology.yaml in the same directory
            self.yaml_filepath = Path(__file__).parent / "config" / "methodology.yaml"
        else:
            self.yaml_filepath = Path(yaml_filepath)
        
        self.config = None
        self._load_config()

    def _load_config(self) -> None:
        """Load the YAML configuration file."""
        try:
            with open(self.yaml_filepath, 'r', encoding='utf-8') as file:
                self.config = yaml.safe_load(file)
            logging.info(f"Successfully loaded methodology configuration from {self.yaml_filepath}")
        except FileNotFoundError:
            logging.error(f"Methodology configuration file not found: {self.yaml_filepath}")
            raise
        except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML configuration: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error loading configuration: {e}")
            raise

    def parse(self) -> Methodology:
        """
        Parse the YAML configuration and return a structured Methodology object.
        """
        if not self.config:
            raise ValueError("Configuration not loaded. Call _load_config() first.")
        
        logging.info("Parsing methodology configuration from YAML")
        
        # Parse onsite tiers
        onsite_tiers = self._parse_onsite_tiers()
        
        # Parse offsite channels
        offsite_channels = self._parse_offsite_channels()
        
        # Create and return methodology object
        methodology = Methodology(
            tiers=onsite_tiers,
            offsite_channels=offsite_channels,
            metadata=self.config.get('metadata', {}),
            scoring_config=self.config.get('scoring', {}),
            calculation_config=self.config.get('calculation', {}),
            gating_rules=self.config.get('gating_rules', {}),
            brand_messaging=self.config.get('messaging', {}),
            validation_flags=self.config.get('validation_flags', {}),
            quality_penalties=self.config.get('quality_penalties', {}),
            evidence_requirements=self.config.get('evidence', {})
        )
        
        return methodology

    def _parse_onsite_tiers(self) -> List[Tier]:
        """Parse the onsite tier configurations."""
        tiers = []
        criteria_config = self.config.get('criteria', {})
        classification_config = self.config.get('classification', {}).get('onsite', {})
        
        # Parse Tier 1
        tier_1_config = classification_config.get('tier_1', {})
        tier_1_criteria = self._parse_tier_criteria('tier_1', criteria_config)
        tier_1 = Tier(
            name="TIER 1 - BRAND POSITIONING",
            criteria=tier_1_criteria,
            weight=tier_1_config.get('weight_in_onsite', 0.3),
            brand_percentage=tier_1_config.get('brand_percentage', 80),
            performance_percentage=tier_1_config.get('performance_percentage', 20),
            triggers=tier_1_config.get('triggers', []),
            examples=tier_1_config.get('examples', [])
        )
        tiers.append(tier_1)
        
        # Parse Tier 2
        tier_2_config = classification_config.get('tier_2', {})
        tier_2_criteria = self._parse_tier_criteria('tier_2', criteria_config)
        tier_2 = Tier(
            name="TIER 2 - VALUE PROPOSITIONS",
            criteria=tier_2_criteria,
            weight=tier_2_config.get('weight_in_onsite', 0.5),
            brand_percentage=tier_2_config.get('brand_percentage', 50),
            performance_percentage=tier_2_config.get('performance_percentage', 50),
            triggers=tier_2_config.get('triggers', []),
            examples=tier_2_config.get('examples', [])
        )
        tiers.append(tier_2)
        
        # Parse Tier 3
        tier_3_config = classification_config.get('tier_3', {})
        tier_3_criteria = self._parse_tier_criteria('tier_3', criteria_config)
        tier_3 = Tier(
            name="TIER 3 - FUNCTIONAL CONTENT",
            criteria=tier_3_criteria,
            weight=tier_3_config.get('weight_in_onsite', 0.2),
            brand_percentage=tier_3_config.get('brand_percentage', 30),
            performance_percentage=tier_3_config.get('performance_percentage', 70),
            triggers=tier_3_config.get('triggers', []),
            examples=tier_3_config.get('examples', [])
        )
        tiers.append(tier_3)
        
        return tiers

    def _parse_tier_criteria(self, tier_name: str, criteria_config: Dict) -> List[Criterion]:
        """Parse criteria for a specific tier."""
        criteria = []
        tier_config = criteria_config.get(tier_name, {})
        
        # Parse brand criteria
        brand_criteria = tier_config.get('brand_criteria', {})
        for criterion_name, criterion_config in brand_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='brand',
                requirements=criterion_config.get('requirements', []),
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        # Parse performance criteria
        performance_criteria = tier_config.get('performance_criteria', {})
        for criterion_name, criterion_config in performance_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='performance',
                requirements=criterion_config.get('requirements', []),
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        # Parse authenticity criteria (for tier 3 if applicable)
        authenticity_criteria = tier_config.get('authenticity_criteria', {})
        for criterion_name, criterion_config in authenticity_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='authenticity',
                requirements=criterion_config.get('requirements', []),
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        return criteria

    def _parse_offsite_channels(self) -> List[OffsiteChannel]:
        """Parse the offsite channel configurations."""
        channels = []
        offsite_criteria = self.config.get('offsite_criteria', {})
        classification_config = self.config.get('classification', {}).get('offsite', {})
        
        # Parse Owned Channels
        owned_config = classification_config.get('owned', {})
        owned_criteria = self._parse_offsite_criteria('owned', offsite_criteria)
        owned_channel = OffsiteChannel(
            name="Owned Channels",
            criteria=owned_criteria,
            weight=owned_config.get('weight_in_offsite', 0.4),
            brand_percentage=owned_config.get('brand_percentage', 60),
            performance_percentage=owned_config.get('performance_percentage', 40),
            examples=owned_config.get('examples', [])
        )
        channels.append(owned_channel)
        
        # Parse Influenced Channels
        influenced_config = classification_config.get('influenced', {})
        influenced_criteria = self._parse_offsite_criteria('influenced', offsite_criteria)
        influenced_channel = OffsiteChannel(
            name="Influenced Channels",
            criteria=influenced_criteria,
            weight=influenced_config.get('weight_in_offsite', 0.35),
            brand_percentage=influenced_config.get('brand_percentage', 40),
            authenticity_percentage=influenced_config.get('authenticity_percentage', 60),
            examples=influenced_config.get('examples', [])
        )
        channels.append(influenced_channel)
        
        # Parse Independent Channels
        independent_config = classification_config.get('independent', {})
        independent_criteria = self._parse_offsite_criteria('independent', offsite_criteria)
        independent_channel = OffsiteChannel(
            name="Independent Channels",
            criteria=independent_criteria,
            weight=independent_config.get('weight_in_offsite', 0.25),
            brand_percentage=independent_config.get('brand_percentage', 20),
            sentiment_percentage=independent_config.get('sentiment_percentage', 80),
            examples=independent_config.get('examples', [])
        )
        channels.append(independent_channel)
        
        return channels

    def _parse_offsite_criteria(self, channel_name: str, offsite_criteria: Dict) -> List[Criterion]:
        """Parse criteria for a specific offsite channel."""
        criteria = []
        channel_config = offsite_criteria.get(channel_name, {})
        
        # Parse brand criteria
        brand_criteria = channel_config.get('brand_criteria', {})
        for criterion_name, criterion_config in brand_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='brand',
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        # Parse performance criteria
        performance_criteria = channel_config.get('performance_criteria', {})
        for criterion_name, criterion_config in performance_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='performance',
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        # Parse authenticity criteria
        authenticity_criteria = channel_config.get('authenticity_criteria', {})
        for criterion_name, criterion_config in authenticity_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='authenticity',
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        # Parse sentiment criteria
        sentiment_criteria = channel_config.get('sentiment_criteria', {})
        for criterion_name, criterion_config in sentiment_criteria.items():
            criterion = Criterion(
                name=criterion_config.get('description', criterion_name),
                weight=criterion_config.get('weight', 0) / 100.0,  # Convert percentage to decimal
                category='sentiment',
                criterion_id=criterion_name
            )
            criteria.append(criterion)
        
        return criteria

    def get_scoring_descriptors(self) -> dict:
        """Get scoring descriptors"""
        return self.config.get('scoring', {}).get('descriptors', {})

    def get_gating_rules(self) -> Dict[str, Dict]:
        """Get the hard gating rules from configuration."""
        return self.config.get('gating_rules', {})

    def get_brand_messaging(self) -> Dict[str, Any]:
        """Get the brand messaging reference from configuration."""
        return self.config.get('messaging', {})

    def get_calculation_config(self) -> dict:
        """Get calculation configuration"""
        return self.config.get('calculation', {})

    def get_quality_penalties(self) -> Dict[str, Dict]:
        """Get the copy quality penalties configuration."""
        return self.config.get('quality_penalties', {})

    def get_validation_flags(self) -> Dict[str, Dict]:
        """Get the validation flags configuration."""
        return self.config.get('validation_flags', {})

    def get_evidence_requirements(self) -> Dict[str, Any]:
        """Get the evidence requirements configuration."""
        return self.config.get('evidence', {})

    def get_examples(self) -> Dict[str, Dict]:
        """Get the calibration examples from configuration."""
        return self.config.get('examples', {})

    def get_metadata(self) -> dict:
        """Get methodology metadata"""
        return self.config.get('metadata', {})

    def get_tier_criteria(self, tier_name: str) -> dict:
        """Get criteria for a specific tier"""
        return self.config.get('criteria', {}).get(tier_name, {})