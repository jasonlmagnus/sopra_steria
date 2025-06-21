import streamlit as st
import os
import subprocess
import tempfile
import re
import glob
import shutil

def get_persona_name(persona_content: str) -> str:
    """Extracts the persona name from the markdown content to find the output dir."""
    match = re.search(r"P\d+", persona_content)
    if match:
        return match.group(0)
    # Fallback for safe directory naming if no P-number is found
    return "default_persona"

def run_audit(persona_file_path, urls_file_path):
    """Runs the audit tool as a subprocess."""
    command = [
        "python",
        "-m",
        "audit_tool.main",
        "--persona",
        persona_file_path,
        "--file",
        urls_file_path,
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8'
    )
    return process

def find_and_parse_reports(persona_name: str) -> dict:
    """Finds all generated report files and groups them by URL."""
    output_dir = os.path.join("audit_outputs", persona_name)
    if not os.path.isdir(output_dir):
        return None

    results = {
        "summary": None,
        "pages": {}
    }

    all_files = glob.glob(os.path.join(output_dir, "*.md"))
    
    for f in all_files:
        filename = os.path.basename(f)
        if filename == "Strategic_Summary.md":
            results["summary"] = f
        elif filename.endswith("_experience_report.md"):
            slug = filename.replace("_experience_report.md", "")
            if slug not in results["pages"]:
                results["pages"][slug] = {}
            results["pages"][slug]["experience"] = f
        elif filename.endswith("_hygiene_scorecard.md"):
            slug = filename.replace("_hygiene_scorecard.md", "")
            if slug not in results["pages"]:
                results["pages"][slug] = {}
            results["pages"][slug]["scorecard"] = f
    
    return results

def main():
    st.set_page_config(layout="wide")

    # --- SESSION STATE INITIALIZATION ---
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""

    st.sidebar.title("Audit Configuration")

    persona_file = st.sidebar.file_uploader(
        "1. Upload Persona File",
        type=['md'],
        disabled=st.session_state.is_running
    )

    st.sidebar.subheader("2. Provide URLs to Audit")
    
    def on_paste():
        st.session_state.urls_text = st.session_state.pasted_urls

    def on_upload():
        if st.session_state.uploaded_url_file:
            file_content = st.session_state.uploaded_url_file.getvalue().decode("utf-8")
            urls_from_file = re.findall(r'https?://[^\s|)]+', file_content)
            if urls_from_file:
                st.session_state.urls_text = "\n".join(urls_from_file)
        else:
            st.session_state.urls_text = ""

    tab1, tab2 = st.sidebar.tabs(["Paste List", "Upload File"])

    with tab1:
        st.text_area(
            "Enter one URL per line...",
            key="pasted_urls",
            on_change=on_paste,
            height=200,
            disabled=st.session_state.is_running,
        )

    with tab2:
        st.file_uploader(
            "Upload a .txt or .md file with one URL per line.",
            key="uploaded_url_file",
            on_change=on_upload,
            type=['txt', 'md'],
            disabled=st.session_state.is_running
        )

    # Disable button if inputs are missing or if the audit is already running
    disable_run_button = not persona_file or not st.session_state.urls_text or st.session_state.is_running
    
    if st.sidebar.button("Run Audit", disabled=disable_run_button):
        st.session_state.is_running = True
        st.session_state.results = None # Clear previous results
        
        temp_dir = tempfile.mkdtemp(prefix="audit_")
        log_expander = st.expander("Audit Log", expanded=True)
        log_container = log_expander.code(f"Preparing audit...", language="log")

        try:
            # Save uploaded files to the temporary directory
            persona_content = persona_file.getvalue().decode("utf-8")
            persona_file_path = os.path.join(temp_dir, persona_file.name)
            with open(persona_file_path, "w", encoding="utf-8") as f:
                f.write(persona_content)

            urls_file_path = os.path.join(temp_dir, "urls_to_audit.txt")
            with open(urls_file_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.urls_text)

            st.session_state.persona_name = get_persona_name(persona_content)

            # --- RUN AUDIT & STREAM LOGS ---
            log_container.text(f"Starting audit for {st.session_state.persona_name}...")
            
            log_content = ""
            process = run_audit(persona_file_path, urls_file_path)

            for line in iter(process.stdout.readline, ''):
                log_content += line
                log_container.text(log_content)
            
            process.wait()
            # --- END AUDIT ---
            
            if process.returncode == 0:
                st.session_state.results = find_and_parse_reports(st.session_state.persona_name)
                st.success("Audit complete!", icon="✅")
            else:
                st.error("Audit failed. Check the log for details.", icon="🚨")
                st.session_state.results = None

        except Exception as e:
            st.error(f"An unexpected error occurred: {e}", icon="🚨")
        finally:
            st.session_state.is_running = False
            # Clean up the temporary directory
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
            st.rerun()

    st.title("Audit Results")

    # This top-level check ensures the main panel doesn't try to render
    # while the audit logic is running in the script's main flow.
    if not st.session_state.is_running:
        if st.session_state.results:
            # --- DISPLAY SUMMARY REPORT ---
            if st.session_state.results["summary"]:
                with st.expander("⭐ Strategic Summary Report", expanded=True):
                    with open(st.session_state.results["summary"], 'r', encoding='utf-8') as f:
                        st.markdown(f.read())
            else:
                st.warning("Strategic Summary report not found.")

            # --- DISPLAY INDIVIDUAL PAGE REPORTS ---
            st.subheader("Individual Page Audits")
            for slug, reports in st.session_state.results["pages"].items():
                with st.expander(f"📄 {slug}"):
                    exp_tab, score_tab = st.tabs(["Experience Report", "Hygiene Scorecard"])
                    
                    if "experience" in reports:
                        with exp_tab:
                            with open(reports["experience"], 'r', encoding='utf-8') as f:
                                st.markdown(f.read())
                    else:
                        exp_tab.warning("Experience report not found.")

                    if "scorecard" in reports:
                        with score_tab:
                            with open(reports["scorecard"], 'r', encoding='utf-8') as f:
                                st.markdown(f.read())
                    else:
                        score_tab.warning("Scorecard not found.")
        else:
            st.info("Results will appear here after the audit is complete.", icon="ℹ️")

if __name__ == "__main__":
    main() 