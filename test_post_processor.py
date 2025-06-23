#!/usr/bin/env python3
"""
Test script for the Audit Post-Processor
Tests the complete pipeline with existing audit data
"""

import sys
import os
import logging
from pathlib import Path

# Add audit_tool to path
sys.path.append(str(Path(__file__).parent / "audit_tool"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_audit_post_processor():
    """Test the audit post-processor with existing data"""
    
    try:
        # Import after path setup
        from audit_tool.audit_post_processor import AuditPostProcessor
        
        print("=== AUDIT POST-PROCESSOR TEST ===")
        print("Testing with: The_BENELUX_Technology_Innovation_Leader")
        print()
        
        # Initialize processor
        processor = AuditPostProcessor('The_BENELUX_Technology_Innovation_Leader')
        
        print(f"Persona: {processor.persona_name}")
        print(f"Audit Output Dir: {processor.audit_output_dir}")
        print(f"Temp Dir: {processor.temp_dir}")
        print()
        
        # Step 1: Initial status check
        print("1. INITIAL STATUS CHECK:")
        status = processor.get_processing_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        print()
        
        # Step 2: Validate audit output
        print("2. VALIDATING AUDIT OUTPUT:")
        is_valid = processor.validate_audit_output()
        print(f"   ✓ Valid audit output: {is_valid}")
        
        if not is_valid:
            print("   ❌ Cannot proceed - no valid audit output found")
            return False
        print()
        
        # Step 3: Test URL extraction
        print("3. EXTRACTING URLs FROM AUDIT FILES:")
        urls = processor._extract_urls_from_audit_files()
        print(f"   ✓ Extracted {len(urls)} URLs from audit files")
        for i, url in enumerate(urls[:3]):  # Show first 3
            print(f"   {i+1}. {url}")
        if len(urls) > 3:
            print(f"   ... and {len(urls)-3} more")
        print()
        
        # Step 4: Test tier classification
        print("4. TESTING TIER CLASSIFICATION:")
        try:
            classifications = processor.classify_page_tiers()
            print(f"   ✓ Classified {len(classifications)} URLs into tiers")
            
            # Show tier distribution
            tier_counts = {}
            for url, info in classifications.items():
                tier = info['tier']
                tier_counts[tier] = tier_counts.get(tier, 0) + 1
            
            print("   Tier Distribution:")
            for tier in sorted(tier_counts.keys()):
                print(f"     Tier {tier}: {tier_counts[tier]} URLs")
            
            # Show examples
            print("   Examples:")
            for url, tier_info in list(classifications.items())[:3]:
                print(f"     {url[:60]}...")
                print(f"       -> Tier {tier_info['tier']} ({tier_info['tier_name']}) weight={tier_info['tier_weight']}")
            
        except Exception as e:
            print(f"   ❌ Tier classification failed: {e}")
            return False
        print()
        
        # Step 5: Check if data already exists
        print("5. CHECKING EXISTING PROCESSED DATA:")
        audit_dir = Path("audit_outputs") / "The_BENELUX_Technology_Innovation_Leader"
        existing_files = {
            'CSV files': list(audit_dir.glob("*.csv")),
            'Parquet files': list(audit_dir.glob("*.parquet")),
            'Strategic Summary': list(audit_dir.glob("Strategic_Summary.md"))
        }
        
        for file_type, files in existing_files.items():
            print(f"   {file_type}: {len(files)} found")
            for file in files[:2]:  # Show first 2
                print(f"     - {file.name}")
        print()
        
        # Step 6: Final status
        print("6. FINAL STATUS:")
        final_status = processor.get_processing_status()
        print(f"   ✓ Audit files found: {final_status['audit_files_found']}")
        print(f"   ✓ Tier classifications: {final_status['tier_classifications_count']}")
        print(f"   ✓ Ready for processing: {len(processor.tier_classifications) > 0}")
        
        print()
        print("=== TEST COMPLETED SUCCESSFULLY ===")
        print("The audit post-processor is working correctly!")
        print()
        print("Next steps:")
        print("1. Run: processor.process_audit_results() - to process the audit")
        print("2. Run: processor.add_to_database() - to add to unified database")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_audit_post_processor()
    sys.exit(0 if success else 1) 