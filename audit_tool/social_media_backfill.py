#!/usr/bin/env python3
"""
Social Media Backfill Utility for Sopra Steria Brand Audit Tool

This utility handles the complete social media data backfill process:
1. Adds missing social media platform entries to the unified audit data
2. Updates scores based on the master social media audit findings
3. Provides verification and reporting capabilities

Usage:
    python social_media_backfill.py --add-platforms    # Add missing platforms
    python social_media_backfill.py --update-scores    # Update scores only
    python social_media_backfill.py --full-backfill    # Complete backfill process
    python social_media_backfill.py --check            # Check current state
"""

import pandas as pd
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Get the path to the audit_data directory relative to this script
SCRIPT_DIR = Path(__file__).parent
AUDIT_DATA_DIR = SCRIPT_DIR.parent / "audit_data"
CSV_PATH = AUDIT_DATA_DIR / "unified_audit_data.csv"

# Social media platform URLs and scores from master audit
SOCIAL_MEDIA_PLATFORMS = {
    'linkedin': {
        'url': 'https://www.linkedin.com/company/soprasteria-benelux/',
        'platform_avg': 6.8,
        'scores': {
            'P1_CSuite': 8.0,
            'P2_TechLeaders': 8.0,
            'P3_Programme': 6.0,
            'P4_Cybersecurity': 5.0,
            'P5_TechInfluencers': 7.0
        }
    },
    'instagram': {
        'url': 'https://www.instagram.com/soprasteria_bnl/',
        'platform_avg': 6.2,
        'scores': {
            'P1_CSuite': 7.0,
            'P2_TechLeaders': 6.0,
            'P3_Programme': 8.0,
            'P4_Cybersecurity': 3.0,
            'P5_TechInfluencers': 7.0
        }
    },
    'facebook': {
        'url': 'https://www.facebook.com/soprasteriabenelux/',
        'platform_avg': 2.8,
        'scores': {
            'P1_CSuite': 4.0,
            'P2_TechLeaders': 3.0,
            'P3_Programme': 2.0,
            'P4_Cybersecurity': 3.0,
            'P5_TechInfluencers': 2.0
        }
    },
    'twitter': {
        'url': 'https://twitter.com/SopraSteria_Bnl',
        'platform_avg': 1.2,
        'scores': {
            'P1_CSuite': 2.0,
            'P2_TechLeaders': 1.0,
            'P3_Programme': 1.0,
            'P4_Cybersecurity': 1.0,
            'P5_TechInfluencers': 1.0
        }
    }
}

# All personas from the existing data
PERSONAS = [
    'The Benelux Cybersecurity Decision Maker',
    'The Benelux Strategic Business Leader (C-Suite Executive)', 
    'The Benelux Transformation Programme Leader',
    'The Technical Influencer',
    'The_BENELUX_Technology_Innovation_Leader'
]

def identify_platform(url):
    """Identify social media platform from URL"""
    url_lower = str(url).lower()
    if 'linkedin' in url_lower:
        return 'linkedin'
    elif 'instagram' in url_lower:
        return 'instagram'
    elif 'facebook' in url_lower:
        return 'facebook'
    elif 'twitter' in url_lower or 'x.com' in url_lower:
        return 'twitter'
    return None

def identify_persona(persona_text):
    """Map persona text to persona code"""
    persona_lower = str(persona_text).lower()
    
    if 'cybersecurity' in persona_lower:
        return 'P4_Cybersecurity'
    elif 'strategic' in persona_lower and 'business' in persona_lower:
        return 'P1_CSuite'
    elif 'technology' in persona_lower and 'innovation' in persona_lower:
        return 'P2_TechLeaders'
    elif 'transformation' in persona_lower and 'programme' in persona_lower:
        return 'P3_Programme'
    elif 'technical' in persona_lower and 'influencer' in persona_lower:
        return 'P5_TechInfluencers'
    
    # Default fallback
    return 'P4_Cybersecurity'

def create_social_media_entry(url, persona_id, platform_name):
    """Create a new social media entry with default values"""
    return {
        'url': url,
        'persona_id': persona_id,
        'page_title': f'Sopra Steria Benelux - {platform_name.title()}',
        'raw_score': 0.0,  # Will be updated by score updater
        'final_score': 0.0,
        'avg_score': 0.0,
        'descriptor': 'PENDING',
        'sentiment_numeric': 5,
        'engagement_numeric': 5,
        'conversion_numeric': 5,
        'overall_sentiment': 'Neutral',
        'engagement_level': 'Medium',
        'conversion_likelihood': 'Medium',
        'critical_issue_flag': False,
        'quick_win_flag': False,
        'success_flag': False,
        'audit_date': datetime.now().strftime('%Y-%m-%d'),
        'audit_timestamp': datetime.now().isoformat(),
        'content_category': 'Social Media',
        'platform_type': 'Social Media',
        'page_type': f'{platform_name.title()} Profile',
        'region': 'Benelux',
        'language': 'Multi',
        'audit_method': 'Social Media Assessment',
        'data_source': 'Social Media Backfill Utility'
    }

