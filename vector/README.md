# Vector Store Setup for Persona Audit Data

This directory contains scripts to compile persona audit outcomes into vector store format, enabling advanced semantic search and analysis capabilities.

## Overview

The pipeline transforms raw audit outputs into searchable vector embeddings that can be queried by:

- **Persona-specific insights**: "What do cybersecurity executives think about our AI content?"
- **Cross-persona comparisons**: "Which pages resonate best with technical vs business audiences?"
- **Thematic analysis**: "Find all pages discussing compliance across all personas"
- **Content discovery**: "Show me pages with trust issues"

## Architecture

```
audit_outputs/ (input)
    ├── The Benelux Cybersecurity Decision Maker/
    │   ├── *_hygiene_scorecard.md
    │   ├── *_experience_report.md
    │   └── *.csv files
    └── [other personas...]

vector/ (this directory)
    ├── compiled_persona_data.json     # Combined data from all personas
    ├── embeddings_data.json          # Full data with embeddings
    ├── vectors.json                  # Lightweight vector format
    └── embedding_statistics.json     # Usage stats
```

## Data Structure

Each document in the vector store contains:

```json
{
  "page_id": "fe8eb8c2",
  "url": "https://www.soprasteria.nl/...",
  "persona": {
    "name": "The Benelux Cybersecurity Decision Maker",
    "description": "An executive responsible for..."
  },
  "hygiene_scorecard": {
    "tier": "Thought Leadership Blog / Insights Page",
    "final_score": 6.8,
    "detailed_scores": {...},
    "recommendations": [...]
  },
  "experience_report": {
    "overall_sentiment": "Neutral",
    "effective_copy": [...],
    "ineffective_copy": [...],
    "strategic_analysis": "..."
  },
  "embeddings_content": {
    "combined_analysis": "Full text for semantic search",
    "key_themes": ["trust", "security", "compliance"],
    "business_impact": "..."
  },
  "metadata": {
    "persona_id": "the_benelux_cybersecurity_decision_maker",
    "domain": "soprasteria.nl",
    "content_type": "blog",
    "regulatory_frameworks": ["GDPR", "NIS2"],
    "has_compliance_content": true,
    ...
  }
}
```

## Setup

### 1. Install Dependencies

```bash
# Core dependencies
pip install pandas numpy openai tiktoken

# Vector store clients (install as needed)
pip install pinecone-client weaviate-client qdrant-client chromadb

# Or install all at once
pip install -r vector/requirements.txt
```

### 2. Set Environment Variables

```bash
# Required for embeddings generation
export OPENAI_API_KEY="your-openai-api-key"

# Optional: for specific vector stores
export PINECONE_API_KEY="your-pinecone-key"
export WEAVIATE_API_KEY="your-weaviate-key"
export QDRANT_API_KEY="your-qdrant-key"
```

## Usage

### Quick Start (Full Pipeline)

```bash
# Run everything and upload to ChromaDB (local)
cd vector
python run_vector_pipeline.py --full --upload-to chroma

# Or upload to Pinecone (cloud)
python run_vector_pipeline.py --full --upload-to pinecone
```

### Step-by-Step

```bash
# 1. Compile persona data from audit outputs
python run_vector_pipeline.py --compile

# 2. Generate embeddings (requires OpenAI API key)
python run_vector_pipeline.py --embeddings

# 3. Upload to vector store
python run_vector_pipeline.py --upload-to chroma
```

### Advanced Usage

```bash
# Force regenerate everything
python run_vector_pipeline.py --full --force-recompile --force-regenerate

# Use custom directories
python run_vector_pipeline.py --full \
  --audit-outputs-dir ../custom_audit_outputs \
  --vector-dir ./custom_vector_dir

# Run individual scripts
python compile_persona_data.py
python embeddings_generator.py
python vector_store_uploader.py --store pinecone
```

## Vector Store Options

### 1. ChromaDB (Recommended for Local Development)

- **Pros**: Easy setup, no API keys required, good for development
- **Cons**: Local only, limited scalability
- **Setup**: No additional configuration needed

```bash
python run_vector_pipeline.py --upload-to chroma
```

### 2. Pinecone (Recommended for Production)

