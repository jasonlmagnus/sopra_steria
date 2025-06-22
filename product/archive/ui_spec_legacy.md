# UI Specification: Brand Audit Tool

**Complete Interface Design for Upload & Report Generation**

**Status: ✅ IMPLEMENTED - Streamlit dashboard fully functional**  
**Location:** `dashboard/streamlit_dashboard.py`

---

## 1. Overview

The Brand Audit Tool is a comprehensive Streamlit web application that enables users to analyze websites against defined personas. The interface consists of two primary states: **Configuration & Upload** and **Report Generation & Viewing**. The design emphasizes clean aesthetics, intuitive workflows, and professional presentation of complex audit data within Streamlit's component framework.

## 1.1 2025-06 Dashboard Revamp (YAML-Driven Pipeline)

The UI now follows the multi-page architecture defined in `product/ui/technical_architecture.md`.
Key pages and their purposes:

| Page                    | Purpose                                                                                |
| ----------------------- | -------------------------------------------------------------------------------------- |
| **Run Audit**           | Upload persona + URLs, trigger audit, live log stream                                  |
| **Executive Overview**  | KPI tiles, descriptor donut, tier contribution bar – high-level health of selected run |
| **Persona Comparison**  | Radar & heat-map to compare criteria scores across personas                            |
| **Criteria Explorer**   | Histogram + evidence modal for a chosen criterion/tier                                 |
| **Priority Actions**    | Critical gaps & quick-wins cards with evidence links                                   |
| **Journey Consistency** | Journey ribbon per persona, variance alerts                                            |
| **Gating Breaches**     | Compliance table filtered by gating-rule severity                                      |
| **Evidence Gallery**    | Best / worst quotes browser, copy-to-clipboard                                         |
| **Run History**         | Trend charts across historical runs                                                    |
| **Raw Data**            | DataFrame viewer & export (CSV/Parquet/JSON)                                           |

The interface state machine remains **Configuration & Upload → Report Viewing**, but the Report state is now broken into the pages above instead of legacy tabs.

All visual components pull data from run-level Parquet/JSON artefacts (`audit_runs/<run_id>/…`) via the **DataGateway** layer described in the Technical Architecture.

---

## 2. Design Principles

- **Clean Streamlit Aesthetics**: Leveraging Streamlit's native design system with custom CSS enhancements
- **Progressive Disclosure**: Information revealed contextually using expanders and tabs
- **Responsive Design**: Streamlit's built-in responsive behavior with custom mobile optimizations
- **Accessibility First**: Following Streamlit's accessibility patterns with ARIA enhancements
- **Performance Focused**: Efficient state management and lazy loading of report content

---

## 3. State 1: Configuration & Upload Interface

### 3.1 Layout Structure

**Header Section**

```python
st.set_page_config(
    page_title="Brand Audit Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2563EB 0%, #1D4ED8 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        color: white;
        border-radius: 0 0 12px 12px;
    }
    .upload-zone {
        border: 2px dashed #CBD5E1;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        background: #F8FAFC;
    }
    .upload-zone:hover {
        border-color: #2563EB;
        background: #EEF2FF;
    }
</style>
""", unsafe_allow_html=True)
```

**Main Content Area**

- Centered layout with Streamlit's container system
- Single-column design using `st.container()` and `st.columns()`
- Card-based design with custom CSS styling
- 8px grid system implemented through padding classes

### 3.2 Upload Configuration Panel

**Container Design**

