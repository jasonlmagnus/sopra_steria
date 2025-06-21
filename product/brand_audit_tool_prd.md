## Product Requirements Document: Persona Experience & Brand Audit Tool

**Status: ✅ FULLY DELIVERED - All requirements implemented and deployed**

### 1. Introduction & Background

**Problem:** The initial brand audit process, whether manual or AI-driven, revealed two distinct needs that were in tension: 1) A subjective, qualitative need to understand the **persona's experience** of our web properties, and 2) An objective, quantitative need to enforce **brand consistency and technical hygiene**. Attempting to conflate these two goals into a single score proved ineffective, unreliable, and failed to serve either purpose well.

**Vision:** To create a dual-output tool that serves both needs independently from a single execution. The tool's primary purpose is to generate a rich, qualitative **"Persona Experience Report"** to inform marketing and strategy. Its secondary function is to produce a deterministic, quantitative **"Brand Hygiene Scorecard"** to guide the web and brand teams.

**Current Status:** ✅ **VISION ACHIEVED** - The tool now generates both persona-aware experience reports and YAML-driven hygiene scorecards from a single execution, with additional strategic summary capabilities.

### 2. Goals & Objectives

- **Primary Goal:** To simulate a target persona's experience of a given URL, generating a narrative report that captures their impressions, emotional response, and likely next actions.
- **Secondary Goal:** To automate a brand hygiene audit based on the objective rules from `audit_method.md`, producing a consistent and repeatable scorecard.
- **Tertiary Goal:** To provide both the strategic marketing team and the operational brand team with dedicated, fit-for-purpose artifacts from a single, efficient process.

### 3. User Personas

- **The Strategist / Marketer:** This user needs to understand the _why_ behind customer behavior. They value the narrative, the voice of the customer, and qualitative insights that can drive better content and messaging. The **Persona Experience Report** is for them.
- **The Brand / Web Manager:** This user needs to ensure consistency, quality, and compliance across all web properties. They value clear, actionable, data-driven metrics to identify and fix issues. The **Brand Hygiene Scorecard** is for them.

### 4. Functional Requirements

The tool will be a script that accepts a URL and a persona, then generates two distinct output files.

| Feature ID   | User Story                                                                                             | Core Functionality                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| :----------- | :----------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **INPUT-01** | As a user, I want to provide the tool with a single URL and a persona file to analyze.                 | - The tool accepts a target URL string and a path to a persona `.md` file.                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **INPUT-02** | As a user, I want to provide a file containing a list of URLs to audit a batch of pages at once.       | - The tool also accepts a `--file` argument pointing to a text file with one URL per line.                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **PROC-01**  | As a user, I want the tool to intelligently scrape the content and structure of the page.              | - Uses a robust web scraping library (e.g., Python with Requests/BeautifulSoup).<br>- Extracts all human-readable text.<br>- Performs objective checks (e.g., logo presence, tagline, 404s, broken links) and stores them as "ground truth" data.                                                                                                                                                                                                                                                                         |
| **OUTPUT-A** | As a Strategist, I want a rich **Persona Experience Report** that tells me a story.                    | - **AI-Driven Narrative Generation:** Makes a comprehensive AI call with the persona and page text.<br>- **Prompt Focus:** "You are [Persona]. Write a first-person narrative about your experience."<br>- **Artifact:** Generates a `[url_slug]_experience_report.md` file.                                                                                                                                                                                                                                              |
| **OUTPUT-B** | As a Brand Manager, I want a quantitative **Brand Hygiene Scorecard** that is accurate and actionable. | - **Code-Driven Scoring:** Programmatically scores all objective criteria based on the ground truth data. Applies all gating rules deterministically.<br>- **AI-Assisted Subjective Scoring:** Makes a second, highly constrained AI call for purely subjective scores (e.g., Emotional Resonance).<br>- **Final Calculation:** Combines objective and subjective scores in code to produce a final, weighted score.<br>- **Artifact:** Generates a `[url_slug]_hygiene_scorecard.md` file with a detailed scoring table. |
| **OUTPUT-C** | As a Strategist, I want a **Strategic Summary Report** that synthesizes all findings for a persona.    | - **Post-Processing Step:** After all individual URLs are audited, the tool aggregates all generated reports.<br>- **Quantitative Aggregation:** Parses all scorecards to calculate average scores and find top/bottom performers.<br>- **Qualitative Synthesis:** Uses an AI call to perform a thematic analysis of all narrative reports, identifying key strengths and weaknesses.<br>- **Artifact:** Generates a single `Strategic_Summary.md` file for the entire batch.                                             |

### 5. Non-Functional Requirements

- **Reliability:** The tool must be resilient to common errors (API failures, bad data) and complete its run without crashing.
- **Maintainability:** The scoring logic for the hygiene scorecard should remain configurable by editing the `audit_method.md` file where possible.
- **Performance:** A full analysis for a single URL (generating both reports) should complete in under 2 minutes.
- **Error Handling:** The tool must gracefully handle failed URL fetches (e.g., timeouts, 404s) and report them clearly in the final audit.

### 6. Technical Implementation Sketch

- **Platform:** Command-line application built in Python.
- **Orchestration:** A main script will orchestrate the dual-output workflow:
  1. Call a `scraper` module to get page text and objective facts.
  2. In parallel (or sequentially):
     - Call an `ai_narrative` module to generate the Experience Report.
     - Call a `scorer` module (which contains a constrained `ai_subjective_score` call) to generate the Hygiene Scorecard.
  3. Save both outputs to disk.
- **Dependencies:**
  - `Playwright` / `BeautifulSoup4`: For scraping.
  - An LLM provider's Python SDK (e.g., `anthropic`).
  - `Jinja2`: For templating the Markdown outputs.

### 7. Success Metrics

- **Primary Metric (Qualitative):** The Persona Experience Reports are consistently rated as "insightful" and "actionable" by the marketing and strategy teams.
- **Secondary Metric (Quantitative):** The Brand Hygiene Scorecard is 100% compliant with the objective rules in the methodology and is used by the web team to track and fix issues.
- **Efficiency:** The end-to-end process is significantly faster and more reliable than previous attempts.

### 8. Out of Scope (Future Work)

- A graphical user interface (GUI).
- Saving and comparing historical audit results.
- Real-time editing of the audit methodology within the tool.
