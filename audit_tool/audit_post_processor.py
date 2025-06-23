"""
Audit Post-Processor: Consolidated pipeline for transforming raw audit outputs 
into dashboard-ready unified data with proper tier classification, strategic analysis, 
and multi-persona integration.

Usage:
    processor = AuditPostProcessor(persona_name="The Technical Influencer")
    processor.process_audit_results()
    processor.add_to_database()
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd

try:
    from .backfill_packager import EnhancedBackfillPackager
    from .tier_classifier import TierClassifier
    from .strategic_summary_generator import StrategicSummaryGenerator
    from .multi_persona_packager import MultiPersonaPackager
    from .methodology_parser import MethodologyParser
except ImportError:
    # Fallback for direct execution
    from backfill_packager import EnhancedBackfillPackager
    from tier_classifier import TierClassifier
    from strategic_summary_generator import StrategicSummaryGenerator
    from multi_persona_packager import MultiPersonaPackager
    from methodology_parser import MethodologyParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditPostProcessor:
    """
    Consolidated post-audit processing pipeline that transforms raw audit outputs
    into dashboard-ready unified data.
    """
    
    def __init__(self, 
                 persona_name: str,
                 audit_output_dir: str = None,
                 methodology_file: str = "audit_tool/config/methodology.yaml"):
        """
        Initialize the post-processor.
        
        Args:
            persona_name: Name of the persona (e.g., "The Technical Influencer")
            audit_output_dir: Override default audit output directory
            methodology_file: Path to methodology YAML file
        """
        self.persona_name = persona_name
        self.methodology_file = methodology_file
        
        # Set up directories
        if audit_output_dir:
            self.audit_output_dir = Path(audit_output_dir)
        else:
            self.audit_output_dir = Path("audit_outputs") / persona_name
            
        self.temp_dir = Path("temp_processing") / persona_name.replace(" ", "_")
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.methodology_parser = MethodologyParser(self.methodology_file)
        self.tier_classifier = TierClassifier()
        self.backfill_packager = None
        self.strategic_generator = None
        self.multi_persona_packager = MultiPersonaPackager()
        
        # Processing state
        self.processed_data = {}
        self.tier_classifications = {}
        self.strategic_summary = None
        
        logger.info(f"Initialized AuditPostProcessor for: {persona_name}")
    
    def validate_audit_output(self) -> bool:
        """
        Validate that audit output directory contains required files.
        
        Returns:
            bool: True if valid audit output exists
        """
        if not self.audit_output_dir.exists():
            logger.error(f"Audit output directory not found: {self.audit_output_dir}")
            return False
            
        # Check for required markdown files
        required_patterns = [
            "*_hygiene_scorecard.md",
            "*_experience_report.md"
        ]
        
        found_files = []
        for pattern in required_patterns:
            files = list(self.audit_output_dir.glob(pattern))
            if not files:
                logger.error(f"No files found matching pattern: {pattern}")
                return False
            found_files.extend(files)
        
        logger.info(f"Found {len(found_files)} audit output files")
        return True
    
    def classify_page_tiers(self) -> Dict[str, Dict]:
        """
        Classify all audited URLs into tiers and channels.
        
        Returns:
            Dict mapping URL to tier/channel classification
        """
        logger.info("Starting tier classification...")
        
        # Extract URLs from audit files
        urls = self._extract_urls_from_audit_files()
        
        # Classify each URL
        classifications = {}
        for url in urls:
            tier_info = self.tier_classifier.classify_url(url)
            classifications[url] = {
                'tier': tier_info.get('tier', 3),
                'tier_name': tier_info.get('tier_name', 'Supporting'),
                'tier_weight': tier_info.get('tier_weight', 0.2),
                'channel': tier_info.get('channel', 'Owned'),
                'channel_weight': tier_info.get('channel_weight', 1.0)
            }
        
        self.tier_classifications = classifications
        logger.info(f"Classified {len(classifications)} URLs into tiers")
        return classifications
    
    def run_backfill_processing(self) -> Dict[str, pd.DataFrame]:
        """
        Run enhanced backfill processing with tier integration.
        
        Returns:
            Dict of processed DataFrames
        """
        logger.info("Starting backfill processing...")
        
        # Initialize backfill packager with tier classifications
        self.backfill_packager = EnhancedBackfillPackager(
            input_dir=str(self.audit_output_dir),
            output_dir=str(self.temp_dir),
            tier_classifications=self.tier_classifications
        )
        
        # Process all audit files
        processed_data = self.backfill_packager.process_all_files()
        
        # Enhance with tier-weighted scores
        if 'criteria_scores' in processed_data:
            processed_data['criteria_scores'] = self._add_tier_weighted_scores(
                processed_data['criteria_scores']
            )
        
        self.processed_data = processed_data
        logger.info(f"Backfill processing complete. Generated {len(processed_data)} datasets")
        return processed_data
    
    def generate_strategic_summary(self) -> str:
        """
        Generate strategic summary using processed data.
        
        Returns:
            Path to generated strategic summary file
        """
        logger.info("Generating strategic summary...")
        
        # Initialize strategic summary generator
        self.strategic_generator = StrategicSummaryGenerator(
            persona_name=self.persona_name,
            data_dir=str(self.temp_dir)
        )
        
        # Generate summary using CSV data (more structured than markdown)
        summary_path = self.strategic_generator.generate_from_csv_data(
            criteria_scores_path=str(self.temp_dir / "criteria_scores.csv"),
            pages_path=str(self.temp_dir / "pages.csv"),
            recommendations_path=str(self.temp_dir / "recommendations.csv")
        )
        
        self.strategic_summary = summary_path
        logger.info(f"Strategic summary generated: {summary_path}")
        return summary_path
    
    def add_to_database(self) -> bool:
        """
        Add processed data to unified multi-persona database.
        
        Returns:
            bool: True if successfully added to database
        """
        logger.info("Adding to unified database...")
        
        try:
            # Prepare data for multi-persona integration
            persona_data = {
                'persona_name': self.persona_name,
                'data_dir': str(self.temp_dir),
                'strategic_summary': self.strategic_summary,
                'tier_classifications': self.tier_classifications,
                'processed_datasets': self.processed_data
            }
            
            # Add to multi-persona database
            success = self.multi_persona_packager.add_persona_data(persona_data)
            
            if success:
                logger.info("Successfully added to unified database")
                # Clean up temp files
                self._cleanup_temp_files()
            else:
                logger.error("Failed to add to unified database")
                
            return success
            
        except Exception as e:
            logger.error(f"Error adding to database: {e}")
            return False
    
    def process_audit_results(self) -> bool:
        """
        Complete processing pipeline: validate -> classify -> backfill -> summarize.
        
        Returns:
            bool: True if processing completed successfully
        """
        logger.info(f"Starting complete audit post-processing for: {self.persona_name}")
        
        try:
            # Step 1: Validate audit output
            if not self.validate_audit_output():
                return False
            
            # Step 2: Classify page tiers
            self.classify_page_tiers()
            
            # Step 3: Run backfill processing
            self.run_backfill_processing()
            
            # Step 4: Generate strategic summary
            self.generate_strategic_summary()
            
            logger.info("Audit post-processing completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in audit post-processing: {e}")
            return False
    
    def get_processing_status(self) -> Dict:
        """
        Get current processing status and results summary.
        
        Returns:
            Dict with processing status information
        """
        return {
            'persona_name': self.persona_name,
            'audit_output_dir': str(self.audit_output_dir),
            'temp_dir': str(self.temp_dir),
            'audit_files_found': self.audit_output_dir.exists(),
            'tier_classifications_count': len(self.tier_classifications),
            'processed_datasets': list(self.processed_data.keys()),
            'strategic_summary_generated': self.strategic_summary is not None,
            'ready_for_database': all([
                self.tier_classifications,
                self.processed_data,
                self.strategic_summary
            ])
        }
    
    # Private helper methods
    
    def _extract_urls_from_audit_files(self) -> List[str]:
        """Extract URLs from audit markdown files."""
        urls = set()
        
        for md_file in self.audit_output_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Extract URLs from markdown content
                # Look for URL patterns in the content
                import re
                url_pattern = r'https?://[^\s\)]+|www\.[^\s\)]+'
                found_urls = re.findall(url_pattern, content)
                urls.update(found_urls)
                
            except Exception as e:
                logger.warning(f"Error reading {md_file}: {e}")
        
        return list(urls)
    
    def _add_tier_weighted_scores(self, criteria_df: pd.DataFrame) -> pd.DataFrame:
        """Add tier-weighted scores to criteria DataFrame."""
        if 'url' not in criteria_df.columns:
            return criteria_df
            
        # Add tier information
        criteria_df['tier'] = criteria_df['url'].map(
            lambda url: self.tier_classifications.get(url, {}).get('tier', 3)
        )
        criteria_df['tier_weight'] = criteria_df['url'].map(
            lambda url: self.tier_classifications.get(url, {}).get('tier_weight', 0.2)
        )
        
        # Calculate tier-weighted score
        if 'raw_score' in criteria_df.columns:
            criteria_df['tier_weighted_score'] = (
                criteria_df['raw_score'] * criteria_df['tier_weight']
            )
        
        return criteria_df
    
    def _cleanup_temp_files(self):
        """Clean up temporary processing files."""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
                logger.info("Cleaned up temporary files")
        except Exception as e:
            logger.warning(f"Error cleaning up temp files: {e}")


# Convenience function for simple usage
def process_completed_audit(persona_name: str, add_to_db: bool = True) -> bool:
    """
    Convenience function to process a completed audit.
    
    Args:
        persona_name: Name of the persona
        add_to_db: Whether to add results to unified database
        
    Returns:
        bool: True if processing completed successfully
    """
    processor = AuditPostProcessor(persona_name)
    
    # Run complete processing pipeline
    success = processor.process_audit_results()
    
    if success and add_to_db:
        success = processor.add_to_database()
    
    return success


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python audit_post_processor.py <persona_name> [--no-db]")
        sys.exit(1)
    
    persona_name = sys.argv[1]
    add_to_db = "--no-db" not in sys.argv
    
    print(f"Processing audit results for: {persona_name}")
    success = process_completed_audit(persona_name, add_to_db)
    
    if success:
        print("✅ Processing completed successfully")
    else:
        print("❌ Processing failed")
        sys.exit(1) 