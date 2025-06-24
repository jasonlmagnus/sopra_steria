import streamlit as st
from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_page_header,
    create_status_card,
    create_metric_card,
    show_success,
    show_warning,
    show_error,
    show_info,
    get_chart_config,
    apply_chart_styling,
    display_dataframe,
    create_columns,
    create_tabs,
    create_expander
)
    apply_perfect_styling,
    create_page_header,
    create_status_card,
    show_success,
    show_warning,
    show_error,
    show_info
)
import os
import subprocess
import tempfile
import re
import glob
import shutil
import sys
from pathlib import Path

# Add audit_tool to path for imports

def get_persona_name(persona_content: str) -> str:
    """Extracts the full persona name from the markdown content."""
    lines = persona_content.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        if first_line.startswith("Persona Brief:"):
            return first_line.replace("Persona Brief:", "").strip()
        elif first_line and not first_line.startswith('#'):
            return first_line
    # Fallback to P-number for directory safety if name extraction fails
    match = re.search(r"P\d+", persona_content)
    if match:
        return match.group(0)
    return "default_persona"

def run_audit(persona_file_path, urls_file_path, output_dir, model_provider="anthropic"):
    """Runs the audit tool as a subprocess with YAML methodology."""
    command = [
        "python",
        "-m",
        "audit_tool.main",
        "--urls",
        urls_file_path,
        "--persona",
        persona_file_path,
        "--output",
        output_dir,
        "--model",
        model_provider
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
    st.set_page_config(
        page_title="Sopra Steria Brand Audit Runner",
        page_icon="🚀",
        layout="wide"
    )

# SINGLE SOURCE OF TRUTH - REPLACES ALL 2,228 STYLING METHODS
apply_perfect_styling()

# Create standardized page header
create_page_header("Dashboard Page", "")

    # --- SESSION STATE INITIALIZATION ---
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'results' not in st.session_state:
        st.session_state.results = None
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "openai"  # Default to cost-effective option

    # Header
    st.title("🚀 Sopra Steria Brand Audit Runner")
    st.markdown("**YAML-Driven Methodology** with **Dual AI Provider Support**")
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎯 Audit Configuration")
        
        # Model Selection
        st.markdown("### 🤖 AI Model Provider")
        
        model_options = {
            "openai": "🔥 OpenAI GPT-4.1-Mini (Cost Effective)",
            "anthropic": "🧠 Anthropic Claude-3-Opus (Premium Quality)"
        }
        
        selected_model = st.radio(
            "Choose your AI model:",
            options=list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=0,  # Default to OpenAI
            disabled=st.session_state.is_running,
            help="OpenAI is more cost-effective for high-volume audits. Anthropic provides premium quality analysis."
        )
        
        st.session_state.selected_model = selected_model
        
        # Show cost information
        if selected_model == "openai":
            st.info("💰 **Cost Effective Choice** - GPT-4.1-Mini offers excellent quality at lower cost")
        else:
            st.warning("💎 **Premium Choice** - Claude-3-Opus provides highest quality but at higher cost")
        
        st.markdown("---")
        
        # Persona Upload
        st.markdown("### 📋 Persona File")
        persona_file = st.file_uploader(
            "Upload Persona File",
            type=['md'],
            disabled=st.session_state.is_running,
            help="Upload a .md file containing your target persona definition"
        )
        
        if persona_file:
            st.success(f"✅ Loaded: {persona_file.name}")
            persona_content = persona_file.getvalue().decode("utf-8")
            persona_name = get_persona_name(persona_content)
            st.info(f"**Detected Persona:** {persona_name}")

        st.markdown("### 🌐 URLs to Audit")
        
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

        tab1, tab2 = st.tabs(["📝 Paste URLs", "📁 Upload File"])

        with tab1:
            st.text_area(
                "Enter one URL per line:",
                key="pasted_urls",
                on_change=on_paste,
                height=200,
                disabled=st.session_state.is_running,
                placeholder="https://example.com\nhttps://example.com/about\nhttps://example.com/services"
            )

        with tab2:
            st.file_uploader(
                "Upload a .txt or .md file with URLs",
                key="uploaded_url_file",
                on_change=on_upload,
                type=['txt', 'md'],
                disabled=st.session_state.is_running,
                help="Upload a file containing one URL per line"
            )

        # URL validation
        if st.session_state.urls_text:
            urls = [url.strip() for url in st.session_state.urls_text.split('\n') if url.strip()]
            valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
            
            st.markdown("#### 📊 URL Summary")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total URLs", len(urls))
            with col_b:
                st.metric("Valid URLs", len(valid_urls))
            
            if len(urls) != len(valid_urls):
                st.warning(f"⚠️ {len(urls) - len(valid_urls)} invalid URLs detected")

        # Disable button if inputs are missing or if the audit is already running
        disable_run_button = not persona_file or not st.session_state.urls_text or st.session_state.is_running
        
        st.markdown("---")
        
        # Run Audit Button
        if st.button(
            f"🚀 Run Audit with {selected_model.upper()}", 
            disabled=disable_run_button,
            use_container_width=True,
            type="primary"
        ):
            st.session_state.is_running = True
            st.session_state.results = None # Clear previous results
            st.rerun()

    with col2:
        st.subheader("📊 Audit Results & Live Log")
        
        # This top-level check ensures the main panel doesn't try to render
        # while the audit logic is running in the script's main flow.
        if st.session_state.is_running:
            st.warning(f"🔄 **Audit Running** - Using {st.session_state.selected_model.upper()}")
            
            temp_dir = tempfile.mkdtemp(prefix="audit_")
            log_expander = st.expander("📋 Live Audit Log", expanded=True)
            log_container = log_expander.empty()

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
                
                # Create output directory for this persona
                output_dir = os.path.join("audit_outputs", st.session_state.persona_name)
                os.makedirs(output_dir, exist_ok=True)

                # --- RUN AUDIT & STREAM LOGS ---
                log_container.code(f"Starting audit for {st.session_state.persona_name} using {st.session_state.selected_model.upper()}...")
                
                process = run_audit(persona_file_path, urls_file_path, output_dir, st.session_state.selected_model)

                log_lines = []
                for line in iter(process.stdout.readline, ''):
                    log_lines.append(line.rstrip())
                    if len(log_lines) > 100:  # Keep only the last 100 lines
                        log_lines = log_lines[-100:]
                    log_container.code('\n'.join(log_lines))
                
                process.wait()
                # --- END AUDIT ---
                
                if process.returncode == 0:
                    st.session_state.results = find_and_parse_reports(st.session_state.persona_name)
                    st.success("✅ Audit completed successfully!", icon="🎉")
                    st.balloons()
                else:
                    st.error("❌ Audit failed. Check the log for details.", icon="🚨")
                    st.session_state.results = None

            except Exception as e:
                st.error(f"💥 Unexpected error: {e}", icon="🚨")
            finally:
                st.session_state.is_running = False
                # Clean up the temporary directory
                if os.path.isdir(temp_dir):
                    shutil.rmtree(temp_dir)
                st.rerun()
        
        elif st.session_state.results:
            # --- DISPLAY SUMMARY REPORT ---
            if st.session_state.results["summary"]:
                with st.expander("⭐ Strategic Summary Report", expanded=True):
                    with open(st.session_state.results["summary"], 'r', encoding='utf-8') as f:
                        st.markdown(f.read())
            else:
                st.warning("Strategic Summary report not found.")

            # --- DISPLAY INDIVIDUAL PAGE REPORTS ---
            st.subheader("📄 Individual Page Audits")
            for slug, reports in st.session_state.results["pages"].items():
                with st.expander(f"🔍 {slug}"):
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
            st.info("🎯 **Ready to Run Audit**\n\nResults will appear here after the audit completes. The YAML-driven methodology will automatically:\n\n- 🏗️ **Classify pages** into Tier 1/2/3 based on URL patterns\n- ⚖️ **Apply appropriate criteria** with proper brand/performance/authenticity weighting\n- 📊 **Generate strategic summary** with methodology-driven insights", icon="ℹ️")

if __name__ == "__main__":
    main() 