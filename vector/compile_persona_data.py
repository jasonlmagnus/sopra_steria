#!/usr/bin/env python3
"""
Compile persona audit outcomes into vector store format.

This script processes all persona audit outputs and combines hygiene scorecards 
and experience reports into unified JSON documents for vector store ingestion.
"""

import json
import os
import re
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PersonaDataCompiler:
    def __init__(self, audit_outputs_dir: str = "audit_outputs", vector_dir: str = "vector"):
        self.audit_outputs_dir = Path(audit_outputs_dir)
        self.vector_dir = Path(vector_dir)
        self.vector_dir.mkdir(exist_ok=True)
        
    def parse_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse markdown file and extract structured data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract header information
            header_info = {}
            
            # Extract URL from header
            url_match = re.search(r'\*\*URL:\*\*\s*(.+?)(?:\s|\n)', content)
            if url_match:
                header_info['url'] = url_match.group(1).strip()
            
            # Extract persona from header
            persona_match = re.search(r'\*\*Persona:\*\*\s*(.+?)(?:\n\n|\*\*)', content, re.DOTALL)
            if persona_match:
                header_info['persona_description'] = persona_match.group(1).strip()
            
            # Extract audit timestamp
            audited_match = re.search(r'\*\*Audited:\*\*\s*(.+?)(?:\s|\n)', content)
            if audited_match:
                header_info['audited_ts'] = audited_match.group(1).strip()
            
            return {
                'header_info': header_info,
                'full_content': content
            }
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return {}
    
    def parse_hygiene_scorecard(self, file_path: Path) -> Dict[str, Any]:
        """Parse hygiene scorecard markdown file."""
        data = self.parse_markdown_file(file_path)
        if not data:
            return {}
        
        content = data['full_content']
        
        # Extract overall assessment
        tier_match = re.search(r'\*\*Tier/Channel:\*\*\s*(.+?)(?:\s|\n)', content)
        score_match = re.search(r'\*\*Final Score:\*\*\s*(\d+\.?\d*)/10', content)
        
        # Extract detailed scoring table
        detailed_scores = {}
        scoring_section = re.search(r'## Detailed Scoring\s*\n(.+?)(?=##|$)', content, re.DOTALL)
        if scoring_section:
            table_content = scoring_section.group(1)
            # Parse table rows
            rows = re.findall(r'\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|', table_content)
            for category, score, rationale in rows:
                detailed_scores[category.strip().lower().replace(' ', '_')] = {
                    'score': int(score),
                    'rationale': rationale.strip()
                }
        
        # Extract recommendations
        recommendations = []
        recommendations_section = re.search(r'## Priority Recommendations\s*\n(.+?)(?=##|$)', content, re.DOTALL)
        if recommendations_section:
            rec_content = recommendations_section.group(1)
            rec_items = re.findall(r'\d+\.\s*\*\*(.+?):\*\*\s*(.+?)(?=\d+\.|$)', rec_content, re.DOTALL)
            for priority, recommendation in rec_items:
                recommendations.append({
                    'priority': priority.strip(),
                    'recommendation': recommendation.strip()
                })
        
        return {
            'header_info': data['header_info'],
            'tier': tier_match.group(1).strip() if tier_match else "",
            'final_score': float(score_match.group(1)) if score_match else 0.0,
            'detailed_scores': detailed_scores,
            'recommendations': recommendations,
            'full_content': content
        }
    
    def parse_experience_report(self, file_path: Path) -> Dict[str, Any]:
        """Parse experience report markdown file."""
        data = self.parse_markdown_file(file_path)
        if not data:
            return {}
        
        content = data['full_content']
        
        # Extract effective and ineffective copy examples from table
        effective_copy = []
        ineffective_copy = []
        
        # Look for table with findings
        table_match = re.search(r'\|\s*Finding\s*\|\s*Example from Text\s*\|\s*Strategic Analysis.*?\n(.+?)(?=\n\n|\n---)', content, re.DOTALL)
        if table_match:
            table_content = table_match.group(1)
            rows = re.findall(r'\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|', table_content)
            
            for finding_type, example_text, analysis in rows:
                finding_type = finding_type.strip()
                if finding_type.lower() == 'effective copy':
                    effective_copy.append({
                        'text': example_text.strip(),
                        'analysis': analysis.strip()
                    })
                elif finding_type.lower() == 'ineffective copy':
                    ineffective_copy.append({
                        'text': example_text.strip(),
                        'analysis': analysis.strip()
                    })
        
        # Extract the narrative sections (after the table)
        narrative_match = re.search(r'---\s*\n(.+)', content, re.DOTALL)
        narrative_content = narrative_match.group(1).strip() if narrative_match else ""
        
        # Split narrative into paragraphs for first impression and overall analysis
        paragraphs = [p.strip() for p in narrative_content.split('\n\n') if p.strip()]
        first_impression = paragraphs[0] if paragraphs else ""
        strategic_analysis = '\n\n'.join(paragraphs[1:]) if len(paragraphs) > 1 else ""
        
        return {
            'header_info': data['header_info'],
            'effective_copy': effective_copy,
            'ineffective_copy': ineffective_copy,
            'first_impression': first_impression,
            'strategic_analysis': strategic_analysis,
            'full_content': content
        }
    
    def load_csv_data(self, persona_dir: Path) -> Dict[str, pd.DataFrame]:
        """Load CSV files from persona directory."""
        csv_files = {}
        for csv_file in persona_dir.glob("*.csv"):
            try:
                df = pd.read_csv(csv_file)
                csv_files[csv_file.stem] = df
                logger.info(f"Loaded {csv_file.name} with {len(df)} rows")
            except Exception as e:
                logger.error(f"Error loading {csv_file}: {e}")
        return csv_files
    
    def extract_page_metadata(self, url: str, slug: str) -> Dict[str, Any]:
        """Extract metadata from URL and slug."""
        from urllib.parse import urlparse
        
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Determine content type from URL patterns
        content_type = "unknown"
        if "blog" in url.lower():
            content_type = "blog"
        elif "news" in url.lower() or "press-release" in url.lower():
            content_type = "news"
        elif "service" in url.lower() or "whatwedo" in url.lower():
            content_type = "service"
        elif "industries" in url.lower():
            content_type = "industry"
        elif "about" in url.lower():
            content_type = "corporate"
        elif "linkedin.com" in domain:
            content_type = "social_media"
        elif "youtube.com" in domain:
            content_type = "video"
        
        # Extract regulatory frameworks mentioned
        regulatory_frameworks = []
        url_lower = url.lower()
        slug_lower = slug.lower()
        
        framework_keywords = {
            "gdpr": ["gdpr", "privacy", "data-protection"],
            "nis2": ["nis2", "cybersecurity", "cyber-security"], 
            "dora": ["dora", "digital-resilience", "operational-resilience"],
            "mifid": ["mifid", "financial-services"],
            "basel": ["basel", "banking"]
        }
        
        for framework, keywords in framework_keywords.items():
            if any(keyword in url_lower or keyword in slug_lower for keyword in keywords):
                regulatory_frameworks.append(framework.upper())
        
        return {
            "domain": domain,
            "content_type": content_type,
            "regulatory_frameworks": regulatory_frameworks,
            "is_benelux": any(tld in domain for tld in [".nl", ".be"]) or "benelux" in url_lower
        }
    
    def create_combined_document(self, page_id: str, persona_name: str, 
                                hygiene_data: Dict, experience_data: Dict, 
                                csv_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Create combined JSON document for vector store."""
        
        # Get page info from CSV data
        page_info = {}
        if 'pages' in csv_data:
            page_row = csv_data['pages'][csv_data['pages']['page_id'] == page_id]
            if not page_row.empty:
                page_info = page_row.iloc[0].to_dict()
        
        # Get experience data from CSV
        experience_csv = {}
        if 'experience' in csv_data:
            exp_row = csv_data['experience'][csv_data['experience']['page_id'] == page_id]
            if not exp_row.empty:
                experience_csv = exp_row.iloc[0].to_dict()
        
        # Extract basic info
        url = hygiene_data.get('header_info', {}).get('url', page_info.get('url', ''))
        slug = page_info.get('slug', '')
        
        # Extract page metadata
        page_metadata = self.extract_page_metadata(url, slug)
        
        # Create embeddings content (combined narrative for semantic search)
        embeddings_content = []
        
        if hygiene_data.get('full_content'):
            embeddings_content.append(f"HYGIENE SCORECARD:\n{hygiene_data['full_content']}")
        
        if experience_data.get('full_content'):
            embeddings_content.append(f"EXPERIENCE REPORT:\n{experience_data['full_content']}")
        
        combined_analysis = "\n\n".join(embeddings_content)
        
        # Extract key themes
        key_themes = []
        content_lower = combined_analysis.lower()
        theme_keywords = {
            "trust": ["trust", "credibility", "reliability"],
            "security": ["security", "cybersecurity", "cyber", "protection"],
            "compliance": ["compliance", "regulation", "gdpr", "nis2", "dora"],
            "innovation": ["innovation", "ai", "artificial intelligence", "digital transformation"],
            "risk": ["risk", "threat", "vulnerability", "resilience"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                key_themes.append(theme)
        
        # Build the unified document
        document = {
            "page_id": page_id,
            "url": url,
            "slug": slug,
            "persona": {
                "name": persona_name,
                "description": hygiene_data.get('header_info', {}).get('persona_description', '')
            },
            "hygiene_scorecard": {
                "tier": hygiene_data.get('tier', ''),
                "final_score": hygiene_data.get('final_score', 0.0),
                "brand_health_index": page_info.get('brand_health_index', 0.0),
                "trust_gap": page_info.get('trust_gap', 0.0),
                "audited_ts": hygiene_data.get('header_info', {}).get('audited_ts', ''),
                "detailed_scores": hygiene_data.get('detailed_scores', {}),
                "recommendations": hygiene_data.get('recommendations', [])
            },
            "experience_report": {
                "overall_sentiment": experience_csv.get('overall_sentiment', 'Unknown'),
                "engagement_level": experience_csv.get('engagement_level', 'Unknown'),
                "conversion_likelihood": experience_csv.get('conversion_likelihood', 'Unknown'),
                "effective_copy": experience_data.get('effective_copy', []),
                "ineffective_copy": experience_data.get('ineffective_copy', []),
                "first_impression": experience_data.get('first_impression', ''),
                "strategic_analysis": experience_data.get('strategic_analysis', '')
            },
            "embeddings_content": {
                "combined_analysis": combined_analysis,
                "key_themes": key_themes,
                "business_impact": experience_data.get('strategic_analysis', '')[:500] + "..." if len(experience_data.get('strategic_analysis', '')) > 500 else experience_data.get('strategic_analysis', '')
            },
            "metadata": {
                "persona_id": persona_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_'),
                "page_id": page_id,
                "tier": hygiene_data.get('tier', '').lower().replace(' ', '_'),
                "final_score": hygiene_data.get('final_score', 0.0),
                "domain": page_metadata["domain"],
                "content_type": page_metadata["content_type"],
                "regulatory_frameworks": page_metadata["regulatory_frameworks"],
                "is_benelux": page_metadata["is_benelux"],
                "has_compliance_content": "compliance" in key_themes,
                "has_security_content": "security" in key_themes,
                "compiled_at": datetime.now().isoformat()
            }
        }
        
        return document
    
    def process_persona_directory(self, persona_dir: Path) -> List[Dict[str, Any]]:
        """Process all files in a persona directory."""
        persona_name = persona_dir.name
        logger.info(f"Processing persona: {persona_name}")
        
        # Load CSV data first
        csv_data = self.load_csv_data(persona_dir)
        
        # Get all markdown files
        hygiene_files = list(persona_dir.glob("*_hygiene_scorecard.md"))
        experience_files = list(persona_dir.glob("*_experience_report.md"))
        
        # Create mapping of slugs to files
        hygiene_map = {}
        experience_map = {}
        
        for file in hygiene_files:
            slug = file.stem.replace('_hygiene_scorecard', '')
            hygiene_map[slug] = file
        
        for file in experience_files:
            slug = file.stem.replace('_experience_report', '')
            experience_map[slug] = file
        
        # Find common slugs (pages that have both reports)
        common_slugs = set(hygiene_map.keys()) & set(experience_map.keys())
        
        documents = []
        
        for slug in common_slugs:
            try:
                # Parse both files
                hygiene_data = self.parse_hygiene_scorecard(hygiene_map[slug])
                experience_data = self.parse_experience_report(experience_map[slug])
                
                # Get page_id from CSV if available
                page_id = None
                if 'pages' in csv_data:
                    page_row = csv_data['pages'][csv_data['pages']['slug'] == slug]
                    if not page_row.empty:
                        page_id = page_row.iloc[0]['page_id']
                
                if not page_id:
                    # Generate a page_id if not found
                    import hashlib
                    page_id = hashlib.md5(slug.encode()).hexdigest()[:8]
                
                # Create combined document
                document = self.create_combined_document(
                    page_id, persona_name, hygiene_data, experience_data, csv_data
                )
                
                documents.append(document)
                logger.info(f"Created document for {slug} (page_id: {page_id})")
                
            except Exception as e:
                logger.error(f"Error processing {slug} for {persona_name}: {e}")
                continue
        
        logger.info(f"Completed {persona_name}: {len(documents)} documents created")
        return documents
    
    def compile_all_personas(self) -> List[Dict[str, Any]]:
        """Compile data from all persona directories."""
        all_documents = []
        
        if not self.audit_outputs_dir.exists():
            logger.error(f"Audit outputs directory not found: {self.audit_outputs_dir}")
            return []
        
        # Get all persona directories
        persona_dirs = [d for d in self.audit_outputs_dir.iterdir() if d.is_dir()]
        
        for persona_dir in persona_dirs:
            documents = self.process_persona_directory(persona_dir)
            all_documents.extend(documents)
        
        logger.info(f"Total documents compiled: {len(all_documents)}")
        return all_documents
    
    def save_compiled_data(self, documents: List[Dict[str, Any]]) -> None:
        """Save compiled documents to JSON files."""
        
        # Save all documents as one large JSON file
        output_file = self.vector_dir / "compiled_persona_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(documents)} documents to {output_file}")
        
        # Save individual files by persona for easier debugging
        persona_docs = {}
        for doc in documents:
            persona_name = doc['persona']['name']
            if persona_name not in persona_docs:
                persona_docs[persona_name] = []
            persona_docs[persona_name].append(doc)
        
        for persona_name, docs in persona_docs.items():
            safe_name = persona_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
            output_file = self.vector_dir / f"persona_{safe_name}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(docs)} documents for {persona_name} to {output_file}")
        
        # Create summary statistics
        summary = {
            "total_documents": len(documents),
            "personas": list(persona_docs.keys()),
            "documents_per_persona": {name: len(docs) for name, docs in persona_docs.items()},
            "unique_pages": len(set(doc['page_id'] for doc in documents)),
            "unique_domains": len(set(doc['metadata']['domain'] for doc in documents)),
            "content_types": list(set(doc['metadata']['content_type'] for doc in documents)),
            "compilation_timestamp": datetime.now().isoformat()
        }
        
        summary_file = self.vector_dir / "compilation_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved compilation summary to {summary_file}")

def main():
    """Main execution function."""
    compiler = PersonaDataCompiler()
    
    logger.info("Starting persona data compilation...")
    documents = compiler.compile_all_personas()
    
    if documents:
        compiler.save_compiled_data(documents)
        logger.info("Compilation completed successfully!")
    else:
        logger.error("No documents were compiled. Check your audit outputs directory.")

if __name__ == "__main__":
    main()