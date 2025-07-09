#!/usr/bin/env python3
"""
Enhanced Backfill Packager for Brand Audit Tool
Converts existing markdown audit outputs into rich, structured CSV format
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedBackfillPackager:
    """Enhanced backfill processor for audit data with proper schema validation"""
    def __init__(self, persona_name: str):
        self.persona_name = persona_name
        self.input_dir = Path(f"audit_outputs/{persona_name}")
        self.output_dir = Path(f"audit_outputs/{persona_name}")
        
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory {self.input_dir} does not exist")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Weight mappings from audit_method.md
        self.tier_weights = {
            "Tier 1": {"brand": 80, "performance": 20},
            "Tier 2": {"brand": 50, "performance": 50}, 
            "Tier 3": {"brand": 30, "performance": 70}
        }
        
        # Criterion weights by tier (from methodology)
        self.criterion_weights = {
            # Tier 1 - Brand Positioning (80% Brand | 20% Performance)
            "corporate_positioning_alignment": 25,  # Brand
            "brand_differentiation": 20,            # Brand  
            "emotional_resonance": 20,              # Brand
            "visual_brand_integrity": 15,           # Brand
            "strategic_clarity": 10,                # Performance
            "trust_credibility_signals": 10,        # Performance
            
            # Tier 2 - Value Proposition (50% Brand | 50% Performance)  
            "regional_narrative_integration": 15,   # Brand
            "brand_message_consistency": 15,        # Brand
            "visual_brand_consistency": 10,         # Brand
            "brand_promise_delivery": 10,           # Brand
            "strategic_value_clarity": 25,          # Performance
            "solution_sophistication": 15,          # Performance
            "proof_points_validation": 10,          # Performance
            
            # Tier 3 - Functional Content (30% Brand | 70% Performance)
            "brand_voice_alignment": 10,            # Brand
            "sub_narrative_integration": 10,        # Brand
            "visual_brand_elements": 10,            # Brand
            "executive_relevance": 25,              # Performance
            "strategic_insight_quality": 20,        # Performance
            "business_value_focus": 15,             # Performance
            "credibility_elements": 10,             # Performance
            
            # Generic criteria (fallback)
            "value_proposition_clarity": 20,
            "call_to_action_effectiveness": 15
        }
    
    def parse_scorecard_markdown(self, file_path: Path) -> Dict:
        """Enhanced parsing of scorecard markdown into structured data"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract page metadata
        url_match = re.search(r'\*\*URL:\*\*\s*(https?://[^\s]+)', content)
        persona_match = re.search(r'\*\*Persona:\*\*\s*([^\n]+)', content)
        audited_match = re.search(r'\*\*Audited:\*\*\s*([^\n]+)', content)
        tier_match = re.search(r'\*\*Tier/Channel:\*\*\s*([^\n]+)', content)
        final_score_match = re.search(r'\*\*Final Score:\*\*\s*(\d+(?:\.\d+)?)/10', content)
        
        metadata = {
            'url': url_match.group(1) if url_match else '',
            'persona': persona_match.group(1) if persona_match else self.persona_name,
            'audited': audited_match.group(1) if audited_match else '',
            'tier': tier_match.group(1) if tier_match else '',
            'final_score': float(final_score_match.group(1)) if final_score_match else 0.0
        }
        
        # Extract criteria scores from table
        # Pattern: | Category | Score | Rationale |
        table_pattern = r'\|\s*([^|]+?)\s*\|\s*(\d+(?:\.\d+)?)\s*\|\s*([^|]+?)\s*\|'
        matches = re.findall(table_pattern, content)
        
        criteria_scores = []
        for criterion_name, score, rationale in matches:
            # Skip header row
            if 'Category' in criterion_name or 'Score' in criterion_name:
                continue
                
            criterion_code = self.normalize_criterion_name(criterion_name.strip())
            criteria_scores.append({
                'criterion_name': criterion_name.strip(),
                'criterion_code': criterion_code,
                'score': float(score),
                'evidence': rationale.strip(),
                'weight_pct': self.criterion_weights.get(criterion_code, 10),  # Default 10%
                'descriptor': self.score_to_descriptor(float(score))
            })
        
        # Extract recommendations
        recommendations = []
        rec_section = re.search(r'## Priority Recommendations(.*?)(?=##|$)', content, re.DOTALL)
        if rec_section:
            rec_text = rec_section.group(1)
            # Find numbered or bulleted recommendations
            rec_pattern = r'(?:^\d+\.|^[-*])\s*\*\*([^*]+)\*\*\s*-\s*([^\n]+)'
            rec_matches = re.findall(rec_pattern, rec_text, re.MULTILINE)
            
            for rec_title, rec_desc in rec_matches:
                recommendations.append({
                    'recommendation': f"{rec_title.strip()}: {rec_desc.strip()}",
                    'strategic_impact': self.categorize_recommendation(rec_title),
                    'complexity': 'Medium',  # Default
                    'urgency': 'Medium',     # Default  
                    'resources': 'TBD'       # Default
                })
        
        return {
            'metadata': metadata,
            'criteria_scores': criteria_scores,
            'recommendations': recommendations,
            'raw_content': content
        }
    
    def normalize_criterion_name(self, name: str) -> str:
        """Convert criterion name to snake_case code"""
        # Remove special characters and convert to lowercase
        normalized = re.sub(r'[^\w\s]', '', name.lower())
        # Replace spaces with underscores
        normalized = re.sub(r'\s+', '_', normalized)
        # Remove duplicate underscores
        normalized = re.sub(r'_+', '_', normalized)
        return normalized.strip('_')
    
    def score_to_descriptor(self, score: float) -> str:
        """Convert numeric score to descriptor based on methodology"""
        if score >= 8.0:
            return "PASS"
        elif score >= 6.0:
            return "WARN"
        elif score >= 4.0:
            return "CONCERN"
        else:
            return "FAIL"
    
    def categorize_recommendation(self, rec_title: str) -> str:
        """Auto-categorize recommendation based on keywords"""
        title_lower = rec_title.lower()
        
        if any(word in title_lower for word in ['differentiation', 'unique', 'positioning']):
            return 'Brand Differentiation'
        elif any(word in title_lower for word in ['cta', 'call-to-action', 'conversion']):
            return 'Conversion Optimization'
        elif any(word in title_lower for word in ['value', 'roi', 'benefit']):
            return 'Value Proposition'
        elif any(word in title_lower for word in ['trust', 'credibility', 'proof']):
            return 'Trust & Credibility'
        else:
            return 'General'
    
    def create_page_id(self, url_slug: str) -> str:
        """Create consistent page_id from URL slug"""
        return hashlib.md5(url_slug.encode()).hexdigest()[:8]
    
    def calculate_brand_health_index(self, hygiene_score: float, positive_sentiment_pct: float, engagement_rate: float) -> float:
        """Calculate composite brand health index"""
        return round(
            hygiene_score * 0.60 +           # Technical quality
            positive_sentiment_pct * 0.25 +  # Emotional resonance  
            engagement_rate * 0.15,          # User behavior
            2
        )
    
    def calculate_impact_score(self, criterion_score: float, weight_pct: float, tier: str) -> float:
        """Calculate impact score for prioritization"""
        # Higher impact for lower scores (problems need fixing)
        severity = 10 - criterion_score  # Invert score (0=perfect, 10=terrible)
        frequency = weight_pct / 100     # Normalize weight
        
        # Business value based on tier
        business_value = {
            'Corporate Website - Home Page': 1.0,
            'Corporate Website - Top Level': 0.9,
            'Thought Leadership Content Page': 0.8,
            'Thought Leadership Blog Post': 0.7,
            'Service Offering Page': 0.8,
            'Industry Solutions Page': 0.7,
            'Services/Solutions Page': 0.7,
            'Press Release': 0.5,
            'About Us - History Page': 0.4,
            'Corporate Responsibility Overview Page': 0.4
        }.get(tier, 0.5)
        
        return round(severity * frequency * business_value * 10, 2)
    
    def calculate_trust_gap(self, criteria_scores: List[Dict]) -> float:
        """Calculate trust gap based on trust-related criteria"""
        trust_criteria = ['trust_credibility_signals', 'credibility_elements', 'proof_points_validation']
        trust_scores = [c['score'] for c in criteria_scores if c['criterion_code'] in trust_criteria]
        
        if not trust_scores:
            return 0.0
        
        # Gap = (10 - average_trust_score) / 10
        avg_trust_score = sum(trust_scores) / len(trust_scores)
        return round((10 - avg_trust_score) / 10, 2)
    
    def determine_quick_win_flag(self, impact_score: float, complexity: str) -> bool:
        """Determine if recommendation is a quick win"""
        complexity_scores = {'Low': 1, 'Medium': 2, 'High': 3}
        complexity_num = complexity_scores.get(complexity, 2)
        
        return complexity_num <= 2 and impact_score >= 7.0

    def create_pages_table(self, parsed_data: List[Dict], experience_data: Optional[List[Dict]] = None) -> pd.DataFrame:
        """Create enhanced pages.csv table with derived metrics"""
        pages = []
        
        for data in parsed_data:
            metadata = data['metadata']
            url_slug = Path(data['file_path']).stem.replace('_hygiene_scorecard', '')
            page_id = self.create_page_id(url_slug)
            
            # Calculate derived metrics
            hygiene_score = metadata['final_score']
            
            # Calculate brand health based on hygiene score only (remove problematic fields)
            # These fields (sentiment, engagement, conversion) should only apply to offsite channels
            brand_health_index = self.calculate_brand_health_index(hygiene_score, 5.0, 5.0)  # Use neutral defaults
            trust_gap = self.calculate_trust_gap(data['criteria_scores'])
            
            pages.append({
                'page_id': page_id,
                'url': metadata['url'],
                'slug': url_slug,
                'persona': self.persona_name,
                'tier': metadata['tier'],
                'final_score': metadata['final_score'],
                'brand_health_index': brand_health_index,
                'trust_gap': trust_gap,
                'audited_ts': metadata['audited']
            })
        
        return pd.DataFrame(pages)
    
    def create_criteria_scores_table(self, parsed_data: List[Dict]) -> pd.DataFrame:
        """Create enhanced criteria_scores.csv table with impact scores"""
        criteria_rows = []
        
        for data in parsed_data:
            url_slug = Path(data['file_path']).stem.replace('_hygiene_scorecard', '')
            page_id = self.create_page_id(url_slug)
            tier = data['metadata']['tier']
            
            for criterion in data['criteria_scores']:
                impact_score = self.calculate_impact_score(
                    criterion['score'], 
                    criterion['weight_pct'], 
                    tier
                )
                
                criteria_rows.append({
                    'page_id': page_id,
                    'criterion_code': criterion['criterion_code'],
                    'criterion_name': criterion['criterion_name'],
                    'score': criterion['score'],
                    'evidence': criterion['evidence'],
                    'weight_pct': criterion['weight_pct'],
                    'tier': tier,
                    'descriptor': criterion['descriptor'],
                    'impact_score': impact_score
                })
        
        return pd.DataFrame(criteria_rows)
    
    def parse_experience_markdown(self, file_path: Path) -> Dict:
        """Extract persona experience data from experience report markdown"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract the structured table data
        findings = []
        table_pattern = r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
        matches = re.findall(table_pattern, content)
        
        for finding_type, example_text, analysis in matches:
            # Skip header rows
            if 'Finding' in finding_type or '---' in finding_type:
                continue
                
            findings.append({
                'finding_type': finding_type.strip(),
                'example_text': example_text.strip(),
                'strategic_analysis': analysis.strip()
            })
        
        # Extract narrative sections
        sections = {}
        
        # First Impression
        first_impression_match = re.search(r'First Impression:(.*?)(?=\n\n[A-Z]|\n[A-Z][^:]*:|$)', content, re.DOTALL)
        if first_impression_match:
            sections['first_impression'] = first_impression_match.group(1).strip()
        
        # Language & Tone
        language_tone_match = re.search(r'Language & Tone:(.*?)(?=\n\n[A-Z]|\n[A-Z][^:]*:|$)', content, re.DOTALL)
        if language_tone_match:
            sections['language_tone'] = language_tone_match.group(1).strip()
        
        # Gaps in Information
        gaps_match = re.search(r'Gaps in Information:(.*?)(?=\n\n[A-Z]|\n[A-Z][^:]*:|$)', content, re.DOTALL)
        if gaps_match:
            sections['information_gaps'] = gaps_match.group(1).strip()
        
        # Trust and Credibility
        trust_match = re.search(r'Trust and Credibility:(.*?)(?=\n\n[A-Z]|\n[A-Z][^:]*:|$)', content, re.DOTALL)
        if trust_match:
            sections['trust_credibility'] = trust_match.group(1).strip()
        
        # Business Impact & Next Steps
        impact_match = re.search(r'Business Impact & Next Steps:(.*?)$', content, re.DOTALL)
        if impact_match:
            sections['business_impact'] = impact_match.group(1).strip()
        
        return {
            'findings': findings,
            'sections': sections,
            'raw_content': content
        }
    
    def create_experience_table(self, parsed_data: List[Dict], experience_data: List[Dict]) -> pd.DataFrame:
        """Create experience.csv table from experience report data"""
        experience_rows = []
        
        # Create a mapping from file paths to experience data
        experience_map = {}
        for exp_data in experience_data:
            file_path = exp_data['file_path']
            url_slug = Path(file_path).stem.replace('_experience_report', '')
            experience_map[url_slug] = exp_data
        
        for data in parsed_data:
            url_slug = Path(data['file_path']).stem.replace('_hygiene_scorecard', '')
            page_id = self.create_page_id(url_slug)
            
            # Get corresponding experience data
            exp_data = experience_map.get(url_slug, {})
            exp_content = exp_data.get('parsed_content', {})
            
            # Extract findings
            findings = exp_content.get('findings', [])
            effective_examples = [f for f in findings if f.get('finding_type', '').lower() == 'effective copy']
            ineffective_examples = [f for f in findings if f.get('finding_type', '').lower() == 'ineffective copy']
            
            # Extract sections
            sections = exp_content.get('sections', {})
            
            experience_rows.append({
                'page_id': page_id,
                'persona_id': self.persona_name,
                'first_impression': sections.get('first_impression', ''),
                'language_tone_feedback': sections.get('language_tone', ''),
                'information_gaps': sections.get('information_gaps', ''),
                'trust_credibility_assessment': sections.get('trust_credibility', ''),
                'business_impact_analysis': sections.get('business_impact', ''),
                'effective_copy_examples': ' | '.join([f"{ex.get('example_text', '')}: {ex.get('strategic_analysis', '')}" for ex in effective_examples]),
                'ineffective_copy_examples': ' | '.join([f"{ex.get('example_text', '')}: {ex.get('strategic_analysis', '')}" for ex in ineffective_examples])
                # Removed problematic fields: overall_sentiment, engagement_level, conversion_likelihood
                # These should only apply to offsite channels, not onsite data (Tier 1, 2, 3)
            })
        
        return pd.DataFrame(experience_rows)
    
    # Removed analyze_sentiment, analyze_engagement, and analyze_conversion methods
    # These methods generated problematic fields that should only apply to offsite channels, not onsite data (Tier 1, 2, 3)

    def create_recommendations_table(self, parsed_data: List[Dict]) -> pd.DataFrame:
        """Create enhanced recommendations.csv table with quick win flags"""
        rec_rows = []
        
        for data in parsed_data:
            url_slug = Path(data['file_path']).stem.replace('_hygiene_scorecard', '')
            page_id = self.create_page_id(url_slug)
            tier = data['metadata']['tier']
            
            for rec in data['recommendations']:
                # Calculate impact score for this recommendation
                # Use average of all criteria scores for this page as baseline
                avg_score = sum(c['score'] for c in data['criteria_scores']) / len(data['criteria_scores']) if data['criteria_scores'] else 5.0
                rec_impact_score = self.calculate_impact_score(avg_score, 20, tier)  # 20% weight for recommendations
                
                # Assign complexity based on strategic impact category
                complexity = self.assign_complexity(rec['strategic_impact'])
                quick_win = self.determine_quick_win_flag(rec_impact_score, complexity)
                
                rec_rows.append({
                    'page_id': page_id,
                    'recommendation': rec['recommendation'],
                    'strategic_impact': rec['strategic_impact'],
                    'complexity': complexity,
                    'urgency': rec['urgency'],
                    'resources': rec['resources'],
                    'impact_score': rec_impact_score,
                    'quick_win_flag': quick_win,
                    'owner': '',        # Empty for user assignment
                    'target_date': '',  # Empty for user assignment
                    'status': 'Not Started'  # Default status
                })
        
        return pd.DataFrame(rec_rows)
    
    def assign_complexity(self, strategic_impact: str) -> str:
        """Assign complexity based on strategic impact category"""
        complexity_map = {
            'Brand Differentiation': 'High',     # Requires strategic thinking
            'Value Proposition': 'Medium',       # Moderate effort
            'Trust & Credibility': 'Low',        # Often simple additions
            'Conversion Optimization': 'Low',    # Usually quick fixes
            'General': 'Medium'                  # Default
        }
        return complexity_map.get(strategic_impact, 'Medium')
    
    def validate_data(self, pages_df: pd.DataFrame, criteria_df: pd.DataFrame) -> List[str]:
        """Validate the parsed data and return list of issues"""
        issues = []
        
        # Check for missing scores
        if criteria_df.empty:
            issues.append("No criteria scores found")
        
        # Check evidence length for high/low scores
        for _, row in criteria_df.iterrows():
            if (row['score'] >= 7 or row['score'] <= 4) and len(row['evidence']) < 25:
                issues.append(f"Page {row['page_id']}: Evidence too short for score {row['score']}")
        
        # Check final scores match
        for _, page in pages_df.iterrows():
            page_criteria = criteria_df[criteria_df['page_id'] == page['page_id']]
            if not page_criteria.empty:
                avg_score = page_criteria['score'].mean()
                if abs(avg_score - page['final_score']) > 1.0:
                    issues.append(f"Page {page['page_id']}: Final score mismatch ({page['final_score']} vs {avg_score:.1f})")
        
        return issues
    
    def backfill_run(self):
        """Main backfill function"""
        print(f"🔄 Backfilling audit data for {self.persona_name}...")
        
        # Parse all scorecard files
        parsed_data = []
        scorecard_files = list(self.input_dir.glob("*_hygiene_scorecard.md"))
        
        if not scorecard_files:
            print("❌ No hygiene scorecard files found")
            return
        
        print(f"📄 Found {len(scorecard_files)} scorecard files")
        
        for scorecard_file in scorecard_files:
            try:
                data = self.parse_scorecard_markdown(scorecard_file)
                data['file_path'] = str(scorecard_file)
                parsed_data.append(data)
                print(f"✅ Parsed {scorecard_file.name}")
            except Exception as e:
                print(f"❌ Error parsing {scorecard_file.name}: {e}")
                continue
        
        if not parsed_data:
            print("❌ No data successfully parsed")
            return
        
        # Parse all experience report files
        experience_data = []
        experience_files = list(self.input_dir.glob("*_experience_report.md"))
        
        print(f"📄 Found {len(experience_files)} experience report files")
        
        for experience_file in experience_files:
            try:
                data = self.parse_experience_markdown(experience_file)
                data['file_path'] = str(experience_file)
                data['parsed_content'] = data  # Store parsed content for table creation
                experience_data.append(data)
                print(f"✅ Parsed experience report {experience_file.name}")
            except Exception as e:
                print(f"❌ Error parsing experience report {experience_file.name}: {e}")
                continue
        
        # Create tables
        print("📊 Creating structured tables...")
        
        pages_df = self.create_pages_table(parsed_data, experience_data)
        criteria_df = self.create_criteria_scores_table(parsed_data)
        recommendations_df = self.create_recommendations_table(parsed_data)
        
        # Create experience table if we have experience data
        experience_df = None
        if experience_data:
            print("📝 Creating experience data table...")
            experience_df = self.create_experience_table(parsed_data, experience_data)
        
        # Validate data
        print("🔍 Validating data...")
        issues = self.validate_data(pages_df, criteria_df)
        if issues:
            print("⚠️  Validation issues found:")
            for issue in issues[:5]:  # Show first 5 issues
                print(f"   - {issue}")
        
        # Save tables
        print("💾 Saving enhanced CSV files...")
        
        pages_df.to_csv(self.output_dir / "pages.csv", index=False)
        criteria_df.to_csv(self.output_dir / "criteria_scores.csv", index=False)
        recommendations_df.to_csv(self.output_dir / "recommendations.csv", index=False)
        
        # Save experience data if available
        if experience_df is not None and not experience_df.empty:
            experience_df.to_csv(self.output_dir / "experience.csv", index=False)
            experience_df.to_parquet(self.output_dir / "experience.parquet", index=False)
            print(f"💭 Saved experience data: {len(experience_df)} persona experiences")
        
        # Also save as parquet for analytics
        pages_df.to_parquet(self.output_dir / "pages.parquet", index=False)
        criteria_df.to_parquet(self.output_dir / "criteria_scores.parquet", index=False)
        recommendations_df.to_parquet(self.output_dir / "recommendations.parquet", index=False)
        
        # Summary stats
        print(f"✅ Backfill complete!")
        print(f"📊 Summary:")
        print(f"   - Pages: {len(pages_df)}")
        print(f"   - Criteria scores: {len(criteria_df)}")
        print(f"   - Recommendations: {len(recommendations_df)}")
        if experience_df is not None:
            print(f"   - Experience reports: {len(experience_df)}")
        print(f"   - Average score: {criteria_df['score'].mean():.2f}")
        print(f"   - Score distribution: {criteria_df['descriptor'].value_counts().to_dict()}")
        
        return self.output_dir

def main():
    """Backfill existing audit outputs"""
    import sys
    
    if len(sys.argv) > 1:
        persona_name = sys.argv[1]
    else:
        persona_name = "The_BENELUX_Technology_Innovation_Leader"
    
    packager = EnhancedBackfillPackager(persona_name)
    packager.backfill_run()

if __name__ == "__main__":
    main() 