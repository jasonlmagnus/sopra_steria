# Implementation Plan: Persona Experience & Brand Audit Tool

This document breaks down the development work for the tool into a prioritized, task-based plan.

---

## **PHASE 1: Core Persona Experience Report (COMPLETE)**

_This phase focused on building the end-to-end pipeline for the primary goal: generating the Persona Experience Report._

- [x] **Project Setup**: Virtual environment, dependencies, `.env`.
- [x] **Initial Scaffolding**: `audit_tool/` directory and empty module files.
- [x] **Core Scraper Implementation**: `Scraper` class with `fetch_page`.
- [x] **Core AI & Narrative Generator Implementation**: `AIInterface` with `generate_narrative`, `NarrativeGenerator` class.
- [x] **Core Reporting Implementation**: `Reporter` class with a basic save method.
- [x] **Main Application Wiring**: `main.py` with `argparse`, component orchestration.

---

## **PHASE 2: Brand Hygiene Scorecard (COMPLETE)**

_This phase implemented the tool's second core output: a deterministic, methodology-driven Brand Hygiene Scorecard._

- [x] **Scraper Enhancement for Objective Data**: Implemented objective checks.
- [x] **Methodology Parser & Rules Engine**: `MethodologyParser` and `Criterion`, `Tier`, `Methodology` dataclasses.
- [x] **Scorecard Generator Implementation**: `ScorecardGenerator` with tier classification and AI-assisted scoring.
- [x] **Reporter Enhancement for Dual Output**: `Jinja2` integration and `scorecard_template.md`.
- [x] **Final Integration in Main**: Added `ScorecardGenerator` to the main execution flow.

---

## **PHASE 3: Bug Fixing & Stabilization (COMPLETE)**

_This phase addressed critical bugs and stability issues to ensure the tool is reliable and produces accurate, high-quality output._

- [x] **Robustness**:
  - [x] Added comprehensive error handling and logging throughout the application.
  - [x] Implemented a retry mechanism for failed API calls in `ai_interface.py`.
  - [x] Implemented robust JSON parsing in `SummaryGenerator` to prevent crashes from malformed AI responses.
- [x] **Core Logic Correction**:
  - [x] **Fixed Persona-Ignoring Bug**: Overhauled the `generate_narrative` prompt in `ai_interface.py` to correctly and forcefully adopt the persona's point of view, removing conflicting instructions.
  - [x] **Fixed Template Crashing Bugs**: Corrected multiple `UndefinedError` crashes in Jinja2 templates by aligning the variables in the templates (`scorecard_template.md`, `summary_template.md`) with the data objects passed from `reporter.py`.
- [x] **Usability**:
  - [x] Added support for batch processing a list of URLs from a file (`--file` argument).
  - [x] Added progress indicators (`tqdm`) for long-running processes.
  - [x] Implemented a file-based caching layer for scraped content to speed up iterative testing.

---

## **PHASE 4: Strategic Summary Generation (COMPLETE)**

_This phase introduced the final component: a generator that synthesizes all individual audit reports into a single, high-level strategic summary._

- [x] **Summary Generator Scaffolding**:
  - [x] In `audit_tool/generators.py`, created the `SummaryGenerator` class.
  - [x] In `audit_tool/reporter.py`, added the `write_summary_report` method.
  - [x] Created the Jinja2 template: `templates/summary_template.md`.
- [x] **Quantitative Data Aggregation**:
  - [x] The `SummaryGenerator` now parses all `_hygiene_scorecard.md` files.
  - [x] It extracts scores, calculates tier averages, and identifies top/bottom pages.
- [x] **Qualitative Thematic Synthesis**:
  - [x] The `SummaryGenerator` parses all `_experience_report.md` files.
  - [x] It uses a dedicated `generate_strategic_summary` method in the `AIInterface` to perform thematic analysis and generate a JSON summary.
- [x] **Final Integration in Main**:
  - [x] After the main URL loop, the `SummaryGenerator` is called to create the summary object, which is then saved by the `Reporter`.

---

## **PHASE 5: UI/UX Development (COMPLETE)**

