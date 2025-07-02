"""
Reports & Export - Comprehensive Data & Audit Management
How do I analyze data and run new audits?
Consolidates Detailed Data + Run Audit functionality
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
import os
import json
from datetime import datetime
import zipfile
import io

# Add parent directory to path to import components
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

# Import HTML report generator with proper path handling
try:
    from audit_tool.html_report_generator import HTMLReportGenerator
except ImportError:
    # Try alternative import path
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent / "audit_tool"))
    from html_report_generator import HTMLReportGenerator

# Page configuration
st.set_page_config(
    page_title="Reports & Export",
    page_icon="📋",
    layout="wide"
)

# Import centralized brand styling (fonts already loaded on home page)
from components.brand_styling import get_brand_css
st.markdown(get_brand_css(), unsafe_allow_html=True)

def main():
    """Reports & Export - Comprehensive Data & Audit Management"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📋 Reports & Export</h1>
        <p>How do I analyze data and run new audits?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data from session state or initialize
    if 'datasets' not in st.session_state or 'master_df' not in st.session_state:
        data_loader = BrandHealthDataLoader()
        datasets, master_df = data_loader.load_all_data()
        st.session_state['datasets'] = datasets
        st.session_state['master_df'] = master_df
    else:
        datasets = st.session_state['datasets']
        master_df = st.session_state['master_df']
    
    # Tab selection
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Explorer", "📈 Custom Reports", "🎨 HTML Reports", "📦 Export Center"])
    
    with tab1:
        display_data_explorer(master_df, datasets)
    
    with tab2:
        display_custom_reports(master_df, datasets)
    
    with tab3:
        display_html_reports(master_df)
    
    with tab4:
        display_export_center(master_df, datasets)

def display_data_explorer(master_df, datasets):
    """Display comprehensive data exploration interface (from Detailed Data page)"""
    st.markdown("## 🔍 Data Explorer")
    
    if master_df.empty:
        st.error("❌ No data available for exploration.")
        return
    
    # Data overview
    display_data_overview(master_df, datasets)
    
    # Interactive data filtering
    display_data_filters(master_df)
    
    # Apply filters and display filtered data
    filtered_df = apply_data_filters(master_df)
    
    # Display filtered data
    display_filtered_data(filtered_df)
    
    # Data quality insights
    display_data_quality_insights(filtered_df)

def display_data_overview(master_df, datasets):
    """Display high-level data overview"""
    st.markdown("### 📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_records = len(master_df)
        st.metric("Total Records", f"{total_records:,}")
    
    with col2:
        unique_pages = len(master_df['page_id'].unique()) if 'page_id' in master_df.columns else 0
        st.metric("Unique Pages", f"{unique_pages:,}")
    
    with col3:
        unique_personas = len(master_df['persona_id'].unique()) if 'persona_id' in master_df.columns else 0
        st.metric("Personas", unique_personas)
    
    with col4:
        data_completeness = (master_df.notna().sum().sum() / (len(master_df) * len(master_df.columns)) * 100) if not master_df.empty else 0
        st.metric("Data Completeness", f"{data_completeness:.1f}%")
    
    # Dataset breakdown
    if datasets:
        st.markdown("### 📋 Dataset Breakdown")
        
        dataset_info = []
        for name, df in datasets.items():
            if df is not None and not df.empty:
                dataset_info.append({
                    'Dataset': name.title(),
                    'Records': len(df),
                    'Columns': len(df.columns),
                    'Memory (MB)': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.1f}"
                })
        
        if dataset_info:
            dataset_df = pd.DataFrame(dataset_info)
            st.dataframe(dataset_df)

    # Only create chart if dataset_info is properly structured
    if dataset_info and isinstance(dataset_info, list) and len(dataset_info) > 0:
        # Convert to DataFrame first to handle structure properly
        dataset_df = pd.DataFrame(dataset_info)
        
        if 'Dataset' in dataset_df.columns and len(dataset_df) > 0:
            fig = px.bar(
                dataset_df,
                x='Count' if 'Count' in dataset_df.columns else dataset_df.columns[1],
                y='Dataset',
                orientation='h',
                title="Dataset Breakdown"
            )
        else:
            # Fallback chart if structure is different
            fig = px.bar(
                x=[len(dataset_info)],
                y=['Total Records'],
                orientation='h',
                title="Dataset Overview"
            )
    fig.update_layout(height=400)
    st.plotly_chart(fig)

