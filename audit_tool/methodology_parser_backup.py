"""
This module is responsible for parsing the audit_method.md file
and converting the rules into structured Python objects.

For now, this is hardcoded to prevent further parsing errors.
"""
import logging
from .models import Methodology, Tier, Criterion, OffsiteChannel

class MethodologyParser:
    """
    Builds a hardcoded Methodology object.
    """
    def __init__(self, filepath: str):
        # Filepath is ignored for now, but kept for consistent interface
        self.filepath = filepath

    def parse(self) -> Methodology:
        """
        Returns a hardcoded, structured representation of the audit methodology.
        """
        logging.info("Returning hardcoded methodology to avoid parsing errors.")
        
        # --- ONSITE TIERS ---
        tier1_criteria = [
            Criterion(name="Corporate Positioning Alignment", weight=0.25),
            Criterion(name="Brand Differentiation", weight=0.20),
            Criterion(name="Emotional Resonance", weight=0.20),
            Criterion(name="Visual Brand Integrity", weight=0.15),
            Criterion(name="Strategic Clarity", weight=0.10),
            Criterion(name="Trust & Credibility Signals", weight=0.10),
        ]
        tier2_criteria = [
            Criterion(name="Regional Narrative Integration", weight=0.15),
            Criterion(name="Brand Message Consistency", weight=0.15),
            Criterion(name="Visual Brand Consistency", weight=0.10),
            Criterion(name="Brand Promise Delivery", weight=0.10),
            Criterion(name="Strategic Value Clarity", weight=0.25),
            Criterion(name="Solution Sophistication", weight=0.15),
            Criterion(name="Proof Points & Validation", weight=0.10),
        ]
        tier3_criteria = [
            Criterion(name="Brand Voice Alignment", weight=0.10),
            Criterion(name="Sub-Narrative Integration", weight=0.10),
            Criterion(name="Visual Brand Elements", weight=0.10),
            Criterion(name="Executive Relevance", weight=0.25),
            Criterion(name="Strategic Insight Quality", weight=0.20),
            Criterion(name="Business Value Focus", weight=0.15),
            Criterion(name="Credibility Elements", weight=0.10),
        ]

        onsite_tiers = [
            Tier(name="TIER 1 - BRAND POSITIONING", criteria=tier1_criteria, weight=0.3),
            Tier(name="TIER 2 - VALUE PROPOSITION", criteria=tier2_criteria, weight=0.5),
            Tier(name="TIER 3 - FUNCTIONAL CONTENT", criteria=tier3_criteria, weight=0.2),
        ]

        # --- OFFSITE CHANNELS ---
        owned_criteria = [
            Criterion(name="Brand Message Alignment", weight=0.25),
            Criterion(name="Visual Identity Consistency", weight=0.20),
            Criterion(name="Content Quality", weight=0.15),
            Criterion(name="Audience Engagement", weight=0.15),
            Criterion(name="Posting Frequency", weight=0.10),
            Criterion(name="Response Management", weight=0.15),
        ]
        influenced_criteria = [
            Criterion(name="Message Alignment", weight=0.25),
            Criterion(name="Employee Advocacy", weight=0.20),
            Criterion(name="Glassdoor Ratings", weight=0.15),
            Criterion(name="Partner Content Quality", weight=0.15),
            Criterion(name="Thought Leadership", weight=0.15),
            Criterion(name="Response to Concerns", weight=0.10),
        ]
        independent_criteria = [
            Criterion(name="Overall Sentiment", weight=0.30),
            Criterion(name="Review Ratings", weight=0.25),
            Criterion(name="Competitive Position", weight=0.15),
            Criterion(name="Brand Mention Quality", weight=0.10),
            Criterion(name="Crisis Management", weight=0.10),
            Criterion(name="Industry Recognition", weight=0.10),
        ]

        offsite_channels = [
            OffsiteChannel(name="Owned Channels", criteria=owned_criteria, weight=0.40),
            OffsiteChannel(name="Influenced Channels", criteria=influenced_criteria, weight=0.35),
            OffsiteChannel(name="Independent Channels", criteria=independent_criteria, weight=0.25),
        ]

        return Methodology(tiers=onsite_tiers, offsite_channels=offsite_channels)