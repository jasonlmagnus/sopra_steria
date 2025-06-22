"""
Content Generators for Brand Audit Tool

STATUS: ACTIVE

This module provides specialized content generation functionality that:
1. Creates structured markdown reports from audit data
2. Generates hygiene scorecards with consistent formatting
3. Produces experience reports with persona-specific insights
4. Formats strategic summaries with executive-level insights
5. Supports both AI-generated and template-based content approaches

The generators ensure consistent output formatting and structure across
different report types, enabling effective communication of audit findings.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class HygieneScorecard:
    """Generates hygiene scorecards in markdown format."""
    
    def __init__(self, url: str, persona_name: str):
        """
        Initialize with URL and persona name.
        
        Args:
            url: The URL being evaluated
            persona_name: The name of the persona
        """
        self.url = url
        self.persona_name = persona_name
        self.criteria_scores = []
        self.final_score = 0.0
        self.recommendations = []
    
    def add_criterion(self, name: str, score: float, evidence: str) -> None:
        """
        Add a criterion score.
        
        Args:
            name: The name of the criterion
            score: The score (0-10)
            evidence: The evidence for the score
        """
        self.criteria_scores.append({
            "name": name,
            "score": score,
            "evidence": evidence
        })
    
    def set_final_score(self, score: float) -> None:
        """
        Set the final score.
        
        Args:
            score: The final score (0-10)
        """
        self.final_score = score
    
    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a recommendation.
        
        Args:
            recommendation: The recommendation text
        """
        self.recommendations.append(recommendation)
    
    def generate(self) -> str:
        """
        Generate the markdown scorecard.
        
        Returns:
            Markdown formatted scorecard
        """
        # Format the header
        markdown = f"# Brand Hygiene Scorecard for {self.persona_name}\n\n"
        markdown += f"## URL: {self.url}\n\n"
        
        # Add introduction
        markdown += "## Introduction\n\n"
        markdown += f"This scorecard evaluates the brand hygiene of the URL from the perspective of {self.persona_name}. "
        markdown += "The evaluation is based on a set of criteria that assess both brand and performance aspects of the content.\n\n"
        
        # Add criteria scores
        markdown += "## Criteria Scores\n\n"
        markdown += "| **Criterion** | **Score** | **Evidence** |\n"
        markdown += "|---------------|-----------|-------------|\n"
        
        for criterion in self.criteria_scores:
            markdown += f"| **{criterion['name']}** | {criterion['score']:.1f}/10 | {criterion['evidence']} |\n"
        
        markdown += "\n"
        
        # Add final score
        markdown += "## Overall Assessment\n\n"
        markdown += f"**Final Score:** {self.final_score:.1f}/10\n\n"
        
        # Add recommendations
        markdown += "## Recommendations\n\n"
        
        for i, recommendation in enumerate(self.recommendations, 1):
            markdown += f"{i}. {recommendation}\n"
        
        return markdown

