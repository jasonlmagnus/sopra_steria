"""
PersonaParser - Extract structured attributes from persona markdown files.
This replaces hardcoded persona assumptions throughout the system.
"""
import re
from dataclasses import dataclass
from typing import List
import logging

@dataclass
class PersonaAttributes:
    name: str
    role: str
    industry: str
    geographic_scope: str
    key_priorities: List[str]
    business_context: str
    communication_style: str
    organization_type: str
    decision_factors: List[str]
    pain_points: List[str]

class PersonaParser:
    def __init__(self):
        self.content = ""
    
    def extract_attributes(self, persona_file_path: str) -> PersonaAttributes:
        """Extract structured attributes from persona markdown file."""
        logging.info(f"Parsing persona file: {persona_file_path}")
        
        with open(persona_file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        
        return PersonaAttributes(
            name=self._extract_name(),
            role=self._extract_role(),
            industry=self._extract_industry(),
            geographic_scope=self._extract_geographic_scope(),
            key_priorities=self._extract_priorities(),
            business_context=self._extract_business_context(),
            communication_style=self._extract_communication_style(),
            organization_type=self._extract_organization_type(),
            decision_factors=self._extract_decision_factors(),
            pain_points=self._extract_pain_points()
        )
    
    def extract_attributes_from_content(self, persona_content: str, log_parsing: bool = True) -> PersonaAttributes:
        """Extract structured attributes from persona content string."""
        if log_parsing:
            logging.info("Parsing persona content...")
        
        self.content = persona_content
        
        return PersonaAttributes(
            name=self._extract_name(),
            role=self._extract_role(),
            industry=self._extract_industry(),
            geographic_scope=self._extract_geographic_scope(),
            key_priorities=self._extract_priorities(),
            business_context=self._extract_business_context(),
            communication_style=self._extract_communication_style(),
            organization_type=self._extract_organization_type(),
            decision_factors=self._extract_decision_factors(),
            pain_points=self._extract_pain_points()
        )
    
    def _extract_name(self) -> str:
        """Extract persona name from file header or content."""
        # Look for "Persona Brief:" pattern
        brief_match = re.search(r'Persona Brief:\s*(.+)', self.content)
        if brief_match:
            return brief_match.group(1).strip()
        
        # Look for title patterns
        title_match = re.search(r'^#\s+(.+)', self.content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        return "Unknown Persona"
    
    def _extract_role(self) -> str:
        """Extract the primary role/title."""
        # Look for Role: pattern in structured content
        role_match = re.search(r'Role:\s*(.+?)(?:\n|$)', self.content, re.IGNORECASE)
        if role_match:
            return role_match.group(1).strip()
        
        # Look for C-suite patterns in persona brief
        if 'C-suite Executive' in self.content:
            return 'C-suite Executive'
        elif 'Chief Information Officer' in self.content or 'CIO' in self.content:
            return 'Chief Information Officer'
        elif 'Chief Digital Officer' in self.content or 'CDO' in self.content:
            return 'Chief Digital Officer'
        elif 'Finance Leader' in self.content:
            return 'Finance Leader'
        
        return "Senior Executive"
    
    def _extract_industry(self) -> str:
        """Extract industry focus."""
        if 'public sector' in self.content.lower():
            return 'Public Sector'
        elif 'financial services' in self.content.lower():
            return 'Financial Services'
        elif 'healthcare' in self.content.lower():
            return 'Healthcare'
        elif 'retail' in self.content.lower():
            return 'Retail'
        else:
            return 'Cross-Industry'
    
    def _extract_geographic_scope(self) -> str:
        """Extract geographic scope."""
        if 'BENELUX' in self.content or 'Benelux' in self.content:
            return 'BENELUX'
        elif 'Europe' in self.content:
            return 'Europe'
        elif 'Global' in self.content:
            return 'Global'
        else:
            return 'Regional'
    
    def _extract_priorities(self) -> List[str]:
        """Extract key priorities from structured content."""
        priorities = []
        
        # Look for "Key Responsibilities:" section
        resp_match = re.search(r'Key Responsibilities:\s*(.+?)(?:\n\s*Content Implication:|\n\s*\d+\.)', self.content, re.DOTALL)
        if resp_match:
            resp_text = resp_match.group(1)
            # Extract bullet points or numbered items
            items = re.findall(r'(?:•|\*|-|\d+\.)\s*(.+?)(?:\n|$)', resp_text)
            for item in items[:5]:  # Limit to top 5
                # Clean up and extract key themes
                clean_item = re.sub(r'^[^:]+:\s*', '', item.strip())
                if len(clean_item) > 20:  # Only meaningful priorities
                    priorities.append(clean_item[:80] + "..." if len(clean_item) > 80 else clean_item)
        
        # If no structured priorities found, extract from content
        if not priorities:
            priority_keywords = [
                'digital transformation', 'operational efficiency', 'regulatory compliance',
                'cost optimization', 'security', 'innovation', 'business model reinvention',
                'risk management', 'competitive advantage', 'enterprise viability'
            ]
            
            for keyword in priority_keywords:
                if keyword in self.content.lower():
                    priorities.append(keyword.title())
        
        return priorities[:5] if priorities else ['Strategic Growth', 'Operational Excellence', 'Risk Management']
    
    def _extract_business_context(self) -> str:
        """Extract business context description."""
        # Look for "User Goal Statement:" section
        goal_match = re.search(r'User Goal Statement:\s*(.+?)(?:\n\s*\n|\n\s*[A-Z])', self.content, re.DOTALL)
        if goal_match:
            return goal_match.group(1).strip()
        
        # Fallback to generic context
        role = self._extract_role()
        industry = self._extract_industry()
        scope = self._extract_geographic_scope()
        
        return f"a {scope} {role.lower()} focused on strategic technology decisions and business transformation"
    
    def _extract_communication_style(self) -> str:
        """Determine communication style based on role."""
        role = self._extract_role().lower()
        
        if 'chief' in role or 'ceo' in role:
            return 'strategic, executive-level, business-focused'
        elif 'finance' in role:
            return 'analytical, risk-aware, ROI-focused'
        elif 'digital' in role or 'cdo' in role:
            return 'innovative, technology-focused, change-oriented'
        elif 'operations' in role:
            return 'process-focused, efficiency-driven, practical'
        else:
            return 'professional, analytical, solution-oriented'
    
    def _extract_organization_type(self) -> str:
        """Extract organization type."""
        if 'public sector' in self.content.lower():
            return 'Public Sector'
        elif 'enterprise' in self.content.lower():
            return 'Enterprise'
        elif 'government' in self.content.lower():
            return 'Government'
        else:
            return 'Corporate'
    
    def _extract_decision_factors(self) -> List[str]:
        """Extract key decision factors."""
        factors = []
        
        factor_keywords = [
            'ROI',
            'security',
            'compliance',
            'scalability',
            'reliability',
            'cost',
            'implementation time',
            'vendor reputation',
            'support quality'
        ]
        
        for keyword in factor_keywords:
            if keyword.lower() in self.content.lower():
                factors.append(keyword.title())
        
        if not factors:
            factors = ['Cost Effectiveness', 'Implementation Risk', 'Strategic Fit']
        
        return factors[:5]
    
    def _extract_pain_points(self) -> List[str]:
        """Extract key pain points from structured content."""
        pain_points = []
        
        # Look for "Pain Points and Challenges" or "Frustrations:" section
        pain_match = re.search(r'(?:Pain Points and Challenges|Frustrations:)\s*(.+?)(?:\n\s*[A-Z][^:]*:|\n\s*\d+\.)', self.content, re.DOTALL)
        if pain_match:
            pain_text = pain_match.group(1)
            # Extract bullet points or listed items
            items = re.findall(r'(?:•|\*|-|The)\s*(.+?)(?:\n|$)', pain_text)
            for item in items[:5]:  # Limit to top 5
                clean_item = item.strip()
                if len(clean_item) > 15:  # Only meaningful pain points
                    pain_points.append(clean_item[:80] + "..." if len(clean_item) > 80 else clean_item)
        
        # Fallback to common pain points if none found
        if not pain_points:
            pain_keywords = [
                'legacy systems', 'budget constraints', 'regulatory pressure',
                'talent shortages', 'cybersecurity threats', 'supply chain disruptions',
                'business model obsolescence', 'compliance complexity'
            ]
            
            for keyword in pain_keywords:
                if keyword in self.content.lower():
                    pain_points.append(keyword.title())
        
        return pain_points[:5] if pain_points else ['Resource Constraints', 'Technology Complexity', 'Market Volatility'] 