#!/usr/bin/env python3
"""
Vector Store Schema Configuration

Defines the schema and configuration for various vector databases.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class VectorStoreType(Enum):
    PINECONE = "pinecone"
    WEAVIATE = "weaviate" 
    QDRANT = "qdrant"
    CHROMA = "chroma"

@dataclass
class VectorStoreConfig:
    """Configuration for vector store setup."""
    
    # Embedding configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    
    # Index configuration
    index_name: str = "sopra-persona-audit"
    namespace: str = "production"
    
    # Metadata fields for filtering
    metadata_fields: Optional[List[str]] = None
    
    # Text fields for search
    text_fields: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.metadata_fields is None:
            self.metadata_fields = [
                "persona_id",
                "page_id", 
                "domain",
                "content_type",
                "tier",
                "final_score",
                "regulatory_frameworks",
                "is_benelux",
                "has_compliance_content",
                "has_security_content",
                "compiled_at"
            ]
            
        if self.text_fields is None:
            self.text_fields = [
                "combined_analysis",
                "first_impression", 
                "strategic_analysis",
                "effective_copy",
                "ineffective_copy",
                "recommendations"
            ]

# Pinecone Configuration
PINECONE_CONFIG = {
    "dimension": 1536,
    "metric": "cosine",
    "spec": {
        "serverless": {
            "cloud": "aws",
            "region": "us-east-1"
        }
    },
    "metadata_config": {
        "indexed": [
            "persona_id",
            "page_id",
            "domain", 
            "content_type",
            "tier",
            "final_score",
            "is_benelux",
            "has_compliance_content",
            "has_security_content"
        ]
    }
}

# Weaviate Configuration  
WEAVIATE_CONFIG = {
    "class_name": "PersonaAuditDocument",
    "properties": [
        {
            "name": "page_id",
            "dataType": ["text"],
            "description": "Unique identifier for the audited page"
        },
        {
            "name": "url", 
            "dataType": ["text"],
            "description": "URL of the audited page"
        },
        {
            "name": "persona_name",
            "dataType": ["text"], 
            "description": "Name of the persona"
        },
        {
            "name": "persona_id",
            "dataType": ["text"],
            "description": "Unique identifier for the persona"
        },
        {
            "name": "domain",
            "dataType": ["text"],
            "description": "Domain of the audited page"
        },
        {
            "name": "content_type",
            "dataType": ["text"],
            "description": "Type of content (blog, service, etc.)"
        },
        {
            "name": "tier",
            "dataType": ["text"],
            "description": "Page tier classification"
        },
        {
            "name": "final_score",
            "dataType": ["number"],
            "description": "Final audit score"
        },
        {
            "name": "brand_health_index", 
            "dataType": ["number"],
            "description": "Brand health index score"
        },
        {
            "name": "trust_gap",
            "dataType": ["number"],
            "description": "Trust gap measurement"
        },
        {
            "name": "combined_analysis",
            "dataType": ["text"],
            "description": "Combined text for semantic search"
        },
        {
            "name": "key_themes",
            "dataType": ["text[]"],
            "description": "Key themes extracted from content"
        },
        {
            "name": "regulatory_frameworks",
            "dataType": ["text[]"],
            "description": "Relevant regulatory frameworks"
        },
        {
            "name": "is_benelux",
            "dataType": ["boolean"],
            "description": "Whether page is Benelux-specific"
        },
        {
            "name": "has_compliance_content",
            "dataType": ["boolean"],
            "description": "Whether page contains compliance content"
        },
        {
            "name": "has_security_content", 
            "dataType": ["boolean"],
            "description": "Whether page contains security content"
        },
        {
            "name": "audited_ts",
            "dataType": ["date"],
            "description": "Timestamp when page was audited"
        },
        {
            "name": "compiled_at",
            "dataType": ["date"],
            "description": "Timestamp when data was compiled"
        }
        # Removed problematic fields: overall_sentiment, engagement_level, conversion_likelihood
        # These should only apply to offsite channels, not onsite data (Tier 1, 2, 3)
    ],
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "text-embedding-3-small",
            "dimensions": 1536,
            "type": "text"
        }
    }
}

# Qdrant Configuration
QDRANT_CONFIG = {
    "collection_name": "sopra_persona_audit",
    "vector_config": {
        "size": 1536,
        "distance": "Cosine"
    },
    "payload_schema": {
        "persona_id": "keyword",
        "page_id": "keyword", 
        "domain": "keyword",
        "content_type": "keyword",
        "tier": "keyword",
        "final_score": "float",
        "brand_health_index": "float",
        "trust_gap": "float",
        "key_themes": "keyword",
        "regulatory_frameworks": "keyword",
        "is_benelux": "bool",
        "has_compliance_content": "bool",
        "has_security_content": "bool",
        "audited_ts": "datetime",
        "compiled_at": "datetime"
        # Removed problematic fields: overall_sentiment, engagement_level, conversion_likelihood
        # These should only apply to offsite channels, not onsite data (Tier 1, 2, 3)
    }
}

# ChromaDB Configuration
CHROMA_CONFIG = {
    "collection_name": "sopra_persona_audit",
    "embedding_function": "OpenAIEmbeddingFunction", 
    "metadata_fields": [
        "persona_id",
        "page_id",
        "domain",
        "content_type", 
        "tier",
        "final_score",
        "brand_health_index",
        "trust_gap",
        "is_benelux",
        "has_compliance_content",
        "has_security_content"
        # Removed problematic fields: overall_sentiment, engagement_level, conversion_likelihood
        # These should only apply to offsite channels, not onsite data (Tier 1, 2, 3)
    ]
}

# Query Templates
QUERY_TEMPLATES = {
    "find_by_persona": {
        "description": "Find all documents for a specific persona",
        "filter_template": {"persona_id": "{persona_id}"},
        "example": {"persona_id": "the_benelux_cybersecurity_decision_maker"}
    },
    
    "find_by_page": {
        "description": "Find all persona assessments for a specific page",
        "filter_template": {"page_id": "{page_id}"},
        "example": {"page_id": "fe8eb8c2"}
    },
    
    "find_high_scoring_pages": {
        "description": "Find pages with high audit scores",
        "filter_template": {"final_score": {"$gte": "{min_score}"}},
        "example": {"final_score": {"$gte": 7.0}}
    },
    
    "find_compliance_content": {
        "description": "Find pages with compliance-related content",
        "filter_template": {"has_compliance_content": True},
        "example": {"has_compliance_content": True}
    },
    
    "find_by_regulatory_framework": {
        "description": "Find pages related to specific regulatory frameworks",
        "filter_template": {"regulatory_frameworks": {"$in": ["{framework}"]}},
        "example": {"regulatory_frameworks": {"$in": ["GDPR"]}}
    },
    
    "find_benelux_content": {
        "description": "Find Benelux-specific content",
        "filter_template": {"is_benelux": True},
        "example": {"is_benelux": True}
    },
    
    "compare_personas_by_page": {
        "description": "Compare how different personas rate the same page",
        "filter_template": {"page_id": "{page_id}"},
        "sort_by": "final_score",
        "example": {"page_id": "fe8eb8c2"}
    },
    
    "find_low_scoring_pages": {
        "description": "Find pages with low audit scores",
        "filter_template": {"final_score": {"$lt": 6.0}},
        "example": {"final_score": {"$lt": 6.0}}
    }
    # Removed find_low_engagement query template - uses problematic engagement_level field
    # This field should only apply to offsite channels, not onsite data (Tier 1, 2, 3)
}

# Semantic Search Templates
SEMANTIC_SEARCH_TEMPLATES = {
    "trust_issues": {
        "query": "trust credibility issues concerns reliability problems",
        "description": "Find content with trust and credibility issues"
    },
    
    "regulatory_compliance": {
        "query": "GDPR NIS2 DORA compliance regulatory requirements legal obligations",
        "description": "Find content related to regulatory compliance"
    },
    
    "cybersecurity_concerns": {
        "query": "cybersecurity security threats vulnerabilities risk management",
        "description": "Find content related to cybersecurity"
    },
    
    "innovation_ai": {
        "query": "artificial intelligence AI innovation digital transformation technology",
        "description": "Find content about AI and innovation"
    },
    
    "financial_services": {
        "query": "banking financial services investment fintech payments",
        "description": "Find content related to financial services"
    },
    
    "public_sector": {
        "query": "government public sector administration civil service",
        "description": "Find content related to public sector"
    },
    
    "negative_sentiment": {
        "query": "poor weak insufficient inadequate missing broken failed",
        "description": "Find content with negative assessments"
    },
    
    "positive_differentiation": {
        "query": "excellent strong differentiated unique competitive advantage",
        "description": "Find content with positive differentiation"
    }
}

def get_vector_store_config(store_type: VectorStoreType) -> Dict[str, Any]:
    """Get configuration for specified vector store type."""
    configs = {
        VectorStoreType.PINECONE: PINECONE_CONFIG,
        VectorStoreType.WEAVIATE: WEAVIATE_CONFIG,
        VectorStoreType.QDRANT: QDRANT_CONFIG,
        VectorStoreType.CHROMA: CHROMA_CONFIG
    }
    return configs.get(store_type, {})

def get_query_template(template_name: str) -> Dict[str, Any]:
    """Get query template by name."""
    return QUERY_TEMPLATES.get(template_name, {})

def get_semantic_search_template(template_name: str) -> Dict[str, Any]:
    """Get semantic search template by name."""
    return SEMANTIC_SEARCH_TEMPLATES.get(template_name, {})

def list_available_templates() -> Dict[str, List[str]]:
    """List all available query and semantic search templates."""
    return {
        "query_templates": list(QUERY_TEMPLATES.keys()),
        "semantic_search_templates": list(SEMANTIC_SEARCH_TEMPLATES.keys())
    } 