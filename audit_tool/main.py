#!/usr/bin/env python3
"""
Main audit tool entry point
"""

import os
import sys
import argparse
import logging
from typing import Optional

from .scraper import Scraper
from .ai_interface import AIInterface
from .generators import ReportGenerator
from .strategic_summary_generator import StrategicSummaryGenerator
from .methodology_parser import MethodologyParser

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def run_audit(urls_file: str, persona_file: str, output_dir: str, 
              generate_summary: bool = True, verbose: bool = False, model_provider: str = "anthropic"):
    """Run complete audit pipeline"""
    
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize components
        logger.info("🚀 Starting Sopra Steria Brand Audit")
        logger.info(f"🤖 Using AI Provider: {model_provider.upper()}")
        
        # Load methodology
        methodology = MethodologyParser()
        logger.info(f"📋 Loaded methodology: {methodology.get_metadata()['name']} v{methodology.get_metadata()['version']}")
        
        # Initialize scraper and AI interface with selected provider
        scraper = Scraper()
        ai_interface = AIInterface(model_provider=model_provider)
        reporter = ReportGenerator(output_dir)
        
        # Load URLs and persona
        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        with open(persona_file, 'r') as f:
            persona_content = f.read()
        
        logger.info(f"📄 Loaded {len(urls)} URLs for audit")
        logger.info(f"🎭 Using persona: {os.path.basename(persona_file)}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Process each URL
        results = []
        for i, url in enumerate(urls, 1):
            logger.info(f"🔍 Processing URL {i}/{len(urls)}: {url}")
            
            try:
                # Scrape content
                page_data = scraper.fetch_page(url)
                if not page_data or page_data.is_404:
                    logger.warning(f"⚠️ Failed to scrape: {url}")
                    continue
                
                page_content = page_data.raw_text
                
                # Generate reports using AI
                hygiene_report = ai_interface.generate_hygiene_scorecard(
                    url, page_content, persona_content, methodology
                )
                
                experience_report = ai_interface.generate_experience_report(
                    url, page_content, persona_content, methodology
                )
                
                # Save individual reports
                page_slug = scraper.url_to_filename(url)
                reporter.save_hygiene_scorecard(page_slug, hygiene_report)
                reporter.save_experience_report(page_slug, experience_report)
                
                results.append({
                    'url': url,
                    'page_slug': page_slug,
                    'hygiene_score': reporter.extract_score_from_report(hygiene_report),
                    'status': 'success'
                })
                
                logger.info(f"✅ Completed: {url}")
                
            except Exception as e:
                logger.error(f"❌ Error processing {url}: {str(e)}")
                results.append({
                    'url': url,
                    'page_slug': scraper.url_to_filename(url),
                    'hygiene_score': 0,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Generate strategic summary using new YAML-driven generator
        if generate_summary and results:
            logger.info("📊 Generating Strategic Summary...")
            
            summary_generator = StrategicSummaryGenerator(output_dir)
            report, data, stats = summary_generator.generate_full_report()
            
            # Save strategic summary
            summary_file = os.path.join(output_dir, "Strategic_Summary.md")
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            # Save raw data for analysis
            import pandas as pd
            df = pd.DataFrame([
                {
                    'page': p['page_slug'],
                    'url': p['url'],
                    'tier': p['tier'],
                    'final_score': p['final_score'],
                    **{c['name']: c['score'] for c in p['criteria']}
                }
                for p in data
            ])
            df.to_csv(os.path.join(output_dir, "scorecard_data.csv"), index=False)
            
            logger.info(f"📄 Strategic Summary saved: {summary_file}")
            logger.info(f"📊 Raw data saved: {os.path.join(output_dir, 'scorecard_data.csv')}")
        
        # Summary stats
        successful = len([r for r in results if r['status'] == 'success'])
        failed = len([r for r in results if r['status'] == 'error'])
        avg_score = sum(r['hygiene_score'] for r in results if r['status'] == 'success') / successful if successful > 0 else 0
        
        logger.info("🎯 Audit Complete!")
        logger.info(f"   ✅ Successful: {successful}")
        logger.info(f"   ❌ Failed: {failed}")
        logger.info(f"   📊 Average Score: {avg_score:.1f}/10")
        logger.info(f"   📁 Output Directory: {output_dir}")
        
        return results
        
    except Exception as e:
        logger.error(f"💥 Audit failed: {str(e)}")
        raise

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Sopra Steria Brand Audit Tool')
    parser.add_argument('--urls', required=True, help='File containing URLs to audit')
    parser.add_argument('--persona', required=True, help='Persona file for evaluation context')
    parser.add_argument('--output', required=True, help='Output directory for reports')
    parser.add_argument('--model', choices=['anthropic', 'openai'], default='anthropic', 
                       help='AI model provider (default: anthropic)')
    parser.add_argument('--no-summary', action='store_true', help='Skip strategic summary generation')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    try:
        results = run_audit(
            urls_file=args.urls,
            persona_file=args.persona,
            output_dir=args.output,
            generate_summary=not args.no_summary,
            verbose=args.verbose,
            model_provider=args.model
        )
        
        print(f"\n🎉 Audit completed successfully!")
        print(f"📁 Results saved to: {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"\n💥 Audit failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 