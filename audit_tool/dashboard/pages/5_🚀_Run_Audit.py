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
from datetime import datetime

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def get_persona_name(persona_content: str, filename: str = None) -> str:
    """Extract a human-readable persona name; fall back to P-number."""
    lines = persona_content.strip().split('\n')
    if lines:
        first = lines[0].strip()
        if first.startswith("Persona Brief:"):
            return first.replace("Persona Brief:", "").strip()
        if first and not first.startswith('#'):
            return first
    # fallback to P1, P2 etc.
    match = re.search(r"P\d+", persona_content)
    if not match and filename:
        match = re.search(r"P\d+", filename)
    return match.group(0) if match else "default_persona"

def run_audit(persona_file_path, urls_file_path, persona_name, model_provider="anthropic"):
    """Runs the audit tool as a subprocess (inherits current working dir)."""
    # Create output directory for this persona
    output_dir = os.path.join("audit_outputs", persona_name)
    os.makedirs(output_dir, exist_ok=True)
    
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

def initialize_audit_state():
    """Initialize audit-related session state variables"""
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""
    if 'audit_complete' not in st.session_state:
        st.session_state.audit_complete = False
    if 'audit_start_time' not in st.session_state:
        st.session_state.audit_start_time = None
    if 'current_url_index' not in st.session_state:
        st.session_state.current_url_index = 0
    if 'total_urls' not in st.session_state:
        st.session_state.total_urls = 0
    if 'persona_name' not in st.session_state:
        st.session_state.persona_name = ""
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = "openai"  # Default to cost-effective option

def stop_audit():
    """Stop the currently running audit"""
    if hasattr(st.session_state, 'audit_process') and st.session_state.audit_process:
        try:
            st.session_state.audit_process.terminate()
            st.session_state.audit_process.wait(timeout=5)
        except:
            try:
                st.session_state.audit_process.kill()
            except:
                pass
    
    st.session_state.is_running = False
    st.session_state.audit_complete = False