def check_current_state():
    """Check current state of social media entries in CSV"""
    if not CSV_PATH.exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        return False
    
    df = pd.read_csv(CSV_PATH)
    print(f"Total rows in CSV: {len(df)}")
    
    # Find social media entries
    social_keywords = ['linkedin', 'twitter', 'facebook', 'instagram', 'x.com']
    social_media_entries = df[df['url'].str.lower().str.contains('|'.join(social_keywords), na=False)]
    
    print(f"\nFound {len(social_media_entries)} social media related entries")
    
    if len(social_media_entries) > 0:
        # Show unique URLs
        unique_urls = social_media_entries['url'].unique()
        print(f"\nUnique social media URLs ({len(unique_urls)}):")
        for i, url in enumerate(unique_urls, 1):
            print(f"{i}. {url}")
        
        # Show current scores by platform
        print("\nCurrent scores by platform:")
        for platform in SOCIAL_MEDIA_PLATFORMS.keys():
            platform_entries = social_media_entries[social_media_entries['url'].str.lower().str.contains(platform, na=False)]
            if len(platform_entries) > 0:
                avg_score = platform_entries['raw_score'].mean()
                expected_score = SOCIAL_MEDIA_PLATFORMS[platform]['platform_avg']
                print(f"\n{platform.capitalize()}:")
                print(f"  - Entries: {len(platform_entries)}")
                print(f"  - Average raw_score: {avg_score:.2f} (expected: {expected_score})")
                print(f"  - Score range: {platform_entries['raw_score'].min():.1f} - {platform_entries['raw_score'].max():.1f}")
    else:
        print("\nNo social media entries found!")
    
    return True