def display_data_filters(master_df):
    """Display interactive data filtering controls"""
    st.markdown("### 🎛️ Data Filters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Persona filter
        personas = ['All'] + sorted(master_df['persona_id'].unique().tolist()) if 'persona_id' in master_df.columns else ['All']
        selected_persona = st.selectbox(
            "👤 Persona",
            personas,
            key="data_persona_filter"
        )
    
    with col2:
        # Tier filter
        tiers = ['All'] + sorted([t for t in master_df['tier'].unique() if pd.notna(t)]) if 'tier' in master_df.columns else ['All']
        selected_tier = st.selectbox(
            "🏗️ Tier",
            tiers,
            key="data_tier_filter"
        )
    
    with col3:
        # Score range
        if 'avg_score' in master_df.columns:
            min_score, max_score = st.slider(
                "📊 Score Range",
                float(master_df['avg_score'].min()),
                float(master_df['avg_score'].max()),
                (float(master_df['avg_score'].min()), float(master_df['avg_score'].max())),
                key="data_score_range"
            )
    
    with col4:
        # Column selection
        available_columns = master_df.columns.tolist()
        selected_columns = st.multiselect(
            "📋 Columns to Display",
            available_columns,
            default=available_columns[:10] if len(available_columns) > 10 else available_columns,
            key="data_columns_filter"
        )

def apply_data_filters(master_df):
    """Apply selected filters to the dataset"""
    filtered_df = master_df.copy()
    
    # Persona filter
    if st.session_state.get('data_persona_filter', 'All') != 'All':
        filtered_df = filtered_df[filtered_df['persona_id'] == st.session_state['data_persona_filter']]
    
    # Tier filter
    if st.session_state.get('data_tier_filter', 'All') != 'All':
        filtered_df = filtered_df[filtered_df['tier'] == st.session_state['data_tier_filter']]
    
    # Score range filter
    if 'avg_score' in filtered_df.columns and 'data_score_range' in st.session_state:
        min_score, max_score = st.session_state['data_score_range']
        filtered_df = filtered_df[(filtered_df['avg_score'] >= min_score) & (filtered_df['avg_score'] <= max_score)]
    
    # Column selection
    if 'data_columns_filter' in st.session_state and st.session_state['data_columns_filter']:
        available_columns = [col for col in st.session_state['data_columns_filter'] if col in filtered_df.columns]
        if available_columns:
            filtered_df = filtered_df[available_columns]
    
    return filtered_df

def display_filtered_data(filtered_df):
    """Display the filtered dataset"""
    st.markdown("### 📊 Filtered Data")
    
    if filtered_df.empty:
        st.warning("⚠️ No data matches the selected filters.")
        return
    
    st.info(f"📊 Showing {len(filtered_df):,} records after filtering")
    
    # Display options
    col1, col2 = st.columns(2)
    
    with col1:
        display_mode = st.radio(
            "Display Mode",
            ["Table View", "Summary Statistics"],
            key="data_display_mode"
        )
    
    with col2:
        if display_mode == "Table View":
            max_rows = st.number_input(
                "Max Rows to Display",
                min_value=10, max_value=1000, value=100,
                key="data_max_rows"
            )
    
    # Display data based on mode
    if display_mode == "Table View":
        max_rows = st.session_state.get('data_max_rows', 100)
        display_df = filtered_df.head(max_rows)
        
        # Style numeric columns
        numeric_columns = display_df.select_dtypes(include=['float64', 'int64']).columns
        styled_df = display_df.style.format({col: '{:.2f}' for col in numeric_columns if col in display_df.columns})
        
        st.dataframe(styled_df)
        
        if len(filtered_df) > max_rows:
            st.info(f"💡 Showing first {max_rows:,} rows of {len(filtered_df):,} total records")
    
    else:  # Summary Statistics
        st.markdown("#### 📈 Summary Statistics")
        
        # Numeric columns summary
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            summary_stats = filtered_df[numeric_cols].describe().round(2)
            st.dataframe(summary_stats)
        
        # Categorical columns summary
        categorical_cols = filtered_df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            st.markdown("#### 📊 Categorical Data Summary")
            
            for col in categorical_cols[:5]:  # Show top 5 categorical columns
                if col in filtered_df.columns:
                    value_counts = filtered_df[col].value_counts().head(10)
                    
                    with st.expander(f"📋 {col} - Top Values"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.dataframe(value_counts.to_frame(name='Count'))
                        
                        with col2:
                            if len(value_counts) > 1:
                                fig = px.bar(
                                    x=value_counts.values,
                                    y=value_counts.index,
                                    orientation='h',
                                    title=f"Top Values - {col}"
                                )
                                fig.update_layout(height=400)
                                st.plotly_chart(fig)

def display_data_quality_insights(filtered_df):
    """Display data quality insights"""
    st.markdown("### 🔍 Data Quality Insights")
    
    if filtered_df.empty:
        st.info("📊 No data available for quality analysis.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Missing Data Analysis")
        
        missing_data = filtered_df.isnull().sum()
        missing_pct = (missing_data / len(filtered_df) * 100).round(1)
        
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Missing %': missing_pct.values
        })
        
        # Filter to show only columns with missing data
        missing_df = missing_df[missing_df['Missing Count'] > 0].sort_values('Missing %', ascending=False)
        
        if not missing_df.empty:
            st.dataframe(missing_df)
        else:
            st.success("✅ No missing data found!")
    
    with col2:
        st.markdown("#### 📈 Data Distribution Insights")
        
        # Numeric columns distribution
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_cols) > 0:
            selected_numeric_col = st.selectbox(
                "Select Column for Distribution Analysis",
                numeric_cols,
                key="quality_numeric_col"
            )
            
            if selected_numeric_col:
                fig = px.histogram(
                    filtered_df,
                    x=selected_numeric_col,
                    title=f"Distribution - {selected_numeric_col}",
                    nbins=30
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig)