def main():
    initialize_audit_state()
    
    st.title("🚀 Run Brand Audit")
    
    # Check if audit is running and show warning
    if st.session_state.is_running:
        st.warning("⚠️ **Audit Currently Running** - Please wait for the current audit to complete or stop it below.")
        
        # Show option to stop current audit
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🛑 Stop Current Audit", type="secondary", use_container_width=True):
                stop_audit()
                st.success("✅ Audit stopped successfully!")
                st.rerun()
        return

    st.markdown("""
    ### 🎯 Launch New Brand Audit
    
    Upload a persona file and provide URLs to analyze. The audit will generate:
    - **Strategic Summary** - High-level insights and recommendations
    - **Experience Reports** - Persona-specific user journey analysis  
    - **Hygiene Scorecards** - Detailed criteria-based evaluations
    - **Enhanced CSV Data** - Structured data for dashboard analysis
    """)

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                    padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem;
                    border: 1px solid #e2e8f0;">
            <h3 style="color: #1e3a8a; margin: 0 0 1rem 0; font-family: 'Inter', sans-serif;">
                📋 Step 1: Upload Persona File
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        persona_file = st.file_uploader(
            "Choose your persona markdown file",
            type=['md'],
            disabled=st.session_state.is_running,
            help="Upload a .md file containing your target persona definition"
        )
        
        if persona_file:
            st.success(f"✅ Persona file loaded: {persona_file.name}")
            persona_content = persona_file.getvalue().decode("utf-8")
            persona_name = get_persona_name(persona_content, persona_file.name)
            st.info(f"Detected persona: **{persona_name}**")
        
        # Model Selection
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%); 
                    padding: 1.5rem; border-radius: 1rem; margin-top: 1rem;
                    border: 1px solid #93c5fd;">
            <h3 style="color: #1e40af; margin: 0 0 1rem 0; font-family: 'Inter', sans-serif;">
                🤖 Step 1.5: Select AI Model
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        model_options = {
            "openai": "🔥 OpenAI GPT-4.1-Mini (Cost Effective)",
            "anthropic": "🧠 Anthropic Claude-3-Opus (Premium Quality)"
        }
        
        selected_model = st.radio(
            "Choose your AI model provider:",
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
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); 
                    padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem;
                    border: 1px solid #e2e8f0;">
            <h3 style="color: #1e3a8a; margin: 0 0 1rem 0; font-family: 'Inter', sans-serif;">
                🌐 Step 2: Provide URLs to Audit
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Paste URLs", "Upload File"])
        
        with tab1:
            urls_text = st.text_area(
                "Enter one URL per line:",
                height=200,
                placeholder="https://example.com\nhttps://example.com/about\nhttps://example.com/services",
                disabled=st.session_state.is_running,
                value=st.session_state.urls_text,
                key="urls_input"
            )
            st.session_state.urls_text = urls_text
        
        with tab2:
            uploaded_file = st.file_uploader(
                "Upload a .txt or .md file with URLs",
                type=['txt', 'md'],
                disabled=st.session_state.is_running
            )
            
            if uploaded_file:
                file_content = uploaded_file.getvalue().decode("utf-8")
                urls_from_file = re.findall(r'https?://[^\s|)]+', file_content)
                if urls_from_file:
                    st.session_state.urls_text = "\n".join(urls_from_file)
                    st.success(f"Loaded {len(urls_from_file)} URLs from file")

    # URL validation and preview
    if st.session_state.urls_text:
        urls = [url.strip() for url in st.session_state.urls_text.split('\n') if url.strip()]
        valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total URLs", len(urls))
        with col2:
            st.metric("Valid URLs", len(valid_urls))
        with col3:
            if len(urls) != len(valid_urls):
                st.metric("Invalid URLs", len(urls) - len(valid_urls))
            else:
                st.metric("Status", "✅ All Valid")

    # Run audit button
    can_run = persona_file is not None and st.session_state.urls_text.strip()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "🚀 Run Brand Audit",
            disabled=not can_run or st.session_state.is_running,
            use_container_width=True,
            type="primary"
        ):
            # Initialize audit state
            st.session_state.is_running = True
            st.session_state.audit_complete = False
            st.session_state.audit_start_time = datetime.now()
            st.session_state.current_url_index = 0
            
            # Count total URLs
            urls = [url.strip() for url in st.session_state.urls_text.split('\n') if url.strip()]
            valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]
            st.session_state.total_urls = len(valid_urls)
            
            # Get persona name
            persona_content = persona_file.getvalue().decode("utf-8")
            st.session_state.persona_name = get_persona_name(persona_content, persona_file.name)
            
            st.rerun()

    # Run audit process
    if st.session_state.is_running:
        st.markdown("---")
        st.markdown(f"### 🔄 Audit in Progress - Using {st.session_state.selected_model.upper()}")
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        log_expander = st.expander("📋 Live Audit Log", expanded=True)
        log_container = log_expander.empty()
        
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

            persona_name = get_persona_name(persona_content, persona_file.name)
            
            # Run audit with live logging and selected model
            status_text.text(f"Starting audit for {persona_name} using {st.session_state.selected_model.upper()}...")
            progress_bar.progress(10)
            
            process = run_audit(persona_file_path, urls_file_path, persona_name, st.session_state.selected_model)
            st.session_state.audit_process = process  # Store process for potential termination
            
            # Stream logs using the same pattern as audit_runner_dashboard.py
            log_lines = []
            
            for line in iter(process.stdout.readline, ''):
                log_lines.append(line.rstrip())
                if len(log_lines) > 100:  # Keep only the last 100 lines
                    log_lines = log_lines[-100:]
                log_container.code('\n'.join(log_lines))
            
            process.wait()
            
            if process.returncode == 0:
                st.success("✅ Audit completed successfully!")
                st.info("🔄 Refresh the dashboard to see new data in other tabs.")
                st.balloons()
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