```python
with st.container():
    st.markdown('<div class="upload-container">', unsafe_allow_html=True)

    # Section 1: Persona File Upload
    st.markdown("### 📋 Step 1: Upload Persona File")
    persona_file = st.file_uploader(
        "Choose your persona markdown file",
        type=['md'],
        help="Upload a .md file containing your target persona definition",
        key="persona_upload"
    )

    # Visual feedback for upload states
    if persona_file:
        st.success(f"✅ Persona file loaded: {persona_file.name}")
        st.info(f"File size: {len(persona_file.getvalue())} bytes")

    st.markdown("---")

    # Section 2: URL Input
    st.markdown("### 🌐 Step 2: Enter URLs to Audit")
    urls_text = st.text_area(
        "URLs to analyze (one per line)",
        height=150,
        placeholder="https://example.com\nhttps://example.com/about\nhttps://example.com/services",
        help="Enter each URL on a separate line"
    )

    # Real-time URL count and validation
    if urls_text:
        urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        valid_urls = [url for url in urls if url.startswith(('http://', 'https://'))]

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total URLs", len(urls))
        with col2:
            st.metric("Valid URLs", len(valid_urls))

        if len(urls) != len(valid_urls):
            st.warning(f"⚠️ {len(urls) - len(valid_urls)} invalid URLs detected")

    st.markdown("---")

    # Section 3: Action Button
    can_run = persona_file is not None and urls_text.strip()

    if st.button(
        "🚀 Run Brand Audit",
        disabled=not can_run or st.session_state.get('audit_running', False),
        use_container_width=True,
        type="primary"
    ):
        st.session_state.audit_running = True
        st.rerun()
```

### 3.3 Visual Hierarchy Implementation

**Typography Scale (Custom CSS)**

```css
.metric-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}
.section-header {
  font-size: 18px;
  font-weight: 500;
  color: #374151;
}
.body-text {
  font-size: 14px;
  line-height: 1.5;
  color: #6b7280;
}
.label-text {
  font-size: 12px;
  font-weight: 500;
  color: #9ca3af;
}
```

**Color System Integration**