def display_custom_reports(master_df, datasets):
    """Display custom report generation interface"""
    st.markdown("## 📈 Custom Reports")
    
    if master_df.empty:
        st.error("❌ No data available for custom reports.")
        return
    
    # Report type selection
    st.markdown("### 📋 Report Configuration")
    
    report_types = [
        "Executive Summary Report",
        "Persona Performance Report",
        "Content Tier Analysis Report",
        "Criteria Deep Dive Report",
        "Success Stories Report",
        "Improvement Opportunities Report"
    ]
    
    selected_report_type = st.selectbox(
        "📊 Report Type",
        report_types,
        key="custom_report_type"
    )
    
    # Report configuration
    display_report_configuration(master_df, selected_report_type)
    
    # Generate report
    if st.button("📊 Generate Custom Report"):
        generate_custom_report(master_df, selected_report_type)

def display_report_configuration(master_df, report_type):
    """Display configuration options for custom reports"""
    st.markdown("### ⚙️ Report Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Date range (if applicable)
        st.date_input(
            "📅 Report Date",
            value=datetime.now().date(),
            key="report_date"
        )
    
    with col2:
        # Persona filter for report
        personas = ['All'] + sorted(master_df['persona_id'].unique().tolist()) if 'persona_id' in master_df.columns else ['All']
        selected_persona = st.selectbox(
            "👤 Focus Persona",
            personas,
            key="report_persona"
        )
    
    with col3:
        # Report format
        report_formats = ["PDF", "PowerPoint", "Excel", "CSV", "JSON"]
        selected_format = st.selectbox(
            "📄 Export Format",
            report_formats,
            key="report_format"
        )
    
    # Report-specific configurations
    if report_type == "Executive Summary Report":
        st.markdown("#### 🎯 Executive Summary Options")
        
        col1, col2 = st.columns(2)
        with col1:
            include_charts = st.checkbox("Include Charts", value=True)
        with col2:
            include_recommendations = st.checkbox("Include AI Recommendations", value=True)
    
    elif report_type == "Persona Performance Report":
        st.markdown("#### 👥 Persona Report Options")
        
        col1, col2 = st.columns(2)
        with col1:
            include_comparison = st.checkbox("Include Persona Comparison", value=True)
        with col2:
            include_journey = st.checkbox("Include Journey Analysis", value=True)

def generate_custom_report(master_df, report_type):
    """Generate the custom report based on configuration"""
    st.markdown("### 📊 Generated Report")
    
    # Initialize metrics calculator
    metrics_calc = BrandHealthMetricsCalculator(master_df, None)
    
    try:
        if report_type == "Executive Summary Report":
            generate_executive_summary_report(master_df, metrics_calc)
        elif report_type == "Persona Performance Report":
            generate_persona_performance_report(master_df, metrics_calc)
        elif report_type == "Content Tier Analysis Report":
            generate_content_tier_report(master_df, metrics_calc)
        elif report_type == "Success Stories Report":
            generate_success_stories_report(master_df, metrics_calc)
        else:
            st.info(f"📊 {report_type} generation is in development.")
        
        st.success("✅ Report generated successfully!")
        
    except Exception as e:
        st.error(f"❌ Error generating report: {str(e)}")

def generate_executive_summary_report(master_df, metrics_calc):
    """Generate executive summary report using real data"""
    st.markdown("#### 🎯 Executive Summary Report")
    
    if master_df.empty:
        st.warning("⚠️ No data available for executive summary.")
        return
    
    # Calculate real metrics from data
    total_records = len(master_df)
    unique_pages = master_df['page_id'].nunique() if 'page_id' in master_df.columns else 0
    avg_score = master_df['final_score'].mean() if 'final_score' in master_df.columns else 0
    
    # Count issues by severity
    critical_issues = len(master_df[master_df['descriptor'] == 'CRITICAL']) if 'descriptor' in master_df.columns else 0
    concerns = len(master_df[master_df['descriptor'] == 'CONCERN']) if 'descriptor' in master_df.columns else 0
    warnings = len(master_df[master_df['descriptor'] == 'WARN']) if 'descriptor' in master_df.columns else 0
    good_scores = len(master_df[master_df['descriptor'] == 'GOOD']) if 'descriptor' in master_df.columns else 0
    
    # Display real metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", f"{total_records:,}")
    with col2:
        st.metric("Unique Pages", f"{unique_pages:,}")
    with col3:
        st.metric("Average Score", f"{avg_score:.1f}/10")
    with col4:
        st.metric("Critical Issues", critical_issues)
    
    st.markdown(f"""
    **Audit Overview:**
    - 🔴 Critical Issues: {critical_issues}
    - 🟠 Concerns: {concerns}  
    - 🟡 Warnings: {warnings}
    - 🟢 Good Scores: {good_scores}
    """)
    
    # Top issues by criteria
    if 'criterion_id' in master_df.columns and 'final_score' in master_df.columns:
        st.markdown("**Top Issues by Criteria:**")
        low_scoring_criteria = master_df[master_df['final_score'] < 6].groupby('criterion_id')['final_score'].mean().sort_values().head(5)
        for criterion, score in low_scoring_criteria.items():
            st.markdown(f"- {criterion.replace('_', ' ').title()}: {score:.1f}/10")

def generate_persona_performance_report(master_df, metrics_calc):
    """Generate persona performance report"""
    st.markdown("#### 👥 Persona Performance Report")
    
    if 'persona_id' in master_df.columns and 'avg_score' in master_df.columns:
        persona_performance = master_df.groupby('persona_id')['avg_score'].agg(['mean', 'count']).round(2)
        persona_performance.columns = ['Average Score', 'Page Count']
        persona_performance = persona_performance.sort_values('Average Score', ascending=False)
        
        st.dataframe(persona_performance)
        
        # Persona insights
        best_persona = persona_performance['Average Score'].idxmax()
        worst_persona = persona_performance['Average Score'].idxmin()
        
        st.markdown(f"""
        **Key Insights:**
        - Best Performing Persona: {best_persona} ({persona_performance.loc[best_persona, 'Average Score']:.1f}/10)
        - Needs Attention: {worst_persona} ({persona_performance.loc[worst_persona, 'Average Score']:.1f}/10)
        """)

def generate_content_tier_report(master_df, metrics_calc):
    """Generate content tier analysis report"""
    st.markdown("#### 🏗️ Content Tier Analysis Report")
    
    if 'tier' in master_df.columns and 'avg_score' in master_df.columns:
        tier_performance = master_df.groupby('tier')['avg_score'].agg(['mean', 'count', 'std']).round(2)
        tier_performance.columns = ['Average Score', 'Page Count', 'Score Variation']
        tier_performance = tier_performance.sort_values('Average Score', ascending=False)
        
        st.dataframe(tier_performance)

def generate_success_stories_report(master_df, metrics_calc):
    """Generate success stories report using real data"""
    st.markdown("#### 🌟 Success Stories Report")
    
    if master_df.empty:
        st.warning("⚠️ No data available for success stories.")
        return
    
    # Find high-scoring pages (success stories)
    if 'final_score' in master_df.columns:
        success_threshold = 7.5
        success_stories = master_df[master_df['final_score'] >= success_threshold]
        
        if not success_stories.empty:
            st.markdown(f"**Found {len(success_stories)} success stories (score ≥ {success_threshold})**")
            
            # Group by page to show unique pages
            if 'page_id' in success_stories.columns:
                page_scores = success_stories.groupby(['page_id', 'url'])['final_score'].mean().sort_values(ascending=False).head(10)
                
                for i, ((page_id, url), score) in enumerate(page_scores.items(), 1):
                    # Get additional info for this page
                    page_data = success_stories[success_stories['page_id'] == page_id].iloc[0]
                    tier = page_data.get('tier_name', 'Unknown') if 'tier_name' in page_data else 'Unknown'
                    
                    st.markdown(f"""
                    **#{i} - Page {page_id}**
                    - Score: {score:.1f}/10
                    - Tier: {tier}
                    - URL: {url[:100]}{'...' if len(url) > 100 else ''}
                    """)
            else:
                # Fallback if no page grouping available
                for i, (_, story) in enumerate(success_stories.head(5).iterrows(), 1):
                    st.markdown(f"""
                    **#{i} - Record {story.get('page_id', 'Unknown')}**
                    - Score: {story['final_score']:.1f}/10
                    - Tier: {story.get('tier_name', 'Unknown')}
                    """)
        else:
            st.info(f"📊 No pages found with score ≥ {success_threshold}. Highest score: {master_df['final_score'].max():.1f}")
    else:
        st.warning("⚠️ No score data available for success stories analysis.")

def display_export_center(master_df, datasets):
    """Display comprehensive export center"""
    st.markdown("## 📦 Export Center")
    
    if master_df.empty:
        st.error("❌ No data available for export.")
        return
    
    # Export options
    display_export_options(master_df, datasets)
    
    # Bulk export functionality
    display_bulk_export(master_df, datasets)

def display_export_options(master_df, datasets):
    """Display individual export options"""
    st.markdown("### 📄 Individual Exports")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📊 Data Exports")
        
        if st.button("📊 Export Master Dataset (CSV)"):
            csv_data = master_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=f"master_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        if st.button("📊 Export Master Dataset (Excel)"):
            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                master_df.to_excel(writer, sheet_name='Master Data', index=False)
            
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name=f"master_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.markdown("#### 📈 Report Exports")
        
        if st.button("📈 Export Summary Report (JSON)"):
            # Generate summary data
            summary_data = {
                "export_timestamp": datetime.now().isoformat(),
                "total_records": len(master_df),
                "unique_pages": len(master_df['page_id'].unique()) if 'page_id' in master_df.columns else 0,
                "unique_personas": len(master_df['persona_id'].unique()) if 'persona_id' in master_df.columns else 0,
                "average_score": master_df['avg_score'].mean() if 'avg_score' in master_df.columns else None
            }
            
            json_data = json.dumps(summary_data, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_data,
                file_name=f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col3:
        st.markdown("#### 🔧 Custom Exports")
        
        # Column selection for custom export
        available_columns = master_df.columns.tolist()
        selected_export_columns = st.multiselect(
            "Select Columns to Export",
            available_columns,
            default=available_columns[:5],
            key="custom_export_columns"
        )
        
        if selected_export_columns and st.button("📊 Export Custom Selection"):
            custom_df = master_df[selected_export_columns]
            csv_data = custom_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Custom CSV",
                data=csv_data,
                file_name=f"custom_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def display_bulk_export(master_df, datasets):
    """Display bulk export functionality"""
    st.markdown("### 📦 Bulk Export")
    
    if st.button("📦 Create Complete Export Package"):
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add master dataset
            csv_data = master_df.to_csv(index=False)
            zip_file.writestr(f"master_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", csv_data)
            
            # Add individual datasets if available
            if datasets:
                for name, df in datasets.items():
                    if df is not None and not df.empty:
                        dataset_csv = df.to_csv(index=False)
                        zip_file.writestr(f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", dataset_csv)
            
            # Add metadata
            metadata = {
                "export_timestamp": datetime.now().isoformat(),
                "total_records": len(master_df),
                "datasets_included": list(datasets.keys()) if datasets else [],
                "export_type": "complete_package"
            }
            zip_file.writestr("export_metadata.json", json.dumps(metadata, indent=2))
        
        st.download_button(
            label="📥 Download Complete Package (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=f"brand_health_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )

def display_html_reports(master_df):
    """Display HTML report generation interface"""
    st.markdown("## 🎨 HTML Brand Experience Reports")
    
    # Check if unified data exists
    unified_data_path = 'audit_data/unified_audit_data.csv'
    if not os.path.exists(unified_data_path):
        st.error("❌ Unified audit data not found. Please ensure `audit_data/unified_audit_data.csv` exists.")
        return
    
    # Load available personas
    try:
        unified_df = pd.read_csv(unified_data_path)
        available_personas = sorted(unified_df['persona_id'].unique().tolist())
    except Exception as e:
        st.error(f"❌ Error loading persona data: {e}")
        return
    
    if not available_personas:
        st.warning("⚠️ No personas found in the unified data.")
        return
    
    st.markdown("### 🎯 Report Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Persona Selection")
        
        # Option to generate for all personas or select specific ones
        generation_mode = st.radio(
            "Generation Mode",
            ["Single Persona", "Multiple Personas", "All Personas", "Consolidated Report"],
            key="html_generation_mode"
        )
        
        if generation_mode == "Single Persona":
            selected_persona = st.selectbox(
                "Select Persona",
                available_personas,
                key="single_persona_select"
            )
            personas_to_generate = [selected_persona]
            
        elif generation_mode == "Multiple Personas":
            selected_personas = st.multiselect(
                "Select Personas",
                available_personas,
                default=[available_personas[0]] if available_personas else [],
                key="multiple_personas_select"
            )
            personas_to_generate = selected_personas
            
        elif generation_mode == "All Personas":
            personas_to_generate = available_personas
            st.info(f"📊 Will generate reports for all {len(available_personas)} personas")
            
        else:  # Consolidated Report
            personas_to_generate = ["CONSOLIDATED"]
            st.info(f"📊 Will generate a single consolidated report across all {len(available_personas)} personas")
    
    with col2:
        st.markdown("#### ⚙️ Report Options")
        
        # Report customization options
        include_tier_analysis = st.checkbox("Include Tier Analysis", value=True)
        include_persona_voice = st.checkbox("Include Persona Voice Insights", value=True)
        include_recommendations = st.checkbox("Include Strategic Recommendations", value=True)
        include_visual_brand = st.checkbox("Include Visual Brand Assessment", value=True)
        
        # Output options
        st.markdown("**Output Options:**")
        auto_open = st.checkbox("Auto-open reports in browser", value=False)
        create_zip = st.checkbox("Create ZIP package for multiple reports", value=True)
    
    # Preview section
    if personas_to_generate:
        st.markdown("### 📋 Generation Preview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Reports to Generate", len(personas_to_generate))
        
        with col2:
            # Estimate data size
            total_records = 0
            for persona in personas_to_generate:
                persona_data = unified_df[unified_df['persona_id'] == persona]
                total_records += len(persona_data)
            st.metric("Total Records", total_records)
        
        with col3:
            estimated_time = len(personas_to_generate) * 2  # Rough estimate: 2 seconds per report
            st.metric("Estimated Time", f"{estimated_time}s")
        
        # Show persona details
        if len(personas_to_generate) <= 5:  # Only show details for small lists
            st.markdown("**Personas to Generate:**")
            for persona in personas_to_generate:
                persona_data = unified_df[unified_df['persona_id'] == persona]
                st.markdown(f"- **{persona}**: {len(persona_data)} records, {persona_data['page_id'].nunique()} pages")
    
    # Generation button
    st.markdown("### 🚀 Generate Reports")
    
    if not personas_to_generate:
        st.warning("⚠️ Please select at least one persona to generate reports.")
    else:
        if st.button("🎨 Generate HTML Reports", type="primary"):
            generate_html_reports(personas_to_generate, {
                'include_tier_analysis': include_tier_analysis,
                'include_persona_voice': include_persona_voice,
                'include_recommendations': include_recommendations,
                'include_visual_brand': include_visual_brand,
                'auto_open': auto_open,
                'create_zip': create_zip
            })

def generate_html_reports(personas_to_generate, options):
    """Generate HTML reports for selected personas"""
    
    # Initialize progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize HTML report generator
        generator = HTMLReportGenerator()
        
        generated_reports = []
        
        for i, persona in enumerate(personas_to_generate):
            if persona == "CONSOLIDATED":
                status_text.text(f"Generating consolidated report across all personas...")
                progress_bar.progress((i + 1) / len(personas_to_generate))
                
                try:
                    # Generate consolidated report
                    output_path = generator.generate_consolidated_report()
                    generated_reports.append({
                        'persona': 'Consolidated Report',
                        'path': output_path,
                        'status': 'success'
                    })
                    
                    st.success(f"✅ Generated consolidated report")
                    
                except Exception as e:
                    st.error(f"❌ Error generating consolidated report: {e}")
                    generated_reports.append({
                        'persona': 'Consolidated Report',
                        'path': None,
                        'status': 'error',
                        'error': str(e)
                    })
            else:
                status_text.text(f"Generating report for {persona}...")
                progress_bar.progress((i + 1) / len(personas_to_generate))
                
                try:
                    # Generate individual persona report
                    output_path = generator.generate_report(persona)
                    generated_reports.append({
                        'persona': persona,
                        'path': output_path,
                        'status': 'success'
                    })
                    
                    st.success(f"✅ Generated report for {persona}")
                    
                except Exception as e:
                    st.error(f"❌ Error generating report for {persona}: {e}")
                    generated_reports.append({
                        'persona': persona,
                        'path': None,
                        'status': 'error',
                        'error': str(e)
                    })
        
        # Update final status
        successful_reports = [r for r in generated_reports if r['status'] == 'success']
        failed_reports = [r for r in generated_reports if r['status'] == 'error']
        
        status_text.text(f"Completed: {len(successful_reports)} successful, {len(failed_reports)} failed")
        
        # Display results
        display_generation_results(successful_reports, failed_reports, options)
        
    except Exception as e:
        st.error(f"❌ Critical error during report generation: {e}")
        status_text.text("Generation failed")

def display_generation_results(successful_reports, failed_reports, options):
    """Display the results of HTML report generation"""
    
    st.markdown("### 📊 Generation Results")
    
    if successful_reports:
        st.success(f"✅ Successfully generated {len(successful_reports)} HTML reports")
        
        # Display successful reports
        st.markdown("#### 🎉 Successful Reports")
        
        for report in successful_reports:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{report['persona']}**")
                st.markdown(f"`{report['path']}`")
            
            with col2:
                # Get file size
                try:
                    file_size = os.path.getsize(report['path']) / 1024  # KB
                    st.metric("Size", f"{file_size:.1f} KB")
                except:
                    st.metric("Size", "N/A")
            
            with col3:
                # Open in browser button
                if st.button(f"🌐 Open", key=f"open_{report['persona']}"):
                    file_url = f"file://{os.path.abspath(report['path'])}"
                    st.markdown(f"[Open Report]({file_url})")
                    st.info(f"📋 Copy this URL to your browser: {file_url}")
        
        # Create ZIP package if requested and multiple reports
        if options.get('create_zip', False) and len(successful_reports) > 1:
            st.markdown("#### 📦 Download Package")
            
            if st.button("📦 Create ZIP Package"):
                create_reports_zip_package(successful_reports)
    
    if failed_reports:
        st.error(f"❌ Failed to generate {len(failed_reports)} reports")
        
        # Display failed reports
        with st.expander("❌ Failed Reports Details"):
            for report in failed_reports:
                st.markdown(f"**{report['persona']}**: {report.get('error', 'Unknown error')}")

def create_reports_zip_package(successful_reports):
    """Create a ZIP package containing all generated HTML reports"""
    
    try:
        # Create zip file in memory
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for report in successful_reports:
                if os.path.exists(report['path']):
                    # Add HTML file to zip
                    zip_file.write(report['path'], f"{report['persona'].replace(' ', '_')}_report.html")
            
            # Add metadata
            metadata = {
                "generated_timestamp": datetime.now().isoformat(),
                "total_reports": len(successful_reports),
                "personas": [r['persona'] for r in successful_reports],
                "generator_version": "1.0"
            }
            zip_file.writestr("package_metadata.json", json.dumps(metadata, indent=2))
        
        # Offer download
        st.download_button(
            label="📥 Download HTML Reports Package",
            data=zip_buffer.getvalue(),
            file_name=f"html_reports_package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip"
        )
        
        st.success("✅ ZIP package created successfully!")
        
    except Exception as e:
        st.error(f"❌ Error creating ZIP package: {e}")

if __name__ == "__main__":
    main() 