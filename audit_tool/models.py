"""
This module defines the data structures used for passing data between modules.
"""
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class PageData:
    """
    A dataclass to hold the scraped data from a single URL.
    """
    url: str
    raw_text: str
    is_404: bool = False
    objective_findings: Dict[str, any] = field(default_factory=dict)

@dataclass
class Criterion:
    """Represents a single scoring criterion from the methodology."""
    name: str
    weight: float
    # We can add more fields later, like 'description' or 'gating_rule'

@dataclass
class Tier:
    """Represents a scoring tier (e.g., Tier 1, Tier 2) from the methodology."""
    name: str
    criteria: List[Criterion]
    weight: float # The weight of this tier in the final onsite score

@dataclass
class OffsiteChannel:
    """Represents an offsite channel type (e.g., Owned, Influenced)."""
    name: str
    criteria: List[Criterion]
    weight: float # The weight of this channel in the final offsite score

@dataclass
class Methodology:
    """Represents the entire scoring methodology, composed of multiple tiers."""
    tiers: List[Tier]
    offsite_channels: List[OffsiteChannel]

@dataclass
class ScoredCriterion:
    """Represents a single criterion after it has been scored."""
    name: str
    weight: float
    score: float
    notes: str = ""

@dataclass
class Scorecard:
    """Represents the final, calculated scorecard for a URL."""
    url: str
    final_score: float
    tier_name: str # For onsite, this is Tier 1/2/3. For offsite, this is Owned/Influenced/Independent.
    scored_criteria: List[ScoredCriterion]

@dataclass
class AggregatedTierScore:
    """Holds the aggregated score for a single tier."""
    tier_name: str
    average_score: float
    page_count: int

@dataclass
class AggregatedOffsiteScore:
    """Holds the aggregated score for a single offsite channel."""
    channel_name: str
    average_score: float
    page_count: int

@dataclass
class RankedPage:
    """Represents a page in a ranked list."""
    url: str
    score: float

@dataclass
class SummaryReport:
    """Holds all the data for the final strategic summary report."""
    persona_name: str
    overall_score: float
    onsite_score: float
    offsite_score: float
    tier_scores: List[AggregatedTierScore]
    offsite_scores: List[AggregatedOffsiteScore]
    top_performing_pages: List[RankedPage]
    bottom_performing_pages: List[RankedPage]
    executive_summary: str
    key_strengths: List[str]
    key_weaknesses: List[str] 