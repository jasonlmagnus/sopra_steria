#!/usr/bin/env python3
"""
Test HTML Report Generator
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path to access audit_tool modules
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from audit_tool.html_report_generator import HTMLReportGenerator
    
    # Test basic initialization
    logger.info("Testing HTMLReportGenerator initialization...")
    generator = HTMLReportGenerator()
    logger.info("✅ Generator initialized successfully")
    
    # Test report generation
    persona_name = "The Technical Influencer"
    output_path = "test_report.html"
    logger.info(f"Testing report generation for {persona_name} to {output_path}...")
    
    try:
        report_path = generator.generate_report(persona_name, output_path)
        logger.info(f"✅ Report generated successfully: {report_path}")
        
    except Exception as e:
        logger.error(f"❌ Error in data processing or report generation: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}") 