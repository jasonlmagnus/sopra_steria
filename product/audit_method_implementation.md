# Brand Audit Methodology - Technical Implementation Guide

## System Architecture Overview

This document describes the **technical implementation** of the Sopra Steria Brand Audit Tool, which uses a YAML-driven methodology configuration system to implement the business methodology defined in `audit_method.md`.

---

## Core Implementation Components

### 1. Configuration System (`audit_tool/config/methodology.yaml`)

The methodology is defined in a structured YAML configuration file that contains:

- **Metadata**: Version 2.0, tagline, description
- **Scoring Configuration**: 0-10 scale with descriptors
- **Calculation Formula**: `(ONSITE_SCORE × 0.7) + (OFFSITE_SCORE × 0.3) × CRISIS_MULTIPLIER`
- **Classification System**: Tier 1/2/3 for onsite, Owned/Influenced/Independent for offsite
- **Tier-Specific Criteria**: Brand and performance criteria with weights
- **Gating Rules**: Hard validation rules
- **Brand Messaging**: Reference messaging and CTAs
- **Quality Penalties**: Copy quality flags and point deductions

### 2. Core Modules

#### `MethodologyParser` (`methodology_parser.py`)

- Loads and parses the YAML methodology configuration
- Converts YAML into structured Python objects (`Methodology`, `Tier`, `Criterion`)
- Provides access to scoring rules, criteria weights, and validation requirements
- Enables YAML-driven configuration without code changes

#### `TierClassifier` (`tier_classifier.py`)

- Classifies URLs into appropriate tiers using regex patterns
- Determines onsite vs offsite classification
- Applies tier-specific evaluation criteria
- Supports both URL pattern matching and content analysis

#### `AIInterface` (`ai_interface.py`)

- Unified interface to multiple AI providers (Anthropic Claude, OpenAI)
- Generates hygiene scorecards and experience reports
- Formats prompts with methodology-specific context
- Handles API errors and retries gracefully

#### `PersonaParser` (`persona_parser.py`)

- Extracts persona attributes from markdown files
- Supports structured persona definition parsing
- Enables persona-specific evaluation context

#### `MultiPersonaPackager` (`multi_persona_packager.py`)

- Orchestrates multi-persona audit workflows
- Aggregates results across multiple personas
- Generates comparative analysis reports

#### `StrategicSummaryGenerator` (`strategic_summary_generator.py`)

- Creates executive-level strategic summaries
- Aggregates data across multiple pages and personas
- Generates actionable recommendations

---

## Methodology Implementation Details

### Scoring System (From `methodology.yaml`)

```yaml
scoring:
  scale:
    min: 0
    max: 10
  descriptors:
    0-3: "Missing / Broken / Off-brand" (FAIL)
    4-5: "Basic presence, no differentiation" (WARNING)
    6-7: "Competent but generic" (WARNING)
    8-9: "Strong, differentiated, persona-relevant" (PASS)
    10: "Exceptional, best-in-class" (EXCELLENT)
```

### Page Classification System

#### Onsite Tiers (Implemented in `TierClassifier`)

**Tier 1 - Brand Positioning (30% of onsite weight)**

- Brand Focus: 80% | Performance Focus: 20%
- Triggers: Homepage, About pages, Corporate content
- Criteria: Corporate positioning alignment, brand differentiation, emotional resonance, visual integrity

**Tier 2 - Value Propositions (50% of onsite weight)**

- Brand Focus: 50% | Performance Focus: 50%
- Triggers: Service pages, industry pages, solution content
- Criteria: Regional narrative integration, strategic value clarity, solution sophistication

**Tier 3 - Functional Content (20% of onsite weight)**

- Brand Focus: 30% | Performance Focus: 70%
- Triggers: Blog posts, case studies, technical content
- Criteria: Executive relevance, strategic insight quality, business value focus

#### Offsite Channels (Implemented in `TierClassifier`)

**Owned Channels (40% of offsite weight)**

- Brand Focus: 60% | Performance Focus: 40%
- Examples: Company LinkedIn, YouTube, owned social media

**Influenced Channels (35% of offsite weight)**

- Brand Focus: 40% | Authenticity Focus: 60%
- Examples: Glassdoor, employee advocacy, partner content

**Independent Channels (25% of offsite weight)**

- Brand Focus: 20% | Sentiment Focus: 80%
- Examples: Review sites, industry reports, third-party mentions

---

## Workflow Implementation

### 1. Main Audit Process (`main.py`)

```python
class BrandAuditTool:
    def __init__(self, config_path: str = None):
        self.methodology = MethodologyParser(config_path)
        self.scraper = Scraper()
        self.ai = AIInterface()
        self.persona_parser = PersonaParser()

    def run_audit(self, urls: List[str], persona_path: str):
        # Load persona and methodology
        # Process each URL through scraping and AI analysis
        # Generate hygiene scorecards and experience reports
        # Create strategic summary
```

### 2. URL Processing Pipeline

1. **URL Classification** (`TierClassifier.classify_url()`)

   - Determines tier/channel type
   - Applies appropriate evaluation criteria

2. **Content Scraping** (`Scraper.scrape_url()`)

   - Extracts page content and metadata
   - Handles 404s and technical issues

3. **AI Analysis** (`AIInterface.generate_hygiene_scorecard()`)

   - Applies methodology-specific prompts
   - Generates structured scoring output
   - Includes evidence and recommendations