- Primary: Streamlit's default blue with custom CSS overrides
- Success: Green (#059669) for completed states
- Warning: Amber (#D97706) for attention items
- Error: Red (#DC2626) for validation issues
- Neutral: Streamlit's gray scale enhanced with custom shades

---

## 4. State 2: Report Generation & Viewing Interface

### 4.1 Layout Transformation

**Header Evolution**

```python
# Progress header during audit
if st.session_state.get('audit_running'):
    progress_container = st.container()
    with progress_container:
        st.markdown("### 🔄 Audit in Progress")
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Real-time progress updates
        for i, url in enumerate(urls):
            progress_bar.progress((i + 1) / len(urls))
            status_text.text(f"Processing: {url}")
```

**Main Layout Structure**

```python
# Two-column layout for reports
if st.session_state.get('audit_complete'):
    sidebar_col, main_col = st.columns([1, 3])

    with sidebar_col:
        st.markdown("### 📊 Navigation")
        # Sidebar navigation implementation

    with main_col:
        st.markdown("### 📈 Audit Results")
        # Main report content
```

### 4.2 Sidebar Navigation (Desktop)

**Audit Configuration Summary**

```python
with st.sidebar:
    st.markdown("### ⚙️ Audit Configuration")

    with st.expander("📋 Persona Details", expanded=False):
        if persona_file:
            st.text(f"File: {persona_file.name}")
            st.text(f"Size: {len(persona_file.getvalue())} bytes")

    with st.expander("🌐 URLs Analyzed", expanded=False):
        for i, url in enumerate(urls, 1):
            st.text(f"{i}. {url}")

    st.markdown("---")

    # Report Navigation
    st.markdown("### 📑 Report Sections")

    report_sections = [
        ("📊 Strategic Summary", "summary"),
        ("🔍 Individual Reports", "individual"),
        ("📋 Audit Log", "log")
    ]

    selected_section = st.radio(
        "Navigate to:",
        options=[section[1] for section in report_sections],
        format_func=lambda x: next(section[0] for section in report_sections if section[1] == x),
        key="navigation"
    )
```

### 4.3 Main Content Area Implementation

**Live Audit Log Section**

```python
if selected_section == "log":
    st.markdown("### 📋 Live Audit Log")

    with st.expander("🖥️ Terminal Output", expanded=True):
        log_container = st.container()

        # Terminal-style log display
        st.markdown("""
        <style>
        .log-container {
            background-color: #1E1E1E;
            color: #FFFFFF;
            font-family: 'Courier New', monospace;
            padding: 1rem;
            border-radius: 8px;
            height: 400px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)

        # Real-time log streaming
        if 'audit_logs' in st.session_state:
            log_text = "\n".join(st.session_state.audit_logs)
            st.code(log_text, language="bash")
```

**Strategic Summary Report**

```python
if selected_section == "summary":
    st.markdown("### 📊 Strategic Summary Report")

    # Key metrics dashboard
    if 'summary_data' in st.session_state:
        summary = st.session_state.summary_data

        # Hero metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Overall Score", f"{summary['overall_score']:.1f}/10")
        with col2:
            st.metric("Pages Analyzed", summary['total_pages'])
        with col3:
            st.metric("Critical Issues", summary['critical_count'])
        with col4:
            st.metric("Success Rate", f"{summary['success_rate']:.0%}")

        # Executive summary
        st.markdown("#### 📝 Executive Summary")
        st.markdown(summary['executive_summary'])

        # Expandable detailed sections
        with st.expander("💪 Key Strengths", expanded=False):
            for strength in summary['key_strengths']:
                st.markdown(f"• {strength}")

        with st.expander("⚠️ Areas for Improvement", expanded=False):
            for weakness in summary['key_weaknesses']:
                st.markdown(f"• {weakness}")
```

**Individual URL Reports**

```python
if selected_section == "individual":
    st.markdown("### 🔍 Individual URL Reports")

    for url_data in st.session_state.get('url_reports', []):
        with st.expander(f"🌐 {url_data['url']}", expanded=False):

            # Score display
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"**Overall Score:** {url_data['score']:.1f}/10")
            with col2:
                # Color-coded score indicator
                score_color = "🟢" if url_data['score'] >= 7 else "🟡" if url_data['score'] >= 4 else "🔴"
                st.markdown(f"{score_color} **{url_data['health_status']}**")

            # Tabbed interface for different report types
            tab1, tab2 = st.tabs(["📖 Experience Report", "📊 Hygiene Scorecard"])

            with tab1:
                st.markdown("#### Persona Experience Analysis")
                st.markdown(url_data['experience_report'])

            with tab2:
                st.markdown("#### Technical Metrics")

                # Score breakdown table
                score_df = pd.DataFrame(url_data['scorecard_data'])
                st.dataframe(score_df, use_container_width=True)

                # Progress bars for each criterion
                for criterion in url_data['criteria']:
                    st.markdown(f"**{criterion['name']}**")
                    st.progress(criterion['score'] / 10)
                    st.caption(criterion['notes'])
```

### 4.4 Report Content Formatting

**Markdown Rendering Enhancement**

```python
# Custom CSS for professional typography
st.markdown("""
<style>
    .report-content {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        line-height: 1.6;
        color: #374151;
    }
    .report-content h1 { color: #1F2937; border-bottom: 2px solid #E5E7EB; }
    .report-content h2 { color: #374151; margin-top: 2rem; }
    .report-content table { border-collapse: collapse; width: 100%; }
    .report-content th, .report-content td {
        border: 1px solid #E5E7EB;
        padding: 0.75rem;
        text-align: left;
    }
    .report-content th { background-color: #F9FAFB; font-weight: 600; }
</style>
""", unsafe_allow_html=True)
```

**Interactive Elements**

```python
# Expandable sections with smooth animations
def create_expandable_section(title, content, expanded=False):
    with st.expander(title, expanded=expanded):
        st.markdown(f'<div class="report-content">{content}</div>',
                   unsafe_allow_html=True)

# Score visualizations
def create_score_chart(scores_data):
    fig = px.bar(
        x=list(scores_data.keys()),
        y=list(scores_data.values()),
        title="Criteria Scores",
        color=list(scores_data.values()),
        color_continuous_scale="RdYlGn"
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
```

---

## 5. Responsive Design Implementation

### 5.1 Streamlit Mobile Adaptations

**Mobile-Optimized Layout**

```python
# Detect mobile viewport
def is_mobile():
    return st.session_state.get('mobile_view', False)

if is_mobile():
    # Single-column layout for mobile
    st.markdown("### 📱 Mobile View")

    # Collapsible navigation
    with st.expander("📑 Navigation Menu", expanded=False):
        selected_section = st.selectbox(
            "Choose section:",
            ["summary", "individual", "log"],
            format_func=lambda x: {
                "summary": "📊 Strategic Summary",
                "individual": "🔍 Individual Reports",
                "log": "📋 Audit Log"
            }[x]
        )

    # Touch-optimized buttons
    st.markdown("""
    <style>
    .stButton > button {
        height: 44px;
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)
```

### 5.2 Responsive Components

**Adaptive Metrics Display**

```python
def display_metrics_responsive(metrics_data):
    # Desktop: 4 columns, Tablet: 2 columns, Mobile: 1 column
    if st.session_state.get('viewport_width', 1200) > 1024:
        cols = st.columns(4)
    elif st.session_state.get('viewport_width', 1200) > 768:
        cols = st.columns(2)
    else:
        cols = [st.container()]

    for i, (key, value) in enumerate(metrics_data.items()):
        with cols[i % len(cols)]:
            st.metric(key, value)
```

---

## 6. Interaction Design

### 6.1 Streamlit Micro-interactions

**Loading States**

```python
# Custom loading spinner
def show_loading_state(message="Processing..."):
    with st.spinner(message):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)

# Success animations
def show_success_message(message):
    st.success(message)
    st.balloons()  # Streamlit's built-in celebration animation
```

**Form Validation**

```python
def validate_urls(urls_text):
    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
    valid_urls = []
    invalid_urls = []

    for url in urls:
        if url.startswith(('http://', 'https://')):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)

    if invalid_urls:
        st.error(f"❌ Invalid URLs detected: {', '.join(invalid_urls)}")
        return False, valid_urls

    return True, valid_urls
```

### 6.2 Navigation Patterns

**Breadcrumb Navigation**

```python
def render_breadcrumbs(current_section):
    breadcrumbs = {
        "home": "🏠 Home",
        "summary": "🏠 Home > 📊 Summary",
        "individual": "🏠 Home > 🔍 Individual Reports",
        "log": "🏠 Home > 📋 Audit Log"
    }

    st.markdown(f"**{breadcrumbs.get(current_section, '🏠 Home')}**")
```

**Search Functionality**

```python
def add_report_search():
    search_term = st.text_input("🔍 Search reports", placeholder="Enter keywords...")

    if search_term:
        # Filter reports based on search term
        filtered_reports = [
            report for report in st.session_state.get('url_reports', [])
            if search_term.lower() in report['content'].lower()
        ]
        return filtered_reports

    return st.session_state.get('url_reports', [])
```

---

## 7. Performance Considerations

### 7.1 Streamlit Optimization

**Caching Strategies**

```python
@st.cache_data
def load_report_data(file_path):
    """Cache report data to avoid reloading"""
    with open(file_path, 'r') as f:
        return f.read()

@st.cache_resource
def initialize_audit_engine():
    """Cache audit engine initialization"""
    return AuditEngine()

# Session state management
if 'report_cache' not in st.session_state:
    st.session_state.report_cache = {}
```

**Lazy Loading Implementation**

```python
def render_reports_paginated(reports, page_size=5):
    """Paginate large report lists"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0

    start_idx = st.session_state.current_page * page_size
    end_idx = start_idx + page_size

    current_reports = reports[start_idx:end_idx]

    for report in current_reports:
        render_single_report(report)

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← Previous", disabled=st.session_state.current_page == 0):
            st.session_state.current_page -= 1
            st.rerun()

    with col2:
        st.write(f"Page {st.session_state.current_page + 1} of {len(reports) // page_size + 1}")

    with col3:
        if st.button("Next →", disabled=end_idx >= len(reports)):
            st.session_state.current_page += 1
            st.rerun()
```

---

## 8. Accessibility Features

### 8.1 Streamlit Accessibility Enhancement

**Screen Reader Support**

```python
# Semantic HTML structure
st.markdown("""
<div role="main" aria-label="Brand Audit Tool Main Content">
    <h1 id="main-heading">Brand Audit Results</h1>
</div>
""", unsafe_allow_html=True)

# ARIA labels for complex components
def accessible_metric(label, value, description=""):
    st.markdown(f"""
    <div role="region" aria-labelledby="metric-{label.lower()}">
        <h3 id="metric-{label.lower()}">{label}</h3>
        <p aria-describedby="metric-desc-{label.lower()}">{value}</p>
        <small id="metric-desc-{label.lower()}">{description}</small>
    </div>
    """, unsafe_allow_html=True)
```

**Keyboard Navigation**

```python
# Focus management for dynamic content
st.markdown("""
<script>
    // Focus management for screen readers
    function focusElement(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.focus();
            element.scrollIntoView({behavior: 'smooth'});
        }
    }
</script>
""", unsafe_allow_html=True)
```

### 8.2 Visual Accessibility

**High Contrast Mode**

```python
def apply_accessibility_theme():
    st.markdown("""
    <style>
    @media (prefers-contrast: high) {
        .stApp {
            --primary-color: #000000;
            --background-color: #FFFFFF;
            --secondary-background-color: #F0F0F0;
            --text-color: #000000;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        * {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
```

---

## 9. Implementation Architecture

### 9.1 Streamlit App Structure

```python
def main():
    # App configuration
    configure_app()

    # Initialize session state
    initialize_session_state()

    # Apply custom styling
    apply_custom_css()

    # Route to appropriate interface state
    if st.session_state.get('audit_complete'):
        render_report_interface()
    else:
        render_upload_interface()

def configure_app():
    st.set_page_config(
        page_title="Brand Audit Tool",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session_state():
    defaults = {
        'audit_running': False,
        'audit_complete': False,
        'report_data': None,
        'current_page': 0,
        'selected_section': 'summary'
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
```

### 9.2 State Management

**Persistent Storage**

```python
def save_session_data():
    """Save important session data to local storage"""
    session_data = {
        'persona_file': st.session_state.get('persona_file'),
        'urls': st.session_state.get('urls'),
        'report_data': st.session_state.get('report_data')
    }

    # Use Streamlit's session state for persistence
    st.session_state['saved_session'] = session_data

def load_session_data():
    """Restore session data from local storage"""
    if 'saved_session' in st.session_state:
        return st.session_state['saved_session']
    return None
```

---

## 10. Future Enhancement Considerations

### 10.1 Advanced Streamlit Features

**Multi-page Application**

```python
# pages/home.py
def render_home_page():
    st.title("🏠 Brand Audit Dashboard")
    # Home page implementation

# pages/history.py
def render_history_page():
    st.title("📈 Audit History")
    # Historical audit tracking

# pages/settings.py
def render_settings_page():
    st.title("⚙️ Settings")
    # User preferences and configuration
```

**Advanced Visualizations**

```python
import plotly.express as px
import plotly.graph_objects as go

def create_audit_dashboard():
    """Advanced dashboard with interactive charts"""

    # Radar chart for multi-dimensional scoring
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(scores.values()),
        theta=list(scores.keys()),
        fill='toself',
        name='Current Audit'
    ))

    st.plotly_chart(fig, use_container_width=True)

    # Time series for historical trends
    if historical_data:
        fig = px.line(
            historical_data,
            x='date',
            y='score',
            title='Audit Score Trends'
        )
        st.plotly_chart(fig, use_container_width=True)
```

### 10.2 Integration Capabilities

**Export Functionality**

```python
def export_reports():
    """Export audit reports in multiple formats"""

    export_format = st.selectbox(
        "Export Format:",
        ["PDF", "Excel", "JSON", "CSV"]
    )

    if st.button("📥 Export Reports"):
        if export_format == "PDF":
            pdf_data = generate_pdf_report()
            st.download_button(
                label="Download PDF Report",
                data=pdf_data,
                file_name="brand_audit_report.pdf",
                mime="application/pdf"
            )
        # Additional export formats...
```

---

This comprehensive UI specification provides the foundation for a professional, accessible, and feature-rich brand audit tool built with Streamlit. The implementation balances Streamlit's native capabilities with custom enhancements to deliver an enterprise-grade user experience.
