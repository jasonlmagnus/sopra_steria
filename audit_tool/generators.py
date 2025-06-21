#!/usr/bin/env python3
"""
Report generators for the audit tool
Now focuses on individual report generation - strategic summaries handled by StrategicSummaryGenerator
"""

import os
import glob
import re
import logging
from datetime import datetime
from typing import List, Dict, Any
from .methodology_parser import MethodologyParser

class ReportGenerator:
    """Generate individual audit reports"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.parser = MethodologyParser()
        
    def save_hygiene_scorecard(self, page_slug: str, report_content: str):
        """Save hygiene scorecard report"""
        filename = f"{page_slug}_hygiene_scorecard.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logging.info(f"Saved hygiene scorecard: {filename}")
    
    def save_experience_report(self, page_slug: str, report_content: str):
        """Save experience report"""
        filename = f"{page_slug}_experience_report.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logging.info(f"Saved experience report: {filename}")
    
    def extract_score_from_report(self, report_content: str) -> float:
        """Extract final score from a report"""
        score_match = re.search(r'Final Score:\*\* (\d+\.?\d*)', report_content)
        if score_match:
            return float(score_match.group(1))
        return 0.0

# Legacy classes for backward compatibility
class NarrativeGenerator:
    """Legacy narrative generator - deprecated"""
    
    def __init__(self, ai_interface):
        self.ai_interface = ai_interface
        logging.warning("NarrativeGenerator is deprecated - use AIInterface directly")
    
    def create_report(self, persona_content: str, page_data: Any) -> str:
        """Create narrative report"""
        return self.ai_interface.generate_experience_report(
            page_data.url, page_data.content, persona_content, MethodologyParser()
        )

class ScorecardGenerator:
    """Legacy scorecard generator - deprecated"""
    
    def __init__(self, methodology: Any, ai_interface):
        self.methodology = methodology
        self.ai_interface = ai_interface
        logging.warning("ScorecardGenerator is deprecated - use AIInterface directly")
    
    def create_scorecard(self, page_data: Any) -> str:
        """Create scorecard"""
        return self.ai_interface.generate_hygiene_scorecard(
            page_data.url, page_data.content, "", MethodologyParser()
        )

class SummaryGenerator:
    """Legacy summary generator - deprecated"""
    
    def __init__(self, persona_name: str, ai_interface, methodology: Any):
        self.persona_name = persona_name
        self.ai_interface = ai_interface
        self.methodology = methodology
        logging.warning("SummaryGenerator is deprecated - use StrategicSummaryGenerator instead")
    
    def create_summary(self) -> str:
        """Create summary - redirects to new generator"""
        from .strategic_summary_generator import StrategicSummaryGenerator
        
        # Determine output directory from persona name
        output_dir = f"audit_outputs/{os.path.basename(self.persona_name).replace('.md', '')}"
        
        generator = StrategicSummaryGenerator(output_dir)
        report, _, _ = generator.generate_full_report()
        
        return report 