4. **Report Generation** (`AIInterface.generate_experience_report()`)
   - Creates persona-specific experience analysis
   - Provides strategic insights and recommendations

### 3. Strategic Summary Generation

The `StrategicSummaryGenerator` aggregates individual page scores into executive-level insights:

- Overall brand health metrics
- Tier-specific performance analysis
- Top performing and underperforming pages
- Strategic recommendations with impact assessment
- Persona-specific journey insights

---

## Data Models (`models.py`)

The system uses structured dataclasses for consistent data representation:

```python
@dataclass
class Methodology:
    tiers: List[Tier]
    offsite_channels: List[OffsiteChannel]
    metadata: Dict[str, Any]
    scoring_config: Dict[str, Any]
    # ... additional configuration

@dataclass
class Scorecard:
    url: str
    final_score: float
    tier_name: str
    scored_criteria: List[ScoredCriterion]
    brand_consistency_check: Dict[str, Any]
    # ... validation results
```

---

## Validation and Quality Control

### Hard Gating Rules (From `methodology.yaml`)

1. **Corporate Tagline Missing**: "The world is how we shape it" → Corporate Positioning ≤ 3
2. **Regional Narrative Missing**: Required sub-narrative missing → Regional Integration ≤ 4
3. **Broken Content**: <50 words or placeholder text → Maximum page score = 4

### Evidence Requirements

- Scores ≥7: Require verbatim quote ≥25 words
- Scores ≤4: Require verbatim quote showing poor content
- Missing evidence: -2 point penalty

### Copy Quality Penalties

- Redundant wording: -1 point
- Empty jargon without proof: -1 point
- Placeholder/Lorem ipsum: -2 points

---

## Configuration Management

### Key Configuration Files

- `audit_tool/config/methodology.yaml`: Complete methodology definition
- `audit_tool/config/unified_csv_columns.yaml`: Data schema definitions
- `audit_inputs/personas/*.md`: Persona definitions
- `audit_inputs/audit_urls.md`: URL lists for batch processing

### Environment Setup

```bash
# Required environment variables
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # Optional, for OpenAI provider

# Install dependencies
pip install -r requirements.txt

# Run audit
python -m audit_tool.main --urls urls.txt --persona persona.md --output results/
```

---

## Dashboard Integration

The audit results integrate with the Brand Health Command Center dashboard:

- **Data Gateway** (`data_gateway.py`): Loads unified audit datasets
- **Metrics Calculator** (`dashboard/components/metrics_calculator.py`): Computes KPIs and insights
- **Multi-Persona Packaging** (`multi_persona_packager.py`): Aggregates cross-persona analysis

---

## Usage Examples

### Single Persona Audit

```python
from audit_tool.main import BrandAuditTool

tool = BrandAuditTool()
results = tool.run_audit(
    urls=['https://soprasteria.com', 'https://soprasteria.be'],
    persona_path='audit_inputs/personas/P1.md'
)
```

### Multi-Persona Analysis

```python
from audit_tool.multi_persona_packager import MultiPersonaPackager

packager = MultiPersonaPackager('audit_outputs/')
report = packager.generate_cross_persona_analysis()
```

---

## Key Implementation Benefits

1. **YAML-Driven Configuration**: Methodology changes without code modifications
2. **Modular Architecture**: Clear separation of concerns across components
3. **Multi-Provider AI Support**: Flexible AI provider selection
4. **Structured Data Models**: Consistent data representation throughout system
5. **Comprehensive Validation**: Hard gating rules and quality control
6. **Dashboard Integration**: Direct connection to Brand Health Command Center
7. **Scalable Processing**: Support for batch processing and multi-persona analysis

---

## Maintenance and Updates

### Methodology Updates

- Edit `audit_tool/config/methodology.yaml`
- No code changes required for criteria adjustments
- Version control tracks methodology evolution

### Adding New Criteria

1. Update YAML configuration with new criteria
2. Adjust weights to maintain 100% totals
3. Update AI prompts if needed in `AIInterface`

### Provider Management

- Switch between Anthropic and OpenAI via `--model` parameter
- Add new providers by extending `AIInterface` class
- Maintain consistent output format across providers

---

## Troubleshooting

### Common Issues

**Column Mismatch Errors**

- Run integrity checker: `python -m audit_tool.dashboard.fix_column_issues`
- Check unified CSV schema in `config/unified_csv_columns.yaml`

**AI Provider Errors**

- Verify API keys in environment variables
- Check rate limits and quotas
- Switch providers using `--model` parameter

**Classification Issues**

- Review URL patterns in `TierClassifier`
- Check methodology YAML for trigger definitions
- Validate regex patterns for new URL structures

---

## Development Workflow

### Adding New Features

1. **Update Methodology**: Modify `methodology.yaml` if needed
2. **Extend Models**: Add new dataclasses to `models.py`
3. **Update Parser**: Modify `MethodologyParser` for new configuration
4. **Test Integration**: Ensure dashboard compatibility
5. **Update Documentation**: Reflect changes in this guide

### Testing

```bash
# Run unit tests
python -m pytest audit_tool/tests/

# Test specific persona
python -m audit_tool.main --urls test_urls.txt --persona test_persona.md --output test_results/

# Validate methodology
python -c "from audit_tool.methodology_parser import MethodologyParser; mp = MethodologyParser(); print('✅ Methodology valid')"
```

---

**Status**: This implementation guide reflects the current v2.0 system architecture and is maintained alongside the business methodology in `audit_method.md`.
