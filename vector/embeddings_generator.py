#!/usr/bin/env python3
"""
Embeddings Generator for Persona Audit Data

Generates embeddings from compiled persona data for vector store ingestion.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
import openai
from openai import OpenAI
import numpy as np
import tiktoken

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model: str = "text-embedding-3-small"
    dimensions: int = 1536
    batch_size: int = 100
    max_tokens: int = 8000
    rate_limit_delay: float = 0.1

class EmbeddingsGenerator:
    """Generate embeddings for persona audit documents."""
    
    def __init__(self, config: EmbeddingConfig = None, vector_dir: str = "vector"):
        self.config = config or EmbeddingConfig()
        self.vector_dir = Path(vector_dir)
        self.client = None
        self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        
        # Initialize OpenAI client
        self._init_openai_client()
    
    def _init_openai_client(self):
        """Initialize OpenAI client with API key."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OpenAI API key is required")
        
        self.client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        return len(self.encoding.encode(text))
    
    def truncate_text(self, text: str, max_tokens: int = None) -> str:
        """Truncate text to fit within token limit."""
        max_tokens = max_tokens or self.config.max_tokens
        
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        
        # Truncate and decode back to text
        truncated_tokens = tokens[:max_tokens]
        truncated_text = self.encoding.decode(truncated_tokens)
        
        logger.warning(f"Truncated text from {len(tokens)} to {len(truncated_tokens)} tokens")
        return truncated_text
    
    def prepare_embedding_text(self, document: Dict[str, Any]) -> str:
        """Prepare text content for embedding generation."""
        text_components = []
        
        # Add persona context
        persona_name = document.get('persona', {}).get('name', '')
        if persona_name:
            text_components.append(f"PERSONA: {persona_name}")
        
        # Add page URL and metadata
        url = document.get('url', '')
        if url:
            text_components.append(f"URL: {url}")
        
        domain = document.get('metadata', {}).get('domain', '')
        content_type = document.get('metadata', {}).get('content_type', '')
        if domain and content_type:
            text_components.append(f"CONTENT: {content_type} from {domain}")
        
        # Add key themes
        key_themes = document.get('embeddings_content', {}).get('key_themes', [])
        if key_themes:
            text_components.append(f"THEMES: {', '.join(key_themes)}")
        
        # Add regulatory frameworks
        frameworks = document.get('metadata', {}).get('regulatory_frameworks', [])
        if frameworks:
            text_components.append(f"REGULATORY: {', '.join(frameworks)}")
        
        # Add scores for context
        final_score = document.get('hygiene_scorecard', {}).get('final_score', 0)
        if final_score:
            text_components.append(f"ASSESSMENT: Score {final_score}/10")
        
        # Add main content
        combined_analysis = document.get('embeddings_content', {}).get('combined_analysis', '')
        if combined_analysis:
            text_components.append(f"ANALYSIS:\n{combined_analysis}")
        
        # Add first impression and strategic analysis
        first_impression = document.get('experience_report', {}).get('first_impression', '')
        if first_impression:
            text_components.append(f"FIRST IMPRESSION:\n{first_impression}")
        
        strategic_analysis = document.get('experience_report', {}).get('strategic_analysis', '')
        if strategic_analysis:
            text_components.append(f"STRATEGIC ANALYSIS:\n{strategic_analysis}")
        
        # Add effective and ineffective copy examples
        effective_copy = document.get('experience_report', {}).get('effective_copy', [])
        if effective_copy:
            effective_texts = [f"{item.get('text', '')}: {item.get('analysis', '')}" for item in effective_copy]
            text_components.append(f"EFFECTIVE COPY:\n" + "\n".join(effective_texts))
        
        ineffective_copy = document.get('experience_report', {}).get('ineffective_copy', [])
        if ineffective_copy:
            ineffective_texts = [f"{item.get('text', '')}: {item.get('analysis', '')}" for item in ineffective_copy]
            text_components.append(f"INEFFECTIVE COPY:\n" + "\n".join(ineffective_texts))
        
        # Add recommendations
        recommendations = document.get('hygiene_scorecard', {}).get('recommendations', [])
        if recommendations:
            rec_texts = [f"{rec.get('priority', '')} Priority: {rec.get('recommendation', '')}" for rec in recommendations]
            text_components.append(f"RECOMMENDATIONS:\n" + "\n".join(rec_texts))
        
        # Combine all components
        full_text = "\n\n".join(text_components)
        
        # Truncate if necessary
        return self.truncate_text(full_text)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            response = self.client.embeddings.create(
                model=self.config.model,
                input=text,
                dimensions=self.config.dimensions
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding with {len(embedding)} dimensions")
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a batch of texts."""
        try:
            response = self.client.embeddings.create(
                model=self.config.model,
                input=texts,
                dimensions=self.config.dimensions
            )
            
            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings in batch")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return []
    
    def process_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process documents and add embeddings."""
        processed_documents = []
        
        logger.info(f"Processing {len(documents)} documents for embeddings")
        
        # Process in batches
        for i in range(0, len(documents), self.config.batch_size):
            batch_end = min(i + self.config.batch_size, len(documents))
            batch_documents = documents[i:batch_end]
            
            logger.info(f"Processing batch {i//self.config.batch_size + 1}: documents {i+1}-{batch_end}")
            
            # Prepare texts for embedding
            batch_texts = []
            for doc in batch_documents:
                embedding_text = self.prepare_embedding_text(doc)
                batch_texts.append(embedding_text)
            
            # Generate embeddings
            batch_embeddings = self.generate_embeddings_batch(batch_texts)
            
            if len(batch_embeddings) != len(batch_documents):
                logger.error(f"Embedding count mismatch: {len(batch_embeddings)} != {len(batch_documents)}")
                continue
            
            # Add embeddings to documents
            for doc, embedding, text in zip(batch_documents, batch_embeddings, batch_texts):
                doc_with_embedding = doc.copy()
                doc_with_embedding['embedding'] = embedding
                doc_with_embedding['embedding_text'] = text
                doc_with_embedding['embedding_tokens'] = self.count_tokens(text)
                doc_with_embedding['embedding_model'] = self.config.model
                doc_with_embedding['embedding_dimensions'] = self.config.dimensions
                
                processed_documents.append(doc_with_embedding)
            
            # Rate limiting
            if i + self.config.batch_size < len(documents):
                time.sleep(self.config.rate_limit_delay)
        
        logger.info(f"Successfully processed {len(processed_documents)} documents with embeddings")
        return processed_documents
    
    def save_embeddings_data(self, documents: List[Dict[str, Any]], filename: str = "embeddings_data.json"):
        """Save documents with embeddings to file."""
        output_file = self.vector_dir / filename
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(documents)} documents with embeddings to {output_file}")
    
    def save_vectors_only(self, documents: List[Dict[str, Any]], filename: str = "vectors.json"):
        """Save only vectors and minimal metadata for efficient loading."""
        vectors_data = []
        
        for doc in documents:
            vector_doc = {
                "id": f"{doc['page_id']}_{doc['metadata']['persona_id']}",
                "vector": doc.get('embedding', []),
                "metadata": {
                    "page_id": doc['page_id'],
                    "persona_id": doc['metadata']['persona_id'],
                    "url": doc['url'],
                    "final_score": doc['hygiene_scorecard']['final_score'],
                    "domain": doc['metadata']['domain'],
                    "content_type": doc['metadata']['content_type'],
                    "tier": doc['metadata']['tier'],
                    "key_themes": doc['embeddings_content']['key_themes'],
                    "regulatory_frameworks": doc['metadata']['regulatory_frameworks'],
                    "is_benelux": doc['metadata']['is_benelux'],
                    "has_compliance_content": doc['metadata']['has_compliance_content'],
                    "has_security_content": doc['metadata']['has_security_content']
                }
            }
            vectors_data.append(vector_doc)
        
        output_file = self.vector_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(vectors_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(vectors_data)} vector documents to {output_file}")
    
    def generate_embedding_statistics(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about embeddings."""
        if not documents:
            return {}
        
        # Calculate statistics
        embedding_dims = [len(doc.get('embedding', [])) for doc in documents]
        token_counts = [doc.get('embedding_tokens', 0) for doc in documents]
        
        stats = {
            "total_documents": len(documents),
            "embedding_dimensions": {
                "min": min(embedding_dims) if embedding_dims else 0,
                "max": max(embedding_dims) if embedding_dims else 0,
                "avg": np.mean(embedding_dims) if embedding_dims else 0
            },
            "token_usage": {
                "min": min(token_counts) if token_counts else 0,
                "max": max(token_counts) if token_counts else 0,
                "avg": np.mean(token_counts) if token_counts else 0,
                "total": sum(token_counts)
            },
            "model_info": {
                "model": self.config.model,
                "dimensions": self.config.dimensions,
                "max_tokens": self.config.max_tokens
            },
            "personas": list(set(doc['metadata']['persona_id'] for doc in documents)),
            "domains": list(set(doc['metadata']['domain'] for doc in documents)),
            "content_types": list(set(doc['metadata']['content_type'] for doc in documents))
        }
        
        return stats
    
    def load_compiled_data(self, filename: str = "compiled_persona_data.json") -> List[Dict[str, Any]]:
        """Load compiled persona data."""
        input_file = self.vector_dir / filename
        
        if not input_file.exists():
            logger.error(f"Compiled data file not found: {input_file}")
            return []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        logger.info(f"Loaded {len(documents)} documents from {input_file}")
        return documents

def main():
    """Main execution function."""
    generator = EmbeddingsGenerator()
    
    logger.info("Starting embeddings generation...")
    
    # Load compiled data
    documents = generator.load_compiled_data()
    if not documents:
        logger.error("No documents found to process")
        return
    
    # Generate embeddings
    documents_with_embeddings = generator.process_documents(documents)
    
    if documents_with_embeddings:
        # Save full data with embeddings
        generator.save_embeddings_data(documents_with_embeddings)
        
        # Save vectors-only format
        generator.save_vectors_only(documents_with_embeddings)
        
        # Generate and save statistics
        stats = generator.generate_embedding_statistics(documents_with_embeddings)
        
        stats_file = generator.vector_dir / "embedding_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved embedding statistics to {stats_file}")
        logger.info(f"Total tokens used: {stats['token_usage']['total']}")
        logger.info("Embeddings generation completed successfully!")
    else:
        logger.error("Failed to generate embeddings")

if __name__ == "__main__":
    main() 