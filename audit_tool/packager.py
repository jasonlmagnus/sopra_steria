#!/usr/bin/env python3
"""
Data Packager for Brand Audit Tool
Converts markdown audit outputs into structured Parquet/JSON format
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class AuditDataPackager:
    def __init__(self, persona_name: str):
        self.persona_name = persona_name
        # Use absolute paths from project root
        current_dir = Path(__file__).parent
        project_root = current_dir.parent
        self.input_dir = project_root / f"audit_outputs/{persona_name}"
        self.output_dir = project_root / f"audit_runs/{persona_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"
        
    def parse_scorecard_markdown(self, file_path: Path) -> Dict:
        """Parse scorecard markdown into structured data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract scores using regex patterns for table format
        scores = {}
        
        # Look for table pattern: | **Criterion Name** | X.X/10 | Rationale |
        table_pattern = r'\|\s*\*\*(.*?)\*\*\s*\|\s*(\d+(?:\.\d+)?)/10\s*\|\s*(.*?)\s*\|'
        matches = re.findall(table_pattern, content)
        
        for criterion, score, rationale in matches:
            clean_criterion = criterion.lower().replace(' ', '_').replace('-', '_')
            scores[clean_criterion] = float(score)
            
        # Also look for overall score
        overall_pattern = r'\*\*Final Score:\*\*\s*(\d+(?:\.\d+)?)/10'
        overall_match = re.search(overall_pattern, content)
        if overall_match:
            scores['overall'] = float(overall_match.group(1))
            
        # Extract justifications and recommendations (if present)
        justification_pattern = r'Justification:(.*?)(?=Recommendation:|$)'
        recommendation_pattern = r'Recommendation:(.*?)(?=\*\*|$)'
        
        justifications = re.findall(justification_pattern, content, re.DOTALL)
        recommendations = re.findall(recommendation_pattern, content, re.DOTALL)
        
        return {
            'scores': scores,
            'justifications': [j.strip() for j in justifications],
            'recommendations': [r.strip() for r in recommendations],
            'raw_content': content
        }
    
    def parse_experience_report(self, file_path: Path) -> Dict:
        """Parse experience report markdown"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract key insights
        insights = []
        insight_pattern = r'##\s*(.*?)(?=##|$)'
        matches = re.findall(insight_pattern, content, re.DOTALL)
        
        for match in matches:
            if len(match.strip()) > 50:  # Filter out short matches
                insights.append(match.strip())
        
        return {
            'insights': insights,
            'raw_content': content
        }
    
    def reconstruct_url(self, url_slug: str) -> str:
        """Convert URL slug back to actual URL"""
        # Simple reconstruction - could be enhanced with mapping table
        if url_slug.startswith('www_'):
            return f"https://{url_slug.replace('_', '.')}"
        else:
            return f"https://www.soprasteria.be/{url_slug.replace('_', '/')}"
    
    def get_tier_from_criterion(self, criterion: str) -> str:
        """Map criterion to tier - simplified mapping"""
        tier_mapping = {
            'headline': 'messaging',
            'content': 'content',
            'pain_points': 'relevance',
            'value_prop': 'value',
            'trust': 'credibility',
            'cta': 'conversion'
        }
        
        for key, tier in tier_mapping.items():
            if key in criterion:
                return tier
        
        return 'other'
    
    def score_to_descriptor(self, score: float) -> str:
        """Convert numeric score to descriptor"""
        if score >= 4.0:
            return "PASS"
        elif score >= 2.0:
            return "WARN"
        else:
            return "FAIL"
    
    def create_page_facts_table(self) -> pd.DataFrame:
        """Create the main page_facts Parquet table"""
        facts = []
        
        # Process all scorecard files
        for scorecard_file in self.input_dir.glob("*_hygiene_scorecard.md"):
            url_slug = scorecard_file.name.replace("_hygiene_scorecard.md", "")
            
            # Parse scorecard data
            try:
                scorecard_data = self.parse_scorecard_markdown(scorecard_file)
                
                # Create page_id hash
                page_id = hashlib.md5(url_slug.encode()).hexdigest()[:8]
                
                # Create rows for each criterion
                for criterion, score in scorecard_data['scores'].items():
                    facts.append({
                        'run_id': self.output_dir.name,
                        'persona_id': self.persona_name,
                        'page_id': page_id,
                        'url_slug': url_slug,
                        'url': self.reconstruct_url(url_slug),
                        'tier': self.get_tier_from_criterion(criterion),
                        'criterion_id': criterion,
                        'raw_score': score,
                        'weighted_score': score,  # Apply weighting from methodology later
                        'descriptor': self.score_to_descriptor(score)
                    })
                    
            except Exception as e:
                print(f"Error processing {scorecard_file}: {e}")
                continue
        
        return pd.DataFrame(facts)
    
    def create_evidence_table(self) -> pd.DataFrame:
        """Create evidence table with justifications and recommendations"""
        evidence = []
        
        for scorecard_file in self.input_dir.glob("*_hygiene_scorecard.md"):
            url_slug = scorecard_file.name.replace("_hygiene_scorecard.md", "")
            page_id = hashlib.md5(url_slug.encode()).hexdigest()[:8]
            
            try:
                scorecard_data = self.parse_scorecard_markdown(scorecard_file)
                
                # Add justifications
                for i, justification in enumerate(scorecard_data['justifications']):
                    evidence.append({
                        'run_id': self.output_dir.name,
                        'persona_id': self.persona_name,
                        'page_id': page_id,
                        'evidence_type': 'justification',
                        'evidence_text': justification,
                        'sequence': i
                    })
                
                # Add recommendations
                for i, recommendation in enumerate(scorecard_data['recommendations']):
                    evidence.append({
                        'run_id': self.output_dir.name,
                        'persona_id': self.persona_name,
                        'page_id': page_id,
                        'evidence_type': 'recommendation',
                        'evidence_text': recommendation,
                        'sequence': i
                    })
                    
            except Exception as e:
                print(f"Error processing evidence from {scorecard_file}: {e}")
                continue
        
        return pd.DataFrame(evidence)
    
    def package_run(self):
        """Main packaging function"""
        print(f"📦 Packaging audit data for {self.persona_name}...")
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create page_facts table
        print("Creating page_facts table...")
        page_facts = self.create_page_facts_table()
        
        if page_facts.empty:
            print("❌ No data found to package")
            return
        
        page_facts.to_parquet(self.output_dir / "page_facts.parquet")
        print(f"✅ Saved {len(page_facts)} page facts")
        
        # Create evidence table
        print("Creating evidence table...")
        evidence = self.create_evidence_table()
        evidence.to_parquet(self.output_dir / "evidence.parquet")
        print(f"✅ Saved {len(evidence)} evidence records")
        
        # Create run manifest
        print("Creating run manifest...")
        manifest = {
            'run_id': self.output_dir.name,
            'timestamp': datetime.now().isoformat(),
            'persona_id': self.persona_name,
            'total_pages': len(page_facts['page_id'].unique()),
            'total_criteria': len(page_facts),
            'average_score': float(page_facts['raw_score'].mean()),
            'aggregates': {
                'by_tier': page_facts.groupby('tier')['raw_score'].mean().to_dict(),
                'by_descriptor': page_facts['descriptor'].value_counts().to_dict(),
                'by_criterion': page_facts.groupby('criterion_id')['raw_score'].mean().to_dict()
            },
            'score_distribution': {
                'min': float(page_facts['raw_score'].min()),
                'max': float(page_facts['raw_score'].max()),
                'std': float(page_facts['raw_score'].std())
            }
        }
        
        with open(self.output_dir / "run_manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Packaged run data to {self.output_dir}")
        print(f"📊 Summary: {manifest['total_pages']} pages, {manifest['total_criteria']} criteria, avg score: {manifest['average_score']:.2f}")
        
        return self.output_dir.name

def main():
    """Package existing audit outputs"""
    import sys
    
    if len(sys.argv) > 1:
        persona_name = sys.argv[1]
    else:
        # Default to P1 if no argument provided
        persona_name = "P1"
    
    packager = AuditDataPackager(persona_name)
    packager.package_run()

if __name__ == "__main__":
    main() 