#!/usr/bin/env python3
"""
Test script for the Sopra Steria Brand Audit Tool
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path so we can import audit_tool modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_yaml_configuration():
    """Test YAML methodology loading"""
    print("🧪 Testing YAML Configuration...")
    
    try:
        from audit_tool.methodology_parser import MethodologyParser
        
        parser = MethodologyParser()
        methodology = parser.parse()
        
        assert methodology.metadata['name'] == "Sopra Steria Brand Audit Methodology"
        assert methodology.metadata['version'] == "2.0"
        assert len(methodology.tiers) == 3
        assert len(methodology.offsite_channels) == 3
        
        print("✅ YAML Configuration test passed")
        return True
        
    except Exception as e:
        print(f"❌ YAML Configuration test failed: {e}")
        return False

def test_persona_parsing():
    """Test persona parsing functionality"""
    print("🧪 Testing Persona Parsing...")
    
    try:
        from audit_tool.persona_parser import PersonaParser
        
        parser = PersonaParser()
        
        # Test with the simple persona file
        persona_file = Path(__file__).parent / "test_persona_simple.md"
        persona = parser.extract_attributes(str(persona_file))
        
        assert persona.name == "Test CEO"
        assert persona.role == "Chief Executive Officer"
        assert persona.industry == "Financial Services"
        assert len(persona.key_priorities) > 0
        assert len(persona.pain_points) > 0
        
        print("✅ Persona Parsing test passed")
        return True
        
    except Exception as e:
        print(f"❌ Persona Parsing test failed: {e}")
        return False

def test_scraper():
    """Test web scraping functionality"""
    print("🧪 Testing Web Scraper...")
    
    try:
        from audit_tool.scraper import Scraper
        
        scraper = Scraper()
        
        # Test with a simple URL
        page_data = scraper.fetch_page('https://www.soprasteria.com')
        
        assert page_data is not None
        assert not page_data.is_404
        assert len(page_data.raw_text) > 100
        assert 'objective_findings' in page_data.__dict__
        
        print("✅ Web Scraper test passed")
        return True
        
    except Exception as e:
        print(f"❌ Web Scraper test failed: {e}")
        return False

def test_ai_interface():
    """Test AI interface functionality"""
    print("🧪 Testing AI Interface...")
    
    try:
        from audit_tool.ai_interface import AIInterface
        
        ai_interface = AIInterface()
        
        # Test template loading
        template = ai_interface._load_prompt_template("narrative_analysis")
        assert len(template) > 100
        assert "{persona_name}" in template
        assert "persona*role" not in template  # Ensure syntax error is fixed
        
        system_msg = ai_interface._get_system_message("narrative_analysis")
        assert len(system_msg) > 10
        
        print("✅ AI Interface test passed")
        return True
        
    except Exception as e:
        print(f"❌ AI Interface test failed: {e}")
        return False

def test_full_audit_pipeline():
    """Test the complete audit pipeline"""
    print("🧪 Testing Full Audit Pipeline...")
    
    try:
        # Create temporary output directory
        with tempfile.TemporaryDirectory() as temp_dir:
            from audit_tool.main import run_audit
            
            test_dir = Path(__file__).parent
            urls_file = test_dir / "test_single_url.txt"
            persona_file = test_dir / "test_persona_simple.md"
            
            # Run audit with no summary to speed up test
            results = run_audit(
                urls_file=str(urls_file),
                persona_file=str(persona_file),
                output_dir=temp_dir,
                generate_summary=False,
                verbose=False
            )
            
            assert len(results) == 1
            assert results[0]['status'] == 'success'
            assert results[0]['hygiene_score'] > 0
            
            # Check that output files were created
            output_files = list(Path(temp_dir).glob("*.md"))
            assert len(output_files) >= 2  # At least hygiene and experience reports
            
        print("✅ Full Audit Pipeline test passed")
        return True
        
    except Exception as e:
        print(f"❌ Full Audit Pipeline test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Sopra Steria Brand Audit Tool Tests")
    print("=" * 50)
    
    tests = [
        test_yaml_configuration,
        test_persona_parsing,
        test_scraper,
        test_ai_interface,
        test_full_audit_pipeline
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 