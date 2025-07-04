# Social Media Backfill Utility Guide

## Overview

The Social Media Backfill Utility is a comprehensive tool for managing social media platform data in the Sopra Steria Brand Audit system. It ensures that all social media platforms are properly represented in the audit data with accurate scores from the master social media audit.

## Quick Start

```bash
# Navigate to audit tool directory
cd audit_tool

# Complete backfill process (recommended for first-time use)
python social_media_backfill.py --full-backfill
```

## Detailed Usage

### 1. Check Current State

**Purpose**: Inspect existing social media data without making changes

```bash
python social_media_backfill.py --check
```

**Expected Output**:

- Total CSV rows count
- Number of social media entries found
- Unique social media URLs
- Current scores by platform with persona breakdowns

### 2. Add Missing Platforms

**Purpose**: Add missing social media platform entries to the CSV

```bash
python social_media_backfill.py --add-platforms
```

**What it does**:

- Identifies missing platforms (Instagram, Facebook, Twitter/X)
- Creates entries for all personas on missing platforms
- Generates automatic backup before changes
- Adds new entries with default values (scores will be updated separately)

### 3. Update Scores

**Purpose**: Apply scores from master social media audit to existing entries

```bash
python social_media_backfill.py --update-scores
```

**What it does**:

- Updates scores for all social media entries
- Applies persona-specific scores from master audit
- Updates sentiment, engagement, and conversion metrics
- Updates descriptors (SUCCESS/WARN/CONCERN/FAIL)
- Updates various flags for dashboard filtering

### 4. Full Backfill Process

**Purpose**: Complete social media data backfill (recommended)

```bash
python social_media_backfill.py --full-backfill
```

**Process**:

1. **Step 1**: Check current state
2. **Step 2**: Add missing platforms
3. **Step 3**: Update scores
4. **Step 4**: Final verification

## Platform Details

### Supported Platforms

| Platform      | URL                             | Average Score | Status                      |
| ------------- | ------------------------------- | ------------- | --------------------------- |
| **LinkedIn**  | `/company/soprasteria-benelux/` | 6.8/10        | ✅ Strong Performance       |
| **Instagram** | `@soprasteria_bnl`              | 6.2/10        | ✅ Good Visual Storytelling |
| **Facebook**  | `/soprasteriabenelux/`          | 2.8/10        | ⚠️ Limited Impact           |
| **Twitter/X** | `@SopraSteria_Bnl`              | 1.2/10        | ❌ Critical Failure         |

### Persona-Specific Scores

| Persona                   | LinkedIn | Instagram | Facebook | Twitter/X |
| ------------------------- | -------- | --------- | -------- | --------- |
| **P1 (C-Suite)**          | 8.0      | 7.0       | 4.0      | 2.0       |
| **P2 (Tech Leaders)**     | 8.0      | 6.0       | 3.0      | 1.0       |
| **P3 (Programme)**        | 6.0      | 8.0       | 2.0      | 1.0       |
| **P4 (Cybersecurity)**    | 5.0      | 3.0       | 3.0      | 1.0       |
| **P5 (Tech Influencers)** | 7.0      | 7.0       | 2.0      | 1.0       |

## Safety Features

### Automatic Backups

The utility automatically creates backups before any changes:

- **Adding platforms**: `unified_audit_data_before_adding_social_platforms.csv`
- **Updating scores**: `unified_audit_data_before_social_score_update.csv`

### Validation Checks

- **File existence**: Verifies CSV file exists before processing
- **Platform detection**: Uses robust URL pattern matching
- **Persona mapping**: Handles various persona name formats
- **Score validation**: Ensures scores are within valid ranges (0-10)

## Data Structure

### New Entry Fields

When adding new social media platforms, entries include:

```python
{
    'url': 'https://platform.com/soprasteria',
    'persona_id': 'The Benelux Cybersecurity Decision Maker',
    'page_title': 'Sopra Steria Benelux - Platform',
    'raw_score': 0.0,  # Updated by score updater
    'final_score': 0.0,
    'avg_score': 0.0,
    'descriptor': 'PENDING',
    'content_category': 'Social Media',
    'platform_type': 'Social Media',
    'audit_method': 'Social Media Assessment',
    'data_source': 'Social Media Backfill Utility'
}
```

### Score Updates

When updating scores, the utility modifies:

- `raw_score` → Persona-specific score from master audit
- `final_score` → Same as raw_score
- `avg_score` → Platform average score
- `descriptor` → SUCCESS/WARN/CONCERN/FAIL based on score
- `sentiment_numeric` → Derived from score (1-10)
- `engagement_numeric` → Derived from score (1-10)
- `conversion_numeric` → Derived from score (1-10)
- `overall_sentiment` → Positive/Neutral/Negative
- `engagement_level` → High/Medium/Low
- `conversion_likelihood` → High/Medium/Low
- `critical_issue_flag` → True if score < 3
- `quick_win_flag` → True if 5 ≤ score < 7
- `success_flag` → True if score ≥ 8

## Troubleshooting

### Common Issues

#### 1. CSV File Not Found

**Error**: `Error: CSV file not found at /path/to/unified_audit_data.csv`
**Solution**:

- Verify you're running from `audit_tool/` directory
- Check that `../audit_data/unified_audit_data.csv` exists
- Ensure proper file permissions

#### 2. Platform Not Detected

**Issue**: Platforms not being identified from URLs
**Solution**:

- Check URL format matches expected patterns
- Verify URLs contain platform keywords (linkedin, instagram, facebook, twitter, x.com)
- Update platform detection logic if needed

#### 3. Persona Mapping Issues

**Issue**: Personas not being mapped to correct codes
**Solution**:

- Check persona names in CSV match expected formats
- Review persona mapping logic in `identify_persona()` function
- Add new persona patterns if needed

#### 4. Score Validation Errors

**Issue**: Scores outside expected ranges
**Solution**:

- Verify scores are between 0-10
- Check master audit data for accuracy
- Review score calculation logic

### Debug Mode

For detailed debugging, add print statements or modify the utility to show more verbose output:

```python
# Add to functions for debugging
print(f"Processing URL: {url}")
print(f"Identified platform: {platform}")
print(f"Persona mapping: {persona} → {persona_code}")
print(f"Score update: {old_score} → {new_score}")
```

## Integration with Main Audit Tool

The social media backfill utility integrates seamlessly with the main audit system:

1. **Data Source**: Updates the same `unified_audit_data.csv` used by dashboards
2. **Score Format**: Maintains compatibility with existing score analysis
3. **Persona Structure**: Uses same persona identification system
4. **Backup Strategy**: Follows same backup patterns as other tools

## Best Practices

### When to Use Each Command

- **`--check`**: Regular monitoring and verification
- **`--add-platforms`**: When new social media platforms are identified
- **`--update-scores`**: When master audit scores are updated
- **`--full-backfill`**: Initial setup or major updates

### Workflow Recommendations

1. **Initial Setup**: Use `--full-backfill` to establish complete social media data
2. **Regular Updates**: Use `--update-scores` when audit findings change
3. **Verification**: Use `--check` to monitor data quality
4. **New Platforms**: Use `--add-platforms` when expanding social media presence

### Data Quality Maintenance

- Run `--check` monthly to verify data integrity
- Keep master social media audit document updated
- Review scores quarterly for accuracy
- Monitor backup files to track changes over time

## Support

For issues with the social media backfill utility:

1. Check this guide for common solutions
2. Review the main README.md for general troubleshooting
3. Examine backup files to understand what changed
4. Test individual functions to isolate issues

## Version History

- **v1.0**: Initial consolidated utility with full backfill capabilities
- **Source**: Combined functionality from multiple temporary scripts
- **Integration**: Moved to `audit_tool/` directory for proper organization
