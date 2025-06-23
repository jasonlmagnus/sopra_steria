# Functional Specification: Persona Experience & Brand Audit Tool

**Status: ✅ FUNCTIONAL - Core Pipeline Operational**

**Current Reality:** Manual 4-stage process with all components working. Dashboard fully operational.
**Latest Enhancement:** Fixed data pipeline issues, standardized schema, eliminated column mismatches.

## 1. Overview

This document provides a functional specification for the Persona Experience & Brand Audit Tool. It describes the system's behavior, features, and component interactions.

The system is a Python command-line application that audits a list of URLs from the perspective of a defined persona. For a given persona, it produces:

1.  A **Persona Experience Report** for each URL.
2.  A **Brand Hygiene Scorecard** for each URL.
3.  A single, consolidated **Strategic Summary** report that aggregates findings from all audited URLs.

### 1.1. High-Level Architecture

The application follows a modular design with **automated post-processing pipeline** for seamless dashboard integration.

- **Technology Stack:** Python 3.10+, Requests, BeautifulSoup4, Anthropic SDK, OpenAI SDK, PyYAML, Pandas, Streamlit.
- **Current Execution Flow (Automated Pipeline):**
  1.  **Stage 1 - Audit Generation:** `python -m audit_tool.main` generates markdown scorecards and experience reports.
  2.  **Stage 2 - Post-Processing:** Automated via `AuditPostProcessor` - converts markdown to structured data, applies tier classification, generates strategic summary, and integrates with unified database.
  3.  **Stage 3 - Dashboard Integration:** Immediate data availability via cache refresh - no app restart required.

### 1.2. Workflow Improvements

- **Automated Process:** Single-click "ADD TO DATABASE" button eliminates manual steps
- **Immediate Integration:** Automatic cache refresh makes new data available instantly
- **Error Recovery:** Comprehensive validation and graceful error handling
- **Progress Tracking:** Live progress indicators with step-by-step status updates
- **User Experience:** Seamless workflow from audit completion to dashboard viewing

## 2. Component Specification

### 2.1. Main Orchestrator (`main.py`)

- **Purpose:** Entry point and controller of the application via `BrandAuditTool` class.
- **Interface:** Accepts command-line arguments: `python -m audit_tool.main --urls <path> --persona <path> --output <path> --model <provider>`.
- **Logic:**
  1.  Parses arguments and initializes `BrandAuditTool`.
  2.  Initializes components (`Scraper`, `AIInterface`, `MethodologyParser`, `PersonaParser`).
  3.  Loads persona and creates output directory.
  4.  Loops through URLs: scrapes content, generates hygiene scorecard and experience report via `AIInterface`.
  5.  Saves markdown reports to persona-specific directory.
  6.  Generates strategic summary using `StrategicSummaryGenerator`.

### 2.2. Scraper Module (`scraper.py`)

- **Purpose:** To fetch web content with caching support.
- **Functions:**
  - `scrape_url(url: str) -> PageData`:
    - Uses `requests` and `BeautifulSoup` to extract page content.
    - Implements file-based caching to improve performance.
    - Handles 404s and technical issues gracefully.
    - Returns a `PageData` object containing URL, raw text, and metadata.

### 2.3. AI Module (`ai_interface.py`)

- **Purpose:** To abstract all interactions with multiple AI providers (Anthropic Claude, OpenAI).
- **Functions:**
  - `generate_hygiene_scorecard(url: str, page_content: str, persona_content: str, methodology: Any) -> str`:
    - Constructs methodology-specific prompts for hygiene scorecard generation.
    - Supports both Anthropic and OpenAI providers.
    - Returns the generated Markdown scorecard as a string.
  - `generate_experience_report(url: str, page_content: str, persona_content: str, methodology: Any) -> str`:
    - Constructs persona-specific prompts for experience report generation.
    - Uses provider-specific prompt formatting.
    - Returns the generated Markdown narrative as a string.
  - `generate_strategic_summary(persona_name: str, scorecard_data: List[Dict], methodology: Any) -> str`:
    - Takes aggregated scorecard data and generates executive-level insights.
    - Integrates with methodology configuration for consistent analysis.
    - Returns comprehensive strategic summary as Markdown.

### 2.4. Generators Module (`generators.py`)

- **Purpose:** To create structured markdown reports from audit data.
- **Classes:**
  - `HygieneScorecard`: Generates hygiene scorecards in markdown format with criteria scores, evidence, and recommendations.
  - `ExperienceReport`: Generates experience reports with persona-specific insights, sentiment metrics, and recommendations.
  - `StrategicSummary`: Generates strategic summaries with executive insights, key findings, and actionable recommendations.
- **Functions:**
  - `parse_ai_scorecard(markdown: str) -> Dict[str, Any]`: Parses AI-generated scorecard markdown into structured data.
  - `parse_ai_experience_report(markdown: str) -> Dict[str, Any]`: Parses AI-generated experience reports into structured data.

