"""
Brand Audit Tool Package

STATUS: ACTIVE

This package provides a comprehensive toolkit for evaluating brand presence across digital touchpoints.
Key components include:
1. Scraping and content extraction from web pages
2. AI-powered analysis of brand positioning and messaging
3. Persona-specific experience evaluation
4. Structured reporting and visualization
5. Multi-persona comparison and insights

The tool supports both command-line operation and dashboard-based visualization,
enabling detailed brand audits from multiple persona perspectives.
"""

__version__ = "1.2.0"
__author__ = "Sopra Steria Digital Experience Team"
__email__ = "digital.experience@soprasteria.com"
__license__ = "Proprietary"

# Public helper
def get_version() -> str:
    """Return the current package version."""
    return __version__

# Import key components for easier access
from .ai_interface import AIInterface
from .methodology_parser import MethodologyParser
from .persona_parser import PersonaParser
from .tier_classifier import TierClassifier
from .strategic_summary_generator import StrategicSummaryGenerator
from .multi_persona_packager import MultiPersonaPackager
from .main import BrandAuditTool
