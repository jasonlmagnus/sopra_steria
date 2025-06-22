"""
Data Models for Brand Audit Tool

STATUS: ACTIVE

This module defines the core data models used throughout the brand audit tool:
1. Structured data classes for audit data representation
2. Type definitions for consistent data handling
3. Data validation and transformation utilities
4. Object-relational mapping for data persistence
5. Serialization/deserialization support for data exchange

The models provide a consistent data structure across the application,
ensuring type safety and enabling efficient data processing and analysis.
"""

import re
import json
import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class PageData:
    """Data class representing a scraped web page."""
    
    url: str
    title: str
    raw_text: str
    html: str
    meta_description: str = ""
    meta_keywords: str = ""
    h1_tags: List[str] = field(default_factory=list)
    h2_tags: List[str] = field(default_factory=list)
    images: List[Dict[str, str]] = field(default_factory=list)
    links: List[Dict[str, str]] = field(default_factory=list)
    is_404: bool = False
    scrape_time: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = self.to_dict()
        data['scrape_time'] = data['scrape_time'].isoformat()
        return json.dumps(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PageData':
        """Create from dictionary."""
        if 'scrape_time' in data and isinstance(data['scrape_time'], str):
            data['scrape_time'] = datetime.fromisoformat(data['scrape_time'])
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PageData':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

@dataclass
class CriterionScore:
    """Data class representing a criterion score."""
    
    page_id: str
    criterion_code: str
    criterion_name: str
    score: float
    evidence: str = ""
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class PageScore:
    """Data class representing a page score."""
    
    page_id: str
    url: str
    tier: str
    final_score: float
    criteria_scores: List[CriterionScore] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['criteria_scores'] = [cs.to_dict() for cs in self.criteria_scores]
        return data
    
    def calculate_final_score(self) -> float:
        """Calculate the final score based on weighted criteria scores."""
        if not self.criteria_scores:
            return 0.0
        
        total_weight = sum(cs.weight for cs in self.criteria_scores)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(cs.score * cs.weight for cs in self.criteria_scores)
        return weighted_sum / total_weight

@dataclass
class ExperienceMetric:
    """Data class representing an experience metric."""
    
    page_id: str
    url: str
    persona: str
    sentiment: str  # Positive, Neutral, Negative
    engagement: str  # High, Medium, Low
    conversion: str  # High, Medium, Low
    first_impression: str = ""
    content_relevance: str = ""
    brand_perception: str = ""
    journey_analysis: str = ""
    emotional_response: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

@dataclass
class Recommendation:
    """Data class representing a recommendation."""
    
    page_id: str
    url: str
    persona: str
    recommendation: str
    category: str = ""  # e.g., Content, Design, UX, Brand, Technical
    priority: int = 2  # 1 (high) to 3 (low)
    effort: int = 2  # 1 (low) to 3 (high)
    impact: int = 2  # 1 (low) to 3 (high)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @property
    def value_score(self) -> float:
        """Calculate value score (impact / effort)."""
        if self.effort == 0:
            return 0.0
        return self.impact / self.effort

@dataclass
class AuditResult:
    """Data class representing an audit result."""
    
    persona: str
    pages: List[Dict[str, Any]] = field(default_factory=list)
    criteria: List[Dict[str, Any]] = field(default_factory=list)
    experience: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditResult':
        """Create from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AuditResult':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

def sanitize_page_id(url: str) -> str:
    """
    Convert a URL to a safe page ID.
    
    Args:
        url: The URL to convert
        
    Returns:
        A safe page ID
    """
    # Remove protocol
    page_id = url.replace('https://', '').replace('http://', '')
    
    # Replace special characters
    page_id = re.sub(r'[^a-zA-Z0-9_]', '_', page_id)
    
    # Remove consecutive underscores
    page_id = re.sub(r'_+', '_', page_id)
    
    # Remove trailing underscore
    page_id = page_id.rstrip('_')
    
    return page_id

def get_sentiment_score(sentiment: str) -> float:
    """
    Convert sentiment string to numeric score.
    
    Args:
        sentiment: Sentiment string (Positive, Neutral, Negative)
        
    Returns:
        Numeric score (0.0 to 10.0)
    """
    sentiment_map = {
        "positive": 8.0,
        "neutral": 5.0,
        "negative": 2.0
    }
    
    return sentiment_map.get(sentiment.lower(), 5.0)

def get_engagement_score(engagement: str) -> float:
    """
    Convert engagement string to numeric score.
    
    Args:
        engagement: Engagement string (High, Medium, Low)
        
    Returns:
        Numeric score (0.0 to 10.0)
    """
    engagement_map = {
        "high": 8.0,
        "medium": 5.0,
        "low": 2.0
    }
    
    return engagement_map.get(engagement.lower(), 5.0)
