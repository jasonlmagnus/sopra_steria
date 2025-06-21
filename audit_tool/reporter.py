"""
This module is responsible for saving the generated reports to files.
"""
import os
from urllib.parse import urlparse
from .models import Scorecard, SummaryReport
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import logging

class Reporter:
    """
    Handles the saving of generated reports to the filesystem.
    """
    def __init__(self, persona_name: str, output_dir_base="audit_outputs"):
        # Sanitize persona_name from path to be a valid directory name (e.g., "P1")
        safe_persona_name = os.path.basename(persona_name).replace('.md', '')
        self.output_dir = os.path.join(output_dir_base, safe_persona_name)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def _url_to_filename(self, url: str, suffix: str) -> str:
        """Converts a URL into a safe filename."""
        parsed_url = urlparse(url)
        # Use path and query to create a unique name, replace slashes
        filename = (parsed_url.path + parsed_url.query).replace('/', '_').replace('=', '')
        # Remove leading underscore if it exists
        if filename.startswith('_'):
            filename = filename[1:]
        # Fallback to netloc if path is empty
        if not filename:
            filename = parsed_url.netloc.replace('.', '_')
        return f"{filename}_{suffix}.md"

    def write_narrative_report(self, url: str, narrative_content: str):
        """Saves the narrative experience report."""
        filename = self._url_to_filename(url, "experience_report")
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(narrative_content)
        logging.info(f"Narrative report saved to {filepath}")

    def write_scorecard(self, scorecard: Scorecard):
        """Saves the brand hygiene scorecard using a Jinja2 template."""
        template = self.jinja_env.get_template("scorecard_template.md")
        
        rendered_report = template.render(
            scorecard=scorecard,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        filename = self._url_to_filename(scorecard.url, "hygiene_scorecard")
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(rendered_report)
        logging.info(f"Scorecard saved to {filepath}")

    def write_summary_report(self, summary_report: SummaryReport):
        """Saves the strategic summary report using a Jinja2 template."""
        template = self.jinja_env.get_template("summary_template.md")
        
        rendered_report = template.render(
            report=summary_report,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        filename = "Strategic_Summary.md"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(rendered_report)
        logging.info(f"Summary report saved to {filepath}") 