### 2.5. Reporting Module (`reporter.py`)

- **Purpose:** To write generated reports to markdown files using templates.
- **Functions:**
  - `save_report(content: str, filepath: str)`: Saves content to specified file path.
  - Template-based rendering for consistent report formatting.

### 2.6. Additional Core Modules

#### MethodologyParser (`methodology_parser.py`)

- **Purpose:** Loads and parses YAML methodology configuration.
- **Functions:**
  - `parse() -> Methodology`: Converts YAML config into structured Python objects.
  - `get_tier_criteria(tier_name: str)`: Returns criteria for specific tier.

#### PersonaParser (`persona_parser.py`)

- **Purpose:** Extracts persona attributes from markdown files.
- **Functions:**
  - `extract_attributes_from_content(content: str) -> Persona`: Parses persona definitions.

#### TierClassifier (`tier_classifier.py`)

- **Purpose:** Classifies URLs into appropriate tiers using regex patterns.
- **Functions:**
  - `classify_url(url: str) -> Tuple[str, Dict]`: Determines tier and configuration.

#### EnhancedBackfillPackager (`backfill_packager.py`)

- **Purpose:** Processes markdown reports into structured CSV data.
- **Functions:**
  - `process_persona(persona_name: str)`: Generates enhanced CSV files from markdown.

#### StrategicSummaryGenerator (`strategic_summary_generator.py`)

- **Purpose:** Creates executive-level strategic summaries.
- **Functions:**
  - `generate_full_report() -> Tuple[str, List, Dict]`: Aggregates data and generates insights.

#### MultiPersonaPackager (`multi_persona_packager.py`)

- **Purpose:** Unifies data across multiple personas for dashboard consumption.
- **Functions:**
  - `process_all_personas()`: Creates unified parquet files for cross-persona analysis.

### 2.7. Audit Post-Processor (`audit_post_processor.py`)

- **Purpose:** Consolidated post-audit processing pipeline that automates the conversion of raw audit outputs into dashboard-ready unified data.
- **Interface:** Can be used programmatically or via the Streamlit UI:

  ```python
  # Simple usage
  from audit_tool.audit_post_processor import process_completed_audit
  success = process_completed_audit("Persona_Name", add_to_db=True)

  # Advanced usage
  processor = AuditPostProcessor("Persona_Name")
  success = processor.process_audit_results()
  if success:
      processor.add_to_database()
  ```

- **Functions:**
  - `validate_audit_output() -> bool`: Checks that required markdown files exist (hygiene scorecards + experience reports)
  - `classify_page_tiers() -> Dict[str, Dict]`: Applies `TierClassifier` to extract and classify all audited URLs
  - `run_backfill_processing() -> Dict[str, pd.DataFrame]`: Converts markdown files to structured CSV/Parquet using `EnhancedBackfillPackager`
  - `generate_strategic_summary() -> str`: Creates executive-level insights via `StrategicSummaryGenerator`
  - `add_to_database() -> bool`: Integrates processed data with unified multi-persona dataset via `MultiPersonaPackager`
  - `process_audit_results() -> bool`: Executes complete processing pipeline (validate → classify → backfill → summarize)
  - `get_processing_status() -> Dict`: Returns current processing state and readiness for database integration

**UI Integration:**

- **Streamlit Integration:** Seamlessly integrated with Run Audit page UI
- **Progress Tracking:** Live progress bar with step-by-step status updates (10% → 20% → 40% → 60% → 80% → 90% → 100%)
- **Cache Management:** Automatically clears Streamlit cache (`st.cache_data.clear()`) to make new data immediately available
- **Error Handling:** Comprehensive error reporting with detailed status messages
- **State Management:** Proper session state handling for multi-audit workflows

**Workflow Benefits:**

- **Eliminates Manual Steps:** Replaces 4-stage manual process with single-click automation
- **Immediate Data Availability:** New audit data visible in dashboard without app restart
- **Error Recovery:** Graceful handling of processing failures with detailed error reporting
- **User Experience:** Seamless workflow from audit completion to dashboard integration

## 3. Data Flow Diagram

### Current Implementation (Automated Post-Processing Pipeline)