_This next phase will focus on building a user-friendly interface for the tool, moving beyond the command line._

- **Task 1: Static UI Layout**

  - **Implementation:** Create the `dashboard/streamlit_dashboard.py` file. Lay out the static Streamlit components: `st.sidebar` with `st.title`, `st.file_uploader`, `st.text_area`, and `st.button`. Create the main panel with a title and a placeholder for the results.
  - **Testing:** Run the script and visually confirm that all static elements appear in the correct places.

- **Task 2: State Management and Input Logic**

  - **Implementation:** Initialize `st.session_state` to track `is_running` (default `False`). Implement the logic to disable the "Run Audit" button if the persona file or URL text area is empty, or if `st.session_state.is_running` is `True`.
  - **Testing:** Verify the button is disabled initially. Add a persona and URLs and confirm it becomes enabled.

- **Task 3: Backend Process Execution**

  - **Implementation:** Write the core logic for the "Run Audit" button. On click, it should set `is_running` to `True`. It must save the uploaded persona and the text-area URLs to temporary files within a `temp/` directory. Use `subprocess.Popen` to launch the `python -m audit_tool.main` script with the correct file paths.
  - **Testing:** Click the button and verify that the `temp/` directory and temporary files are created, and that the Python subprocess starts (you can check this in your system's activity monitor).

- **Task 4: Real-time Log Streaming**

  - **Implementation:** Enhance the `subprocess` logic to capture `stdout` in real time. Create the "Audit Log" expander and a `st.code` block inside it. As the subprocess runs, read its output line-by-line and append it to the code block.
  - **Testing:** Run an audit and confirm that the log messages from the tool appear live in the "Audit Log" expander.

- **Task 5: Results Discovery and Parsing**

  - **Implementation:** After the subprocess completes, write a helper function that scans the `audit_outputs/` directory. The function should identify the `Strategic_Summary.md` and then find all `_experience_report.md` and `_hygiene_scorecard.md` files, grouping them by a common URL slug. It should return a structured dictionary of the results.
  - **Testing:** Run an audit. After it finishes, manually check that the helper function correctly identifies and groups all the generated report files.

- **Task 6: Dynamic Results Display**

  - **Implementation:** Based on the dictionary from the previous step, render the results. First, display the `Strategic_Summary.md` in a dedicated expander. Then, loop through the grouped results and create an `st.expander` for each URL. Inside each, use `st.tabs` to display the content of the narrative and scorecard reports using `st.markdown`.
  - **Testing:** Run an audit and verify that all results are displayed correctly, the expanders and tabs work, and the markdown content is rendered properly.

- **Task 7: Final Polish & Cleanup**
  - **Implementation:** Add a `finally` block or similar mechanism to ensure the temporary files are deleted after the audit run, even if it fails. Add user-friendly error messages if the subprocess returns a non-zero exit code. Reset the `is_running` state.
  - **Testing:** Run a successful audit and confirm the temp files are deleted. Manually introduce an error into the backend script and run an audit to confirm the error is handled gracefully and the UI resets.

---

## **PHASE 6: Future Enhancements (TO DO)**

_This phase outlines potential future work to further improve the tool._

- **[ ] Task 1: Historical Trend Analysis**

  - **Goal:** Allow users to compare audit results over time to track improvements.
  - **Implementation:**
    - Modify the `Reporter` to save outputs in timestamped directories.
    - Add a UI component to select and compare two different audit runs.
    - Visualize score changes and highlight new or resolved issues.

- **[ ] Task 2: Advanced Visualization**

  - **Goal:** Make the quantitative data easier to digest.
  - **Implementation:**
    - Integrate a charting library (e.g., Altair, Vega-Lite) into the Streamlit dashboard.
    - Create bar charts for tier scores and radar charts for individual criteria scores.

- **[ ] Task 3: Deployment**
  - **Goal:** Make the tool easily accessible to non-technical users.
  - **Implementation:**
    - Write a Dockerfile for the application.
    - Create a deployment script or guide for deploying the Streamlit app to a cloud service (e.g., Streamlit Community Cloud, AWS, Google Cloud).
