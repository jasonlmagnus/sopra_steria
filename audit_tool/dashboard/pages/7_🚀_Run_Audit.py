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

# Page configuration
st.set_page_config(
    page_title="Run Audit",
    page_icon="🚀",
    layout="wide"
)

# Import centralized brand styling
sys.path.append(str(Path(__file__).parent.parent))
from components.brand_styling import get_brand_css
st.markdown(get_brand_css(), unsafe_allow_html=True)

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
    if 'completed_persona_name' not in st.session_state:
        st.session_state.completed_persona_name = ""
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False

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
    
    # Header with brand styling
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Run Brand Audit</h1>
        <p>Launch new audits with YAML-driven methodology and dual AI provider support</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if audit is running and show warning
    if st.session_state.is_running:
        st.warning("⚠️ **Audit Currently Running** - Please wait for the current audit to complete or stop it below.")
        
        # Show option to stop current audit
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🛑 Stop Current Audit", type="secondary"):
                stop_audit()
                st.success("✅ Audit stopped successfully!")
                st.rerun()
        return

    st.markdown("""
    ### 🎯 Launch New Brand Audit
    
    Upload a persona file and provide URLs to analyze. The audit will generate **raw analysis files**:
    - **Experience Reports** - Persona-specific user journey analysis (markdown)
    - **Hygiene Scorecards** - Detailed criteria-based evaluations (markdown)
    
    After completion, use **"ADD TO DATABASE"** to process these into dashboard-ready data:
    - **Strategic Summary** - Executive insights and recommendations
    - **Structured CSV/Parquet** - Dashboard-compatible datasets
    - **Tier Classifications** - Business importance rankings
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
                st.session_state.audit_complete = True
                st.session_state.completed_persona_name = persona_name
                st.balloons()
            else:
                st.error("❌ Audit failed. Check the log for details.")
                
        except Exception as e:
            st.error(f"💥 Unexpected error: {e}")
        finally:
            st.session_state.is_running = False
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)

    # Post-audit processing section
    if st.session_state.get('audit_complete', False) and not st.session_state.get('is_running', False):
        st.markdown("---")
        st.markdown("### 🎯 Audit Complete - Next Steps")
        
        persona_name = st.session_state.get('completed_persona_name', 'Unknown')
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                    color: white; padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem;">
            <h3 style="margin: 0 0 0.5rem 0;">✅ Audit Complete: {persona_name}</h3>
            <p style="margin: 0; opacity: 0.9;">Raw audit files have been generated successfully.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            **What happens when you click "ADD TO DATABASE":**
            1. 🏷️ **Tier Classification** - URLs classified into business importance tiers
            2. 📊 **Data Processing** - Convert markdown reports to structured CSV/Parquet
            3. 📋 **Strategic Summary** - Generate executive-level insights and recommendations  
            4. 🗄️ **Database Integration** - Add to unified multi-persona dataset
            5. 🔄 **Dashboard Update** - New data becomes available across all dashboard pages
            """)
            
        with col2:
            st.markdown("**Processing Status:**")
            # Check if post-processing has been done
            audit_dir = Path(f"audit_outputs/{persona_name}")
            has_csv = len(list(audit_dir.glob("*.csv"))) > 0 if audit_dir.exists() else False
            has_strategic = (audit_dir / "Strategic_Summary.md").exists() if audit_dir.exists() else False
            
            if has_csv and has_strategic:
                st.success("✅ Already processed")
                st.info("Data is ready for dashboard")
            else:
                st.warning("⏳ Raw files only")
                st.info("Needs processing for dashboard")
        
        # Add to Database button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(
                "🗄️ ADD TO DATABASE",
                
                type="primary",
                disabled=st.session_state.get('is_processing', False),
                help="Process audit results and add to unified database for dashboard viewing"
            ):
                st.session_state.is_processing = True
                st.rerun()
        
        # Post-processing execution
        if st.session_state.get('is_processing', False):
            st.markdown("---")
            st.markdown("### 🔄 Processing Audit Results...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Import the post-processor
                import sys
                sys.path.append(str(Path(__file__).parent.parent.parent))
                
                status_text.text("📦 Importing post-processor...")
                progress_bar.progress(10)
                
                try:
                    from audit_tool.audit_post_processor import AuditPostProcessor
                    
                    status_text.text("🏗️ Initializing processor...")
                    progress_bar.progress(20)
                    
                    processor = AuditPostProcessor(persona_name)
                    
                    status_text.text("✅ Validating audit output...")
                    progress_bar.progress(30)
                    
                    if not processor.validate_audit_output():
                        st.error("❌ Invalid audit output - cannot process")
                        st.session_state.is_processing = False
                        st.stop()
                    
                    status_text.text("🏷️ Classifying page tiers...")
                    progress_bar.progress(40)
                    
                    classifications = processor.classify_page_tiers()
                    st.success(f"✅ Classified {len(classifications)} URLs into tiers")
                    
                    status_text.text("📊 Processing backfill data...")
                    progress_bar.progress(60)
                    
                    processed_data = processor.run_backfill_processing()
                    st.success(f"✅ Generated {len(processed_data)} datasets")
                    
                    status_text.text("📋 Generating strategic summary...")
                    progress_bar.progress(80)
                    
                    summary_path = processor.generate_strategic_summary()
                    st.success(f"✅ Strategic summary created")
                    
                    status_text.text("🗄️ Adding to unified database...")
                    progress_bar.progress(90)
                    
                    db_success = processor.add_to_database()
                    progress_bar.progress(100)
                    
                    if db_success:
                        st.success("🎉 Successfully added to database!")
                        
                        # Clear Streamlit cache to refresh data
                        st.cache_data.clear()
                        
                        st.success("🔄 **Dashboard cache refreshed!** New data is now available.")
                        st.info("✨ Navigate to other dashboard pages to see your new audit data")
                        
                        # Add navigation and reset buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🏠 Go to Dashboard Home", type="secondary"):
                                st.switch_page("audit_tool/dashboard/brand_health_command_center.py")
                        with col2:
                            if st.button("🚀 Run Another Audit", type="primary"):
                                # Reset audit state
                                st.session_state.audit_complete = False
                                st.session_state.completed_persona_name = ""
                                st.session_state.is_processing = False
                                st.rerun()
                    else:
                        st.error("❌ Failed to add to database")
                    
                except ImportError as e:
                    st.error(f"❌ Import error: {e}")
                    st.error("Make sure all required modules are available")
                except Exception as e:
                    st.error(f"❌ Processing error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
                    
            finally:
                st.session_state.is_processing = False
                status_text.text("✅ Processing complete")

if __name__ == "__main__":
    main() 