```mermaid
sequenceDiagram
    participant User
    participant RunAuditUI
    participant BrandAuditTool
    participant Scraper
    participant AIInterface
    participant PostProcessor
    participant BackfillPackager
    participant StrategicSummaryGenerator
    participant MultiPersonaPackager
    participant Dashboard

    User->>RunAuditUI: Upload persona + URLs
    RunAuditUI->>BrandAuditTool: Execute audit
    BrandAuditTool->>BrandAuditTool: Initialize components

    loop For Each URL
        BrandAuditTool->>Scraper: scrape_url(url)
        Scraper-->>BrandAuditTool: Returns PageData

        BrandAuditTool->>AIInterface: generate_hygiene_scorecard(...)
        AIInterface-->>BrandAuditTool: Returns scorecard_md

        BrandAuditTool->>AIInterface: generate_experience_report(...)
        AIInterface-->>BrandAuditTool: Returns experience_md

        BrandAuditTool->>BrandAuditTool: Save markdown files
    end

    BrandAuditTool-->>RunAuditUI: ✅ Audit Complete (raw files)
    RunAuditUI-->>User: Show "ADD TO DATABASE" button

    User->>RunAuditUI: Click "ADD TO DATABASE"
    RunAuditUI->>PostProcessor: process_audit_results()

    PostProcessor->>PostProcessor: 1. Validate audit output
    PostProcessor->>PostProcessor: 2. Classify page tiers
    PostProcessor->>BackfillPackager: 3. Process markdown to CSV
    BackfillPackager-->>PostProcessor: Returns structured data
    PostProcessor->>StrategicSummaryGenerator: 4. Generate strategic summary
    StrategicSummaryGenerator-->>PostProcessor: Returns summary
    PostProcessor->>MultiPersonaPackager: 5. Add to unified database
    MultiPersonaPackager-->>PostProcessor: Database updated

    PostProcessor-->>RunAuditUI: ✅ Processing Complete
    RunAuditUI->>RunAuditUI: Clear cache (st.cache_data.clear())
    RunAuditUI-->>User: "New data available - navigate to dashboard"

    User->>Dashboard: Navigate to other pages
    Dashboard-->>User: Shows new audit data immediately
```

## 4. Error Handling

- **Network Errors:** The `scraper.py` module handles basic errors, but the primary resilience comes from its cache-first approach during development.
- **AI API Errors:** The `ai_interface.py` module implements a retry mechanism for transient API failures.
- **Parsing Errors:** The `SummaryGenerator` includes a robust JSON cleaning function (`_extract_json_from_response`) and a `try-except` block to prevent crashes from malformed AI responses, ensuring the program can complete even if the final qualitative summary fails.

## 5. Strategic Summary Generation Functional Requirements

The summary generation process fulfills the following requirements:

- **FS-5.1:** The system shall generate a single, consolidated strategic summary report after all individual URL audits for a persona are complete.
- **FS-5.2 (Quantitative):** The system parses all generated `_hygiene_scorecard.md` files to aggregate scores, calculate averages for each tier, and identify top/bottom performing pages.
- **FS-5.3 (Qualitative):** The system concatenates all `_experience_report.md` files and uses the `AIInterface` to perform a thematic analysis, generating an executive summary, key strengths, and key weaknesses.
- **FS-5.4 (Reporting):** The system uses a Jinja2 template (`summary_template.md`) to format the aggregated quantitative and qualitative data into a final `Strategic_Summary.md` file.

## 6. Enhanced UX Requirements (Phase 2)

### 6.1 Executive Dashboard Requirements

- **FS-6.1 (Executive Landing):** The system shall provide a story-driven executive dashboard as the default landing experience with brand health score, AI-generated summary, and top 3 wins/risks.
- **FS-6.2 (Derived Metrics):** The system shall calculate and display enhanced metrics including brand_health_index, impact_score, trust_gap, and quick_win_flag across all data outputs.
- **FS-6.3 (Progressive Disclosure):** The system shall implement progressive disclosure with 5 focused sections: Executive Dashboard → Persona Storyboards → Action Roadmap → Evidence Explorer → System Settings.
- **FS-6.4 (Action Orientation):** The system shall provide actionable insights with owner assignment, target dates, and progress tracking for all recommendations.

### 6.2 Enhanced Data Model Requirements

- **FS-6.5 (Brand Health Index):** The system shall calculate a composite brand health index using the formula: hygiene*score * 0.60 + positive*sentiment_pct * 0.25 + engagement_rate \* 0.15.
- **FS-6.6 (Impact Scoring):** The system shall calculate impact scores for all criteria and recommendations using severity × frequency × business_value methodology.
- **FS-6.7 (Quick Win Identification):** The system shall automatically flag recommendations as quick wins when complexity ≤ 2 AND impact_score ≥ 7.0.
- **FS-6.8 (Trust Gap Analysis):** The system shall calculate trust gaps based on trust-related criteria performance: (10 - average_trust_score) / 10.

### 6.3 User Experience Requirements

- **FS-6.9 (Time to Insight):** The executive dashboard shall enable understanding of brand health, persona sentiment, and priority actions within 60 seconds.
- **FS-6.10 (Visual Hierarchy):** The system shall implement card-based design with hero metrics, insight cards, and progressive detail disclosure.
- **FS-6.11 (Color Psychology):** The system shall use consistent color coding: Green (success/positive), Amber (caution/mixed), Red (risk/negative), Blue (information), Purple (AI insights).
- **FS-6.12 (Responsive Design):** The dashboard shall adapt to different screen sizes and maintain usability across desktop and tablet devices.
