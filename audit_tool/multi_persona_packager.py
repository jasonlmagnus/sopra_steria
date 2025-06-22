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
import logging

logger = logging.getLogger(__name__)

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
            if persona_dir.is_dir() and not persona_dir.name.startswith('.'):
                # Include all directories that contain audit data
                if any(persona_dir.glob("*_hygiene_scorecard.md")) or any(persona_dir.glob("*.csv")):
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
    
    def process_csv_data(self, persona_dir: Path, persona: str) -> List[Dict]:
        """Process CSV-based audit data with comprehensive data integration"""
        data_rows = []
        
        # Load all CSV files
        criteria_file = persona_dir / "criteria_scores.csv"
        pages_file = persona_dir / "pages.csv"
        experience_file = persona_dir / "experience.csv"
        recommendations_file = persona_dir / "recommendations.csv"
        
        if not criteria_file.exists():
            return data_rows
            
        try:
            # Load core datasets
            criteria_df = pd.read_csv(criteria_file)
            pages_df = pd.read_csv(pages_file) if pages_file.exists() else pd.DataFrame()
            experience_df = pd.read_csv(experience_file) if experience_file.exists() else pd.DataFrame()
            recommendations_df = pd.read_csv(recommendations_file) if recommendations_file.exists() else pd.DataFrame()
            
            logger.info(f"Processing {persona}: criteria={len(criteria_df)}, pages={len(pages_df)}, experience={len(experience_df)}, recommendations={len(recommendations_df)}")
            
            # Create comprehensive merged dataset
            for _, criteria_row in criteria_df.iterrows():
                page_id = criteria_row.get('page_id', '')
                
                # Get page metadata
                page_data = {}
                if not pages_df.empty:
                    page_match = pages_df[pages_df['page_id'] == page_id]
                    if not page_match.empty:
                        page_data = page_match.iloc[0].to_dict()
                
                # Get experience data for this page
                experience_data = {}
                if not experience_df.empty:
                    exp_match = experience_df[experience_df['page_id'] == page_id]
                    if not exp_match.empty:
                        experience_data = exp_match.iloc[0].to_dict()
                
                # Create comprehensive row with all required columns
                row = {
                    # Core audit data
                    'persona_id': persona,
                    'page_id': page_id,
                    'url_slug': page_data.get('slug', page_id),
                    'url': page_data.get('url', criteria_row.get('url', '')),
                    'tier': page_data.get('tier', criteria_row.get('tier', 'Unknown')),
                    'criterion_id': criteria_row.get('criterion_code', ''),  # Use criterion_code as the ID
                    'criterion_code': criteria_row.get('criterion_code', ''),  # Dashboard expects this
                    'raw_score': criteria_row.get('score', 0),
                    'final_score': criteria_row.get('score', 0),  # Dashboard expects this
                    'descriptor': criteria_row.get('descriptor', ''),
                    'rationale': criteria_row.get('rationale', ''),
                    
                    # Experience data (merged from experience.csv)
                    'first_impression': experience_data.get('first_impression', ''),
                    'language_tone_feedback': experience_data.get('language_tone_feedback', ''),
                    'information_gaps': experience_data.get('information_gaps', ''),
                    'trust_credibility_assessment': experience_data.get('trust_credibility_assessment', ''),
                    'business_impact_analysis': experience_data.get('business_impact_analysis', ''),
                    'effective_copy_examples': experience_data.get('effective_copy_examples', ''),
                    'ineffective_copy_examples': experience_data.get('ineffective_copy_examples', ''),
                    'overall_sentiment': experience_data.get('overall_sentiment', 'Neutral'),
                    'engagement_level': experience_data.get('engagement_level', 'Medium'),
                    'conversion_likelihood': experience_data.get('conversion_likelihood', 'Medium'),
                    
                    # Pages metadata
                    'slug': page_data.get('slug', page_id),
                    'audited_ts': page_data.get('audited_ts', ''),
                    
                    # Computed flags and scores
                    'quick_win_flag': 6 <= criteria_row.get('score', 0) <= 8,
                    'critical_issue_flag': criteria_row.get('score', 0) < 4,
                    'success_flag': criteria_row.get('score', 0) >= 8,
                }
                
                # Add numeric mappings for text fields
                row.update(self._create_numeric_mappings(row))
                
                data_rows.append(row)
            
            # Add page-level avg_score computation
            if data_rows:
                df = pd.DataFrame(data_rows)
                page_scores = df.groupby(['persona_id', 'page_id'])['raw_score'].mean().reset_index()
                page_scores.rename(columns={'raw_score': 'avg_score'}, inplace=True)
                
                # Merge avg_score back
                df = df.merge(page_scores, on=['persona_id', 'page_id'], how='left')
                data_rows = df.to_dict('records')
            
            logger.info(f"Created {len(data_rows)} comprehensive unified rows for {persona}")
            return data_rows
            
        except Exception as e:
            logger.error(f"Error processing CSV data for {persona}: {str(e)}")
            return []

    def process_experience_data(self, persona_dir: Path, persona: str) -> List[Dict]:
        """Process experience data from CSV files"""
        experience_rows = []
        
        experience_file = persona_dir / "experience.csv"
        
        if experience_file.exists():
            try:
                experience_df = pd.read_csv(experience_file)
                
                for _, row in experience_df.iterrows():
                    experience_rows.append({
                        'persona_id': persona,
                        'page_id': row.get('page_id', 'unknown'),
                        'first_impression': row.get('first_impression', ''),
                        'language_tone_feedback': row.get('language_tone_feedback', ''),
                        'information_gaps': row.get('information_gaps', ''),
                        'trust_credibility_assessment': row.get('trust_credibility_assessment', ''),
                        'business_impact_analysis': row.get('business_impact_analysis', ''),
                        'effective_copy_examples': row.get('effective_copy_examples', ''),
                        'ineffective_copy_examples': row.get('ineffective_copy_examples', ''),
                        'overall_sentiment': row.get('overall_sentiment', ''),
                        'engagement_level': row.get('engagement_level', ''),
                        'conversion_likelihood': row.get('conversion_likelihood', '')
                    })
                    
                print(f"  ✅ Loaded {len(experience_rows)} experience records from CSV")
                
            except Exception as e:
                print(f"  ❌ Error processing experience data: {e}")
                
        return experience_rows

    def create_unified_dataset(self) -> pd.DataFrame:
        """Create unified dataset combining all persona analyses"""
        all_data = []
        
        personas = self.get_available_personas()
        print(f"📊 Found personas: {personas}")
        
        for persona in personas:
            persona_dir = self.audit_outputs_dir / persona
            print(f"Processing {persona}...")
            
            # First try CSV format (newer, preferred)
            csv_data = self.process_csv_data(persona_dir, persona)
            if csv_data:
                all_data.extend(csv_data)
                continue
            
            # Fallback to markdown parsing (older format)
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

    def create_unified_experience_dataset(self) -> pd.DataFrame:
        """Create unified experience dataset combining all persona experience data"""
        all_experience_data = []
        
        personas = self.get_available_personas()
        print(f"📊 Processing experience data for personas: {personas}")
        
        for persona in personas:
            persona_dir = self.audit_outputs_dir / persona
            print(f"Processing experience data for {persona}...")
            
            # Process experience data
            experience_data = self.process_experience_data(persona_dir, persona)
            if experience_data:
                all_experience_data.extend(experience_data)
        
        return pd.DataFrame(all_experience_data)
    
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
    
    def _create_numeric_mappings(self, row: Dict) -> Dict:
        """Create numeric mappings for text fields"""
        mappings = {}
        
        # Sentiment mapping
        sentiment_map = {
            'Positive': 8, 'Very Positive': 9, 'Extremely Positive': 10,
            'Neutral': 5, 'Mixed': 5,
            'Negative': 2, 'Very Negative': 1, 'Extremely Negative': 0
        }
        mappings['sentiment_numeric'] = sentiment_map.get(row.get('overall_sentiment', 'Neutral'), 5)
        
        # Engagement mapping
        engagement_map = {
            'High': 8, 'Very High': 9, 'Extremely High': 10,
            'Medium': 5, 'Moderate': 5,
            'Low': 2, 'Very Low': 1, 'Extremely Low': 0
        }
        mappings['engagement_numeric'] = engagement_map.get(row.get('engagement_level', 'Medium'), 5)
        
        # Conversion likelihood mapping
        conversion_map = {
            'High': 8, 'Very High': 9, 'Extremely High': 10,
            'Medium': 5, 'Moderate': 5,
            'Low': 2, 'Very Low': 1, 'Extremely Low': 0
        }
        mappings['conversion_numeric'] = conversion_map.get(row.get('conversion_likelihood', 'Medium'), 5)
        
        return mappings

    # enhance_unified_dataset method removed - original data already contains all required columns
    
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
        
        # Create unified experience dataset
        print("\n🔄 Creating unified experience dataset...")
        experience_df = self.create_unified_experience_dataset()
        
        if not experience_df.empty:
            experience_df.to_parquet(self.output_dir / "unified_experience_data.parquet")
            experience_df.to_csv(self.output_dir / "unified_experience_data.csv", index=False)
            print(f"✅ Saved {len(experience_df)} experience records")
        else:
            print("⚠️ No experience data found")
        
        # Create summary statistics
        summary = self.create_summary_stats(unified_df)
        
        # Add experience data stats to summary
        if not experience_df.empty:
            summary['experience_stats'] = {
                'total_experience_records': len(experience_df),
                'personas_with_experience': len(experience_df['persona_id'].unique()),
                'pages_with_experience': len(experience_df['page_id'].unique())
            }
        
        with open(self.output_dir / "summary_stats.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary:")
        print(f"  • {summary['total_personas']} personas")
        print(f"  • {summary['total_pages']} pages")
        print(f"  • {summary['total_criteria']} criteria")
        print(f"  • {summary['total_evaluations']} total evaluations")
        print(f"  • {summary['average_score']:.2f} average score")
        
        if 'experience_stats' in summary:
            print(f"  • {summary['experience_stats']['total_experience_records']} experience records")
            print(f"  • {summary['experience_stats']['personas_with_experience']} personas with experience data")
        
        # Create persona comparison data
        persona_comparison = unified_df.pivot_table(
            values='raw_score',
            index=['url_slug', 'criterion_id'],
            columns='persona_id',
            aggfunc='mean'
        ).reset_index()
        
        persona_comparison.to_parquet(self.output_dir / "persona_comparison.parquet")
        print(f"✅ Created persona comparison matrix")
        
        # Note: Enhanced dataset removed - original data already contains all required columns
        
        return self.output_dir

def main():
    """Package all persona data into unified dataset"""
    packager = MultiPersonaPackager()
    packager.package_all_data()

if __name__ == "__main__":
    main() 