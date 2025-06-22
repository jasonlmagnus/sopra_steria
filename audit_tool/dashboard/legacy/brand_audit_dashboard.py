#!/usr/bin/env python3
"""
Complete Brand Audit Dashboard
Combines audit running functionality with multi-persona analysis
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import os
import subprocess
import tempfile
import re
import shutil
import time
from datetime import datetime, timedelta
import psutil

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def initialize_audit_state():
    """Initialize all audit-related session state variables"""
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'audit_complete' not in st.session_state:
        st.session_state.audit_complete = False
    if 'audit_process' not in st.session_state:
        st.session_state.audit_process = None
    if 'audit_start_time' not in st.session_state:
        st.session_state.audit_start_time = None
    if 'current_url_index' not in st.session_state:
        st.session_state.current_url_index = 0
    if 'total_urls' not in st.session_state:
        st.session_state.total_urls = 0
    if 'persona_name' not in st.session_state:
        st.session_state.persona_name = ""
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""

def get_audit_status():
    """Get current audit status information"""
    if not st.session_state.is_running:
        return {
            'status': 'idle',
            'message': 'No audit running',
            'progress': 0,
            'elapsed_time': None
        }
    
    elapsed_time = None
    if st.session_state.audit_start_time:
        elapsed_time = datetime.now() - st.session_state.audit_start_time
    
    progress = 0
    if st.session_state.total_urls > 0:
        progress = (st.session_state.current_url_index / st.session_state.total_urls) * 100
    
    return {
        'status': 'running',
        'message': f'Processing {st.session_state.persona_name} audit',
        'progress': progress,
        'elapsed_time': elapsed_time,
        'current_url': st.session_state.current_url_index,
        'total_urls': st.session_state.total_urls
    }

def stop_audit():
    """Stop the currently running audit"""
    if st.session_state.audit_process:
        try:
            # Get the process and terminate it
            process = st.session_state.audit_process
            if process.poll() is None:  # Process is still running
                # Try to terminate gracefully first
                process.terminate()
                time.sleep(2)
                
                # If still running, force kill
                if process.poll() is None:
                    process.kill()
            
            st.session_state.audit_process = None
        except Exception as e:
            st.error(f"Error stopping audit: {e}")
    
    # Reset state
    st.session_state.is_running = False
    st.session_state.audit_start_time = None
    st.session_state.current_url_index = 0
    st.session_state.total_urls = 0

def render_audit_status_header():
    """Render the global audit status header"""
    status = get_audit_status()
    
    if status['status'] == 'idle':
        return  # Don't show header when idle
    
    # Create prominent status header with Sopra Steria styling
    st.markdown("""
    <style>
    .audit-status-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        font-family: 'Inter', sans-serif;
        backdrop-filter: blur(10px);
    }
    .status-running {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f97316 100%);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.9; }
    }
    .status-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1.5rem;
    }
    .status-info {
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    .status-progress {
        min-width: 250px;
    }
    .status-text {
        font-weight: 600;
        font-size: 1.1rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .status-detail {
        font-weight: 400;
        font-size: 0.95rem;
        opacity: 0.9;
    }
    </style>
    """, unsafe_allow_html=True)
    
    header_class = "audit-status-header status-running" if status['status'] == 'running' else "audit-status-header"
    
    with st.container():
        st.markdown(f'<div class="{header_class}">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        
        with col1:
            st.markdown(f'<div class="status-text">🔄 {status["message"]}</div>', unsafe_allow_html=True)
            if status['elapsed_time']:
                elapsed_str = str(status['elapsed_time']).split('.')[0]  # Remove microseconds
                st.markdown(f'<div class="status-detail">⏱️ Running for: {elapsed_str}</div>', unsafe_allow_html=True)
        
        with col2:
            if status['status'] == 'running':
                st.markdown(f'<div class="status-detail">📊 Progress: {status["current_url"]}/{status["total_urls"]} URLs</div>', unsafe_allow_html=True)
        
        with col3:
            if status['status'] == 'running':
                progress_val = status['progress'] / 100 if status['progress'] > 0 else 0
                st.progress(progress_val)
                st.markdown(f'<div class="status-detail">{status["progress"]:.1f}% Complete</div>', unsafe_allow_html=True)
        
        with col4:
            if status['status'] == 'running':
                if st.button("🛑 Stop Audit", type="secondary", help="Stop the running audit"):
                    stop_audit()
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

@st.cache_data
def load_audit_data():
    """Load the enhanced audit dataset from individual persona directories"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    audit_outputs_dir = project_root / "audit_outputs"
    
    if not audit_outputs_dir.exists():
        return None, None
    
    all_data = []
    all_pages = []
    all_recommendations = []
    all_experience = []
    personas_found = []
    
    # Scan for persona directories with enhanced CSV data
    for persona_dir in audit_outputs_dir.iterdir():
        if persona_dir.is_dir():
            criteria_file = persona_dir / "criteria_scores.csv"
            pages_file = persona_dir / "pages.csv"
            recommendations_file = persona_dir / "recommendations.csv"
            
            if criteria_file.exists():
                try:
                    # Load criteria scores (main dataset)
                    criteria_df = pd.read_csv(criteria_file)
                    criteria_df['persona_id'] = persona_dir.name
                    all_data.append(criteria_df)
                    
                    # Load pages metadata
                    if pages_file.exists():
                        pages_df = pd.read_csv(pages_file)
                        pages_df['persona_id'] = persona_dir.name
                        all_pages.append(pages_df)
                    
                    # Load recommendations
                    if recommendations_file.exists():
                        rec_df = pd.read_csv(recommendations_file)
                        rec_df['persona_id'] = persona_dir.name
                        all_recommendations.append(rec_df)
                    
                    # Load experience data
                    experience_file = persona_dir / "experience.csv"
                    if experience_file.exists():
                        exp_df = pd.read_csv(experience_file)
                        exp_df['persona_id'] = persona_dir.name
                        all_experience.append(exp_df)
                    
                    personas_found.append(persona_dir.name)
                    
                except Exception as e:
                    st.warning(f"Error loading data for {persona_dir.name}: {e}")
                    continue
    
    if not all_data:
        return None, None
    
    # Combine all data
    df = pd.concat(all_data, ignore_index=True)
    
    # Combine experience data if available
    experience_df = None
    if all_experience:
        experience_df = pd.concat(all_experience, ignore_index=True)
    
    # Combine pages data if available
    pages_df = None
    if all_pages:
        pages_df = pd.concat(all_pages, ignore_index=True)
    
    # Combine recommendations data if available
    recommendations_df = None
    if all_recommendations:
        recommendations_df = pd.concat(all_recommendations, ignore_index=True)
    
    # Create comprehensive joined dataset
    if pages_df is not None:
        # Start with pages as the master table
        master_df = pages_df.copy()
        
        # Add criteria scores
        criteria_summary = df.groupby(['page_id', 'persona_id']).agg({
            'score': ['mean', 'min', 'max', 'count'],
            'tier': 'first'  # Should be same for all criteria of a page
        }).round(2)
        criteria_summary.columns = ['avg_score', 'min_score', 'max_score', 'criteria_count', 'criteria_tier']
        criteria_summary = criteria_summary.reset_index()
        
        master_df = master_df.merge(criteria_summary, on=['page_id', 'persona_id'], how='left')
        
        # Add experience data
        if experience_df is not None:
            master_df = master_df.merge(experience_df, on=['page_id', 'persona_id'], how='left')
        
        # Add recommendations summary
        if recommendations_df is not None:
            rec_summary = recommendations_df.groupby(['page_id']).agg({
                'recommendation': 'count',
                'strategic_impact': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
            }).rename(columns={'recommendation': 'rec_count', 'strategic_impact': 'primary_impact'})
            rec_summary = rec_summary.reset_index()
            master_df = master_df.merge(rec_summary, on='page_id', how='left')
        
        # Fill missing values
        master_df['rec_count'] = master_df['rec_count'].fillna(0)
        master_df['primary_impact'] = master_df['primary_impact'].fillna('None')
        
        # Create enhanced criteria dataset with experience context
        df_enhanced = df.merge(
            master_df[['page_id', 'persona_id', 'url', 'slug', 'tier', 'final_score', 
                      'overall_sentiment', 'engagement_level', 'conversion_likelihood']],
            on=['page_id', 'persona_id'], how='left', suffixes=('', '_page')
        )
        
        # Use page tier if available, otherwise keep original
        df_enhanced['tier'] = df_enhanced['tier_page'].fillna(df_enhanced['tier'])
        df_enhanced = df_enhanced.drop('tier_page', axis=1)
        df_enhanced['url_slug'] = df_enhanced['slug'].fillna(df_enhanced['page_id'])
        
        # Store the master dataset for comprehensive analysis
        df = df_enhanced
        
    else:
        master_df = None
        df['url_slug'] = df['page_id']
    
    # Rename columns to match expected format
    if 'score' in df.columns:
        df['raw_score'] = df['score']
    if 'criterion_code' in df.columns:
        df['criterion_id'] = df['criterion_code']
    if 'evidence' in df.columns:
        df['rationale'] = df['evidence']
    
    # Create summary statistics
    summary = {
        'total_personas': len(personas_found),
        'total_pages': df['page_id'].nunique(),
        'total_evaluations': len(df),
        'total_experiences': len(experience_df) if experience_df is not None else 0,
        'total_recommendations': len(recommendations_df) if recommendations_df is not None else 0,
        'average_score': df['raw_score'].mean(),
        'personas': personas_found,
        'has_experience_data': experience_df is not None and not experience_df.empty,
        'has_recommendations': recommendations_df is not None and not recommendations_df.empty
    }
    
    # Add descriptor based on score
    def get_descriptor(score):
        if score >= 8.0:
            return 'EXCELLENT'
        elif score >= 4.0:
            return 'PASS'
        else:
            return 'FAIL'
    
    df['descriptor'] = df['raw_score'].apply(get_descriptor)
    
    # Return comprehensive dataset package
    datasets = {
        'criteria': df,  # Enhanced criteria with experience context
        'experience': experience_df,
        'pages': pages_df, 
        'recommendations': recommendations_df,
        'master': master_df  # Comprehensive joined dataset
    }
    
    return datasets, summary

def get_persona_name(persona_content: str, filename: str = None) -> str:
    """Extracts the persona name from the content or filename to find the output dir."""
    # First try to extract the actual persona name from content
    lines = persona_content.split('\n')
    for line in lines[:10]:  # Check first 10 lines
        line = line.strip()
        if line.startswith("Persona:"):
            # Extract the persona name after "Persona:"
            persona_name = line.replace("Persona:", "").strip()
            # Clean up the name for use as directory name
            clean_name = re.sub(r'[^\w\s-]', '', persona_name)
            clean_name = re.sub(r'\s+', '_', clean_name)
            return clean_name
    
    # Fallback to filename pattern if provided
    if filename:
        match = re.search(r"P\d+", filename)
        if match:
            return match.group(0)
    
    # Last resort: search content for P\d+ pattern
    match = re.search(r"P\d+", persona_content)
    if match:
        return match.group(0)
    
    return "default_persona"

def run_audit(persona_file_path, urls_file_path, persona_name):
    """Runs the audit tool as a subprocess."""
    # Get the project root directory (go up from dashboard to audit_tool to project root)
    current_dir = Path(__file__).parent  # dashboard/
    project_root = current_dir.parent.parent  # project root
    
    # Create output directory for this persona
    output_dir = project_root / "audit_outputs" / persona_name
    
    command = [
        "python",
        "-m",
        "audit_tool.main",
        "--urls",
        urls_file_path,
        "--persona",
        persona_file_path,
        "--output",
        str(output_dir)
    ]
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        cwd=str(project_root)  # Run from project root so module can be found
    )
    return process

def repackage_data():
    """Repackage all persona data after a new audit completes"""
    try:
        # Import and run the multi-persona packager
        from multi_persona_packager import MultiPersonaPackager
        packager = MultiPersonaPackager()
        packager.package_all_data()
        return True
    except Exception as e:
        st.error(f"Error repackaging data: {e}")
        return False

def render_audit_runner():
    """Render the audit running interface"""
    st.title("🚀 Run New Audit")
    
    # Check if audit is running and show warning
    if st.session_state.is_running:
        st.warning("⚠️ **Audit Currently Running** - Please wait for the current audit to complete or stop it from the status header above.")
        st.info("💡 You can monitor progress above and use the 'Analyze Results' tab to view existing data.")
        
        # Show option to stop current audit
        if st.button("🛑 Stop Current Audit", type="secondary"):
            stop_audit()
            st.success("✅ Audit stopped successfully!")
            st.rerun()
        return

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
        st.markdown("### 🔄 Audit in Progress")
        
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
            
            # Run audit with live logging
            status_text.text(f"Starting audit for {persona_name}...")
            progress_bar.progress(10)
            
            process = run_audit(persona_file_path, urls_file_path, persona_name)
            st.session_state.audit_process = process  # Store process for potential termination
            
            # Stream logs - keep last 50 lines for better performance
            log_lines = []
            url_count = 0
            
            for line in iter(process.stdout.readline, ''):
                # Check if audit was stopped
                if not st.session_state.is_running:
                    process.terminate()
                    break
                    
                log_lines.append(line.rstrip())
                # Keep only last 50 lines to prevent memory issues and UI slowdown
                if len(log_lines) > 50:
                    log_lines = log_lines[-50:]
                
                # Display in code block with limited height
                log_text = '\n'.join(log_lines)
                log_container.code(log_text, language=None)
                
                # Update progress based on log content
                if "Processing URL" in line:
                    url_count += 1
                    st.session_state.current_url_index = url_count
                    progress = 10 + (url_count / st.session_state.total_urls) * 80  # 10% start, 80% for URLs
                    progress_bar.progress(min(90, progress / 100))
            
            process.wait()
            progress_bar.progress(100)
            
            if process.returncode == 0:
                status_text.text("✅ Audit completed successfully!")
                st.success("🎉 Audit completed! Repackaging data for analysis...")
                
                # Repackage data to include new results
                if repackage_data():
                    st.success("✅ Data repackaged successfully!")
                    st.session_state.audit_complete = True
                    # Clear cache to reload new data
                    load_audit_data.clear()
                else:
                    st.warning("⚠️ Audit completed but data repackaging failed")
                
            else:
                status_text.text("❌ Audit failed")
                st.error("Audit failed. Check the log for details.")
                
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        finally:
            # Clean up state
            st.session_state.is_running = False
            st.session_state.audit_process = None
            st.session_state.audit_start_time = None
            st.session_state.current_url_index = 0
            
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
            
            if st.session_state.audit_complete:
                st.balloons()
                st.info("🔄 Switch to the 'Analyze Results' tab to see updated results!")

def render_analysis_dashboard():
    """Render the analysis dashboard"""
    st.title("📊 Multi-Persona Analysis")
    
    # Show warning if audit is running
    if st.session_state.is_running:
        st.warning("⚠️ **Audit in Progress** - The data shown below may not include the latest audit results. Results will be updated automatically when the audit completes.")
    
    # Add cache clear button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Refresh Data", help="Clear cache and reload latest data"):
            load_audit_data.clear()
            st.rerun()
    
    # Load data
    datasets, summary = load_audit_data()
    
    if datasets is None or datasets['criteria'] is None:
        st.warning("No audit data found. Please run an audit first or check if data exists.")
        st.info("💡 Switch to the 'Run Audit' tab to create new audit data")
        return
    
    # Extract datasets
    df = datasets['criteria']  # Main criteria dataset with experience context
    experience_df = datasets['experience']
    pages_df = datasets['pages']
    recommendations_df = datasets['recommendations']
    master_df = datasets['master']  # Comprehensive joined dataset
    
    # Show data info with enhanced context
    experience_info = f", {summary['total_experiences']} experiences" if summary['total_experiences'] > 0 else ""
    rec_info = f", {summary['total_recommendations']} recommendations" if summary['total_recommendations'] > 0 else ""
    st.info(f"📊 Loaded data: {summary['total_personas']} personas, {summary['total_pages']} pages, {summary['total_evaluations']} evaluations{experience_info}{rec_info}")
    
    # Show data integration status
    if summary['has_experience_data']:
        st.success("✅ Experience data integrated - persona sentiment and engagement available contextually")
    if summary['has_recommendations']:
        st.success("✅ Recommendations data integrated - strategic actions available by page")
    
    # Sidebar filters
    with st.sidebar:
        st.header("🎛️ Analysis Filters")
        
        # Persona filter
        available_personas = sorted(df['persona_id'].unique())
        selected_personas = st.multiselect(
            "Select Personas:",
            available_personas,
            default=available_personas,
            help="Choose which personas to analyze"
        )
        
        # Tier filter
        available_tiers = sorted(df['tier'].unique())
        selected_tiers = st.multiselect(
            "Select Tiers:",
            available_tiers,
            default=available_tiers,
            help="Choose which performance tiers to include"
        )
        
        # Score filter
        score_range = st.slider(
            "Score Range:",
            float(df['raw_score'].min()),
            float(df['raw_score'].max()),
            (float(df['raw_score'].min()), float(df['raw_score'].max())),
            help="Filter by score range"
        )
    
    # Apply filters
    filtered_df = df[
        (df['persona_id'].isin(selected_personas)) &
        (df['tier'].isin(selected_tiers)) &
        (df['raw_score'] >= score_range[0]) &
        (df['raw_score'] <= score_range[1])
    ]
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🎯 Executive Summary",
        "💡 AI Strategic Insights", 
        "📈 Overview", 
        "👥 Persona Comparison", 
        "🎯 Criteria Deep Dive",
        "📄 Page Performance", 
        "🔍 Evidence Explorer",
        "👤 Persona Experience",
        "📋 Detailed Data"
    ])
    
    with tab1:
        st.markdown("### 🎯 Executive Brand Health Summary")
        
        # Hero metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            overall_avg = filtered_df['raw_score'].mean()
            health_status = "🟢 Excellent" if overall_avg >= 7 else "🟡 Good" if overall_avg >= 4 else "🔴 Critical"
            st.metric("Brand Health Score", f"{overall_avg:.1f}/10", help="Overall weighted average across all evaluations")
            st.markdown(f"**Status:** {health_status}")
        
        with col2:
            total_pages = filtered_df['page_id'].nunique()
            critical_pages = len(filtered_df[filtered_df['raw_score'] < 4.0]['page_id'].unique())
            st.metric("Pages Analyzed", total_pages)
            st.metric("Critical Issues", critical_pages)
        
        with col3:
            if summary['has_experience_data']:
                positive_sentiment = (filtered_df['overall_sentiment'] == 'Positive').sum()
                total_with_sentiment = len(filtered_df['overall_sentiment'].dropna())
                sentiment_pct = (positive_sentiment / total_with_sentiment * 100) if total_with_sentiment > 0 else 0
                st.metric("Positive Sentiment", f"{sentiment_pct:.0f}%")
                
                high_conversion = (filtered_df['conversion_likelihood'] == 'High').sum()
                conversion_pct = (high_conversion / total_with_sentiment * 100) if total_with_sentiment > 0 else 0
                st.metric("High Conversion", f"{conversion_pct:.0f}%")
            else:
                pass_rate = (filtered_df['descriptor'].isin(['PASS', 'EXCELLENT'])).mean() * 100
                st.metric("Success Rate", f"{pass_rate:.1f}%")
        
        with col4:
            if summary['has_recommendations']:
                total_recs = summary['total_recommendations']
                quick_wins = len(recommendations_df[recommendations_df['complexity'] == 'Low']) if recommendations_df is not None else 0
                st.metric("Total Recommendations", total_recs)
                st.metric("Quick Wins Available", quick_wins)
            else:
                excellent_count = (filtered_df['descriptor'] == 'EXCELLENT').sum()
                st.metric("Excellence Examples", excellent_count)
        
        # Critical Issues Alert
        critical_issues = filtered_df[filtered_df['raw_score'] < 4.0]
        if not critical_issues.empty:
            st.markdown("---")
            st.markdown("### 🚨 Critical Issues Requiring Immediate Attention")
            
            critical_pages = critical_issues.groupby('url_slug').agg({
                'raw_score': 'mean',
                'criterion_id': 'count'
            }).sort_values('raw_score').head(3)
            
            for page, data in critical_pages.iterrows():
                st.error(f"**{page.replace('_', ' ').title()}** - Average Score: {data['raw_score']:.1f}/10 ({data['criterion_id']} failing criteria)")
        
        # Top Opportunities
        st.markdown("---")
        st.markdown("### 🎯 Top 3 Improvement Opportunities")
        
        # Find worst performing criteria with highest impact
        criteria_impact = filtered_df.groupby('criterion_id').agg({
            'raw_score': ['mean', 'count'],
            'page_id': 'nunique'
        }).round(2)
        criteria_impact.columns = ['avg_score', 'evaluations', 'pages_affected']
        criteria_impact['impact_score'] = (10 - criteria_impact['avg_score']) * criteria_impact['pages_affected']
        top_opportunities = criteria_impact.sort_values('impact_score', ascending=False).head(3)
        
        col1, col2, col3 = st.columns(3)
        
        for i, (criterion, data) in enumerate(top_opportunities.iterrows()):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                **{i+1}. {criterion.replace('_', ' ').title()}**
                
                - Current Score: {data['avg_score']:.1f}/10
                - Pages Affected: {data['pages_affected']}
                - Impact Score: {data['impact_score']:.1f}
                """)
        
        # Segmented Tier Analysis with Experience Data
        st.markdown("---")
        st.markdown("### 📊 Performance by Content Tier")
        
        if summary['has_experience_data'] and master_df is not None:
            # Create comprehensive tier analysis with experience context
            tier_analysis = master_df.groupby('tier').agg({
                'avg_score': 'mean',
                'overall_sentiment': lambda x: (x == 'Positive').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
                'engagement_level': lambda x: (x == 'High').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
                'conversion_likelihood': lambda x: (x == 'High').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
                'page_id': 'count'
            }).round(1)
            tier_analysis.columns = ['Avg Score', 'Positive Sentiment %', 'High Engagement %', 'High Conversion %', 'Page Count']
            tier_analysis = tier_analysis.sort_values('Avg Score', ascending=False)
            
            # Display tier cards
            for tier, data in tier_analysis.iterrows():
                tier_display = tier.replace('_', ' ').title()
                score_color = "🟢" if data['Avg Score'] >= 7 else "🟡" if data['Avg Score'] >= 4 else "🔴"
                
                with st.expander(f"{score_color} {tier_display} ({int(data['Page Count'])} pages) - Score: {data['Avg Score']:.1f}/10"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Average Score", f"{data['Avg Score']:.1f}/10")
                    with col2:
                        sentiment_icon = "🟢" if data['Positive Sentiment %'] >= 60 else "🟡" if data['Positive Sentiment %'] >= 40 else "🔴"
                        st.metric("Positive Sentiment", f"{sentiment_icon} {data['Positive Sentiment %']:.0f}%")
                    with col3:
                        engagement_icon = "🟢" if data['High Engagement %'] >= 60 else "🟡" if data['High Engagement %'] >= 40 else "🔴"
                        st.metric("High Engagement", f"{engagement_icon} {data['High Engagement %']:.0f}%")
                    with col4:
                        conversion_icon = "🟢" if data['High Conversion %'] >= 60 else "🟡" if data['High Conversion %'] >= 40 else "🔴"
                        st.metric("High Conversion", f"{conversion_icon} {data['High Conversion %']:.0f}%")
                    
                    # Show best and worst performing pages in this tier
                    tier_pages = master_df[master_df['tier'] == tier].sort_values('avg_score', ascending=False)
                    if not tier_pages.empty:
                        col1, col2 = st.columns(2)
                        with col1:
                            best_page = tier_pages.iloc[0]
                            st.markdown("**🏆 Best Performing Page:**")
                            st.write(f"• {best_page['slug'].replace('_', ' ').title()}")
                            st.write(f"• Score: {best_page['avg_score']:.1f}/10")
                            if pd.notna(best_page['overall_sentiment']):
                                st.write(f"• Sentiment: {best_page['overall_sentiment']}")
                        
                        with col2:
                            if len(tier_pages) > 1:
                                worst_page = tier_pages.iloc[-1]
                                st.markdown("**⚠️ Needs Attention:**")
                                st.write(f"• {worst_page['slug'].replace('_', ' ').title()}")
                                st.write(f"• Score: {worst_page['avg_score']:.1f}/10")
                                if pd.notna(worst_page['overall_sentiment']):
                                    st.write(f"• Sentiment: {worst_page['overall_sentiment']}")
        else:
            # Fallback tier analysis without experience data
            tier_scores = filtered_df.groupby('tier').agg({
                'raw_score': ['mean', 'count'],
                'descriptor': lambda x: (x == 'EXCELLENT').sum()
            }).round(2)
            tier_scores.columns = ['Avg Score', 'Page Count', 'Excellence Count']
            tier_scores = tier_scores.sort_values('Avg Score', ascending=False)
            
            for tier, data in tier_scores.iterrows():
                tier_display = tier.replace('_', ' ').title()
                score_color = "🟢" if data['Avg Score'] >= 7 else "🟡" if data['Avg Score'] >= 4 else "🔴"
                st.markdown(f"{score_color} **{tier_display}**: {data['Avg Score']:.1f}/10 ({int(data['Page Count'])} pages, {int(data['Excellence Count'])} excellent)")
        
        # Success Stories
        st.markdown("---")
        st.markdown("### 🏆 Success Stories to Replicate")
        
        excellent_examples = filtered_df[filtered_df['raw_score'] >= 8.0]
        if not excellent_examples.empty:
            success_stories = excellent_examples.groupby(['url_slug', 'criterion_id']).first().sort_values('raw_score', ascending=False).head(3)
            
            for i, ((page, criterion), data) in enumerate(success_stories.iterrows()):
                with st.expander(f"🌟 Success #{i+1}: {page.replace('_', ' ').title()} - {criterion.replace('_', ' ').title()}"):
                    st.write(f"**Score:** {data['raw_score']}/10")
                    st.write(f"**Why it works:** {data['rationale']}")
                    if 'url' in data and pd.notna(data['url']):
                        st.write(f"**URL:** {data['url']}")
    
    with tab2:
        st.markdown("### 💡 AI-Powered Strategic Insights")
        
        # Comprehensive insights generation
        insights = []
        recommendations = []
        
        # Overall performance analysis
        overall_avg = filtered_df['raw_score'].mean()
        total_evaluations = len(filtered_df)
        
        if overall_avg >= 7:
            insights.append("🟢 **Excellent Overall Performance** - Average score exceeds 7.0/10")
            recommendations.append("Continue current strategies and consider sharing best practices across all pages")
        elif overall_avg >= 4:
            insights.append("🟡 **Good Performance** - Average score is acceptable but has room for enhancement")
            recommendations.append("Focus on optimizing underperforming criteria to achieve excellence")
        else:
            insights.append("🔴 **Performance Needs Attention** - Average score below 4.0/10 indicates critical issues")
            recommendations.append("Immediate action required - prioritize fixing fundamental brand positioning issues")
        
        # Persona-specific insights
        if len(selected_personas) > 1:
            persona_scores = filtered_df.groupby('persona_id')['raw_score'].mean()
            score_diff = persona_scores.max() - persona_scores.min()
            if score_diff > 1.0:
                best_persona = persona_scores.idxmax()
                worst_persona = persona_scores.idxmin()
                insights.append(f"⚖️ **Significant Persona Variance** - {score_diff:.2f} point difference between {best_persona} and {worst_persona}")
                recommendations.append(f"Investigate why {worst_persona} has lower scores - may indicate targeting gaps")
        
        # Criteria-specific insights
        criteria_performance = filtered_df.groupby('criterion_id')['raw_score'].mean().sort_values()
        worst_criterion = criteria_performance.index[0]
        best_criterion = criteria_performance.index[-1]
        
        insights.append(f"📊 **Best Performing Area**: {best_criterion.replace('_', ' ').title()} ({criteria_performance.iloc[-1]:.2f}/10)")
        insights.append(f"⚠️ **Biggest Opportunity**: {worst_criterion.replace('_', ' ').title()} ({criteria_performance.iloc[0]:.2f}/10)")
        
        if criteria_performance.iloc[0] < 4.0:
            recommendations.append(f"Critical: Address {worst_criterion.replace('_', ' ').title()} immediately - scoring below pass threshold")
        
        # Page-specific insights
        page_performance = filtered_df.groupby('url_slug')['raw_score'].mean().sort_values()
        if len(page_performance) > 1:
            worst_page = page_performance.index[0]
            best_page = page_performance.index[-1]
            
            insights.append(f"🏆 **Top Performing Page**: {best_page.replace('_', ' ').title()} ({page_performance.iloc[-1]:.2f}/10)")
            insights.append(f"🔧 **Page Needing Most Attention**: {worst_page.replace('_', ' ').title()} ({page_performance.iloc[0]:.2f}/10)")
            
            if page_performance.iloc[0] < 4.0:
                recommendations.append(f"Priority: Redesign or optimize {worst_page.replace('_', ' ').title()} page")
        
        # Consistency insights
        score_std = filtered_df['raw_score'].std()
        if score_std > 2.0:
            insights.append(f"📈 **High Variability** - Score standard deviation of {score_std:.2f} indicates inconsistent experience")
            recommendations.append("Focus on standardizing brand experience across all touchpoints")
        elif score_std < 1.0:
            insights.append(f"✅ **Consistent Experience** - Low variability ({score_std:.2f}) shows uniform brand delivery")
        
        # Display insights and recommendations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔍 Key Insights")
            for insight in insights:
                st.markdown(f"- {insight}")
        
        with col2:
            st.markdown("#### 🎯 Strategic Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
        
        # Advanced analytics
        st.markdown("---")
        st.markdown("### 📈 Advanced Performance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Performance distribution analysis
            performance_dist = filtered_df['descriptor'].value_counts()
            fig_perf_dist = px.pie(
                values=performance_dist.values,
                names=performance_dist.index,
                title="Performance Distribution",
                color_discrete_map={
                    'EXCELLENT': '#22c55e',
                    'PASS': '#eab308', 
                    'FAIL': '#ef4444'
                }
            )
            st.plotly_chart(fig_perf_dist, use_container_width=True)
        
        with col2:
            # Score correlation analysis
            if len(selected_personas) > 1:
                pivot_scores = filtered_df.pivot_table(
                    values='raw_score', 
                    index=['url_slug', 'criterion_id'], 
                    columns='persona_id'
                ).corr()
                
                fig_corr = px.imshow(
                    pivot_scores.values,
                    x=pivot_scores.columns,
                    y=pivot_scores.index,
                    color_continuous_scale='RdBu',
                    title="Persona Score Correlations"
                )
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.info("Correlation analysis requires multiple personas")
        
        # Actionable insights with specific examples
        st.markdown("### 🚀 Actionable Recommendations with Evidence")
        
        # Find specific examples for recommendations
        critical_issues = filtered_df[filtered_df['raw_score'] < 4.0]
        if not critical_issues.empty:
            with st.expander("🔴 Critical Issues Requiring Immediate Attention"):
                for _, issue in critical_issues.iterrows():
                    st.markdown(f"""
                    **Page:** {issue['url_slug'].replace('_', ' ').title()}  
                    **Issue:** {issue['criterion_id'].replace('_', ' ').title()}  
                    **Score:** {issue['raw_score']}/10  
                    **Persona Impact:** {issue['persona_id']}  
                    **AI Analysis:** {issue['rationale']}
                    
                    ---
                    """)
        
        excellent_examples = filtered_df[filtered_df['raw_score'] >= 8.0]
        if not excellent_examples.empty:
            with st.expander("🟢 Excellence Examples to Replicate"):
                sample_excellent = excellent_examples.sample(min(5, len(excellent_examples)))
                for _, example in sample_excellent.iterrows():
                    st.markdown(f"""
                    **Page:** {example['url_slug'].replace('_', ' ').title()}  
                    **Excellence Area:** {example['criterion_id'].replace('_', ' ').title()}  
                    **Score:** {example['raw_score']}/10  
                    **Success Factor:** {example['rationale']}
                    
                    ---
                    """)
        
        # Export insights report
        st.markdown("---")
        
        # Generate comprehensive insights report
        insights_report = f"""
