#!/usr/bin/env python3
"""
Vector Pipeline Runner

Orchestrates the complete pipeline from persona data compilation to vector store upload.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from compile_persona_data import PersonaDataCompiler
from embeddings_generator import EmbeddingsGenerator
from vector_store_uploader import VectorStoreManager, VectorStoreType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorPipelineRunner:
    """Orchestrates the complete vector pipeline."""
    
    def __init__(self, audit_outputs_dir: str = "audit_outputs", vector_dir: str = "vector"):
        self.audit_outputs_dir = audit_outputs_dir
        self.vector_dir = vector_dir
        
        # Initialize components
        self.compiler = PersonaDataCompiler(audit_outputs_dir, vector_dir)
        self.embeddings_generator = EmbeddingsGenerator(vector_dir=vector_dir)
        self.vector_manager = VectorStoreManager(vector_dir)
    
    def run_compilation(self, force_recompile: bool = False) -> bool:
        """Run the persona data compilation step."""
        logger.info("=== STEP 1: Compiling Persona Data ===")
        
        compiled_file = Path(self.vector_dir) / "compiled_persona_data.json"
        
        if compiled_file.exists() and not force_recompile:
            logger.info(f"Compiled data already exists at {compiled_file}")
            logger.info("Use --force-recompile to regenerate")
            return True
        
        try:
            documents = self.compiler.compile_all_personas()
            
            if documents:
                self.compiler.save_compiled_data(documents)
                logger.info(f"✅ Successfully compiled {len(documents)} documents")
                return True
            else:
                logger.error("❌ No documents were compiled")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during compilation: {e}")
            return False
    
    def run_embeddings(self, force_regenerate: bool = False) -> bool:
        """Run the embeddings generation step."""
        logger.info("=== STEP 2: Generating Embeddings ===")
        
        embeddings_file = Path(self.vector_dir) / "embeddings_data.json"
        
        if embeddings_file.exists() and not force_regenerate:
            logger.info(f"Embeddings already exist at {embeddings_file}")
            logger.info("Use --force-regenerate to recreate embeddings")
            return True
        
        try:
            # Check for OpenAI API key
            if not os.getenv('OPENAI_API_KEY'):
                logger.error("❌ OPENAI_API_KEY environment variable not set")
                logger.info("Please set your OpenAI API key: export OPENAI_API_KEY='your-key-here'")
                return False
            
            # Load compiled data
            documents = self.embeddings_generator.load_compiled_data()
            if not documents:
                logger.error("❌ No compiled data found. Run compilation step first.")
                return False
            
            # Generate embeddings
            documents_with_embeddings = self.embeddings_generator.process_documents(documents)
            
            if documents_with_embeddings:
                # Save embeddings data
                self.embeddings_generator.save_embeddings_data(documents_with_embeddings)
                self.embeddings_generator.save_vectors_only(documents_with_embeddings)
                
                # Generate statistics
                stats = self.embeddings_generator.generate_embedding_statistics(documents_with_embeddings)
                
                stats_file = Path(self.vector_dir) / "embedding_statistics.json"
                import json
                with open(stats_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Successfully generated embeddings for {len(documents_with_embeddings)} documents")
                logger.info(f"📊 Total tokens used: {stats['token_usage']['total']}")
                return True
            else:
                logger.error("❌ Failed to generate embeddings")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during embeddings generation: {e}")
            return False
    
    def run_upload(self, vector_store: str) -> bool:
        """Run the vector store upload step."""
        logger.info(f"=== STEP 3: Uploading to {vector_store.upper()} ===")
        
        try:
            # Validate vector store type
            try:
                store_type = VectorStoreType(vector_store)
            except ValueError:
                logger.error(f"❌ Unsupported vector store: {vector_store}")
                logger.info("Supported stores: pinecone, weaviate, qdrant, chroma")
                return False
            
            # Check for required API keys
            api_key_map = {
                'pinecone': 'PINECONE_API_KEY',
                'weaviate': 'WEAVIATE_API_KEY',
                'qdrant': 'QDRANT_API_KEY'
            }
            
            if vector_store in api_key_map:
                env_var = api_key_map[vector_store]
                if not os.getenv(env_var):
                    logger.warning(f"⚠️  {env_var} not set. Trying with default configuration...")
            
            # Load embeddings data
            documents = self.vector_manager.load_embeddings_data()
            if not documents:
                logger.error("❌ No embeddings data found. Run embeddings generation first.")
                return False
            
            # Upload to vector store
            success = self.vector_manager.upload_to_store(store_type, documents)
            
            if success:
                logger.info(f"✅ Successfully uploaded {len(documents)} documents to {vector_store}")
                return True
            else:
                logger.error(f"❌ Failed to upload to {vector_store}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error during upload: {e}")
            return False
    
    def run_full_pipeline(self, vector_store: str = None, force_recompile: bool = False, 
                         force_regenerate: bool = False) -> bool:
        """Run the complete pipeline."""
        logger.info("🚀 Starting Vector Pipeline")
        
        # Step 1: Compile persona data
        if not self.run_compilation(force_recompile):
            return False
        
        # Step 2: Generate embeddings
        if not self.run_embeddings(force_regenerate):
            return False
        
        # Step 3: Upload to vector store (if specified)
        if vector_store:
            if not self.run_upload(vector_store):
                return False
        else:
            logger.info("📦 Vector store not specified. Skipping upload step.")
            logger.info("Data is ready for upload. Use --upload-to <store> to upload.")
        
        logger.info("🎉 Pipeline completed successfully!")
        return True

def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Run vector pipeline for persona audit data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline and upload to Pinecone
  python run_vector_pipeline.py --full --upload-to pinecone

  # Just compile data
  python run_vector_pipeline.py --compile

  # Generate embeddings only
  python run_vector_pipeline.py --embeddings

  # Upload existing data to ChromaDB
  python run_vector_pipeline.py --upload-to chroma

  # Force regenerate everything
  python run_vector_pipeline.py --full --force-recompile --force-regenerate
        """
    )
    
    # Action arguments
    parser.add_argument('--full', action='store_true', 
                       help='Run the complete pipeline')
    parser.add_argument('--compile', action='store_true',
                       help='Run only the compilation step')
    parser.add_argument('--embeddings', action='store_true',
                       help='Run only the embeddings generation step')
    parser.add_argument('--upload-to', choices=['pinecone', 'weaviate', 'qdrant', 'chroma'],
                       help='Upload to specified vector store')
    
    # Configuration arguments
    parser.add_argument('--audit-outputs-dir', default='audit_outputs',
                       help='Directory containing audit outputs (default: audit_outputs)')
    parser.add_argument('--vector-dir', default='vector',
                       help='Directory for vector data (default: vector)')
    
    # Force arguments
    parser.add_argument('--force-recompile', action='store_true',
                       help='Force recompilation even if data exists')
    parser.add_argument('--force-regenerate', action='store_true',
                       help='Force regeneration of embeddings even if they exist')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.full, args.compile, args.embeddings, args.upload_to]):
        parser.error("Please specify an action: --full, --compile, --embeddings, or --upload-to")
    
    # Initialize pipeline runner
    runner = VectorPipelineRunner(
        audit_outputs_dir=args.audit_outputs_dir,
        vector_dir=args.vector_dir
    )
    
    # Execute requested actions
    success = True
    
    if args.full:
        success = runner.run_full_pipeline(
            vector_store=args.upload_to,
            force_recompile=args.force_recompile,
            force_regenerate=args.force_regenerate
        )
    else:
        if args.compile:
            success = runner.run_compilation(args.force_recompile)
        
        if success and args.embeddings:
            success = runner.run_embeddings(args.force_regenerate)
        
        if success and args.upload_to:
            success = runner.run_upload(args.upload_to)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 