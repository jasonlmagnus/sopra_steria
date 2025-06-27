#!/usr/bin/env python3
"""
Sopra Steria Brand Audit Tool - Main CLI Entry Point

🐍 PYTHON PROJECT - This is the main CLI for the Python-based brand audit tool
Test change to see if Codex creates PRs for Python backend changes

Usage:
    python -m audit_tool.main --help

STATUS: ACTIVE

This module serves as the primary entry point for the brand audit tool, providing:
1. Command-line interface for running brand audits
2. Orchestration of the entire audit workflow
3. Integration of scraping, AI analysis, and reporting components
4. Support for both single-URL and batch processing modes
5. Configuration management and environment setup

The module implements a comprehensive workflow that processes URLs through
scraping, AI-based analysis, and structured output generation, supporting
both single-persona and multi-persona audit scenarios.
"""

import os
import sys
import time
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from .scraper import Scraper
from .ai_interface import AIInterface
from .methodology_parser import MethodologyParser
from .persona_parser import PersonaParser
from .multi_persona_packager import MultiPersonaPackager
from .strategic_summary_generator import StrategicSummaryGenerator
from . import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('audit_tool.log')
    ]
)

logger = logging.getLogger(__name__)

class BrandAuditTool:
    """Main class for running brand audits."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the brand audit tool.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        logger.info("Initializing Brand Audit Tool")
        
        # Initialize components
        self.methodology = MethodologyParser(config_path)
        self.scraper = Scraper()
        self.ai = AIInterface()
        self.persona_parser = PersonaParser()
        
        # Set default paths
        self.audit_inputs_dir = Path("audit_inputs")
        self.audit_outputs_dir = Path("audit_outputs")
        self.personas_dir = self.audit_inputs_dir / "personas"
        
        # Ensure directories exist
        os.makedirs(self.audit_outputs_dir, exist_ok=True)
        
        logger.info("Brand Audit Tool initialized")
    
    def run_audit(self, urls: List[str], persona_path: str) -> Dict[str, Any]:
        """
        Run a brand audit for a list of URLs and a specific persona.
        
        Args:
            urls: List of URLs to audit
            persona_path: Path to the persona markdown file
            
        Returns:
            Dictionary of audit results
        """
        logger.info(f"Starting audit for {len(urls)} URLs with persona {persona_path}")
        
        # Load persona
        with open(persona_path, 'r', encoding='utf-8') as f:
            persona_content = f.read()
        
        persona = self.persona_parser.extract_attributes_from_content(persona_content)
        logger.info(f"Loaded persona: {persona.name}")
        
        # Create output directory for this persona
        persona_dir = self.audit_outputs_dir / persona.name
        os.makedirs(persona_dir, exist_ok=True)
        
        results = {}
        
        # Process each URL
        for url in urls:
            try:
                logger.info(f"Processing URL: {url}")
                
                # Scrape the URL
                page_data = self.scraper.scrape_url(url)
                
                if page_data.is_404:
                    logger.warning(f"URL returned 404: {url}")
                    results[url] = {"status": "error", "message": "Page not found (404)"}
                    continue
                
                # Generate hygiene scorecard
                hygiene_scorecard = self.ai.generate_hygiene_scorecard(
                    url=url,
                    page_content=page_data.raw_text,
                    persona_content=persona_content,
                    methodology=self.methodology
                )
                
                # Generate experience report
                experience_report = self.ai.generate_experience_report(
                    url=url,
                    page_content=page_data.raw_text,
                    persona_content=persona_content,
                    methodology=self.methodology
                )
                
                # Save outputs
                url_slug = self._url_to_slug(url)
                
                with open(persona_dir / f"{url_slug}_hygiene_scorecard.md", 'w', encoding='utf-8') as f:
                    f.write(hygiene_scorecard)
                
                with open(persona_dir / f"{url_slug}_experience_report.md", 'w', encoding='utf-8') as f:
                    f.write(experience_report)
                
                results[url] = {
                    "status": "success",
                    "hygiene_scorecard": hygiene_scorecard,
                    "experience_report": experience_report
                }
                
                logger.info(f"Completed processing for URL: {url}")
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {str(e)}")
                results[url] = {"status": "error", "message": str(e)}
        
        # Generate strategic summary
        try:
            summary_generator = StrategicSummaryGenerator(str(persona_dir))
            summary, _, _ = summary_generator.generate_full_report()
            
            with open(persona_dir / "Strategic_Summary.md", 'w', encoding='utf-8') as f:
                f.write(summary)
            
            logger.info(f"Generated strategic summary for {persona.name}")
            
        except Exception as e:
            logger.error(f"Error generating strategic summary: {str(e)}")
        
        logger.info(f"Audit completed for {len(urls)} URLs with persona {persona.name}")
        
        return results
    
    def run_multi_persona_audit(self, urls: List[str], persona_paths: List[str]) -> Dict[str, Any]:
        """
        Run a brand audit for multiple personas.
        
        Args:
            urls: List of URLs to audit
            persona_paths: List of paths to persona markdown files
            
        Returns:
            Dictionary of audit results by persona
        """
        logger.info(f"Starting multi-persona audit for {len(urls)} URLs with {len(persona_paths)} personas")
        
        results = {}
        
        # Process each persona
        for persona_path in persona_paths:
            try:
                persona_results = self.run_audit(urls, persona_path)
                
                # Extract persona name from path
                persona_name = Path(persona_path).stem
                results[persona_name] = persona_results
                
                logger.info(f"Completed audit for persona: {persona_name}")
                
            except Exception as e:
                logger.error(f"Error processing persona {persona_path}: {str(e)}")
                results[Path(persona_path).stem] = {"status": "error", "message": str(e)}
        
        # Generate unified data files
        try:
            packager = MultiPersonaPackager()
            packager.process_all_personas()
            logger.info("Generated unified data files")
        except Exception as e:
            logger.error(f"Error generating unified data files: {str(e)}")
        
        logger.info(f"Multi-persona audit completed for {len(urls)} URLs with {len(persona_paths)} personas")
        
        return results
    
    def _url_to_slug(self, url: str) -> str:
        """
        Convert a URL to a filename-safe slug.
        
        Args:
            url: The URL to convert
            
        Returns:
            A filename-safe slug
        """
        # Remove protocol
        slug = url.replace('https://', '').replace('http://', '')
        
        # Replace special characters
        slug = slug.replace('/', '_').replace('.', '_').replace('-', '_').replace('?', '_').replace('&', '_')
        slug = slug.replace('=', '_').replace('%', '_').replace('#', '_').replace('@', '_').replace(':', '_')
        
        # Remove trailing underscores
        slug = slug.rstrip('_')
        
        return slug


def run_audit(urls_file: str = None, persona_file: str = None,
              output_dir: str = "audit_outputs", generate_summary: bool = True,
              verbose: bool = True, config: str | None = None) -> List[Dict[str, Any]]:
    """Convenience function to run a simple audit."""
    if not verbose:
        logging.getLogger().setLevel(logging.WARNING)

    tool = BrandAuditTool(config)
    tool.audit_outputs_dir = Path(output_dir)
    os.makedirs(tool.audit_outputs_dir, exist_ok=True)

    persona_name = None
    if persona_file:
        persona = PersonaParser().extract_attributes(persona_file)
        persona_name = persona.name

    urls = []
    if urls_file:
        with open(urls_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]

    if not hasattr(tool.scraper, 'scrape_url'):
        tool.scraper.scrape_url = tool.scraper.fetch_page  # type: ignore

    results_dict = tool.run_audit(urls, persona_file)

    if persona_name:
        persona_dir = tool.audit_outputs_dir / persona_name
        for p in persona_dir.glob("*.md"):
            shutil.copy(p, tool.audit_outputs_dir / p.name)

    ordered_results = []
    for url in urls:
        data = results_dict.get(url, {})
        ordered_results.append({
            'url': url,
            'status': data.get('status'),
            'hygiene_score': 1.0 if data.get('status') == 'success' else 0.0
        })

    return ordered_results

def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Brand Audit Tool')
    
    parser.add_argument('--urls', type=str, help='Path to file containing URLs to audit')
    parser.add_argument('--url', type=str, help='Single URL to audit')
    parser.add_argument('--persona', type=str, help='Path to persona file')
    parser.add_argument('--all-personas', action='store_true', help='Run audit with all personas')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--output-dir', type=str, help='Output directory')
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    
    args = parser.parse_args()

    if args.version:
        print(f"Sopra Steria Brand Audit Tool {__version__}")
        return
    
    # Initialize the tool
    tool = BrandAuditTool(args.config)
    
    # Set output directory if specified
    if args.output_dir:
        tool.audit_outputs_dir = Path(args.output_dir)
        os.makedirs(tool.audit_outputs_dir, exist_ok=True)
    
    # Get URLs
    urls = []
    if args.url:
        urls = [args.url]
    elif args.urls:
        with open(args.urls, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    else:
        logger.error("No URLs specified. Use --url or --urls")
        sys.exit(1)
    
    # Get personas
    if args.all_personas:
        persona_paths = list(Path("audit_inputs/personas").glob("*.md"))
        if not persona_paths:
            logger.error("No persona files found in audit_inputs/personas/")
            sys.exit(1)
        
        # Run multi-persona audit
        tool.run_multi_persona_audit(urls, [str(p) for p in persona_paths])
        
    elif args.persona:
        # Run single persona audit
        tool.run_audit(urls, args.persona)
        
    else:
        logger.error("No persona specified. Use --persona or --all-personas")
        sys.exit(1)
    
    logger.info("Audit completed successfully")

if __name__ == "__main__":
    main()