# Brand Audit Insights Report

## Executive Summary
- **Total Evaluations:** {total_evaluations}
- **Overall Average Score:** {overall_avg:.2f}/10
- **Personas Analyzed:** {len(selected_personas)}
- **Pages Analyzed:** {len(filtered_df['url_slug'].unique())}

## Key Insights
{chr(10).join(f"- {insight}" for insight in insights)}

## Strategic Recommendations
{chr(10).join(f"{i}. {rec}" for i, rec in enumerate(recommendations, 1))}

## Performance Breakdown
### Top Performing Criteria
{chr(10).join(f"- {criterion.replace('_', ' ').title()}: {score:.2f}/10" for criterion, score in criteria_performance.tail(3).items())}

### Areas for Improvement
{chr(10).join(f"- {criterion.replace('_', ' ').title()}: {score:.2f}/10" for criterion, score in criteria_performance.head(3).items())}

---
Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        st.download_button(
            "📋 Download Insights Report",
            insights_report.encode('utf-8'),
            f"brand_audit_insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            "text/markdown"
        )
    
    with tab3:
        # Enhanced Key metrics with better context
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Personas", len(filtered_df['persona_id'].unique()))
        
        with col2:
            st.metric("Pages Analyzed", len(filtered_df['page_id'].unique()))
        
        with col3:
            avg_score = filtered_df['raw_score'].mean()
            st.metric("Average Score", f"{avg_score:.2f}/10")
        
        with col4:
            pass_rate = (filtered_df['descriptor'].isin(['PASS', 'EXCELLENT'])).mean() * 100
            st.metric("Success Rate", f"{pass_rate:.1f}%")
            
        with col5:
            critical_fails = (filtered_df['raw_score'] < 4.0).sum()
            st.metric("Critical Issues", critical_fails)
        
        st.markdown("---")
        
        # Enhanced Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution with better context
            fig_hist = px.histogram(
                filtered_df,
                x='raw_score',
                title="📊 Score Distribution Across All Evaluations",
                nbins=20,
                color_discrete_sequence=['#3b82f6'],
                labels={'raw_score': 'Score', 'count': 'Number of Evaluations'}
            )
            fig_hist.add_vline(x=4.0, line_dash="dash", line_color="orange", annotation_text="PASS (4.0)")
            fig_hist.add_vline(x=7.0, line_dash="dash", line_color="green", annotation_text="EXCELLENT (7.0)")
            fig_hist.update_layout(
                xaxis_title="Score (1-10)",
                yaxis_title="Number of Evaluations",
                showlegend=False
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            # Performance by tier with experience context
            if summary['has_experience_data'] and 'overall_sentiment' in filtered_df.columns:
                # Enhanced tier analysis with experience data
                tier_analysis = filtered_df.groupby('tier').agg({
                    'raw_score': 'mean',
                    'overall_sentiment': lambda x: (x == 'Positive').sum() / len(x.dropna()) if len(x.dropna()) > 0 else 0,
                    'engagement_level': lambda x: (x == 'High').sum() / len(x.dropna()) if len(x.dropna()) > 0 else 0
                }).round(2)
                tier_analysis.columns = ['Avg Score', 'Positive Sentiment %', 'High Engagement %']
                tier_analysis = tier_analysis.reset_index()
                tier_analysis['tier'] = tier_analysis['tier'].str.replace('_', ' ').str.title()
                
                fig_bar = px.bar(
                    tier_analysis,
                    x='tier',
                    y='Avg Score',
                    title="🎯 Performance by Category (with Experience Context)",
                    color='Positive Sentiment %',
                    color_continuous_scale='RdYlGn',
                    labels={'tier': 'Category', 'Avg Score': 'Average Score'},
                    hover_data=['High Engagement %']
                )
            else:
                # Fallback to basic tier analysis
                tier_scores = filtered_df.groupby('tier')['raw_score'].mean().reset_index()
                tier_scores['tier'] = tier_scores['tier'].str.replace('_', ' ').str.title()
                fig_bar = px.bar(
                    tier_scores,
                    x='tier',
                    y='raw_score',
                    title="🎯 Average Performance by Category",
                    color='raw_score',
                    color_continuous_scale='RdYlGn',
                    labels={'tier': 'Category', 'raw_score': 'Average Score'}
                )
            
            fig_bar.update_layout(
                xaxis_title="Category",
                yaxis_title="Average Score",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Experience context by tier (if available)
        if summary['has_experience_data'] and master_df is not None:
            st.markdown("### 🎭 Experience Context by Tier")
            
            # Create tier experience summary
            tier_experience = master_df.groupby('tier').agg({
                'avg_score': 'mean',
                'overall_sentiment': lambda x: x.value_counts().to_dict() if len(x.dropna()) > 0 else {},
                'engagement_level': lambda x: (x == 'High').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
                'conversion_likelihood': lambda x: (x == 'High').sum() / len(x.dropna()) * 100 if len(x.dropna()) > 0 else 0,
                'page_id': 'count'
            }).round(1)
            tier_experience.columns = ['Avg Score', 'Sentiment Mix', 'High Engagement %', 'High Conversion %', 'Page Count']
            
            for tier, row in tier_experience.iterrows():
                with st.expander(f"🏷️ {tier.replace('_', ' ').title()} ({int(row['Page Count'])} pages)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Average Score", f"{row['Avg Score']:.1f}/10")
                        st.metric("High Engagement", f"{row['High Engagement %']:.0f}%")
                    
                    with col2:
                        st.metric("High Conversion", f"{row['High Conversion %']:.0f}%")
                        # Show sentiment breakdown
                        if isinstance(row['Sentiment Mix'], dict) and row['Sentiment Mix']:
                            sentiment_text = " | ".join([f"{k}: {v}" for k, v in row['Sentiment Mix'].items()])
                            st.write(f"**Sentiment:** {sentiment_text}")
                    
                    with col3:
                        # Get sample page for this tier
                        tier_pages = master_df[master_df['tier'] == tier]
                        if not tier_pages.empty:
                            best_page = tier_pages.loc[tier_pages['avg_score'].idxmax()]
                            st.write(f"**Best Performing:**")
                            st.write(f"{best_page['slug'].replace('_', ' ').title()[:40]}...")
                            st.write(f"Score: {best_page['avg_score']:.1f}/10")
        
        # Performance trend by page
        st.markdown("### 📈 Page Performance Overview")
        page_performance = filtered_df.groupby(['url_slug', 'persona_id'])['raw_score'].mean().reset_index()
        page_performance['url_display'] = page_performance['url_slug'].str.replace('_', ' ').str.title()
        
        fig_page_trend = px.box(
            filtered_df,
            x='url_slug',
            y='raw_score',
            color='persona_id',
            title="📄 Score Distribution by Page",
            labels={'url_slug': 'Page', 'raw_score': 'Score', 'persona_id': 'Persona'}
        )
        fig_page_trend.update_xaxes(tickangle=45)
        fig_page_trend.update_layout(height=500)
        st.plotly_chart(fig_page_trend, use_container_width=True)
    
    with tab4:
        st.markdown("### 👥 Persona Comparison Analysis")
        
        if len(selected_personas) < 2:
            st.warning("Select at least 2 personas to see comparisons.")
        else:
            # Enhanced persona performance comparison
            persona_scores = filtered_df.groupby('persona_id')['raw_score'].mean().reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_persona = px.bar(
                    persona_scores,
                    x='persona_id',
                    y='raw_score',
                    title="🏆 Overall Performance by Persona",
                    color='raw_score',
                    color_continuous_scale='RdYlGn',
                    labels={'persona_id': 'Persona', 'raw_score': 'Average Score'}
                )
                fig_persona.update_layout(
                    xaxis_title="Persona",
                    yaxis_title="Average Score",
                    showlegend=False
                )
                st.plotly_chart(fig_persona, use_container_width=True)
            
            with col2:
                # Enhanced radar chart with better formatting
                radar_data = filtered_df.groupby(['persona_id', 'tier'])['raw_score'].mean().unstack(fill_value=0)
                
                fig_radar = go.Figure()
                colors = px.colors.qualitative.Set3
                for i, persona in enumerate(radar_data.index):
                    fig_radar.add_trace(go.Scatterpolar(
                        r=radar_data.loc[persona].values,
                        theta=[col.replace('_', ' ').title() for col in radar_data.columns],
                        fill='toself',
                        name=persona,
                        line_color=colors[i % len(colors)]
                    ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                    title="🎯 Multi-Dimensional Performance Radar"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            
            # Detailed persona comparison matrix
            st.markdown("### 📊 Detailed Performance Matrix")
            
            # Create comparison matrix
            comparison_matrix = filtered_df.groupby(['persona_id', 'criterion_id'])['raw_score'].mean().unstack(fill_value=0)
            
            if not comparison_matrix.empty:
                # Create heatmap
                fig_heatmap = px.imshow(
                    comparison_matrix.values,
                    x=[col.replace('_', ' ').title() for col in comparison_matrix.columns],
                    y=comparison_matrix.index,
                    color_continuous_scale='RdYlGn',
                    aspect='auto',
                    title="🔥 Performance Heatmap: Persona vs Criteria"
                )
                fig_heatmap.update_layout(
                    xaxis_title="Evaluation Criteria",
                    yaxis_title="Persona",
                    height=400
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
            
            # Side-by-side comparison
            st.markdown("### ⚖️ Side-by-Side Analysis")
            
            for persona in selected_personas:
                persona_data = filtered_df[filtered_df['persona_id'] == persona]
                avg_score = persona_data['raw_score'].mean()
                
                with st.expander(f"📋 {persona} - Average Score: {avg_score:.2f}/10"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🏆 Top Performing Areas:**")
                        top_criteria = persona_data.groupby('criterion_id')['raw_score'].mean().sort_values(ascending=False).head(5)
                        for criterion, score in top_criteria.items():
                            st.write(f"• {criterion.replace('_', ' ').title()}: {score:.2f}/10")
                    
                    with col2:
                        st.markdown("**⚠️ Areas for Improvement:**")
                        bottom_criteria = persona_data.groupby('criterion_id')['raw_score'].mean().sort_values(ascending=True).head(5)
                        for criterion, score in bottom_criteria.items():
                            st.write(f"• {criterion.replace('_', ' ').title()}: {score:.2f}/10")
    
    with tab5:
        st.markdown("### 🎯 Criteria Deep Dive Analysis")
        
        # Criteria performance overview
        criteria_performance = filtered_df.groupby('criterion_id').agg({
            'raw_score': ['mean', 'std', 'min', 'max', 'count']
        }).round(2)
        criteria_performance.columns = ['Average', 'Std Dev', 'Min', 'Max', 'Count']
        criteria_performance = criteria_performance.sort_values('Average', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Performing Criteria")
            top_criteria = criteria_performance.head(5)
            for idx, (criterion, row) in enumerate(top_criteria.iterrows()):
                st.markdown(f"""
                **{idx+1}. {criterion.replace('_', ' ').title()}**  
                Average: {row['Average']:.2f}/10 | Evaluations: {row['Count']}
                """)
        
        with col2:
            st.markdown("#### ⚠️ Areas Needing Attention")
            bottom_criteria = criteria_performance.tail(5)
            for idx, (criterion, row) in enumerate(bottom_criteria.iterrows()):
                st.markdown(f"""
                **{idx+1}. {criterion.replace('_', ' ').title()}**  
                Average: {row['Average']:.2f}/10 | Evaluations: {row['Count']}
                """)
        
        # Detailed criteria analysis
        st.markdown("### 📊 Criteria Performance Distribution")
        
        unique_criteria = filtered_df['criterion_id'].dropna().astype(str).unique()
        selected_criterion = st.selectbox(
            "Select criterion for detailed analysis:",
            options=sorted(unique_criteria),
            format_func=lambda x: str(x).replace('_', ' ').title()
        )
        
        if selected_criterion:
            criterion_data = filtered_df[filtered_df['criterion_id'] == selected_criterion]
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Score distribution for this criterion
                fig_criterion_dist = px.histogram(
                    criterion_data,
                    x='raw_score',
                    color='persona_id',
                    title=f"Score Distribution: {selected_criterion.replace('_', ' ').title()}",
                    nbins=10,
                    barmode='overlay'
                )
                st.plotly_chart(fig_criterion_dist, use_container_width=True)
            
            with col2:
                # Performance by page for this criterion
                criterion_by_page = criterion_data.groupby('url_slug')['raw_score'].mean().sort_values(ascending=True)
                fig_criterion_pages = px.bar(
                    x=criterion_by_page.values,
                    y=[slug.replace('_', ' ').title() for slug in criterion_by_page.index],
                    orientation='h',
                    title=f"Page Performance: {selected_criterion.replace('_', ' ').title()}",
                    color=criterion_by_page.values,
                    color_continuous_scale='RdYlGn'
                )
                fig_criterion_pages.update_layout(showlegend=False)
                st.plotly_chart(fig_criterion_pages, use_container_width=True)
            
            # Show rationale examples for this criterion
            st.markdown(f"### 💭 AI Rationale Examples for {selected_criterion.replace('_', ' ').title()}")
            
            # Get diverse examples (high, medium, low scores)
            high_score = criterion_data[criterion_data['raw_score'] >= 7.0].sample(min(2, len(criterion_data[criterion_data['raw_score'] >= 7.0])))
            med_score = criterion_data[(criterion_data['raw_score'] >= 4.0) & (criterion_data['raw_score'] < 7.0)].sample(min(2, len(criterion_data[(criterion_data['raw_score'] >= 4.0) & (criterion_data['raw_score'] < 7.0)])))
            low_score = criterion_data[criterion_data['raw_score'] < 4.0].sample(min(2, len(criterion_data[criterion_data['raw_score'] < 4.0])))
            
            examples = pd.concat([high_score, med_score, low_score]).sort_values('raw_score', ascending=False)
            
            for _, row in examples.iterrows():
                score_color = "🟢" if row['raw_score'] >= 7 else "🟡" if row['raw_score'] >= 4 else "🔴"
                with st.expander(f"{score_color} {row['url_slug'].replace('_', ' ').title()} - Score: {row['raw_score']}/10"):
                    st.write(f"**Persona:** {row['persona_id']}")
                    st.write(f"**Performance:** {row['descriptor']}")
                    st.write(f"**AI Rationale:** {row['rationale']}")
    
    with tab6:
        st.markdown("### 📄 Page Performance Analysis")
        
        # Page performance overview
        page_performance = filtered_df.groupby('url_slug').agg({
            'raw_score': ['mean', 'std', 'min', 'max', 'count']
        }).round(2)
        page_performance.columns = ['Average', 'Std Dev', 'Min', 'Max', 'Evaluations']
        page_performance = page_performance.sort_values('Average', ascending=False)
        
        # Best and worst performing pages
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏆 Top Performing Pages")
            top_pages = page_performance.head(5)
            for idx, (page, row) in enumerate(top_pages.iterrows()):
                st.markdown(f"""
                **{idx+1}. {page.replace('_', ' ').title()}**  
                Average: {row['Average']:.2f}/10 | Evaluations: {int(row['Evaluations'])}
                """)
        
        with col2:
            st.markdown("#### ⚠️ Pages Needing Improvement")
            bottom_pages = page_performance.tail(5)
            for idx, (page, row) in enumerate(bottom_pages.iterrows()):
                st.markdown(f"""
                **{idx+1}. {page.replace('_', ' ').title()}**  
                Average: {row['Average']:.2f}/10 | Evaluations: {int(row['Evaluations'])}
                """)
        
        # Detailed page analysis
        st.markdown("### 🔍 Individual Page Deep Dive")
        
        unique_pages = filtered_df['url_slug'].dropna().astype(str).unique()
        selected_page = st.selectbox(
            "Select page for detailed analysis:",
            options=sorted(unique_pages),
            format_func=lambda x: str(x).replace('_', ' ').title()
        )
        
        if selected_page:
            page_data = filtered_df[filtered_df['url_slug'] == selected_page]
            
            # Page metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Average Score", f"{page_data['raw_score'].mean():.2f}/10")
            with col2:
                st.metric("Total Evaluations", len(page_data))
            with col3:
                pass_rate = (page_data['descriptor'].isin(['PASS', 'EXCELLENT'])).mean() * 100
                st.metric("Success Rate", f"{pass_rate:.1f}%")
            with col4:
                st.metric("Personas", len(page_data['persona_id'].unique()))
            
            # Performance breakdown
            col1, col2 = st.columns(2)
            
            with col1:
                # Criteria performance for this page
                criteria_scores = page_data.groupby('criterion_id')['raw_score'].mean().sort_values(ascending=True)
                fig_page_criteria = px.bar(
                    x=criteria_scores.values,
                    y=[c.replace('_', ' ').title() for c in criteria_scores.index],
                    orientation='h',
                    title=f"Criteria Performance: {selected_page.replace('_', ' ').title()}",
                    color=criteria_scores.values,
                    color_continuous_scale='RdYlGn'
                )
                fig_page_criteria.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_page_criteria, use_container_width=True)
            
            with col2:
                # Persona comparison for this page
                if len(page_data['persona_id'].unique()) > 1:
                    persona_scores = page_data.groupby('persona_id')['raw_score'].mean()
                    fig_page_personas = px.bar(
                        x=persona_scores.index,
                        y=persona_scores.values,
                        title=f"Persona Performance: {selected_page.replace('_', ' ').title()}",
                        color=persona_scores.values,
                        color_continuous_scale='RdYlGn'
                    )
                    fig_page_personas.update_layout(showlegend=False)
                    st.plotly_chart(fig_page_personas, use_container_width=True)
                else:
                    st.info("Only one persona evaluated this page")
            
            # Show URL and detailed breakdown
            page_url = page_data['url'].iloc[0] if 'url' in page_data.columns else "URL not available"
            st.markdown(f"**Page URL:** {page_url}")
            
            # Detailed evaluation results
            st.markdown("### 📋 Detailed Evaluation Results")
            page_display = page_data[['persona_id', 'tier', 'criterion_id', 'raw_score', 'descriptor', 'rationale']].copy()
            page_display['tier'] = page_display['tier'].str.replace('_', ' ').str.title()
            page_display['criterion_id'] = page_display['criterion_id'].str.replace('_', ' ').str.title()
            page_display.columns = ['Persona', 'Category', 'Criterion', 'Score', 'Performance', 'AI Rationale']
            
            st.dataframe(page_display, use_container_width=True, height=400)
    
    with tab7:
        st.markdown("### 🔍 Evidence & Rationale Explorer")
        
        # Search through AI rationale
        col1, col2 = st.columns([2, 1])
        with col1:
            search_rationale = st.text_input("🔍 Search AI rationale:", placeholder="Enter keywords to search through AI explanations...")
        with col2:
            min_score_filter = st.slider("Minimum score:", 0.0, 10.0, 0.0, 0.5)
        
        # Filter data based on search
        evidence_df = filtered_df[filtered_df['raw_score'] >= min_score_filter].copy()
        if search_rationale:
            evidence_df = evidence_df[evidence_df['rationale'].str.contains(search_rationale, case=False, na=False)]
        
        if evidence_df.empty:
            st.warning("No evidence found matching your search criteria.")
        else:
            st.info(f"Found {len(evidence_df)} evaluations matching your criteria")
            
            # Group by performance level
            performance_groups = evidence_df.groupby('descriptor')
            
            for performance, group in performance_groups:
                if performance == 'EXCELLENT':
                    icon = "🟢"
                elif performance == 'PASS':
                    icon = "🟡" 
                else:
                    icon = "🔴"
                
                with st.expander(f"{icon} {performance} Performance ({len(group)} evaluations)"):
                    for _, row in group.iterrows():
                        st.markdown(f"""
                        **Page:** {row['url_slug'].replace('_', ' ').title()}  
                        **Criterion:** {row['criterion_id'].replace('_', ' ').title()}  
                        **Persona:** {row['persona_id']}  
                        **Score:** {row['raw_score']}/10  
                        **AI Explanation:** {row['rationale']}
                        
                        ---
                        """)
    
    with tab8:
        st.markdown("### 👤 Persona Experience Analysis")
        
        if experience_df is None or experience_df.empty:
            st.warning("No persona experience data available. Experience data provides rich insights into how personas actually feel about each page.")
            st.info("💡 Experience data includes first impressions, language feedback, trust assessments, and conversion likelihood.")
            return
        
        # Experience overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            positive_sentiment = (experience_df['overall_sentiment'] == 'Positive').sum()
            st.metric("Positive Sentiment", f"{positive_sentiment}/{len(experience_df)}")
        
        with col2:
            high_engagement = (experience_df['engagement_level'] == 'High').sum()
            st.metric("High Engagement", f"{high_engagement}/{len(experience_df)}")
        
        with col3:
            high_conversion = (experience_df['conversion_likelihood'] == 'High').sum()
            st.metric("High Conversion", f"{high_conversion}/{len(experience_df)}")
        
        with col4:
            avg_sentiment_score = {'Positive': 3, 'Mixed': 2, 'Negative': 1, 'Neutral': 1.5}
            sentiment_scores = experience_df['overall_sentiment'].map(avg_sentiment_score)
            st.metric("Avg Sentiment", f"{sentiment_scores.mean():.1f}/3.0")
        
        # Sentiment analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Sentiment distribution
            sentiment_counts = experience_df['overall_sentiment'].value_counts()
            fig_sentiment = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                title="📊 Overall Sentiment Distribution",
                color_discrete_map={
                    'Positive': '#22c55e',
                    'Mixed': '#eab308',
                    'Negative': '#ef4444',
                    'Neutral': '#94a3b8'
                }
            )
            st.plotly_chart(fig_sentiment, use_container_width=True)
        
        with col2:
            # Engagement vs Conversion
            engagement_conversion = experience_df.groupby(['engagement_level', 'conversion_likelihood']).size().reset_index(name='count')
            fig_eng_conv = px.scatter(
                engagement_conversion,
                x='engagement_level',
                y='conversion_likelihood',
                size='count',
                title="🎯 Engagement vs Conversion Likelihood",
                color='count',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_eng_conv, use_container_width=True)
        
        # Page-level experience analysis
        st.markdown("### 📄 Page Experience Breakdown")
        
        # Merge with page data for better display
        if 'url_slug' in df.columns:
            page_experience = experience_df.merge(
                df[['page_id', 'url_slug', 'tier']].drop_duplicates(),
                on='page_id',
                how='left'
            )
        else:
            page_experience = experience_df.copy()
            page_experience['url_slug'] = page_experience['page_id']
        
        # Experience heatmap
        experience_metrics = page_experience.groupby('url_slug').agg({
            'overall_sentiment': lambda x: (x == 'Positive').sum() / len(x),
            'engagement_level': lambda x: (x == 'High').sum() / len(x),
            'conversion_likelihood': lambda x: (x == 'High').sum() / len(x)
        }).round(2)
        
        experience_metrics.columns = ['Positive Sentiment %', 'High Engagement %', 'High Conversion %']
        
        fig_heatmap = px.imshow(
            experience_metrics.T.values,
            x=[slug.replace('_', ' ').title()[:30] + '...' if len(slug) > 30 else slug.replace('_', ' ').title() for slug in experience_metrics.index],
            y=experience_metrics.columns,
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title="🔥 Page Experience Heatmap"
        )
        fig_heatmap.update_layout(height=300)
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Detailed experience explorer
        st.markdown("### 🔍 Detailed Experience Explorer")
        
        # Page selector - fix sorting error by handling mixed data types
        unique_slugs = page_experience['url_slug'].dropna().astype(str).unique()
        selected_page = st.selectbox(
            "Select page for detailed experience analysis:",
            options=sorted(unique_slugs),
            format_func=lambda x: str(x).replace('_', ' ').title()
        )
        
        if selected_page:
            page_exp = page_experience[page_experience['url_slug'] == selected_page].iloc[0]
            
            # Experience summary
            col1, col2, col3 = st.columns(3)
            with col1:
                sentiment_color = {"Positive": "🟢", "Mixed": "🟡", "Negative": "🔴", "Neutral": "⚪"}
                st.metric("Sentiment", f"{sentiment_color.get(page_exp['overall_sentiment'], '⚪')} {page_exp['overall_sentiment']}")
            with col2:
                engagement_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
                st.metric("Engagement", f"{engagement_color.get(page_exp['engagement_level'], '⚪')} {page_exp['engagement_level']}")
            with col3:
                conversion_color = {"High": "🟢", "Medium": "🟡", "Low": "🔴"}
                st.metric("Conversion", f"{conversion_color.get(page_exp['conversion_likelihood'], '⚪')} {page_exp['conversion_likelihood']}")
            
            # Detailed feedback sections
            col1, col2 = st.columns(2)
            
            with col1:
                if page_exp['first_impression']:
                    st.markdown("#### 👁️ First Impression")
                    st.write(page_exp['first_impression'])
                
                if page_exp['language_tone_feedback']:
                    st.markdown("#### 🗣️ Language & Tone Feedback")
                    st.write(page_exp['language_tone_feedback'])
                
                if page_exp['information_gaps']:
                    st.markdown("#### ❓ Information Gaps")
                    st.write(page_exp['information_gaps'])
            
            with col2:
                if page_exp['trust_credibility_assessment']:
                    st.markdown("#### 🛡️ Trust & Credibility Assessment")
                    st.write(page_exp['trust_credibility_assessment'])
                
                if page_exp['business_impact_analysis']:
                    st.markdown("#### 💼 Business Impact Analysis")
                    st.write(page_exp['business_impact_analysis'])
            
            # Copy examples
            if page_exp['effective_copy_examples']:
                st.markdown("#### ✅ Effective Copy Examples")
                effective_examples = page_exp['effective_copy_examples'].split(' | ')
                for example in effective_examples:
                    if example.strip():
                        st.success(example)
            
            if page_exp['ineffective_copy_examples']:
                st.markdown("#### ❌ Ineffective Copy Examples")
                ineffective_examples = page_exp['ineffective_copy_examples'].split(' | ')
                for example in ineffective_examples:
                    if example.strip():
                        st.error(example)
    
    with tab7:
        st.markdown("### 📋 Data Explorer")
        
        # Enhanced search and sort
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("🔍 Search pages:", placeholder="Enter URL or page name...")
        with col2:
            sort_by = st.selectbox("Sort by:", ['raw_score', 'persona_id', 'tier', 'criterion_id'])
        with col3:
            sort_order = st.selectbox("Order:", ['Descending', 'Ascending'])
        
        # Filter and display data
        display_df = filtered_df.copy()
        if search_term:
            display_df = display_df[display_df['url_slug'].str.contains(search_term, case=False, na=False)]
        
        ascending = sort_order == 'Ascending'
        display_df = display_df.sort_values(sort_by, ascending=ascending)
        
        # Format for display
        display_columns = ['persona_id', 'url_slug', 'tier', 'criterion_id', 'raw_score', 'descriptor', 'rationale']
        display_df_formatted = display_df[display_columns].copy()
        display_df_formatted['url_slug'] = display_df_formatted['url_slug'].str.replace('_', ' ').str.title()
        display_df_formatted['criterion_id'] = display_df_formatted['criterion_id'].str.replace('_', ' ').str.title()
        display_df_formatted['tier'] = display_df_formatted['tier'].str.replace('_', ' ').str.title()
        display_df_formatted.columns = ['Persona', 'Page', 'Category', 'Criterion', 'Score', 'Performance', 'AI Rationale']
        
        st.dataframe(display_df_formatted, use_container_width=True, height=500)
        
        # Enhanced export options
        col1, col2, col3 = st.columns(3)
        with col1:
            csv_data = display_df.to_csv(index=False).encode('utf-8')
            st.download_button("📄 Download Full CSV", csv_data, "full_audit_data.csv", "text/csv")
        with col2:
            summary_data = display_df.groupby(['persona_id', 'url_slug'])['raw_score'].mean().reset_index()
            summary_csv = summary_data.to_csv(index=False).encode('utf-8')
            st.download_button("📊 Download Summary CSV", summary_csv, "audit_summary.csv", "text/csv")
        with col3:
            rationale_data = display_df[['persona_id', 'url_slug', 'criterion_id', 'raw_score', 'rationale']]
            rationale_csv = rationale_data.to_csv(index=False).encode('utf-8')
            st.download_button("💭 Download Rationale CSV", rationale_csv, "audit_rationale.csv", "text/csv")
    
    with tab9:
        st.markdown("### 📋 Detailed Data Explorer")
        st.info("This tab provides comprehensive data export and detailed analysis capabilities.")
        
        # Show data summary
        st.markdown("#### 📊 Data Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Records", len(filtered_df))
        with col2:
            st.metric("Unique Pages", filtered_df['page_id'].nunique())
        with col3:
            st.metric("Unique Criteria", filtered_df['criterion_id'].nunique())
        with col4:
            st.metric("Average Score", f"{filtered_df['raw_score'].mean():.2f}")
        
        # Full data table with advanced filtering
        st.markdown("#### 🔍 Complete Dataset")
        
        # Advanced filters
        col1, col2, col3 = st.columns(3)
        with col1:
            search_all = st.text_input("🔍 Search all fields:", placeholder="Search across all data...")
        with col2:
            unique_criteria = filtered_df['criterion_id'].dropna().astype(str).unique()
            selected_criteria = st.multiselect("Filter by criteria:", options=sorted(unique_criteria))
        with col3:
            score_filter = st.slider("Score range:", 0.0, 10.0, (0.0, 10.0), 0.1)
        
        # Apply advanced filters
        advanced_df = filtered_df.copy()
        
        if search_all:
            mask = (
                advanced_df['url_slug'].str.contains(search_all, case=False, na=False) |
                advanced_df['criterion_id'].str.contains(search_all, case=False, na=False) |
                advanced_df['rationale'].str.contains(search_all, case=False, na=False) |
                advanced_df['tier'].str.contains(search_all, case=False, na=False)
            )
            advanced_df = advanced_df[mask]
        
        if selected_criteria:
            advanced_df = advanced_df[advanced_df['criterion_id'].isin(selected_criteria)]
        
        advanced_df = advanced_df[
            (advanced_df['raw_score'] >= score_filter[0]) & 
            (advanced_df['raw_score'] <= score_filter[1])
        ]
        
        st.info(f"Showing {len(advanced_df)} records after filtering")
        
        # Display filtered data
        if not advanced_df.empty:
            display_cols = ['persona_id', 'url_slug', 'tier', 'criterion_id', 'raw_score', 'descriptor', 'rationale']
            if 'overall_sentiment' in advanced_df.columns:
                display_cols.insert(-1, 'overall_sentiment')
            if 'engagement_level' in advanced_df.columns:
                display_cols.insert(-1, 'engagement_level')
            
            formatted_df = advanced_df[display_cols].copy()
            formatted_df['url_slug'] = formatted_df['url_slug'].str.replace('_', ' ').str.title()
            formatted_df['criterion_id'] = formatted_df['criterion_id'].str.replace('_', ' ').str.title()
            formatted_df['tier'] = formatted_df['tier'].str.replace('_', ' ').str.title()
            
            st.dataframe(formatted_df, use_container_width=True, height=600)
            
            # Export options
            st.markdown("#### 📤 Export Options")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                full_csv = advanced_df.to_csv(index=False).encode('utf-8')
                st.download_button("📄 Full Dataset CSV", full_csv, "complete_audit_data.csv", "text/csv")
            
            with col2:
                summary_export = advanced_df.groupby(['persona_id', 'url_slug']).agg({
                    'raw_score': ['mean', 'min', 'max', 'count'],
                    'descriptor': lambda x: x.value_counts().index[0] if len(x) > 0 else 'Unknown'
                }).round(2)
                summary_export.columns = ['avg_score', 'min_score', 'max_score', 'evaluations', 'primary_performance']
                summary_csv = summary_export.reset_index().to_csv(index=False).encode('utf-8')
                st.download_button("📊 Summary Report CSV", summary_csv, "audit_summary_report.csv", "text/csv")
            
            with col3:
                insights_export = advanced_df[advanced_df['raw_score'] < 4.0][['persona_id', 'url_slug', 'criterion_id', 'raw_score', 'rationale']]
                if not insights_export.empty:
                    insights_csv = insights_export.to_csv(index=False).encode('utf-8')
                    st.download_button("⚠️ Critical Issues CSV", insights_csv, "critical_issues.csv", "text/csv")
                else:
                    st.info("No critical issues found")
            
            with col4:
                excellence_export = advanced_df[advanced_df['raw_score'] >= 8.0][['persona_id', 'url_slug', 'criterion_id', 'raw_score', 'rationale']]
                if not excellence_export.empty:
                    excellence_csv = excellence_export.to_csv(index=False).encode('utf-8')
                    st.download_button("🏆 Excellence Examples CSV", excellence_csv, "excellence_examples.csv", "text/csv")
                else:
                    st.info("No excellence examples found")
        else:
            st.warning("No data matches the current filters.")

def main():
    st.set_page_config(
        page_title="Brand Audit Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    # Add Sopra Steria inspired styling
    st.markdown("""
    <style>
    /* Import Sopra Steria-inspired fonts and colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom header styling */
    .sopra-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #8b5cf6 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    }
    
    .sopra-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .sopra-header p {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 0.75rem;
        padding: 0.25rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background: transparent;
        border-radius: 0.5rem;
        color: #64748b;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Metric cards styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 0.75rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    
    .stButton > button[kind="secondary"]:hover {
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #3b82f6;
        border-radius: 0.75rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        transition: all 0.2s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #8b5cf6;
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 1rem;
    }
    
    /* Text input styling */
    .stTextArea > div > div > textarea {
        border: 2px solid #e2e8f0;
        border-radius: 0.75rem;
        font-family: 'Inter', sans-serif;
        transition: border-color 0.2s ease;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Success/Warning/Error message styling */
    .stSuccess {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        border: none;
        border-radius: 0.75rem;
        color: white;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        border: none;
        border-radius: 0.75rem;
        color: white;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        border: none;
        border-radius: 0.75rem;
        color: white;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        border: none;
        border-radius: 0.75rem;
        color: white;
    }
    
    /* Chart containers */
    .js-plotly-plot {
        border-radius: 0.75rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Data frame styling */
    .stDataFrame {
        border-radius: 0.75rem;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 0.75rem;
        border: 1px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
    }
    
    /* Custom spacing */
    .element-container {
        margin-bottom: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize audit state
    initialize_audit_state()
    
    # Render global audit status header (only when audit is running)
    render_audit_status_header()
    
    # Custom Sopra Steria inspired header
    st.markdown("""
    <div class="sopra-header">
        <h1>🔍 Brand Audit Dashboard</h1>
        <p>Complete audit solution - run new audits and analyze multi-persona results</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main navigation
    tab1, tab2 = st.tabs(["🚀 Run Audit", "📊 Analyze Results"])
    
    with tab1:
        render_audit_runner()
    
    with tab2:
        render_analysis_dashboard()

if __name__ == "__main__":
    main() 