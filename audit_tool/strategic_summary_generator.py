"""
Strategic Summary Generator for Brand Audit Tool

STATUS: ACTIVE

This module generates comprehensive strategic summaries from audit data.
It serves as a critical analysis component that:
1. Aggregates data from multiple hygiene scorecards and experience reports
2. Calculates tier-specific and overall brand health scores
3. Identifies key strengths, weaknesses, and patterns across pages
4. Generates executive-level strategic insights and recommendations
5. Creates markdown-formatted strategic summary reports

The generator supports both direct AI-based summary generation and
data-driven statistical analysis approaches, providing a comprehensive
view of brand health across the audited digital estate.
"""

import os
import re
import glob
import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

from .ai_interface import AIInterface
from .methodology_parser import MethodologyParser

logger = logging.getLogger(__name__)

class StrategicSummaryGenerator:
    """Generates strategic summaries from audit data."""
    
    def __init__(self, audit_dir: str):
        """
        Initialize with path to audit output directory.
        
        Args:
            audit_dir: Path to the audit output directory containing scorecards
        """
        self.audit_dir = Path(audit_dir)
        self.methodology = MethodologyParser()
        
        # Ensure the audit directory exists
        if not self.audit_dir.exists():
            raise ValueError(f"Audit directory does not exist: {self.audit_dir}")
    
    def generate_full_report(self) -> Tuple[str, List[Dict], Dict]:
        """
        Generate a complete strategic summary report.
        
        Returns:
            Tuple of (report_markdown, page_data, summary_stats)
        """
        logger.info(f"Generating strategic summary for {self.audit_dir}")
        
        # Extract persona name from directory
        persona_name = self.audit_dir.name
        
        # Load and process all scorecard data
        page_data = self._load_scorecard_data()
        
        if not page_data:
            logger.warning("No scorecard data found, cannot generate summary")
            return "# No Data Available\n\nNo scorecard data was found to generate a summary.", [], {}
        
        # Calculate summary statistics
        summary_stats = self._calculate_summary_stats(page_data)
        
        # Generate the report
        report = self._generate_report_markdown(persona_name, page_data, summary_stats)
        
        # Save the report
        output_path = self.audit_dir / "Strategic_Summary.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        logger.info(f"Strategic summary saved to {output_path}")
        
        return report, page_data, summary_stats
    
    def _load_scorecard_data(self) -> List[Dict]:
        """
        Load and parse all scorecard data from the audit directory.
        
        Returns:
            List of page data dictionaries
        """
        page_data = []
        
        # First try to load from CSV (newer format)
        csv_path = self.audit_dir / "criteria_scores.csv"
        pages_path = self.audit_dir / "pages.csv"
        
        if csv_path.exists() and pages_path.exists():
            try:
                # Load CSV data
                criteria_df = pd.read_csv(csv_path)
                pages_df = pd.read_csv(pages_path)
                
                # Process each page
                for page_id in pages_df['page_id'].unique():
                    page_row = pages_df[pages_df['page_id'] == page_id].iloc[0]
                    criteria_rows = criteria_df[criteria_df['page_id'] == page_id]
                    
                    # Skip if no criteria data
                    if criteria_rows.empty:
                        continue
                    
                    # Get URL and tier
                    url = page_row['url']
                    tier = page_row.get('tier', 'tier_2')  # Default to tier_2 if not specified
                    
                    # Extract criteria scores
                    criteria = []
                    for _, row in criteria_rows.iterrows():
                        criteria.append({
                            'name': row['criterion_code'],
                            'score': row['score'],
                            'evidence': row.get('evidence', '')
                        })
                    
                    # Calculate final score
                    final_score = criteria_rows['score'].mean()
                    
                    # Add to page data
                    page_data.append({
                        'page_id': page_id,
                        'url': url,
                        'tier': tier,
                        'criteria': criteria,
                        'final_score': final_score
                    })
                
                logger.info(f"Loaded {len(page_data)} pages from CSV data")
                return page_data
                
            except Exception as e:
                logger.error(f"Error loading CSV data: {e}")
                # Fall back to markdown parsing
        
        # Fall back to parsing markdown files
        scorecard_files = list(self.audit_dir.glob("*_hygiene_scorecard.md"))
        
        if not scorecard_files:
            logger.warning("No scorecard files found")
            return []
        
        for scorecard_file in scorecard_files:
            try:
                # Extract URL slug from filename
                url_slug = scorecard_file.stem.replace("_hygiene_scorecard", "")
                
                # Reconstruct URL from slug
                url = self._reconstruct_url(url_slug)
                
                # Parse scorecard content
                with open(scorecard_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extract final score
                final_score_match = re.search(r"\*\*Final Score:\*\*\s*([\d.]+)/10", content)
                final_score = float(final_score_match.group(1)) if final_score_match else 5.0
                
                # Extract criteria scores
                criteria = []
                criteria_pattern = r"\|\s*\*\*(.*?)\*\*\s*\|\s*([\d.]+)/10\s*\|\s*(.*?)\s*\|"
                for match in re.finditer(criteria_pattern, content):
                    criteria.append({
                        'name': match.group(1),
                        'score': float(match.group(2)),
                        'evidence': match.group(3)
                    })
                
                # Determine tier based on URL
                tier_name, _ = self.methodology.classify_url(url)
                
                # Add to page data
                page_data.append({
                    'page_id': url_slug,
                    'url': url,
                    'tier': tier_name,
                    'criteria': criteria,
                    'final_score': final_score
                })
                
            except Exception as e:
                logger.error(f"Error parsing scorecard {scorecard_file}: {e}")
        
        logger.info(f"Loaded {len(page_data)} pages from markdown files")
        return page_data
    
    def _reconstruct_url(self, url_slug: str) -> str:
        """
        Convert URL slug back to actual URL.
        
        Args:
            url_slug: The URL slug from the filename
            
        Returns:
            The reconstructed URL
        """
        if url_slug.startswith('www'):
            return f"https://{url_slug.replace('_', '.')}"
        elif url_slug.startswith('@'):
            # Social media links
            return f"https://linkedin.com/company/{url_slug[1:].replace('_', '-')}"
        else:
            return f"https://www.soprasteria.be/{url_slug.replace('_', '/')}"
    
    def _calculate_summary_stats(self, page_data: List[Dict]) -> Dict:
        """
        Calculate summary statistics from page data.
        
        Args:
            page_data: List of page data dictionaries
            
        Returns:
            Dictionary of summary statistics
        """
        # Initialize stats
        stats = {
            'overall_score': 0.0,
            'tier_scores': defaultdict(list),
            'criterion_scores': defaultdict(list),
            'top_pages': [],
            'bottom_pages': [],
            'strengths': [],
            'weaknesses': []
        }
        
        # Calculate overall score
        if page_data:
            stats['overall_score'] = sum(p['final_score'] for p in page_data) / len(page_data)
        
        # Calculate tier scores
        for page in page_data:
            tier = page['tier']
            stats['tier_scores'][tier].append(page['final_score'])
            
            # Add to criterion scores
            for criterion in page['criteria']:
                stats['criterion_scores'][criterion['name']].append(criterion['score'])
        
        # Calculate average tier scores
        stats['tier_averages'] = {
            tier: sum(scores) / len(scores) if scores else 0.0
            for tier, scores in stats['tier_scores'].items()
        }
        
        # Calculate average criterion scores
        stats['criterion_averages'] = {
            criterion: sum(scores) / len(scores) if scores else 0.0
            for criterion, scores in stats['criterion_scores'].items()
        }
        
        # Identify top and bottom pages
        sorted_pages = sorted(page_data, key=lambda p: p['final_score'], reverse=True)
        stats['top_pages'] = sorted_pages[:5]
        stats['bottom_pages'] = sorted_pages[-5:] if len(sorted_pages) >= 5 else sorted_pages
        
        # Identify strengths and weaknesses
        sorted_criteria = sorted(stats['criterion_averages'].items(), key=lambda x: x[1], reverse=True)
        stats['strengths'] = sorted_criteria[:3]
        stats['weaknesses'] = sorted_criteria[-3:] if len(sorted_criteria) >= 3 else sorted_criteria
        
        return stats
    
    def _generate_report_markdown(self, persona_name: str, page_data: List[Dict], stats: Dict) -> str:
        """
        Generate the markdown report.
        
        Args:
            persona_name: Name of the persona
            page_data: List of page data dictionaries
            stats: Summary statistics
            
        Returns:
            Markdown formatted report
        """
        # Format the report
        report = f"""# Strategic Brand Audit Summary for {persona_name}

## Executive Summary

This report presents a comprehensive analysis of Sopra Steria's brand presence across {len(page_data)} digital touchpoints, evaluated from the perspective of {persona_name}. The overall brand health score is **{stats['overall_score']:.1f}/10**.

"""
        
        # Add tier breakdown
        report += "## Tier Performance\n\n"
        for tier, avg in stats['tier_averages'].items():
            tier_name = tier.replace('_', ' ').title()
            report += f"- **{tier_name}**: {avg:.1f}/10\n"
        
        report += "\n"
        
        # Add strengths and weaknesses
        report += "## Key Strengths\n\n"
        for criterion, score in stats['strengths']:
            report += f"- **{criterion}**: {score:.1f}/10\n"
        
        report += "\n## Key Weaknesses\n\n"
        for criterion, score in stats['weaknesses']:
            report += f"- **{criterion}**: {score:.1f}/10\n"
        
        report += "\n"
        
        # Add top and bottom pages
        report += "## Top Performing Pages\n\n"
        for page in stats['top_pages']:
            report += f"- [{page['url']}]({page['url']}): {page['final_score']:.1f}/10\n"
        
        report += "\n## Lowest Performing Pages\n\n"
        for page in stats['bottom_pages']:
            report += f"- [{page['url']}]({page['url']}): {page['final_score']:.1f}/10\n"
        
        report += "\n"
        
        # Add strategic recommendations
        report += """## Strategic Recommendations

1. **Strengthen Brand Positioning**: Focus on improving the clarity and consistency of brand messaging across all digital touchpoints.

2. **Enhance Persona Relevance**: Tailor content more specifically to address the needs and priorities of this persona.

3. **Address Content Gaps**: Develop more comprehensive content in areas identified as weaknesses.

4. **Optimize Top Performers**: Use insights from top-performing pages to improve lower-performing content.

5. **Implement Regular Audits**: Establish a regular cadence of brand audits to track improvements over time.

## Next Steps

1. Prioritize recommendations based on business impact and implementation effort
2. Develop a detailed implementation plan with clear ownership and timelines
3. Establish metrics to track progress and impact
4. Schedule follow-up audit to measure improvements

"""
        
        return report
    
    def generate_ai_summary(self, model_provider: str = "anthropic") -> str:
        """
        Generate a summary using AI.
        
        Args:
            model_provider: The AI provider to use ("anthropic" or "openai")
            
        Returns:
            AI-generated summary
        """
        logger.info(f"Generating AI summary using {model_provider}")
        
        # Load scorecard data
        page_data = self._load_scorecard_data()
        
        if not page_data:
            logger.warning("No scorecard data found, cannot generate AI summary")
            return "# No Data Available\n\nNo scorecard data was found to generate a summary."
        
        # Initialize AI interface
        ai = AIInterface(model_provider=model_provider)
        
        # Generate summary
        summary = ai.generate_strategic_summary(
            persona_name=self.audit_dir.name,
            scorecard_data=page_data,
            methodology=self.methodology
        )
        
        # Save the summary
        output_path = self.audit_dir / "Strategic_Summary.md"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary)
        
        logger.info(f"AI summary saved to {output_path}")
        
        return summary
