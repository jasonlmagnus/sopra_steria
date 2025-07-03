import streamlit as st
import os
import glob
from datetime import datetime
import webbrowser
from pathlib import Path
import subprocess
import platform

st.set_page_config(
    page_title="HTML Reports",
    page_icon="📄",
    layout="wide"
)

# Page styling
st.markdown("""
<style>
    .report-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4D1D82;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .report-title {
        color: #4D1D82;
        font-size: 1.2em;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .report-meta {
        color: #666;
        font-size: 0.9em;
        margin-bottom: 0.5rem;
    }
    .report-description {
        color: #444;
        line-height: 1.5;
    }
    .stats-container {
        background: linear-gradient(135deg, #4D1D82, #8b1d82);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
    }
    .stat-item {
        text-align: center;
        padding: 1rem;
    }
    .stat-number {
        font-size: 2em;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .stat-label {
        font-size: 0.9em;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

def get_file_size(file_path):
    """Get file size in KB"""
    try:
        size_bytes = os.path.getsize(file_path)
        return f"{size_bytes / 1024:.1f} KB"
    except:
        return "Unknown"

def get_file_modification_date(file_path):
    """Get file modification date"""
    try:
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    except:
        return "Unknown"

def open_file_in_browser(file_path):
    """Open HTML file in default browser"""
    try:
        abs_path = os.path.abspath(file_path)
        if platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', abs_path])
        elif platform.system() == 'Windows':
            subprocess.run(['start', abs_path], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', abs_path])
        return True
    except Exception as e:
        st.error(f"Could not open file: {e}")
        return False

def scan_html_reports():
    """Scan the html_reports directory for all HTML files"""
    reports = []
    html_reports_dir = "html_reports"
    
    if not os.path.exists(html_reports_dir):
        return reports
    
    # Find all HTML files
    html_files = glob.glob(os.path.join(html_reports_dir, "**/*.html"), recursive=True)
    
    for file_path in html_files:
        rel_path = os.path.relpath(file_path, html_reports_dir)
        file_name = os.path.basename(file_path)
        dir_name = os.path.dirname(rel_path)
        
        # Determine report type and category
        if "consolidated" in file_name.lower():
            report_type = "Consolidated Report"
            category = "Executive"
        elif "brand_audit" in file_name.lower():
            report_type = "Strategic Analysis"
            category = "Executive"
        elif "brand_experience_report" in file_name.lower():
            report_type = "Persona Report"
            category = "Persona"
        else:
            report_type = "Other Report"
            category = "Other"
        
        # Get persona name from directory
        if dir_name and dir_name != ".":
            persona_name = dir_name.replace("_", " ").replace("-", " ")
            # Clean up common naming patterns
            persona_name = persona_name.replace("C Suite Executive", "(C-Suite Executive)")
        else:
            persona_name = "Root Directory"
        
        reports.append({
            'file_path': file_path,
            'file_name': file_name,
            'persona_name': persona_name,
            'report_type': report_type,
            'category': category,
            'size': get_file_size(file_path),
            'modified': get_file_modification_date(file_path),
            'relative_path': rel_path
        })
    
    return sorted(reports, key=lambda x: (x['category'], x['persona_name']))

# Main page content
st.title("📄 HTML Reports Manager")
st.markdown("### Comprehensive Brand Experience Reports Dashboard")

# Scan for HTML reports
reports = scan_html_reports()

if not reports:
    st.warning("No HTML reports found in the `html_reports/` directory.")
    st.info("Generate HTML reports using the Reports Export page or run the HTML Report Generator.")
    st.stop()

# Quick stats
col1, col2, col3, col4 = st.columns(4)

executive_reports = [r for r in reports if r['category'] == 'Executive']
persona_reports = [r for r in reports if r['category'] == 'Persona']
total_size_kb = sum([float(r['size'].replace(' KB', '')) for r in reports if 'KB' in r['size']])

with col1:
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">{len(reports)}</div>
            <div class="stat-label">Total Reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">{len(executive_reports)}</div>
            <div class="stat-label">Executive Reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">{len(persona_reports)}</div>
            <div class="stat-label">Persona Reports</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">{total_size_kb:.1f}</div>
            <div class="stat-label">Total Size (KB)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Quick Actions
st.markdown("---")
st.subheader("🚀 Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🌐 Open Reports Index", use_container_width=True):
        index_path = "html_reports/index.html"
        if os.path.exists(index_path):
            if open_file_in_browser(index_path):
                st.success("Opening reports index in browser...")
        else:
            st.error("Reports index not found!")

with col2:
    if st.button("📊 Open Consolidated Report", use_container_width=True):
        consolidated_report = next((r for r in reports if "consolidated" in r['file_name'].lower()), None)
        if consolidated_report:
            if open_file_in_browser(consolidated_report['file_path']):
                st.success("Opening consolidated report...")
        else:
            st.error("Consolidated report not found!")

with col3:
    if st.button("🎯 Open Strategic Report", use_container_width=True):
        strategic_report = next((r for r in reports if "brand_audit" in r['file_name'].lower()), None)
        if strategic_report:
            if open_file_in_browser(strategic_report['file_path']):
                st.success("Opening strategic report...")
        else:
            st.error("Strategic report not found!")

with col4:
    if st.button("📋 Generate New Reports", use_container_width=True):
        st.switch_page("pages/6_📋_Reports_Export.py")

# Main reports display
st.markdown("---")

# Group reports by category
executive_reports = [r for r in reports if r['category'] == 'Executive']
persona_reports = [r for r in reports if r['category'] == 'Persona']
other_reports = [r for r in reports if r['category'] == 'Other']

# Executive Reports Section
if executive_reports:
    st.subheader("📊 Executive Reports")
    
    for report in executive_reports:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="report-card">
                    <div class="report-title">{report['persona_name']}</div>
                    <div class="report-meta">
                        📄 {report['report_type']} | 📅 Modified: {report['modified']} | 💾 Size: {report['size']}
                    </div>
                    <div class="report-description">
                        File: <code>{report['file_name']}</code><br>
                        Path: <code>{report['relative_path']}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"🌐 Open", key=f"exec_{report['file_path']}", use_container_width=True):
                    if open_file_in_browser(report['file_path']):
                        st.success("Opening report...")
                
                if st.button(f"📋 Copy Path", key=f"copy_exec_{report['file_path']}", use_container_width=True):
                    st.code(os.path.abspath(report['file_path']))

# Persona Reports Section
if persona_reports:
    st.markdown("---")
    st.subheader("👥 Persona Reports")
    
    # Group persona reports by persona
    persona_groups = {}
    for report in persona_reports:
        persona = report['persona_name']
        if persona not in persona_groups:
            persona_groups[persona] = []
        persona_groups[persona].append(report)
    
    for persona, persona_reports_list in persona_groups.items():
        with st.expander(f"📊 {persona} ({len(persona_reports_list)} report{'s' if len(persona_reports_list) > 1 else ''})", expanded=True):
            
            for report in persona_reports_list:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="report-card">
                        <div class="report-title">{report['report_type']}</div>
                        <div class="report-meta">
                            📅 Modified: {report['modified']} | 💾 Size: {report['size']}
                        </div>
                        <div class="report-description">
                            File: <code>{report['file_name']}</code><br>
                            Path: <code>{report['relative_path']}</code>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button(f"🌐 Open", key=f"persona_{report['file_path']}", use_container_width=True):
                        if open_file_in_browser(report['file_path']):
                            st.success("Opening report...")
                    
                    if st.button(f"📋 Copy Path", key=f"copy_persona_{report['file_path']}", use_container_width=True):
                        st.code(os.path.abspath(report['file_path']))

# Other Reports Section
if other_reports:
    st.markdown("---")
    st.subheader("📁 Other Reports")
    
    for report in other_reports:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="report-card">
                    <div class="report-title">{report['file_name']}</div>
                    <div class="report-meta">
                        📄 {report['report_type']} | 📅 Modified: {report['modified']} | 💾 Size: {report['size']}
                    </div>
                    <div class="report-description">
                        Path: <code>{report['relative_path']}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"🌐 Open", key=f"other_{report['file_path']}", use_container_width=True):
                    if open_file_in_browser(report['file_path']):
                        st.success("Opening report...")
                
                if st.button(f"📋 Copy Path", key=f"copy_other_{report['file_path']}", use_container_width=True):
                    st.code(os.path.abspath(report['file_path']))

# Technical Details Section
st.markdown("---")
with st.expander("🔧 Technical Details & File Management"):
    st.subheader("HTML Reports Directory Structure")
    
    if os.path.exists("html_reports"):
        # Show directory tree
        st.code(f"""
📁 html_reports/
├── 📄 index.html (Reports Index)
├── 📁 Consolidated_Brand_Report/
│   └── 📄 consolidated_brand_experience_report.html
├── 📁 The_Technical_Influencer/
│   └── 📄 brand_experience_report.html
├── 📁 The_Benelux_Cybersecurity_Decision_Maker/
│   └── 📄 brand_experience_report.html
├── 📁 The_Benelux_Strategic_Business_Leader_C-Suite_Executive/
│   └── 📄 brand_experience_report.html
├── 📁 The_Benelux_Transformation_Programme_Leader/
│   └── 📄 brand_experience_report.html
├── 📁 The_BENELUX_Technology_Innovation_Leader/
│   └── 📄 brand_experience_report.html
└── 📄 sopra_brand_audit_1.html (Strategic Report)
        """)
        
        st.subheader("Directory Information")
        html_reports_path = os.path.abspath("html_reports")
        st.info(f"**Full Path:** `{html_reports_path}`")
        
        # Directory stats
        total_files = len(glob.glob("html_reports/**/*", recursive=True))
        html_files = len(glob.glob("html_reports/**/*.html", recursive=True))
        directories = len([d for d in glob.glob("html_reports/**", recursive=True) if os.path.isdir(d)])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Files", total_files)
        with col2:
            st.metric("HTML Files", html_files)
        with col3:
            st.metric("Directories", directories)
    
    st.subheader("File Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Reports List", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("📁 Open Reports Folder", use_container_width=True):
            reports_dir = os.path.abspath("html_reports")
            if open_file_in_browser(reports_dir):
                st.success("Opening reports folder...")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <strong>HTML Reports Manager</strong><br>
    Manage and access all generated brand experience reports<br>
    <small>Reports are served directly from the html_reports/ directory</small>
</div>
""", unsafe_allow_html=True) 