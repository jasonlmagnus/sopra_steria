#!/usr/bin/env python3
"""
Run Audit Page
Integrated audit runner functionality within the main dashboard
"""

import streamlit as st
import os
import subprocess
import tempfile
import re
import glob
import shutil
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def get_persona_name(persona_content: str) -> str:
    """Extracts the persona name from the markdown content to find the output dir."""
    match = re.search(r"P\d+", persona_content)
    if match:
        return match.group(0)
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

def main():
    st.title("🚀 Run Brand Audit")
    
    # Initialize session state
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""
    
    st.markdown("""
    ### 🎯 Launch New Brand Audit
    
    Upload a persona file and provide URLs to analyze. The audit will generate:
    - **Strategic Summary** - High-level insights and recommendations
    - **Experience Reports** - Persona-specific user journey analysis  
    - **Hygiene Scorecards** - Detailed criteria-based evaluations
    - **Enhanced CSV Data** - Structured data for dashboard analysis
    """)
    
    # Configuration
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📄 1. Upload Persona File")
        persona_file = st.file_uploader(
            "Choose persona markdown file:",
            type=['md'],
            disabled=st.session_state.is_running
        )
    
    with col2:
        st.markdown("#### 🔗 2. Provide URLs to Audit")
        urls_text = st.text_area(
            "Enter URLs (one per line):",
            value=st.session_state.urls_text,
            height=200,
            disabled=st.session_state.is_running
        )
        st.session_state.urls_text = urls_text
    
    # Run button
    can_run = persona_file is not None and st.session_state.urls_text.strip() and not st.session_state.is_running
    
    if st.button("🚀 Start Brand Audit", disabled=not can_run, type="primary"):
        st.session_state.is_running = True
        
        temp_dir = tempfile.mkdtemp(prefix="audit_")
        
        try:
            # Save files
            persona_content = persona_file.getvalue().decode("utf-8")
            persona_file_path = os.path.join(temp_dir, persona_file.name)
            with open(persona_file_path, "w", encoding="utf-8") as f:
                f.write(persona_content)
            
            urls_file_path = os.path.join(temp_dir, "urls_to_audit.txt")
            with open(urls_file_path, "w", encoding="utf-8") as f:
                f.write(st.session_state.urls_text)
            
            persona_name = get_persona_name(persona_content)
            
            # Run audit
            st.info(f"🚀 Starting audit for persona: {persona_name}")
            log_placeholder = st.empty()
            
            process = run_audit(persona_file_path, urls_file_path)
            
            log_content = ""
            for line in iter(process.stdout.readline, ''):
                log_content += line
                display_log = log_content[-2000:] if len(log_content) > 2000 else log_content
                log_placeholder.code(display_log, language="log")
            
            process.wait()
            
            if process.returncode == 0:
                st.success("✅ Audit completed successfully!")
                st.info("🔄 Refresh the dashboard to see new data in other tabs.")
            else:
                st.error("❌ Audit failed. Check the log for details.")
                
        except Exception as e:
            st.error(f"💥 Unexpected error: {e}")
        finally:
            st.session_state.is_running = False
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)

if __name__ == "__main__":
    main() 