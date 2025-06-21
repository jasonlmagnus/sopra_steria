# Functional Specification: Persona Experience & Brand Audit Tool

## 1. Overview

This document provides a functional specification for the Persona Experience & Brand Audit Tool. It describes the system's behavior, features, and component interactions.

The system is a Python command-line application that audits a list of URLs from the perspective of a defined persona. For a given persona, it produces:

1.  A **Persona Experience Report** for each URL.
2.  A **Brand Hygiene Scorecard** for each URL.
3.  A single, consolidated **Strategic Summary** report that aggregates findings from all audited URLs.

### 1.1. High-Level Architecture

The application follows a modular, orchestrated design. A central `main.py` script coordinates the work of specialized modules for scraping, analysis, scoring, and reporting in a clear, linear flow.

- **Technology Stack:** Python 3.10+, Requests, BeautifulSoup4, Anthropic SDK, Jinja2.
- **Execution Flow:**
  1.  Initialize with a persona file and a file containing a list of URLs.
  2.  Load the scoring `Methodology` from disk.
  3.  **Loop through URLs:** For each URL:
      a. **Scrape:** Collect page content.
      b. **Generate Narrative:** Create the persona-driven qualitative report.
      c. **Generate Scorecard:** Create the quantitative scorecard based on the methodology.
      d. **Write Reports:** Save the two generated reports to disk.
  4.  **Summarize:** After the loop, aggregate all generated reports to produce and save a final `Strategic_Summary.md`.

## 2. Component Specification

### 2.1. Main Orchestrator (`main.py`)

- **Purpose:** Entry point and controller of the application.
- **Interface:** Accepts command-line arguments: `python -m audit_tool.main --persona <path> --file <path>`.
- **Logic:**
  1.  Parses arguments.
  2.  Initializes all necessary components (`Scraper`, `AIInterface`, `MethodologyParser`, `NarrativeGenerator`, `ScorecardGenerator`, `SummaryGenerator`, `Reporter`).
  3.  Loops through the URLs provided in the file. Inside the loop, it calls the appropriate generators and reporter methods for each URL.
  4.  After the loop, it calls the `SummaryGenerator` and `Reporter` to create the final summary.

### 2.2. Scraper Module (`scraper.py`)

- **Purpose:** To fetch web content.
- **Functions:**
  - `fetch_page(url: str) -> PageData`:
    - Uses `requests` and `BeautifulSoup` to get page content.
    - Implements a simple file-based cache to speed up development.
    - Returns a `PageData` object containing the URL and raw text content.

### 2.3. AI Module (`ai_interface.py`)

- **Purpose:** To abstract all interactions with the Anthropic LLM API.
- **Functions:**
  - `generate_narrative(persona_content: str, page_text: str) -> str`:
    - Constructs a detailed prompt instructing the AI to adopt the specified persona and analyze the provided text from that point of view.
    - Returns the generated Markdown narrative as a string.
  - `get_subjective_score(criterion_name: str, page_text: str) -> float`:
    - Constructs a highly-constrained prompt asking for a single numerical score (0.0-10.0) for a given criterion.
    - Returns a single float.
  - `generate_strategic_summary(compiled_text: str) -> str`:
    - Takes the concatenated text of all narrative reports for a persona.
    - Asks the AI to perform a thematic analysis and return a raw, valid JSON object containing an `executive_summary`, `key_strengths`, and `key_weaknesses`.

### 2.4. Generators Module (`generators.py`)

- **Purpose:** To create the content for all reports.
- **Classes:**
  - `NarrativeGenerator`: A lightweight wrapper that calls `ai_interface.generate_narrative`.
  - `ScorecardGenerator`: Classifies the page (e.g., Onsite Tier 1), then iterates through the relevant criteria from the methodology, calling `ai_interface.get_subjective_score` for each. It calculates a final weighted score and returns a structured `Scorecard` object.
  - `SummaryGenerator`: Orchestrates the final summary. It has private methods to parse all generated scorecards and narrative reports from the filesystem. It calls `ai_interface.generate_strategic_summary` to get the qualitative analysis and then aggregates all data into a `SummaryReport` object. It includes a robust helper function to parse the AI's JSON output.

### 2.5. Reporting Module (`reporter.py`)

- **Purpose:** To write the generated report objects to markdown files using Jinja2 templates.
- **Functions:**
  - `write_narrative_report(...)`: Writes the narrative string to a `.md` file.
  - `write_scorecard(...)`: Renders a `Scorecard` object using the `scorecard_template.md`.
  - `write_summary_report(...)`: Renders a `SummaryReport` object using the `summary_template.md`.

## 3. Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant Scraper
    participant Generators
    participant Reporter
    participant AIInterface

    User->>Main: Executes with --persona and --file
    Main->>Main: Initializes all components

    loop For Each URL
        Main->>Scraper: fetch_page(url)
        Scraper-->>Main: Returns PageData object

        Main->>Generators: create_report(persona, page_data)
        Generators->>AIInterface: generate_narrative(persona, text)
        AIInterface-->>Generators: Returns narrative_string

        Main->>Generators: create_scorecard(page_data)
        Generators->>AIInterface: get_subjective_score(...)
        AIInterface-->>Generators: Returns score
        Generators-->>Main: Returns Scorecard object

        Main->>Reporter: write_narrative_report(...)
        Main->>Reporter: write_scorecard(...)
    end

    Main->>Generators: create_summary()
    Generators->>AIInterface: generate_strategic_summary(...)
    AIInterface-->>Generators: Returns summary_json
    Generators-->>Main: Returns SummaryReport object

    Main->>Reporter: write_summary_report(...)
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
