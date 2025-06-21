# UI Specification: Brand Audit Tool

This document outlines the specification for a web-based user interface for the Persona Experience & Brand Audit Tool. The goal is to create an intuitive, user-friendly application that encapsulates the functionality of the underlying command-line tool.

---

## 1. Overview

The UI will be built as a **Streamlit** application. This choice leverages the existing Python backend and allows for rapid development of a clean, interactive interface. The application will guide the user through the process of setting up and running an audit, and will present the results in a clear and accessible manner.

The main script for this UI will be `streamlit_ui.py` at the root of the project.

---

## 2. Key Features & Layout

The application will have a simple two-column layout.

### **Sidebar (Input Panel)**

The left-hand sidebar will contain all the user inputs required to run an audit.

- **Title:** "Audit Configuration"
- **Persona Upload:**
  - A `st.file_uploader` component.
  - Label: "1. Upload Persona File"
  - Accepts only `.md` files.
- **URL Input:**
  - A `st.text_area` component.
  - Label: "2. Enter URLs to Audit"
  - A placeholder text: `Enter one URL per line...`
  - Height should be sufficient for ~10 URLs.
- **Run Button:**
  - A `st.button` component.
  - Label: "Run Audit"
  - This button will be the primary trigger for the audit process. It should be disabled while an audit is running.

### **Main Panel (Output & Results)**

The main area of the page will be dedicated to displaying the status of the audit and the final results.

- **Title:** "Audit Results"
- **Progress Display:**
  - A section to show the real-time status of the audit.
  - This can be implemented using a `st.expander` titled "Audit Log" that is collapsed by default.
  - Inside the expander, a `st.code` block will display the live `stdout` from the `main.py` script's logging.
- **Results Section:**
  - This section will appear or be populated once the audit is complete.
  - It will display a list of the generated reports, grouped by the URL that was audited.
  - For each URL, a `st.expander` should be created.
    - The expander title should be the URL.
    - Inside the expander, there will be two sub-sections or links:
      1.  **Experience Report:** A link to view the generated narrative report. Clicking it could display the markdown content within the app using `st.markdown`.
      2.  **Hygiene Scorecard:** A link to view the scorecard report, also displayed using `st.markdown`.
- **Summary Report Display:**
  - At the top of the main panel, above the individual results, there will be a section for the summary.
  - A `st.expander` titled "Strategic Summary Report" will contain the full text of the `Strategic_Summary.md` file, rendered as markdown. This should only be visible once an audit is complete.

---

## 3. User Flow

1.  The user runs `streamlit run streamlit_ui.py` to launch the application.
2.  The user is presented with the UI. The "Run Audit" button is visible but might be disabled until both a persona and URLs are provided.
3.  The user uploads a persona markdown file via the sidebar widget.
4.  The user pastes a list of URLs into the text area in the sidebar.
5.  The "Run Audit" button becomes active. The user clicks it.
6.  The "Run Audit" button becomes disabled to prevent multiple simultaneous runs.
7.  The "Audit Log" expander in the main panel starts displaying the logging output from the tool as it runs.
8.  When the audit process for all URLs is complete, the main panel is updated:
    - The "Strategic Summary Report" expander appears at the top, displaying the summary.
    - The series of expanders for each individual URL appears below it.
9.  The user can click on an expander for a URL to see links to the two generated reports.
10. Clicking on a report link will display the content of the markdown file directly within the Streamlit application.
11. The "Run Audit" button is re-enabled.

---

## 4. Prompt for UI Generation

Here is a prompt that can be used to generate the `streamlit_dashboard.py` file. It is aligned with the plan above.

**Prompt:**

> You are an expert Streamlit developer. Create a Python script named `streamlit_dashboard.py` that provides a web UI for a command-line tool.
>
> **Tool Background:**
> The command-line tool is invoked like this: `python -m audit_tool.main --file <path_to_urls_file> --persona <path_to_persona_file>`. It processes a file of URLs against a given persona file and generates a `Strategic_Summary.md` and two markdown reports for each URL inside a persona-specific subdirectory of `audit_outputs/` (e.g., `audit_outputs/P1/`). The tool logs its progress to standard output.
>
> **UI Requirements:**
>
> 1.  **Framework:** Use Streamlit.
> 2.  **Layout:** Create a sidebar for inputs and a main panel for outputs.
> 3.  **Sidebar Inputs:**
>     - A `st.file_uploader` to upload the persona `.md` file.
>     - A `st.text_area` for the user to paste a list of URLs (one per line).
>     - A `st.button` labeled "Run Audit". This button should be disabled if no persona is uploaded or no URLs are provided. It should also be disabled while the audit is running.
> 4.  **Backend Logic:**
>     - When the "Run Audit" button is clicked, the script must:
>       a. Save the content of the uploaded persona file to a temporary file (e.g., in a `temp/` directory).
>       b. Save the URLs from the text area to another temporary file.
>       c. Use Python's `subprocess.Popen` to call the command-line tool: `python -m audit_tool.main --file <temp_url_file> --persona <temp_persona_file>`. Ensure the command runs in a way that you can capture its `stdout` in real time.
>       d. Create a `temp/` directory if it doesn't exist for these temporary files.
> 5.  **Main Panel Outputs:**
>     - **Live Log:** Create a `st.expander` labeled "Audit Log". Inside it, display the `stdout` from the subprocess in real time as the audit runs.
>     - **Results Display:** After the subprocess finishes, find all generated report files in the persona-specific `audit_outputs/` subdirectory.
>     - **Summary First:** Find, read, and display the `Strategic_Summary.md` at the top of the results area in an expander.
>     - **Grouped Reports:** Group the remaining reports by the original URL. A good way to do this is to parse the filenames.
>     - For each audited URL, display a `st.expander` with the URL as the title.
>     - Inside each URL expander, provide two `st.tabs`, one for the "Experience Report" and one for the "Hygiene Scorecard".
>     - Read the content of the corresponding markdown files and display them within their tabs using `st.markdown`.
>
> **Code Style:**
>
> - The code should be clean, well-commented, and robust.
> - Include necessary imports like `streamlit`, `os`, `subprocess`, `tempfile`, and `time`.
> - Clean up temporary files after the audit is complete.
> - Add session state (`st.session_state`) to manage the state of the application (e.g., `is_running`, `results`).
