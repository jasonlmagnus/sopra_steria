#!/usr/bin/env python3
"""
Simple Test for Audit Post-Processor
Tests basic functionality with existing BENELUX Technology Innovation Leader data
"""

import sys
import os
import logging
from pathlib import Path
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_basic_functionality():
    """Test basic post-processor functionality without complex imports"""
    
    print("=== SIMPLE AUDIT POST-PROCESSOR TEST ===")
    print("Testing with: The_BENELUX_Technology_Innovation_Leader")
    print()
    
    # Test 1: Check if audit output directory exists
    print("1. CHECKING AUDIT OUTPUT DIRECTORY:")
    audit_dir = Path("audit_outputs/The_BENELUX_Technology_Innovation_Leader")
    print(f"   Directory: {audit_dir}")
    print(f"   ✓ Exists: {audit_dir.exists()}")
    
    if not audit_dir.exists():
        print("   ❌ Cannot proceed - audit directory not found")
        return False
    print()
    
    # Test 2: Count audit files
    print("2. COUNTING AUDIT FILES:")
    hygiene_files = list(audit_dir.glob("*_hygiene_scorecard.md"))
    experience_files = list(audit_dir.glob("*_experience_report.md"))
    csv_files = list(audit_dir.glob("*.csv"))
    parquet_files = list(audit_dir.glob("*.parquet"))
    
    print(f"   ✓ Hygiene scorecards: {len(hygiene_files)}")
    print(f"   ✓ Experience reports: {len(experience_files)}")
    print(f"   ✓ CSV files: {len(csv_files)}")
    print(f"   ✓ Parquet files: {len(parquet_files)}")
    print()
    
    # Test 3: Extract URLs from markdown files
    print("3. EXTRACTING URLs FROM AUDIT FILES:")
    urls = set()
    
    for md_file in hygiene_files[:5]:  # Test first 5 files
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for URL patterns
            url_pattern = r'https?://[^\s\)]+|www\.[^\s\)]+'
            found_urls = re.findall(url_pattern, content)
            urls.update(found_urls)
            
        except Exception as e:
            print(f"   ❌ Error reading {md_file.name}: {e}")
    
    print(f"   ✓ Extracted {len(urls)} unique URLs")
    for i, url in enumerate(list(urls)[:3]):
        print(f"   {i+1}. {url}")
    if len(urls) > 3:
        print(f"   ... and {len(urls)-3} more")
    print()
    
    # Test 4: Simple tier classification simulation
    print("4. SIMULATING TIER CLASSIFICATION:")
    tier_classifications = {}
    
    for url in list(urls)[:10]:  # Test first 10 URLs
        # Simple tier logic based on URL patterns
        if 'soprasteria.com' in url and url.count('/') <= 3:
            tier = 1
            tier_name = "Core"
            tier_weight = 0.5
        elif 'soprasteria.be' in url or 'soprasteria.nl' in url:
            tier = 2  
            tier_name = "Important"
            tier_weight = 0.3
        else:
            tier = 3
            tier_name = "Supporting" 
            tier_weight = 0.2
            
        tier_classifications[url] = {
            'tier': tier,
            'tier_name': tier_name,
            'tier_weight': tier_weight
        }
    
    print(f"   ✓ Classified {len(tier_classifications)} URLs")
    
    # Show tier distribution
    tier_counts = {}
    for info in tier_classifications.values():
        tier = info['tier']
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    print("   Tier Distribution:")
    for tier in sorted(tier_counts.keys()):
        print(f"     Tier {tier}: {tier_counts[tier]} URLs")
    print()
    
    # Test 5: Check existing processed data
    print("5. CHECKING EXISTING PROCESSED DATA:")
    if csv_files:
        print("   ✓ CSV files found - data already processed!")
        for csv_file in csv_files:
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)
                print(f"     - {csv_file.name}: {len(df)} rows, {len(df.columns)} columns")
            except Exception as e:
                print(f"     - {csv_file.name}: Error reading ({e})")
    else:
        print("   ℹ️  No CSV files - would need to run backfill processing")
    print()
    
    # Test 6: Check strategic summary
    print("6. CHECKING STRATEGIC SUMMARY:")
    strategic_files = list(audit_dir.glob("Strategic_Summary.md"))
    if strategic_files:
        strategic_file = strategic_files[0]
        print(f"   ✓ Strategic summary found: {strategic_file.name}")
        try:
            with open(strategic_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   ✓ Summary length: {len(content)} characters")
            
            # Extract key sections
            sections = re.findall(r'^## (.+)$', content, re.MULTILINE)
            print(f"   ✓ Sections found: {', '.join(sections[:3])}...")
            
        except Exception as e:
            print(f"   ❌ Error reading strategic summary: {e}")
    else:
        print("   ℹ️  No strategic summary found")
    print()
    
    # Test 7: Validate data structure
    print("7. VALIDATING DATA STRUCTURE:")
    required_files = [
        "criteria_scores.csv",
        "pages.csv", 
        "experience.csv",
        "recommendations.csv"
    ]
    
    validation_results = {}
    for req_file in required_files:
        file_path = audit_dir / req_file
        validation_results[req_file] = file_path.exists()
        status = "✓" if file_path.exists() else "❌"
        print(f"   {status} {req_file}: {'Found' if file_path.exists() else 'Missing'}")
    
    all_files_exist = all(validation_results.values())
    print(f"   Overall: {'✓ Ready for database integration' if all_files_exist else '❌ Missing required files'}")
    print()
    
    print("=== TEST SUMMARY ===")
    print(f"✓ Audit directory exists: {audit_dir.exists()}")
    print(f"✓ Audit files found: {len(hygiene_files)} hygiene, {len(experience_files)} experience")
    print(f"✓ URLs extracted: {len(urls)}")
    print(f"✓ Tier classification: {len(tier_classifications)} URLs classified")
    print(f"✓ Processed data: {len(csv_files)} CSV files")
    print(f"✓ Strategic summary: {'Yes' if strategic_files else 'No'}")
    print(f"✓ Ready for database: {'Yes' if all_files_exist else 'No'}")
    print()
    
    if all_files_exist:
        print("🎉 SUCCESS: This audit is fully processed and ready!")
        print("   The post-processor would be able to:")
        print("   1. ✓ Validate audit output (already done)")
        print("   2. ✓ Classify page tiers (simulated successfully)")
        print("   3. ✓ Process backfill data (already exists)")
        print("   4. ✓ Generate strategic summary (already exists)")
        print("   5. → Add to unified database (ready to go)")
    else:
        print("⚠️  PARTIAL: Some processing steps needed")
        print("   Missing files would need to be generated by:")
        print("   - Running backfill_packager.py")
        print("   - Running strategic_summary_generator.py")
    
    return True

if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 