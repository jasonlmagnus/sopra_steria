#!/usr/bin/env python3
"""
Multi-Persona Data Packager for Brand Audit Tool
Combines all persona analyses into a single comparable dataset
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib

class MultiPersonaPackager:
    def __init__(self):
        # Use absolute paths from project root
        current_dir = Path(__file__).parent
        self.project_root = current_dir.parent
        self.audit_outputs_dir = self.project_root / "audit_outputs"
        self.output_dir = self.project_root / "audit_data"
        
    def get_available_personas(self) -> List[str]:
        """Get list of available persona analyses"""
        personas = []
        for persona_dir in self.audit_outputs_dir.iterdir():
            if persona_dir.is_dir() and persona_dir.name.startswith('P'):
                personas.append(persona_dir.name)
        return sorted(personas)
    
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
            scores[clean_criterion] = {
                'score': float(score),
                'rationale': rationale.strip()
            }
            
        # Also look for overall score
        overall_pattern = r'\*\*Final Score:\*\*\s*(\d+(?:\.\d+)?)/10'
        overall_match = re.search(overall_pattern, content)
        if overall_match:
            scores['overall'] = {
                'score': float(overall_match.group(1)),
                'rationale': 'Overall assessment'
            }
            
        return scores
    
    def get_tier_from_criterion(self, criterion: str) -> str:
        """Map criterion to tier - simplified mapping"""
        tier_mapping = {
            'corporate_positioning_alignment': 'brand_positioning',
            'brand_differentiation': 'brand_positioning',
            'emotional_resonance': 'brand_positioning',
            'visual_brand_integrity': 'brand_positioning',
            'strategic_clarity': 'brand_positioning',
            'trust_credibility_signals': 'credibility',
            'overall': 'summary'
        }
        
        return tier_mapping.get(criterion, 'other')
    
    def score_to_descriptor(self, score: float) -> str:
        """Convert numeric score to descriptor"""
        if score >= 7.0:
            return "EXCELLENT"
        elif score >= 4.0:
            return "PASS"
        elif score >= 2.0:
            return "WARN"
        else:
            return "FAIL"
    
    def create_unified_dataset(self) -> pd.DataFrame:
        """Create unified dataset combining all persona analyses"""
        all_data = []
        
        personas = self.get_available_personas()
        print(f"📊 Found personas: {personas}")
        
        for persona in personas:
            persona_dir = self.audit_outputs_dir / persona
            print(f"Processing {persona}...")
            
            # Process all scorecard files for this persona
            for scorecard_file in persona_dir.glob("*_hygiene_scorecard.md"):
                url_slug = scorecard_file.name.replace("_hygiene_scorecard.md", "")
                
                try:
                    scorecard_data = self.parse_scorecard_markdown(scorecard_file)
                    
                    # Create page_id hash
                    page_id = hashlib.md5(url_slug.encode()).hexdigest()[:8]
                    
                    # Create rows for each criterion
                    for criterion, data in scorecard_data.items():
                        all_data.append({
                            'persona_id': persona,
                            'page_id': page_id,
                            'url_slug': url_slug,
                            'url': self.reconstruct_url(url_slug),
                            'tier': self.get_tier_from_criterion(criterion),
                            'criterion_id': criterion,
                            'raw_score': data['score'],
                            'descriptor': self.score_to_descriptor(data['score']),
                            'rationale': data['rationale']
                        })
                        
                except Exception as e:
                    print(f"Error processing {scorecard_file}: {e}")
                    continue
        
        return pd.DataFrame(all_data)
    
    def reconstruct_url(self, url_slug: str) -> str:
        """Convert URL slug back to actual URL"""
        if url_slug.startswith('www_'):
            return f"https://{url_slug.replace('_', '.')}"
        elif url_slug.startswith('@'):
            # Social media links
            return f"https://linkedin.com/company/{url_slug[1:].replace('_', '-')}"
        else:
            return f"https://www.soprasteria.be/{url_slug.replace('_', '/')}"
    
    def create_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Create summary statistics"""
        return {
            'total_personas': len(df['persona_id'].unique()),
            'total_pages': len(df['page_id'].unique()),
            'total_criteria': len(df['criterion_id'].unique()),
            'total_evaluations': len(df),
            'average_score': float(df['raw_score'].mean()),
            'score_by_persona': df.groupby('persona_id')['raw_score'].mean().to_dict(),
            'score_by_tier': df.groupby('tier')['raw_score'].mean().to_dict(),
            'score_by_criterion': df.groupby('criterion_id')['raw_score'].mean().to_dict(),
            'descriptor_distribution': df['descriptor'].value_counts().to_dict(),
            'generated_at': datetime.now().isoformat()
        }
    
    def package_all_data(self):
        """Main packaging function - combine all persona data"""
        print("🔄 Creating unified multi-persona dataset...")
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Create unified dataset
        unified_df = self.create_unified_dataset()
        
        if unified_df.empty:
            print("❌ No data found to package")
            return
        
        # Save main dataset
        unified_df.to_parquet(self.output_dir / "unified_audit_data.parquet")
        unified_df.to_csv(self.output_dir / "unified_audit_data.csv", index=False)
        print(f"✅ Saved {len(unified_df)} evaluation records")
        
        # Create summary statistics
        summary = self.create_summary_stats(unified_df)
        
        with open(self.output_dir / "summary_stats.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary:")
        print(f"  • {summary['total_personas']} personas")
        print(f"  • {summary['total_pages']} pages")
        print(f"  • {summary['total_criteria']} criteria")
        print(f"  • {summary['total_evaluations']} total evaluations")
        print(f"  • {summary['average_score']:.2f} average score")
        
        # Create persona comparison data
        persona_comparison = unified_df.pivot_table(
            values='raw_score',
            index=['url_slug', 'criterion_id'],
            columns='persona_id',
            aggfunc='mean'
        ).reset_index()
        
        persona_comparison.to_parquet(self.output_dir / "persona_comparison.parquet")
        print(f"✅ Created persona comparison matrix")
        
        return self.output_dir

def main():
    """Package all persona data into unified dataset"""
    packager = MultiPersonaPackager()
    packager.package_all_data()

if __name__ == "__main__":
    main() 