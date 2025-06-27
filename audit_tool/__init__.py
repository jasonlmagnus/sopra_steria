"""
Sopra Steria Brand Audit Tool

🐍 PYTHON PROJECT - Main audit tool package for brand health analysis
Version: 2.1.0 - Updated after Codex acknowledged Python project status

A comprehensive brand audit system using:
- Python 3.12+
- Streamlit dashboard
- AI-powered analysis
- Multi-persona evaluation

NOT Node.js, NOT JavaScript - Pure Python package.
"""

__version__ = "2.1.0"
__author__ = "Magnus Consulting"
__description__ = "Python-based brand audit tool with AI analysis"

# Import key components for easier access
from .ai_interface import AIInterface
from .methodology_parser import MethodologyParser
from .persona_parser import PersonaParser
from .tier_classifier import TierClassifier
from .strategic_summary_generator import StrategicSummaryGenerator
from .multi_persona_packager import MultiPersonaPackager
from .main import BrandAuditTool