- **Pros**: Managed service, excellent performance, scalable
- **Cons**: Requires API key, paid service
- **Setup**: Set `PINECONE_API_KEY`

```bash
export PINECONE_API_KEY="your-key"
python run_vector_pipeline.py --upload-to pinecone
```

### 3. Weaviate

- **Pros**: Rich schema, built-in ML models, GraphQL queries
- **Cons**: More complex setup
- **Setup**: Set `WEAVIATE_URL` and optionally `WEAVIATE_API_KEY`

```bash
export WEAVIATE_URL="http://localhost:8080"
python run_vector_pipeline.py --upload-to weaviate
```

### 4. Qdrant

- **Pros**: High performance, rich filtering, open source
- **Cons**: Requires separate deployment
- **Setup**: Set `QDRANT_URL` and optionally `QDRANT_API_KEY`

```bash
export QDRANT_URL="http://localhost:6333"
python run_vector_pipeline.py --upload-to qdrant
```

## Query Examples

Once data is uploaded, you can query using the vector store's native tools or build custom applications. Here are some example query patterns:

### Semantic Search Examples

```python
# Find trust issues across all personas
query = "trust credibility reliability problems concerns"

# Find regulatory compliance content
query = "GDPR NIS2 DORA compliance regulatory requirements"

# Find cybersecurity-related content
query = "cybersecurity security threats vulnerabilities risk"
```

### Metadata Filtering Examples

```python
# Find high-scoring pages from cybersecurity persona
filters = {
    "persona_id": "the_benelux_cybersecurity_decision_maker",
    "final_score": {"$gte": 7.0}
}

# Find Benelux-specific compliance content
filters = {
    "is_benelux": True,
    "has_compliance_content": True
}

# Compare how different personas rate the same page
filters = {
    "page_id": "fe8eb8c2"  # Returns all persona assessments for this page
}
```

## File Descriptions

- **`compile_persona_data.py`**: Parses audit outputs and creates unified JSON documents
- **`embeddings_generator.py`**: Generates OpenAI embeddings for semantic search
- **`vector_store_uploader.py`**: Uploads data to various vector databases
- **`vector_schema.py`**: Configuration and schemas for different vector stores
- **`run_vector_pipeline.py`**: Orchestration script for the complete pipeline
- **`requirements.txt`**: Python dependencies

## Output Files

After running the pipeline, you'll have:

- **`compiled_persona_data.json`**: Raw compiled data (large file)
- **`embeddings_data.json`**: Full data with embeddings (very large file)
- **`vectors.json`**: Lightweight format with just vectors and metadata
- **`embedding_statistics.json`**: Token usage and processing stats
- **`persona_*.json`**: Individual files per persona for debugging

## Cost Considerations

Embedding generation uses OpenAI's API:

- **Model**: `text-embedding-3-small` (1536 dimensions)
- **Cost**: ~$0.00002 per 1K tokens
- **Estimated cost**: $2-5 for full dataset (depending on content volume)

## Troubleshooting

### Common Issues

1. **"No documents compiled"**

   - Check that `audit_outputs/` directory exists and contains persona folders
   - Verify markdown files follow expected naming pattern

2. **"OPENAI_API_KEY not set"**

   - Set the environment variable: `export OPENAI_API_KEY="your-key"`

3. **Vector store connection errors**

   - Check API keys and connection URLs
   - Verify vector store is running (for local deployments)

4. **Out of memory errors**
   - Reduce batch size in embedding generation
   - Process personas individually using individual scripts

### Debug Mode

For detailed logging:

```bash
export PYTHONPATH=$PYTHONPATH:./vector
python -m logging.basicConfig level=DEBUG
python run_vector_pipeline.py --full
```

## Next Steps

Once your data is in a vector store, you can:

1. **Build semantic search interfaces** for exploring audit results
2. **Create persona comparison dashboards** showing cross-persona insights
3. **Set up automated alerts** for content quality issues
4. **Integrate with LLM applications** for intelligent audit analysis
5. **Develop recommendation engines** for content optimization

## Support

For issues with the vector pipeline, check:

- File permissions in audit_outputs and vector directories
- Python environment and dependency versions
- API key validity and quotas
- Vector store service status
