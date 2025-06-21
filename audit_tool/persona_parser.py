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
    
    def _extract_name(self) -> str:
        """Extract persona name from file header or content."""
        # Look for title patterns
        title_match = re.search(r'^#\s+(.+)', self.content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # Look for "Persona Report:" pattern
        persona_match = re.search(r'Persona Report:\s*(.+)', self.content)
        if persona_match:
            return persona_match.group(1).strip()
        
        return "Unknown Persona"
    
    def _extract_role(self) -> str:
        """Extract the primary role/title."""
        # Look for role patterns in content
        role_patterns = [
            r'Chief\s+\w+\s+Officer',
            r'Senior\s+\w+\s+Executive',
            r'IT\s+Director',
            r'Finance\s+Leader',
            r'Operations\s+Executive'
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Fallback to generic extraction
        if 'CIO' in self.content:
            return 'Chief Information Officer'
        elif 'CDO' in self.content:
            return 'Chief Digital Officer'
        elif 'finance' in self.content.lower():
            return 'Finance Leader'
        elif 'IT' in self.content:
            return 'IT Executive'
        
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
        """Extract key priorities from content."""
        priorities = []
        
        # Common priority patterns
        priority_keywords = [
            'digital transformation',
            'operational efficiency',
            'regulatory compliance',
            'cost optimization',
            'security',
            'innovation',
            'customer experience',
            'data governance',
            'risk management',
            'competitive advantage'
        ]
        
        for keyword in priority_keywords:
            if keyword in self.content.lower():
                priorities.append(keyword.title())
        
        # If no specific priorities found, add generic ones
        if not priorities:
            priorities = ['Operational Excellence', 'Strategic Growth', 'Risk Management']
        
        return priorities[:5]  # Limit to top 5
    
    def _extract_business_context(self) -> str:
        """Generate business context description."""
        role = self._extract_role()
        industry = self._extract_industry()
        scope = self._extract_geographic_scope()
        
        if 'BENELUX' in scope and 'executive' in role.lower():
            return f"a {scope} {role.lower()} evaluating strategic partnerships and digital transformation initiatives"
        elif 'finance' in role.lower():
            return f"a {industry} {role.lower()} focused on cost optimization and regulatory compliance"
        elif 'digital' in role.lower() or 'CDO' in role:
            return f"a {role} driving organizational digital transformation and innovation"
        else:
            return f"a {industry} {role.lower()} responsible for strategic technology decisions"
    
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
        """Extract key pain points."""
        pain_points = []
        
        pain_keywords = [
            'legacy systems',
            'budget constraints',
            'regulatory pressure',
            'skill gaps',
            'digital transformation',
            'operational inefficiency',
            'security threats',
            'compliance burden'
        ]
        
        for keyword in pain_keywords:
            if keyword.lower() in self.content.lower():
                pain_points.append(keyword.title())
        
        if not pain_points:
            pain_points = ['Resource Constraints', 'Technology Complexity', 'Change Management']
        
        return pain_points[:5] 