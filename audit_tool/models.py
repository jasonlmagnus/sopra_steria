"""
This module defines the data structures used for passing data between modules.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

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
    category: str = "general"  # brand, performance, authenticity, sentiment
    requirements: List[str] = field(default_factory=list)
    criterion_id: str = ""
    description: str = ""

@dataclass
class Tier:
    """Represents a scoring tier (e.g., Tier 1, Tier 2) from the methodology."""
    name: str
    criteria: List[Criterion]
    weight: float  # The weight of this tier in the final onsite score
    brand_percentage: int = 50
    performance_percentage: int = 50
    triggers: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)

@dataclass
class OffsiteChannel:
    """Represents an offsite channel type (e.g., Owned, Influenced)."""
    name: str
    criteria: List[Criterion]
    weight: float  # The weight of this channel in the final offsite score
    brand_percentage: int = 50
    performance_percentage: int = 0
    authenticity_percentage: int = 0
    sentiment_percentage: int = 0
    examples: List[str] = field(default_factory=list)

@dataclass
class Methodology:
    """Represents the entire scoring methodology, composed of multiple tiers."""
    tiers: List[Tier]
    offsite_channels: List[OffsiteChannel]
    metadata: Dict[str, Any] = field(default_factory=dict)
    scoring_config: Dict[str, Any] = field(default_factory=dict)
    calculation_config: Dict[str, Any] = field(default_factory=dict)
    gating_rules: Dict[str, Any] = field(default_factory=dict)
    brand_messaging: Dict[str, Any] = field(default_factory=dict)
    validation_flags: Dict[str, Any] = field(default_factory=dict)
    quality_penalties: Dict[str, Any] = field(default_factory=dict)
    evidence_requirements: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScoredCriterion:
    """Represents a single criterion after it has been scored."""
    name: str
    weight: float
    score: float
    notes: str = ""
    evidence: str = ""
    category: str = "general"
    penalties_applied: List[str] = field(default_factory=list)

@dataclass
class Scorecard:
    """Represents the final, calculated scorecard for a URL."""
    url: str
    final_score: float
    tier_name: str  # For onsite, this is Tier 1/2/3. For offsite, this is Owned/Influenced/Independent.
    scored_criteria: List[ScoredCriterion]
    brand_consistency_check: Dict[str, Any] = field(default_factory=dict)
    gating_rules_applied: List[str] = field(default_factory=list)
    quality_penalties: List[str] = field(default_factory=list)

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