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

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent))

@st.cache_data
def load_audit_data():
    """Load the unified audit dataset"""
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    data_dir = project_root / "audit_data"
    
    if not (data_dir / "unified_audit_data.parquet").exists():
        return None, None
    
    # Load main dataset
    df = pd.read_parquet(data_dir / "unified_audit_data.parquet")
    
    # Load summary stats
    with open(data_dir / "summary_stats.json", 'r') as f:
        summary = json.load(f)
    
    return df, summary

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
    
    # Initialize session state
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'audit_complete' not in st.session_state:
        st.session_state.audit_complete = False
    if 'urls_text' not in st.session_state:
        st.session_state.urls_text = ""

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📋 Step 1: Upload Persona File")
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
        st.markdown("### 🌐 Step 2: Provide URLs to Audit")
        
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
            st.session_state.is_running = True
            st.session_state.audit_complete = False
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
            
            log_content = ""
            current_progress = 10
            process = run_audit(persona_file_path, urls_file_path, persona_name)
            
            # Stream logs - keep last 50 lines for better performance
            log_lines = []
            for line in iter(process.stdout.readline, ''):
                log_lines.append(line.rstrip())
                # Keep only last 50 lines to prevent memory issues and UI slowdown
                if len(log_lines) > 50:
                    log_lines = log_lines[-50:]
                
                # Display in code block with limited height
                log_text = '\n'.join(log_lines)
                log_container.code(log_text, language=None)
                
                # Update progress based on log content
                if "Processing URL" in line:
                    current_progress = min(90, current_progress + 4)
                    progress_bar.progress(current_progress)
            
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
                    st.cache_data.clear()
                else:
                    st.warning("⚠️ Audit completed but data repackaging failed")
                
            else:
                status_text.text("❌ Audit failed")
                st.error("Audit failed. Check the log for details.")
                
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        finally:
            st.session_state.is_running = False
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
            
            if st.session_state.audit_complete:
                st.balloons()
                st.info("🔄 Refresh the page or switch to the Analysis tab to see updated results!")

def render_analysis_dashboard():
    """Render the analysis dashboard"""
    st.title("📊 Multi-Persona Analysis")
    
    # Load data
    df, summary = load_audit_data()
    
    if df is None:
        st.warning("No audit data found. Please run an audit first or check if data exists.")
        st.info("💡 Switch to the 'Run Audit' tab to create new audit data")
        return
    
    # Show data info
    st.info(f"📊 Loaded data: {summary['total_personas']} personas, {summary['total_pages']} pages, {summary['total_evaluations']} evaluations")
    
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
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "👥 Persona Comparison", "📋 Detailed Data", "🎯 Insights"])
    
    with tab1:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
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
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_hist = px.histogram(
                filtered_df,
                x='raw_score',
                title="Score Distribution",
                nbins=20,
                color_discrete_sequence=['#3b82f6']
            )
            fig_hist.add_vline(x=4.0, line_dash="dash", line_color="orange", annotation_text="PASS (4.0)")
            fig_hist.add_vline(x=7.0, line_dash="dash", line_color="green", annotation_text="EXCELLENT (7.0)")
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            tier_scores = filtered_df.groupby('tier')['raw_score'].mean().reset_index()
            fig_bar = px.bar(
                tier_scores,
                x='tier',
                y='raw_score',
                title="Average Score by Tier",
                color='raw_score',
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab2:
        st.markdown("### 👥 Persona Comparison")
        
        if len(selected_personas) < 2:
            st.warning("Select at least 2 personas to see comparisons.")
        else:
            # Persona performance comparison
            persona_scores = filtered_df.groupby('persona_id')['raw_score'].mean().reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_persona = px.bar(
                    persona_scores,
                    x='persona_id',
                    y='raw_score',
                    title="Average Score by Persona",
                    color='raw_score',
                    color_continuous_scale='RdYlGn'
                )
                st.plotly_chart(fig_persona, use_container_width=True)
            
            with col2:
                # Radar chart
                radar_data = filtered_df.groupby(['persona_id', 'tier'])['raw_score'].mean().unstack(fill_value=0)
                
                fig_radar = go.Figure()
                colors = px.colors.qualitative.Set3
                for i, persona in enumerate(radar_data.index):
                    fig_radar.add_trace(go.Scatterpolar(
                        r=radar_data.loc[persona].values,
                        theta=radar_data.columns,
                        fill='toself',
                        name=persona,
                        line_color=colors[i % len(colors)]
                    ))
                
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                    title="Persona Performance Radar"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
    
    with tab3:
        st.markdown("### 📋 Data Explorer")
        
        # Search and sort
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("🔍 Search pages:", placeholder="Enter URL or page name...")
        with col2:
            sort_by = st.selectbox("Sort by:", ['raw_score', 'persona_id', 'tier', 'criterion_id'])
        
        # Filter and display data
        display_df = filtered_df.copy()
        if search_term:
            display_df = display_df[display_df['url_slug'].str.contains(search_term, case=False, na=False)]
        
        display_df = display_df.sort_values(sort_by, ascending=False)
        
        # Format for display
        display_columns = ['persona_id', 'url_slug', 'tier', 'criterion_id', 'raw_score', 'descriptor']
        display_df_formatted = display_df[display_columns].copy()
        display_df_formatted['url_slug'] = display_df_formatted['url_slug'].str.replace('_', ' ').str.title()
        display_df_formatted['criterion_id'] = display_df_formatted['criterion_id'].str.replace('_', ' ').str.title()
        display_df_formatted.columns = ['Persona', 'Page', 'Tier', 'Criterion', 'Score', 'Performance']
        
        st.dataframe(display_df_formatted, use_container_width=True, height=400)
        
        # Export
        csv_data = display_df.to_csv(index=False).encode('utf-8')
        st.download_button("📄 Download CSV", csv_data, "audit_data.csv", "text/csv")
    
    with tab4:
        st.markdown("### 🎯 Strategic Insights")
        
        # Generate insights
        insights = []
        overall_avg = filtered_df['raw_score'].mean()
        
        if overall_avg >= 7:
            insights.append("🟢 **Excellent Overall Performance** - Average score exceeds 7.0/10")
        elif overall_avg >= 4:
            insights.append("🟡 **Good Performance** - Average score is acceptable but could be enhanced")
        else:
            insights.append("🔴 **Performance Needs Attention** - Average score below 4.0/10")
        
        if len(selected_personas) > 1:
            persona_scores = filtered_df.groupby('persona_id')['raw_score'].mean()
            score_diff = persona_scores.max() - persona_scores.min()
            if score_diff > 1.0:
                best_persona = persona_scores.idxmax()
                worst_persona = persona_scores.idxmin()
                insights.append(f"⚖️ **Persona Variance** - {score_diff:.2f} point difference between {best_persona} and {worst_persona}")
        
        for insight in insights:
            st.markdown(f"- {insight}")

def main():
    st.set_page_config(
        page_title="Brand Audit Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    # App header
    st.title("🔍 Brand Audit Dashboard")
    st.markdown("Complete audit solution - run new audits and analyze multi-persona results")
    st.markdown("---")
    
    # Main navigation
    tab1, tab2 = st.tabs(["🚀 Run Audit", "📊 Analyze Results"])
    
    with tab1:
        render_audit_runner()
    
    with tab2:
        render_analysis_dashboard()

if __name__ == "__main__":
    main() 