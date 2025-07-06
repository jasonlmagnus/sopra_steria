import streamlit as st
import os
import glob
from datetime import datetime
from pathlib import Path
import zipfile
import io
import sys

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_main_header,
    create_section_header,
    create_metric_card,
    create_four_column_layout,
    create_two_column_layout,
    create_success_alert,
    create_warning_alert,
    create_error_alert,
    create_info_alert,
    create_divider
)

st.set_page_config(
    page_title="Audit Report Viewer",
    page_icon="📄",
    layout="wide"
)

# Apply styling
apply_perfect_styling()

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
            persona_name = "Index/Root"
        
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

def read_html_file(file_path):
    """Read HTML file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"<p>Error reading file: {e}</p>"

def create_download_zip(reports):
    """Create a ZIP file containing all audit reports"""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for report in reports:
            # Add each file to the ZIP
            zip_file.write(report['file_path'], report['relative_path'])
    
    zip_buffer.seek(0)
    return zip_buffer

def regenerate_reports():
    """Regenerate all audit reports"""
    try:
        from audit_tool.html_report_generator import HTMLReportGenerator
        import pandas as pd
        
        # Initialize generator
        generator = HTMLReportGenerator()
        
        # Get all persona names from the data
        df = pd.read_csv('audit_data/unified_audit_data.csv')
        personas = df['persona_id'].unique()
        
        generated_reports = []
        
        # Generate report for each persona
        for persona in personas:
            try:
                result = generator.generate_report(persona)
                generated_reports.append(result)
            except Exception as e:
                st.error(f"Error generating report for {persona}: {e}")
        
        return generated_reports
        
    except Exception as e:
        st.error(f"Error during report generation: {e}")
        return []

def main():
    """Audit Reports Dashboard"""
    
    # Header with brand styling - consistent with Run Audit page
    st.markdown("""
    <div class="main-header">
        <h1>📄 Audit Reports</h1>
        <p>Access and manage comprehensive audit reports and documentation</p>
    </div>
    """, unsafe_allow_html=True)

# Scan for audit reports
reports = scan_html_reports()

if not reports:
    create_warning_alert("No audit reports found in the `html_reports/` directory.")
    
    if st.button("🔄 Generate Reports", type="secondary"):
        with st.spinner("Generating audit reports..."):
            generated = regenerate_reports()
            if generated:
                create_success_alert(f"Successfully generated {len(generated)} reports!")
                st.rerun()
            else:
                create_error_alert("Failed to generate reports. Check the logs for details.")
    
    st.stop()

# Compact stats and viewer in one section
executive_reports = [r for r in reports if r['category'] == 'Executive']
persona_reports = [r for r in reports if r['category'] == 'Persona']
other_reports = [r for r in reports if r['category'] == 'Other']
total_size_kb = sum([float(r['size'].replace(' KB', '')) for r in reports if 'KB' in r['size']])

# Clean 3-metric header
metric_col1, metric_col2, metric_col3 = st.columns(3)

with metric_col1:
    st.metric("📄 Total Reports", len(reports))

with metric_col2:
    st.metric("👥 Persona Reports", len(persona_reports))

with metric_col3:
    st.metric("🎯 Executive Reports", len(executive_reports))
    
# Action buttons above report selector
action_col1, action_col2 = st.columns(2)

with action_col1:
    if st.button("🔄 Regenerate All", type="secondary", use_container_width=True):
        with st.spinner("Regenerating all reports..."):
            generated = regenerate_reports()
            if generated:
                create_success_alert(f"Successfully regenerated {len(generated)} reports!")
                st.rerun()

with action_col2:
    # Download all reports as ZIP
        zip_data = create_download_zip(reports)
        st.download_button(
        label="📦 Download All",
            data=zip_data,
            file_name=f"sopra_brand_reports_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
        type="secondary",
            use_container_width=True
        )

# Report selection dropdown
# Group reports by category for better organization
report_options = {}
for report in reports:
    category = report['category']
    if category not in report_options:
        report_options[category] = []
    
    display_name = f"{report['persona_name']} - {report['report_type']}"
    report_options[category].append((display_name, report))

# Create a flattened list for the selectbox
all_options = []
default_index = 0
current_index = 0

for category, category_reports in report_options.items():
    all_options.append(f"--- {category} Reports ---")
    current_index += 1
    
    for display_name, report in category_reports:
        all_options.append(display_name)
        # Set consolidated report or index as default
        if ("consolidated" in report['file_name'].lower() or 
            "index" in report['file_name'].lower() or 
            report['category'] == 'Executive'):
            default_index = current_index
        current_index += 1

# If no specific default found, use first actual report (skip category headers)
if default_index == 0:
    default_index = 1 if len(all_options) > 1 else 0

# Check if we have a report selected from HTML navigation
if hasattr(st.session_state, 'selected_report_name') and st.session_state.selected_report_name:
    # Find the index of the selected report in the dropdown
    if st.session_state.selected_report_name in all_options:
        default_index = all_options.index(st.session_state.selected_report_name)
    # Clear the session state after using it
    del st.session_state.selected_report_name

selected_option = st.selectbox(
    "🔍 Select Report to View:",
    options=all_options,
    index=default_index
)

# Find the selected report
selected_report = None
if selected_option and not selected_option.startswith("---"):
    for report in reports:
        display_name = f"{report['persona_name']} - {report['report_type']}"
        if display_name == selected_option:
            selected_report = report
            break

# Always show a report (default to first available if none selected)
if not selected_report and reports:
    # Find the best default report (consolidated, index, or first executive)
    default_report = None
    
    # Priority 1: Consolidated report
    for report in reports:
        if "consolidated" in report['file_name'].lower():
            default_report = report
            break
    
    # Priority 2: Index report
    if not default_report:
        for report in reports:
            if "index" in report['file_name'].lower():
                default_report = report
                break
    
    # Priority 3: First executive report
    if not default_report:
        executive_reports = [r for r in reports if r['category'] == 'Executive']
        if executive_reports:
            default_report = executive_reports[0]
    
    # Priority 4: Any report
    if not default_report:
        default_report = reports[0]
    
    selected_report = default_report

if selected_report:
    # Compact report details in one line
    st.markdown(f"**📋 {selected_report['persona_name']} - {selected_report['report_type']}** • 📁 {selected_report['file_name']} • 📏 {selected_report['size']} • 🕒 {selected_report['modified']}")
    
    # Report Content title with download button
    title_col, download_col = st.columns([3, 1])
    
    with title_col:
        st.markdown("### 📄 Report Content")
    
    with download_col:
        with open(selected_report['file_path'], 'rb') as f:
            st.download_button(
                label="⬇️ Download Report",
                data=f.read(),
                file_name=selected_report['file_name'],
                mime="text/html",
                type="secondary",
                use_container_width=True
            )
    
    # Read and display the HTML content
    html_content = read_html_file(selected_report['file_path'])
    
    # Make HTML links functional using bidirectional communication
    import re
    
    # Remove problematic streamlit/localhost links
    html_content = re.sub(r'href="http://localhost:\d+[^"]*"', 'href="#"', html_content)
    html_content = re.sub(r'href=".*streamlit.*"', 'href="#"', html_content)
    
    # Add JavaScript to handle link clicks and communicate back to Streamlit
    navigation_script = '''
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Find all links to HTML reports
        const reportLinks = document.querySelectorAll('a[href$=".html"]');
        
        reportLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault(); // Prevent default navigation
                
                const href = this.getAttribute('href');
                let reportName = '';
                
                // Map filenames to dropdown options
                if (href.includes('consolidated')) {
                    reportName = 'Consolidated Brand Report - Consolidated Report';
                } else if (href.includes('brand_audit') || href.includes('strategic')) {
                    reportName = 'Index/Root - Strategic Analysis';
                } else if (href.includes('technical') || href.includes('Technical_Influencer')) {
                    reportName = 'The Technical Influencer - Persona Report';
                } else if (href.includes('cybersecurity') || href.includes('Cybersecurity_Decision_Maker')) {
                    reportName = 'The Benelux Cybersecurity Decision Maker - Persona Report';
                } else if (href.includes('business') || href.includes('Strategic_Business_Leader')) {
                    reportName = 'The Benelux Strategic Business Leader - Persona Report';
                } else if (href.includes('transformation') || href.includes('Transformation_Programme_Leader')) {
                    reportName = 'The Benelux Transformation Programme Leader - Persona Report';
                } else if (href.includes('technology') || href.includes('Technology_Innovation_Leader')) {
                    reportName = 'The BENELUX Technology Innovation Leader - Persona Report';
                }
                
                                 // Send message to Streamlit
                 if (reportName) {
                     // Try multiple methods to communicate with Streamlit
                     if (window.parent && window.parent.Streamlit && window.parent.Streamlit.setComponentValue) {
                         window.parent.Streamlit.setComponentValue(reportName);
                     } else if (window.Streamlit && window.Streamlit.setComponentValue) {
                         window.Streamlit.setComponentValue(reportName);
                     } else {
                         console.log('Streamlit communication not available, would navigate to:', reportName);
                     }
                 }
            });
        });
    });
    </script>
    '''
    
    # Add the script to the HTML content
    if '<head>' in html_content:
        html_content = html_content.replace('</head>', navigation_script + '</head>')
    else:
        html_content = navigation_script + html_content
    
    # Remove redundant Quick Actions section
    html_content = re.sub(r'<div[^>]*class="quick-actions"[^>]*>.*?</div>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<section[^>]*>.*?Quick Actions.*?</section>', '', html_content, flags=re.DOTALL)
    
    # Remove specific action buttons
    html_content = re.sub(r'<div[^>]*>.*?Return to Dashboard.*?</div>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<div[^>]*>.*?View Consolidated Report.*?</div>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<div[^>]*>.*?View Strategic Report.*?</div>', '', html_content, flags=re.DOTALL)
    html_content = re.sub(r'<div[^>]*>.*?Print This Index.*?</div>', '', html_content, flags=re.DOTALL)
    
    # Remove Quick Actions headings
    html_content = re.sub(r'<h[12]>Quick Actions</h[12]>', '', html_content)
    html_content = re.sub(r'<.*?>Quick Actions<.*?>', '', html_content)
    
    # Add navigation instructions at the top for index pages
    if "persona-specific reports" in html_content.lower() or "view report" in html_content.lower():
        navigation_notice = '''
        <div style="background: linear-gradient(135deg, #4D1D82, #8b1d82); color: white; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 5px solid #cf022b;">
            <strong>🎯 How to Navigate:</strong> Use the dropdown selector above this viewer to switch between different reports. 
            The links below show what reports are available - select the corresponding option from the dropdown to view each report.
        </div>
        '''
        # Insert after body tag or at the beginning
        if '<body' in html_content:
            html_content = re.sub(r'(<body[^>]*>)', r'\1' + navigation_notice, html_content)
        else:
            html_content = navigation_notice + html_content
    
    # Display the HTML report in an iframe-like component with bidirectional communication
    clicked_report = st.components.v1.html(
        html_content,
        height=800,
        scrolling=True
    )
    
    # Handle navigation requests from HTML links
    if clicked_report:
        # Find the report that matches the clicked link
        for report in reports:
            display_name = f"{report['persona_name']} - {report['report_type']}"
            if display_name == clicked_report:
                # Store the selection and rerun to update the dropdown
                st.session_state.selected_report_name = clicked_report
                st.rerun()
    
    # Technical details in a much more compact expander at the bottom
    with st.expander("🔧 Technical Details"):
        details_col1, details_col2 = st.columns(2)
        with details_col1:
            st.write(f"**Path:** `{selected_report['relative_path']}`")
            st.write(f"**Category:** {selected_report['category']}")
        with details_col2:
            st.write(f"**Type:** {selected_report['report_type']}")
            try:
                file_stats = os.stat(selected_report['file_path'])
                st.write(f"**Size:** {file_stats.st_size:,} bytes")
            except:
                st.write("**Size:** Unknown")

else:
    # Fallback if no reports available
    st.markdown("**📋 No Reports Available**")
    st.info("Generate reports using the button above to view audit content.")

# Compact help at the very bottom
with st.expander("ℹ️ Quick Help"):
    st.markdown("""
    **Quick Usage:** Page auto-loads the main report → Use dropdown to switch reports → Download individual or bulk reports
    
    **Features:** Auto-loading default report • In-dashboard viewing • No new windows • ZIP downloads • Auto-regeneration from latest data
    """) 