#!/usr/bin/env python3
"""
Vector Store Uploader for Persona Audit Data

Uploads processed embeddings to various vector databases.
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass
from abc import ABC, abstractmethod

from vector_schema import VectorStoreType, get_vector_store_config, VectorStoreConfig

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorStoreUploader(ABC):
    """Abstract base class for vector store uploaders."""
    
    @abstractmethod
    def create_index(self, config: Dict[str, Any]) -> bool:
        """Create index/collection in vector store."""
        pass
    
    @abstractmethod
    def upload_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to vector store."""
        pass
    
    @abstractmethod
    def query_documents(self, query_vector: List[float], filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query documents from vector store."""
        pass

class PineconeUploader(VectorStoreUploader):
    """Pinecone vector store uploader."""
    
    def __init__(self, api_key: str = None, environment: str = "us-east-1"):
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.environment = environment
        self.pc = None
        self.index = None
        
        if not self.api_key:
            raise ValueError("Pinecone API key is required")
        
        self._init_client()
    
    def _init_client(self):
        """Initialize Pinecone client."""
        try:
            from pinecone import Pinecone
            self.pc = Pinecone(api_key=self.api_key)
            logger.info("Pinecone client initialized")
        except ImportError:
            logger.error("Pinecone package not installed. Run: pip install pinecone-client")
            raise
    
    def create_index(self, config: Dict[str, Any]) -> bool:
        """Create Pinecone index."""
        try:
            index_name = config.get('index_name', 'sopra-persona-audit')
            
            # Check if index exists
            existing_indexes = self.pc.list_indexes()
            if index_name in [idx.name for idx in existing_indexes]:
                logger.info(f"Index {index_name} already exists")
                self.index = self.pc.Index(index_name)
                return True
            
            # Create new index
            self.pc.create_index(
                name=index_name,
                dimension=config.get('dimension', 1536),
                metric=config.get('metric', 'cosine'),
                spec=config.get('spec', {})
            )
            
            # Wait for index to be ready
            while not self.pc.describe_index(index_name).status['ready']:
                time.sleep(1)
            
            self.index = self.pc.Index(index_name)
            logger.info(f"Created Pinecone index: {index_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Pinecone index: {e}")
            return False
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to Pinecone."""
        try:
            if not self.index:
                logger.error("No Pinecone index available")
                return False
            
            # Prepare vectors for upload
            vectors = []
            for doc in documents:
                vector_id = f"{doc['page_id']}_{doc['metadata']['persona_id']}"
                
                metadata = {
                    "page_id": doc['page_id'],
                    "persona_id": doc['metadata']['persona_id'],
                    "url": doc['url'],
                    "final_score": float(doc['hygiene_scorecard']['final_score']),
                    "domain": doc['metadata']['domain'],
                    "content_type": doc['metadata']['content_type'],
                    "tier": doc['metadata']['tier'],
                    "is_benelux": doc['metadata']['is_benelux'],
                    "has_compliance_content": doc['metadata']['has_compliance_content'],
                    "has_security_content": doc['metadata']['has_security_content']
                }
                
                vectors.append({
                    "id": vector_id,
                    "values": doc['embedding'],
                    "metadata": metadata
                })
            
            # Upload in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
                logger.info(f"Uploaded batch {i//batch_size + 1}: {len(batch)} vectors")
            
            logger.info(f"Successfully uploaded {len(vectors)} vectors to Pinecone")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to Pinecone: {e}")
            return False
    
    def query_documents(self, query_vector: List[float], filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query documents from Pinecone."""
        try:
            if not self.index:
                logger.error("No Pinecone index available")
                return []
            
            response = self.index.query(
                vector=query_vector,
                filter=filters,
                top_k=top_k,
                include_metadata=True
            )
            
            results = []
            for match in response['matches']:
                results.append({
                    "id": match['id'],
                    "score": match['score'],
                    "metadata": match['metadata']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying Pinecone: {e}")
            return []

class WeaviateUploader(VectorStoreUploader):
    """Weaviate vector store uploader."""
    
    def __init__(self, url: str = None, api_key: str = None):
        self.url = url or os.getenv('WEAVIATE_URL', 'http://localhost:8080')
        self.api_key = api_key or os.getenv('WEAVIATE_API_KEY')
        self.client = None
        
        self._init_client()
    
    def _init_client(self):
        """Initialize Weaviate client."""
        try:
            import weaviate
            
            if self.api_key:
                self.client = weaviate.Client(
                    url=self.url,
                    auth_client_secret=weaviate.AuthApiKey(api_key=self.api_key)
                )
            else:
                self.client = weaviate.Client(url=self.url)
            
            logger.info("Weaviate client initialized")
        except ImportError:
            logger.error("Weaviate package not installed. Run: pip install weaviate-client")
            raise
    
    def create_index(self, config: Dict[str, Any]) -> bool:
        """Create Weaviate class."""
        try:
            class_name = config.get('class_name', 'PersonaAuditDocument')
            
            # Check if class exists
            if self.client.schema.exists(class_name):
                logger.info(f"Class {class_name} already exists")
                return True
            
            # Create class
            class_obj = {
                "class": class_name,
                "properties": config.get('properties', []),
                "vectorizer": config.get('vectorizer', 'text2vec-openai'),
                "moduleConfig": config.get('moduleConfig', {})
            }
            
            self.client.schema.create_class(class_obj)
            logger.info(f"Created Weaviate class: {class_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Weaviate class: {e}")
            return False
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to Weaviate."""
        try:
            class_name = "PersonaAuditDocument"
            
            # Prepare documents for upload
            with self.client.batch as batch:
                batch.batch_size = 100
                
                for doc in documents:
                    properties = {
                        "page_id": doc['page_id'],
                        "url": doc['url'],
                        "persona_name": doc['persona']['name'],
                        "persona_id": doc['metadata']['persona_id'],
                        "domain": doc['metadata']['domain'],
                        "content_type": doc['metadata']['content_type'],
                        "tier": doc['metadata']['tier'],
                        "final_score": doc['hygiene_scorecard']['final_score'],
                        "brand_health_index": doc['hygiene_scorecard']['brand_health_index'],
                        "trust_gap": doc['hygiene_scorecard']['trust_gap'],
                        "overall_sentiment": doc['experience_report']['overall_sentiment'],
                        "engagement_level": doc['experience_report']['engagement_level'],
                        "conversion_likelihood": doc['experience_report']['conversion_likelihood'],
                        "combined_analysis": doc['embeddings_content']['combined_analysis'],
                        "key_themes": doc['embeddings_content']['key_themes'],
                        "regulatory_frameworks": doc['metadata']['regulatory_frameworks'],
                        "is_benelux": doc['metadata']['is_benelux'],
                        "has_compliance_content": doc['metadata']['has_compliance_content'],
                        "has_security_content": doc['metadata']['has_security_content'],
                        "audited_ts": doc['hygiene_scorecard']['audited_ts'],
                        "compiled_at": doc['metadata']['compiled_at']
                    }
                    
                    batch.add_data_object(
                        data_object=properties,
                        class_name=class_name,
                        vector=doc['embedding']
                    )
            
            logger.info(f"Successfully uploaded {len(documents)} documents to Weaviate")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to Weaviate: {e}")
            return False
    
    def query_documents(self, query_vector: List[float], filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query documents from Weaviate."""
        try:
            query = self.client.query.get("PersonaAuditDocument", [
                "page_id", "url", "persona_name", "final_score", "domain"
            ]).with_near_vector({
                "vector": query_vector
            }).with_limit(top_k)
            
            if filters:
                query = query.with_where(filters)
            
            response = query.do()
            
            results = []
            if 'data' in response and 'Get' in response['data']:
                for item in response['data']['Get']['PersonaAuditDocument']:
                    results.append(item)
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying Weaviate: {e}")
            return []

class QdrantUploader(VectorStoreUploader):
    """Qdrant vector store uploader."""
    
    def __init__(self, url: str = None, api_key: str = None):
        self.url = url or os.getenv('QDRANT_URL', 'http://localhost:6333')
        self.api_key = api_key or os.getenv('QDRANT_API_KEY')
        self.client = None
        
        self._init_client()
    
    def _init_client(self):
        """Initialize Qdrant client."""
        try:
            from qdrant_client import QdrantClient
            
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key
            )
            logger.info("Qdrant client initialized")
        except ImportError:
            logger.error("Qdrant package not installed. Run: pip install qdrant-client")
            raise
    
    def create_index(self, config: Dict[str, Any]) -> bool:
        """Create Qdrant collection."""
        try:
            from qdrant_client.models import Distance, VectorParams
            
            collection_name = config.get('collection_name', 'sopra_persona_audit')
            
            # Check if collection exists
            collections = self.client.get_collections()
            if collection_name in [c.name for c in collections.collections]:
                logger.info(f"Collection {collection_name} already exists")
                return True
            
            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config.get('vector_config', {}).get('size', 1536),
                    distance=Distance.COSINE
                )
            )
            
            logger.info(f"Created Qdrant collection: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating Qdrant collection: {e}")
            return False
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to Qdrant."""
        try:
            from qdrant_client.models import PointStruct
            
            collection_name = "sopra_persona_audit"
            
            # Prepare points for upload
            points = []
            for i, doc in enumerate(documents):
                payload = {
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
                
                points.append(PointStruct(
                    id=i,
                    vector=doc['embedding'],
                    payload=payload
                ))
            
            # Upload points
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
            logger.info(f"Successfully uploaded {len(points)} points to Qdrant")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to Qdrant: {e}")
            return False
    
    def query_documents(self, query_vector: List[float], filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query documents from Qdrant."""
        try:
            collection_name = "sopra_persona_audit"
            
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=filters,
                limit=top_k,
                with_payload=True
            )
            
            results = []
            for point in search_result:
                results.append({
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying Qdrant: {e}")
            return []

class ChromaUploader(VectorStoreUploader):
    """ChromaDB vector store uploader."""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or "./chroma_db"
        self.client = None
        self.collection = None
        
        self._init_client()
    
    def _init_client(self):
        """Initialize ChromaDB client."""
        try:
            import chromadb
            
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            logger.info("ChromaDB client initialized")
        except ImportError:
            logger.error("ChromaDB package not installed. Run: pip install chromadb")
            raise
    
    def create_index(self, config: Dict[str, Any]) -> bool:
        """Create ChromaDB collection."""
        try:
            collection_name = config.get('collection_name', 'sopra_persona_audit')
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Sopra Steria persona audit data"}
            )
            
            logger.info(f"ChromaDB collection ready: {collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating ChromaDB collection: {e}")
            return False
    
    def upload_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to ChromaDB."""
        try:
            if not self.collection:
                logger.error("No ChromaDB collection available")
                return False
            
            # Prepare data for upload
            ids = []
            embeddings = []
            metadatas = []
            documents_text = []
            
            for doc in documents:
                doc_id = f"{doc['page_id']}_{doc['metadata']['persona_id']}"
                ids.append(doc_id)
                embeddings.append(doc['embedding'])
                
                metadata = {
                    "page_id": doc['page_id'],
                    "persona_id": doc['metadata']['persona_id'],
                    "url": doc['url'],
                    "final_score": doc['hygiene_scorecard']['final_score'],
                    "domain": doc['metadata']['domain'],
                    "content_type": doc['metadata']['content_type'],
                    "tier": doc['metadata']['tier'],
                    "is_benelux": doc['metadata']['is_benelux'],
                    "has_compliance_content": doc['metadata']['has_compliance_content'],
                    "has_security_content": doc['metadata']['has_security_content']
                }
                metadatas.append(metadata)
                
                # Use combined analysis as document text
                documents_text.append(doc['embeddings_content']['combined_analysis'][:1000])
            
            # Upload to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            
            logger.info(f"Successfully uploaded {len(ids)} documents to ChromaDB")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading to ChromaDB: {e}")
            return False
    
    def query_documents(self, query_vector: List[float], filters: Dict[str, Any] = None, top_k: int = 10) -> List[Dict[str, Any]]:
        """Query documents from ChromaDB."""
        try:
            if not self.collection:
                logger.error("No ChromaDB collection available")
                return []
            
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=filters,
                include=["metadatas", "distances", "documents"]
            )
            
            query_results = []
            if results['metadatas']:
                for i, metadata in enumerate(results['metadatas'][0]):
                    query_results.append({
                        "id": results['ids'][0][i],
                        "distance": results['distances'][0][i],
                        "metadata": metadata,
                        "document": results['documents'][0][i] if results['documents'] else ""
                    })
            
            return query_results
            
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

class VectorStoreManager:
    """Manager class for handling multiple vector stores."""
    
    def __init__(self, vector_dir: str = "vector"):
        self.vector_dir = Path(vector_dir)
        self.uploaders: Dict[str, VectorStoreUploader] = {}
    
    def get_uploader(self, store_type: VectorStoreType) -> Optional[VectorStoreUploader]:
        """Get uploader for specified vector store type."""
        if store_type.value not in self.uploaders:
            try:
                if store_type == VectorStoreType.PINECONE:
                    self.uploaders[store_type.value] = PineconeUploader()
                elif store_type == VectorStoreType.WEAVIATE:
                    self.uploaders[store_type.value] = WeaviateUploader()
                elif store_type == VectorStoreType.QDRANT:
                    self.uploaders[store_type.value] = QdrantUploader()
                elif store_type == VectorStoreType.CHROMA:
                    self.uploaders[store_type.value] = ChromaUploader()
                else:
                    logger.error(f"Unsupported vector store type: {store_type}")
                    return None
            except Exception as e:
                logger.error(f"Error initializing {store_type.value} uploader: {e}")
                return None
        
        return self.uploaders.get(store_type.value)
    
    def upload_to_store(self, store_type: VectorStoreType, documents: List[Dict[str, Any]]) -> bool:
        """Upload documents to specified vector store."""
        uploader = self.get_uploader(store_type)
        if not uploader:
            return False
        
        # Get configuration for the store type
        config = get_vector_store_config(store_type)
        
        # Create index/collection
        if not uploader.create_index(config):
            logger.error(f"Failed to create index for {store_type.value}")
            return False
        
        # Upload documents
        return uploader.upload_documents(documents)
    
    def load_embeddings_data(self, filename: str = "embeddings_data.json") -> List[Dict[str, Any]]:
        """Load embeddings data from file."""
        input_file = self.vector_dir / filename
        
        if not input_file.exists():
            logger.error(f"Embeddings data file not found: {input_file}")
            return []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
        
        logger.info(f"Loaded {len(documents)} documents with embeddings")
        return documents

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload persona audit data to vector stores')
    parser.add_argument('--store', choices=['pinecone', 'weaviate', 'qdrant', 'chroma'], 
                       required=True, help='Vector store type')
    parser.add_argument('--data-file', default='embeddings_data.json', 
                       help='Input embeddings data file')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = VectorStoreManager()
    
    # Load data
    documents = manager.load_embeddings_data(args.data_file)
    if not documents:
        logger.error("No documents to upload")
        return
    
    # Upload to specified store
    store_type = VectorStoreType(args.store)
    success = manager.upload_to_store(store_type, documents)
    
    if success:
        logger.info(f"Successfully uploaded to {args.store}")
    else:
        logger.error(f"Failed to upload to {args.store}")

if __name__ == "__main__":
    main()