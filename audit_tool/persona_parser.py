"""
Persona Parser for Brand Audit Tool

STATUS: ACTIVE

This module provides functionality to parse and extract persona information:
1. Loads and parses persona definitions from markdown files
2. Extracts structured attributes like demographics, goals, and pain points
3. Creates persona objects for use in audit evaluations
4. Supports persona-specific analysis and reporting
5. Enables consistent persona application across the audit process

The parser ensures that persona information is consistently structured and
available throughout the audit workflow, enabling persona-specific evaluations.
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class Persona:
    """Data class representing a persona."""

    name: str
    role: str
    company: str = ""
    industry: str = ""
    geographic_scope: str = ""
    age: str = ""
    location: str = ""
    goals: List[str] = None
    challenges: List[str] = None
    pain_points: List[str] = None
    key_responsibilities: List[str] = None
    key_priorities: List[str] = None
    motivations: List[str] = None
    tech_comfort: str = ""
    brand_awareness: str = ""
    decision_factors: List[str] = None
    information_sources: List[str] = None
    quote: str = ""
    bio: str = ""
    
    def __post_init__(self):
        """Initialize list attributes if None."""
        if self.goals is None:
            self.goals = []
        if self.challenges is None:
            self.challenges = []
        if self.pain_points is None:
            self.pain_points = []
        if self.key_responsibilities is None:
            self.key_responsibilities = []
        if self.key_priorities is None:
            self.key_priorities = []
        if self.motivations is None:
            self.motivations = []
        if self.decision_factors is None:
            self.decision_factors = []
        if self.information_sources is None:
            self.information_sources = []

class PersonaParser:
    """Parses persona information from markdown files."""

    def __init__(self):
        """Initialize the persona parser."""
        logger.info("Persona parser initialized")

    def extract_attributes(self, file_path: str) -> Persona:
        """Wrapper for backward compatibility."""
        return self.extract_attributes_from_file(file_path)
    
    def extract_attributes_from_file(self, file_path: str) -> Persona:
        """
        Extract persona attributes from a markdown file.
        
        Args:
            file_path: Path to the persona markdown file
            
        Returns:
            Persona object with extracted attributes
        """
        logger.info(f"Extracting persona attributes from {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.extract_attributes_from_content(content)
            
        except Exception as e:
            logger.error(f"Error extracting persona attributes from {file_path}: {str(e)}")
            # Return a minimal persona with just a name based on the filename
            import os
            name = os.path.basename(file_path).replace('.md', '')
            return Persona(name=name, role="Unknown")
    
    def extract_attributes_from_content(self, content: str) -> Persona:
        """
        Extract persona attributes from markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            Persona object with extracted attributes
        """
        # Extract name from heading or fallback patterns
        name_match = re.search(r'^#\s+(.+?)(?:\n|$)', content)
        if not name_match:
            name_match = re.search(r'(?:^|\n)Persona\s+Brief:\s*(.+)', content, re.IGNORECASE)
        if not name_match:
            name_match = re.search(r'(?:^|\n)Name:\s*(.+)', content, re.IGNORECASE)
        name = name_match.group(1).strip() if name_match else "Unknown Persona"
        
        # Extract role
        role_match = re.search(r'(?:^|\n)##\s+Role\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not role_match:
            role_match = re.search(r'(?:^|\n)Role:\s*(.+)', content, re.IGNORECASE)
        role = role_match.group(1).strip() if role_match else ""
        
        # If no explicit role section, try to extract from title or first paragraph
        if not role:
            role_from_title = re.search(r'^#\s+.+?\((.*?)\)', content)
            if role_from_title:
                role = role_from_title.group(1)
            else:
                first_para = re.search(r'^#.+?\n\n(.+?)(?:\n\n|$)', content, re.DOTALL)
                if first_para:
                    role = first_para.group(1)[:50]  # Limit to 50 chars
        
        # Create persona with required fields
        persona = Persona(name=name, role=role)
        
        # Extract company
        company_match = re.search(r'(?:^|\n)##\s+Company\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not company_match:
            company_match = re.search(r'(?:^|\n)Company:\s*(.+)', content, re.IGNORECASE)
        if company_match:
            persona.company = company_match.group(1).strip()
        
        # Extract industry
        industry_match = re.search(r'(?:^|\n)##\s+Industry\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not industry_match:
            industry_match = re.search(r'(?:^|\n)Industry:\s*(.+)', content, re.IGNORECASE)
        if industry_match:
            persona.industry = industry_match.group(1).strip()

        # Extract geographic scope
        geo_match = re.search(r'(?:^|\n)##\s+Geographic Scope\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not geo_match:
            geo_match = re.search(r'(?:^|\n)Geographic Scope:\s*(.+)', content, re.IGNORECASE)
        if geo_match:
            persona.geographic_scope = geo_match.group(1).strip()
        
        # Extract age
        age_match = re.search(r'(?:^|\n)##\s+Age\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not age_match:
            age_match = re.search(r'(?:^|\n)Age:\s*(.+)', content, re.IGNORECASE)
        if age_match:
            persona.age = age_match.group(1).strip()
        
        # Extract location
        location_match = re.search(r'(?:^|\n)##\s+Location\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not location_match:
            location_match = re.search(r'(?:^|\n)Location:\s*(.+)', content, re.IGNORECASE)
        if location_match:
            persona.location = location_match.group(1).strip()
        
        # Extract goals
        goals_match = re.search(r'(?:^|\n)##\s+Goals\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not goals_match:
            goals_match = re.search(r'(?:^|\n)Goals:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if goals_match:
            goals_text = goals_match.group(1)
            persona.goals = self._extract_list_items(goals_text)
        
        # Extract challenges
        challenges_match = re.search(r'(?:^|\n)##\s+Challenges\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not challenges_match:
            challenges_match = re.search(r'(?:^|\n)Challenges:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if challenges_match:
            challenges_text = challenges_match.group(1)
            persona.challenges = self._extract_list_items(challenges_text)
        
        # Extract pain points
        pain_points_match = re.search(r'(?:^|\n)##\s+Pain Points\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not pain_points_match:
            pain_points_match = re.search(r'(?:^|\n)Pain Points:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if pain_points_match:
            pain_points_text = pain_points_match.group(1)
            persona.pain_points = self._extract_list_items(pain_points_text)
        
        # Extract motivations
        motivations_match = re.search(r'(?:^|\n)##\s+Motivations\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not motivations_match:
            motivations_match = re.search(r'(?:^|\n)Motivations:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if motivations_match:
            motivations_text = motivations_match.group(1)
            persona.motivations = self._extract_list_items(motivations_text)
        
        # Extract tech comfort
        tech_comfort_match = re.search(r'(?:^|\n)##\s+Tech(?:nology)? Comfort\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not tech_comfort_match:
            tech_comfort_match = re.search(r'(?:^|\n)Tech(?:nology)? Comfort:\s*(.+)', content, re.IGNORECASE)
        if tech_comfort_match:
            persona.tech_comfort = tech_comfort_match.group(1)
        
        # Extract brand awareness
        brand_awareness_match = re.search(r'(?:^|\n)##\s+Brand Awareness\s*\n\s*(.+?)(?:\n|$)', content, re.IGNORECASE)
        if not brand_awareness_match:
            brand_awareness_match = re.search(r'(?:^|\n)Brand Awareness:\s*(.+)', content, re.IGNORECASE)
        if brand_awareness_match:
            persona.brand_awareness = brand_awareness_match.group(1)
        
        # Extract decision factors
        decision_factors_match = re.search(r'(?:^|\n)##\s+Decision Factors\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not decision_factors_match:
            decision_factors_match = re.search(r'(?:^|\n)Decision Factors:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if decision_factors_match:
            decision_factors_text = decision_factors_match.group(1)
            persona.decision_factors = self._extract_list_items(decision_factors_text)
        
        # Extract information sources
        info_sources_match = re.search(r'(?:^|\n)##\s+Information Sources\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not info_sources_match:
            info_sources_match = re.search(r'(?:^|\n)Information Sources:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if info_sources_match:
            info_sources_text = info_sources_match.group(1)
            persona.information_sources = self._extract_list_items(info_sources_text)
        
        # Extract quote
        quote_match = re.search(r'(?:^|\n)##\s+Quote\s*\n\s*(?:>)?\s*"?(.+?)"?(?:\n|$)', content, re.IGNORECASE)
        if not quote_match:
            quote_match = re.search(r'(?:^|\n)Quote:\s*(?:>)?\s*"?(.+?)"?(?:\n|$)', content, re.IGNORECASE)
        if quote_match:
            persona.quote = quote_match.group(1)
        
        # Extract bio
        bio_match = re.search(r'(?:^|\n)##\s+Bio\s*\n\s*(.+?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not bio_match:
            bio_match = re.search(r'(?:^|\n)Bio:\s*(.+)', content, re.IGNORECASE)
        if bio_match:
            persona.bio = bio_match.group(1).strip()

        # Extract key responsibilities
        resp_match = re.search(r'(?:^|\n)##\s+Key Responsibilities\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not resp_match:
            resp_match = re.search(r'(?:^|\n)Key Responsibilities:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if resp_match:
            persona.key_responsibilities = self._extract_list_items(resp_match.group(1))

        # Extract key priorities
        priorities_match = re.search(r'(?:^|\n)##\s+Key Priorities\s*\n(.*?)(?:\n\n|\n##|$)', content, re.DOTALL | re.IGNORECASE)
        if not priorities_match:
            priorities_match = re.search(r'(?:^|\n)Key Priorities:\s*\n(.*?)(?:\n\n|\n[A-Z][^:]+:|$)', content, re.DOTALL)
        if priorities_match:
            persona.key_priorities = self._extract_list_items(priorities_match.group(1))
        
        logger.info(f"Extracted persona: {persona.name}")
        return persona
    
    def _extract_list_items(self, text: str) -> List[str]:
        """
        Extract list items from markdown text.
        
        Args:
            text: Markdown text containing list items
            
        Returns:
            List of extracted items
        """
        items = []
        
        # Extract bullet points
        bullet_matches = re.finditer(r'(?:^|\n)\s*[-*]\s*(.+?)(?:\n|$)', text)
        for match in bullet_matches:
            items.append(match.group(1).strip())
        
        # If no bullet points found, try numbered lists
        if not items:
            numbered_matches = re.finditer(r'(?:^|\n)\s*\d+\.\s*(.+?)(?:\n|$)', text)
            for match in numbered_matches:
                items.append(match.group(1).strip())
        
        # If still no items found, split by newlines
        if not items and text.strip():
            items = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        return items
    
    def persona_to_markdown(self, persona: Persona) -> str:
        """
        Convert a persona object to markdown.
        
        Args:
            persona: The persona object
            
        Returns:
            Markdown representation of the persona
        """
        markdown = f"# {persona.name}\n\n"
        
        if persona.role:
            markdown += f"## Role\n{persona.role}\n\n"
        
        if persona.company:
            markdown += f"## Company\n{persona.company}\n\n"
        
        if persona.industry:
            markdown += f"## Industry\n{persona.industry}\n\n"

        if persona.geographic_scope:
            markdown += f"## Geographic Scope\n{persona.geographic_scope}\n\n"
        
        if persona.age:
            markdown += f"## Age\n{persona.age}\n\n"
        
        if persona.location:
            markdown += f"## Location\n{persona.location}\n\n"
        
        if persona.bio:
            markdown += f"## Bio\n{persona.bio}\n\n"

        if persona.key_responsibilities:
            markdown += "## Key Responsibilities\n"
            for item in persona.key_responsibilities:
                markdown += f"- {item}\n"
            markdown += "\n"
        
        if persona.goals:
            markdown += "## Goals\n"
            for goal in persona.goals:
                markdown += f"- {goal}\n"
            markdown += "\n"
        
        if persona.challenges:
            markdown += "## Challenges\n"
            for challenge in persona.challenges:
                markdown += f"- {challenge}\n"
            markdown += "\n"
        
        if persona.pain_points:
            markdown += "## Pain Points\n"
            for pain_point in persona.pain_points:
                markdown += f"- {pain_point}\n"
            markdown += "\n"

        if persona.key_priorities:
            markdown += "## Key Priorities\n"
            for priority in persona.key_priorities:
                markdown += f"- {priority}\n"
            markdown += "\n"
        
        if persona.motivations:
            markdown += "## Motivations\n"
            for motivation in persona.motivations:
                markdown += f"- {motivation}\n"
            markdown += "\n"
        
        if persona.tech_comfort:
            markdown += f"## Technology Comfort\n{persona.tech_comfort}\n\n"
        
        if persona.brand_awareness:
            markdown += f"## Brand Awareness\n{persona.brand_awareness}\n\n"
        
        if persona.decision_factors:
            markdown += "## Decision Factors\n"
            for factor in persona.decision_factors:
                markdown += f"- {factor}\n"
            markdown += "\n"
        
        if persona.information_sources:
            markdown += "## Information Sources\n"
            for source in persona.information_sources:
                markdown += f"- {source}\n"
            markdown += "\n"
        
        if persona.quote:
            markdown += f"## Quote\n> \"{persona.quote}\"\n\n"
        
        return markdown