def add_missing_platforms():
    """Add missing social media platform entries to CSV"""
    if not CSV_PATH.exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        return False
    
    # Read CSV
    print(f"Reading CSV from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    original_count = len(df)
    
    # Create backup
    backup_path = str(CSV_PATH).replace('.csv', '_before_adding_social_platforms.csv')
    df.to_csv(backup_path, index=False)
    print(f"Backup created at: {backup_path}")
    
    # Check existing platforms
    existing_platforms = set()
    for idx, row in df.iterrows():
        platform = identify_platform(row['url'])
        if platform:
            existing_platforms.add(platform)
    
    print(f"\nExisting platforms in CSV: {existing_platforms}")
    
    # Add missing platforms
    new_entries = []
    added_count = 0
    
    for platform, data in SOCIAL_MEDIA_PLATFORMS.items():
        if platform not in existing_platforms:
            print(f"\nAdding {platform} entries...")
            for persona in PERSONAS:
                entry = create_social_media_entry(data['url'], persona, platform)
                new_entries.append(entry)
                added_count += 1
                print(f"  - Added {platform} for {persona}")
    
    if new_entries:
        # Convert new entries to DataFrame
        new_df = pd.DataFrame(new_entries)
        
        # Ensure all columns match
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = None
        
        # Reorder columns to match original
        new_df = new_df[df.columns]
        
        # Append to original DataFrame
        df_updated = pd.concat([df, new_df], ignore_index=True)
        
        # Save updated CSV
        df_updated.to_csv(CSV_PATH, index=False)
        print(f"\nAdded {added_count} new social media entries")
        print(f"Total entries: {original_count} → {len(df_updated)}")
        print(f"Saved to: {CSV_PATH}")
        
        return True
    else:
        print("\nNo new platforms to add - all platforms already exist in CSV")
        return False

def update_scores():
    """Update social media scores based on master audit findings"""
    if not CSV_PATH.exists():
        print(f"Error: CSV file not found at {CSV_PATH}")
        return False
    
    # Read CSV
    print(f"Reading CSV from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    
    # Create backup
    backup_path = str(CSV_PATH).replace('.csv', '_before_social_score_update.csv')
    df.to_csv(backup_path, index=False)
    print(f"Backup created at: {backup_path}")
    
    # Find social media entries
    social_media_mask = df['url'].apply(lambda x: identify_platform(x) is not None)
    social_media_entries = df[social_media_mask]
    
    print(f"\nFound {len(social_media_entries)} social media entries to update")
    
    # Update scores
    updates = 0
    for idx in social_media_entries.index:
        url = df.loc[idx, 'url']
        persona = df.loc[idx, 'persona_id']
        
        platform = identify_platform(url)
        persona_code = identify_persona(persona)
        
        if platform and persona_code in SOCIAL_MEDIA_PLATFORMS[platform]['scores']:
            new_score = SOCIAL_MEDIA_PLATFORMS[platform]['scores'][persona_code]
            platform_avg = SOCIAL_MEDIA_PLATFORMS[platform]['platform_avg']
            
            # Update scores
            df.loc[idx, 'raw_score'] = new_score
            df.loc[idx, 'final_score'] = new_score
            df.loc[idx, 'avg_score'] = platform_avg
            
            # Update descriptor
            if new_score >= 8:
                descriptor = 'SUCCESS'
            elif new_score >= 6:
                descriptor = 'WARN'
            elif new_score >= 4:
                descriptor = 'CONCERN'
            else:
                descriptor = 'FAIL'
            df.loc[idx, 'descriptor'] = descriptor
            
            # Update sentiment metrics
            if new_score >= 7:
                df.loc[idx, 'sentiment_numeric'] = 8
                df.loc[idx, 'engagement_numeric'] = 7
                df.loc[idx, 'conversion_numeric'] = 6
                df.loc[idx, 'overall_sentiment'] = 'Positive'
                df.loc[idx, 'engagement_level'] = 'High'
                df.loc[idx, 'conversion_likelihood'] = 'High'
            elif new_score >= 5:
                df.loc[idx, 'sentiment_numeric'] = 6
                df.loc[idx, 'engagement_numeric'] = 5
                df.loc[idx, 'conversion_numeric'] = 4
                df.loc[idx, 'overall_sentiment'] = 'Neutral'
                df.loc[idx, 'engagement_level'] = 'Medium'
                df.loc[idx, 'conversion_likelihood'] = 'Medium'
            else:
                df.loc[idx, 'sentiment_numeric'] = 3
                df.loc[idx, 'engagement_numeric'] = 2
                df.loc[idx, 'conversion_numeric'] = 2
                df.loc[idx, 'overall_sentiment'] = 'Negative'
                df.loc[idx, 'engagement_level'] = 'Low'
                df.loc[idx, 'conversion_likelihood'] = 'Low'
            
            # Update flags
            df.loc[idx, 'critical_issue_flag'] = (new_score < 3)
            df.loc[idx, 'quick_win_flag'] = (5 <= new_score < 7)
            df.loc[idx, 'success_flag'] = (new_score >= 8)
            
            updates += 1
            print(f"Updated {platform} for {persona_code}: {new_score}")
    
    # Save updated CSV
    df.to_csv(CSV_PATH, index=False)
    print(f"\nUpdated {updates} entries")
    print(f"Saved to: {CSV_PATH}")
    
    # Print summary
    print("\nSocial Media Score Summary:")
    for platform, data in SOCIAL_MEDIA_PLATFORMS.items():
        platform_entries = df[df['url'].apply(lambda x: identify_platform(x) == platform)]
        if not platform_entries.empty:
            avg = platform_entries['raw_score'].mean()
            expected = data['platform_avg']
            print(f"{platform.capitalize()}: {avg:.2f} (expected: {expected})")
    
    return True

def full_backfill():
    """Complete social media backfill process"""
    print("Starting full social media backfill process...")
    print("=" * 50)
    
    # Step 1: Check current state
    print("\nStep 1: Checking current state")
    check_current_state()
    
    # Step 2: Add missing platforms
    print("\nStep 2: Adding missing platforms")
    add_missing_platforms()
    
    # Step 3: Update scores
    print("\nStep 3: Updating scores")
    update_scores()
    
    # Step 4: Final verification
    print("\nStep 4: Final verification")
    check_current_state()
    
    print("\n" + "=" * 50)
    print("Social media backfill process completed!")

def main():
    parser = argparse.ArgumentParser(description='Social Media Backfill Utility')
    parser.add_argument('--add-platforms', action='store_true', 
                       help='Add missing social media platforms to CSV')
    parser.add_argument('--update-scores', action='store_true',
                       help='Update social media scores from master audit')
    parser.add_argument('--full-backfill', action='store_true',
                       help='Complete backfill process (add platforms + update scores)')
    parser.add_argument('--check', action='store_true',
                       help='Check current state of social media entries')
    
    args = parser.parse_args()
    
    if args.check:
        check_current_state()
    elif args.add_platforms:
        add_missing_platforms()
    elif args.update_scores:
        update_scores()
    elif args.full_backfill:
        full_backfill()
    else:
        print("No action specified. Use --help for available options.")
        print("\nQuick start:")
        print("  python social_media_backfill.py --full-backfill")

if __name__ == "__main__":
    main() 