class ExperienceReport:
    """Generates experience reports in markdown format."""
    
    def __init__(self, url: str, persona_name: str):
        """
        Initialize with URL and persona name.
        
        Args:
            url: The URL being evaluated
            persona_name: The name of the persona
        """
        self.url = url
        self.persona_name = persona_name
        self.sections = {}
        self.sentiment = "Neutral"
        self.engagement = "Medium"
        self.conversion = "Medium"
        self.recommendations = []
    
    def add_section(self, name: str, content: str) -> None:
        """
        Add a section to the report.
        
        Args:
            name: The name of the section
            content: The content of the section
        """
        self.sections[name] = content
    
    def set_metrics(self, sentiment: str, engagement: str, conversion: str) -> None:
        """
        Set the experience metrics.
        
        Args:
            sentiment: Overall sentiment (Positive, Neutral, Negative)
            engagement: Engagement level (High, Medium, Low)
            conversion: Conversion likelihood (High, Medium, Low)
        """
        self.sentiment = sentiment
        self.engagement = engagement
        self.conversion = conversion
    
    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a recommendation.
        
        Args:
            recommendation: The recommendation text
        """
        self.recommendations.append(recommendation)
    
    def generate(self) -> str:
        """
        Generate the markdown report.
        
        Returns:
            Markdown formatted report
        """
        # Format the header
        markdown = f"# Brand Experience Report for {self.persona_name}\n\n"
        markdown += f"## URL: {self.url}\n\n"
        
        # Add introduction
        markdown += "## Introduction\n\n"
        markdown += f"This report analyzes the brand experience of the URL from the perspective of {self.persona_name}. "
        markdown += "The analysis evaluates how effectively the content resonates with this specific persona and identifies opportunities for improvement.\n\n"
        
        # Add sections
        for name, content in self.sections.items():
            markdown += f"## {name}\n\n{content}\n\n"
        
        # Add experience metrics
        markdown += "## Experience Metrics\n\n"
        markdown += f"**Overall Sentiment:** {self.sentiment}\n\n"
        markdown += f"**Engagement Level:** {self.engagement}\n\n"
        markdown += f"**Conversion Likelihood:** {self.conversion}\n\n"
        
        # Add recommendations
        markdown += "## Recommendations\n\n"
        
        for i, recommendation in enumerate(self.recommendations, 1):
            markdown += f"{i}. {recommendation}\n"
        
        return markdown

class StrategicSummary:
    """Generates strategic summaries in markdown format."""
    
    def __init__(self, persona_name: str):
        """
        Initialize with persona name.
        
        Args:
            persona_name: The name of the persona
        """
        self.persona_name = persona_name
        self.executive_summary = ""
        self.key_findings = []
        self.strengths = []
        self.weaknesses = []
        self.recommendations = []
        self.next_steps = []
    
    def set_executive_summary(self, summary: str) -> None:
        """
        Set the executive summary.
        
        Args:
            summary: The executive summary text
        """
        self.executive_summary = summary
    
    def add_key_finding(self, finding: str) -> None:
        """
        Add a key finding.
        
        Args:
            finding: The key finding text
        """
        self.key_findings.append(finding)
    
    def add_strength(self, strength: str) -> None:
        """
        Add a strength.
        
        Args:
            strength: The strength text
        """
        self.strengths.append(strength)
    
    def add_weakness(self, weakness: str) -> None:
        """
        Add a weakness.
        
        Args:
            weakness: The weakness text
        """
        self.weaknesses.append(weakness)
    
    def add_recommendation(self, recommendation: str) -> None:
        """
        Add a recommendation.
        
        Args:
            recommendation: The recommendation text
        """
        self.recommendations.append(recommendation)
    
    def add_next_step(self, next_step: str) -> None:
        """
        Add a next step.
        
        Args:
            next_step: The next step text
        """
        self.next_steps.append(next_step)
    
    def generate(self) -> str:
        """
        Generate the markdown summary.
        
        Returns:
            Markdown formatted summary
        """
        # Format the header
        markdown = f"# Strategic Brand Audit Summary for {self.persona_name}\n\n"
        
        # Add executive summary
        markdown += "## Executive Summary\n\n"
        markdown += f"{self.executive_summary}\n\n"
        
        # Add key findings
        markdown += "## Key Findings\n\n"
        
        for finding in self.key_findings:
            markdown += f"- {finding}\n"
        
        markdown += "\n"
        
        # Add strengths and weaknesses
        markdown += "## Strengths\n\n"
        
        for strength in self.strengths:
            markdown += f"- {strength}\n"
        
        markdown += "\n## Weaknesses\n\n"
        
        for weakness in self.weaknesses:
            markdown += f"- {weakness}\n"
        
        markdown += "\n"
        
        # Add recommendations
        markdown += "## Strategic Recommendations\n\n"
        
        for i, recommendation in enumerate(self.recommendations, 1):
            markdown += f"{i}. **{recommendation.split(':')[0]}**: {':'.join(recommendation.split(':')[1:])}\n"
        
        markdown += "\n"
        
        # Add next steps
        markdown += "## Next Steps\n\n"
        
        for i, next_step in enumerate(self.next_steps, 1):
            markdown += f"{i}. {next_step}\n"
        
        return markdown

def parse_ai_scorecard(markdown: str) -> Dict[str, Any]:
    """
    Parse an AI-generated hygiene scorecard.
    
    Args:
        markdown: The markdown content
        
    Returns:
        Dictionary of parsed data
    """
    data = {
        "criteria": [],
        "final_score": 0.0,
        "recommendations": []
    }
    
    try:
        # Extract final score
        final_score_match = re.search(r"\*\*Final Score:\*\*\s*([\d.]+)/10", markdown)
        if final_score_match:
            data["final_score"] = float(final_score_match.group(1))
        
        # Extract criteria scores
        criteria_pattern = r"\|\s*\*\*(.*?)\*\*\s*\|\s*([\d.]+)/10\s*\|\s*(.*?)\s*\|"
        for match in re.finditer(criteria_pattern, markdown):
            data["criteria"].append({
                "name": match.group(1),
                "score": float(match.group(2)),
                "evidence": match.group(3)
            })
        
        # Extract recommendations
        recommendations_section = re.search(r"## Recommendations\s*\n\n(.*?)(?:\n\n|$)", markdown, re.DOTALL)
        if recommendations_section:
            recommendations_text = recommendations_section.group(1)
            recommendations = re.findall(r"\d+\.\s*(.*?)(?:\n|$)", recommendations_text)
            data["recommendations"] = recommendations
        
    except Exception as e:
        logger.error(f"Error parsing AI scorecard: {str(e)}")
    
    return data

def parse_ai_experience_report(markdown: str) -> Dict[str, Any]:
    """
    Parse an AI-generated experience report.
    
    Args:
        markdown: The markdown content
        
    Returns:
        Dictionary of parsed data
    """
    data = {
        "sections": {},
        "sentiment": "Neutral",
        "engagement": "Medium",
        "conversion": "Medium",
        "recommendations": []
    }
    
    try:
        # Extract sections
        section_pattern = r"## (.*?)\n\n(.*?)(?=\n\n## |$)"
        for match in re.finditer(section_pattern, markdown, re.DOTALL):
            section_name = match.group(1)
            section_content = match.group(2).strip()
            
            if section_name != "Experience Metrics" and section_name != "Recommendations":
                data["sections"][section_name] = section_content
        
        # Extract metrics
        sentiment_match = re.search(r"\*\*Overall Sentiment:\*\*\s*(.*?)(?:\n|$)", markdown)
        if sentiment_match:
            data["sentiment"] = sentiment_match.group(1)
        
        engagement_match = re.search(r"\*\*Engagement Level:\*\*\s*(.*?)(?:\n|$)", markdown)
        if engagement_match:
            data["engagement"] = engagement_match.group(1)
        
        conversion_match = re.search(r"\*\*Conversion Likelihood:\*\*\s*(.*?)(?:\n|$)", markdown)
        if conversion_match:
            data["conversion"] = conversion_match.group(1)
        
        # Extract recommendations
        recommendations_section = re.search(r"## Recommendations\s*\n\n(.*?)(?:\n\n|$)", markdown, re.DOTALL)
        if recommendations_section:
            recommendations_text = recommendations_section.group(1)
            recommendations = re.findall(r"\d+\.\s*(.*?)(?:\n|$)", recommendations_text)
            data["recommendations"] = recommendations
        
    except Exception as e:
        logger.error(f"Error parsing AI experience report: {str(e)}")
    
    return data
