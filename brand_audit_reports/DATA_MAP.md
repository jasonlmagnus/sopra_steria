# Brand Audit Data Map

## Core Audit Data (Tier 1-3 Analysis)
**Location:** `/audit_data/unified_audit_data.csv`
- **21 unique URLs** audited across **5 personas**
- **447 total criteria evaluations** (21 URLs × 5 personas × ~4.3 criteria each)
- Each record represents one criterion evaluation for one URL by one persona
- Individual `.md` reports in `/audit_outputs/*/` - Detailed narrative analysis

**Key Fields:**
- `page_id`, `criterion_code`, `raw_score`, `final_score`, `tier`, `descriptor`, `evidence`
- `persona_id`, `overall_sentiment`, `engagement_level`, `conversion_likelihood`
- `url`, `url_slug` - The actual page being evaluated

## Visual Brand Standards (Cross-Tier)
**Location:** `/audit_inputs/visual_brand/`
- `visual_audit.md` (34KB) - Comprehensive visual brand analysis
- `brand_audit_scores.csv` (2.5KB) - Quantitative brand compliance scores

**Contains:**
- Logo usage compliance
- Color palette consistency
- Typography standards
- Visual hierarchy assessment

## Social Media Brand Application (Tier 3/4)
**Location:** `/audit_inputs/social_media/`
- `MASTER_SOCIAL_MEDIA_AUDIT.md` (11KB) - Main social media findings
- `MASTER_SM_DASHBOARD_DATA.md` (23KB) - Platform-specific data
- `MASTER_SM_PAGE_SPEC.md` (9.5KB) - Social media specifications
- `Sopra Steria Benelux Social Media Assessment - UPDATED WITH INSTAGRAM ANALYSIS.md` (7.6KB)

**Platforms Covered:**
- LinkedIn Company Profile
- Instagram Business
- Other social touchpoints

## Methodology & Configuration
**Location:** `/audit_tool/config/`
- `methodology.yaml` - Scoring framework, tier definitions
- `unified_csv_columns.yaml` - Data structure reference

## Persona Definitions
**Location:** `/audit_inputs/personas/`
- `P1.md` - The Benelux Cybersecurity Decision Maker
- `P2.md` - The Benelux Strategic Business Leader (C-Suite Executive)
- `P3.md` - The Benelux Transformation Programme Leader
- `P4.md` - The Technical Influencer
- `P5.md` - The BENELUX Technology Innovation Leader

## Persona Journey Maps
**Location:** `/audit_inputs/persona_journeys/`
- Persona-specific journey analysis files

## Audit Prompts & Criteria
**Location:** `/audit_inputs/prompts/`
- `hygiene_scorecard.md` - Scoring criteria
- `narrative_analysis.md` - Narrative assessment framework
- `visual_audit.md` - Visual brand evaluation criteria

## Generated Reports (Existing)
**Location:** `/html_reports/`
- Individual persona HTML reports
- Consolidated brand report

## Data Integration Strategy

### Tier 1-3: Website/Digital Touchpoints
- **Source:** `audit_outputs/*/criteria_scores.csv`
- **Metrics:** Average scores, consistency (std dev), critical issues
- **Analysis:** Cross-persona performance, tier-weighted scoring

### Tier 3/4: Social Media
- **Source:** `audit_inputs/social_media/MASTER_SM_DASHBOARD_DATA.md`
- **Metrics:** Platform-specific brand compliance, engagement alignment
- **Analysis:** Social media brand consistency vs. main brand

### Cross-Tier: Visual Brand
- **Source:** `audit_inputs/visual_brand/brand_audit_scores.csv`
- **Metrics:** Logo, color, typography compliance scores
- **Analysis:** Visual consistency across all touchpoints

### Methodology Reference
- **Source:** `audit_tool/config/methodology.yaml`
- **Usage:** Tier definitions, scoring thresholds, weighting factors

## Output Targets

1. **Executive Summary** - Overall brand health across all tiers
2. **Tier Consistency Analysis** - Tier 1-4 performance with visual/social data
3. **Cross-Channel Insights** - Website vs. social media brand application
4. **Visual Brand Compliance** - Logo, color, typography consistency
5. **Persona-Specific Recommendations** - Tailored improvement strategies
6. **Implementation Roadmap** - Prioritized actions by effort/impact

## Next Steps

1. Parse social media data format
2. Integrate visual brand scores
3. Enhance tier analysis with off-site touchpoints
4. Generate comprehensive cross-channel report 