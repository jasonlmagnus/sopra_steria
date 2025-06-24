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

from components.data_loader import BrandHealthDataLoader
from components.metrics_calculator import BrandHealthMetricsCalculator

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
    tab1, tab2, tab3 = st.tabs(["📊 Data Explorer", "📈 Custom Reports", "📦 Export Center"])
    
    with tab1:
        display_data_explorer(master_df, datasets)
    
    with tab2:
        display_custom_reports(master_df, datasets)
    
    with tab3:
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
            st.dataframe(dataset_df, use_container_width=True)

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
    st.plotly_chart(fig, use_container_width=True)

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
        
        st.dataframe(styled_df, use_container_width=True)
        
        if len(filtered_df) > max_rows:
            st.info(f"💡 Showing first {max_rows:,} rows of {len(filtered_df):,} total records")
    
    else:  # Summary Statistics
        st.markdown("#### 📈 Summary Statistics")
        
        # Numeric columns summary
        numeric_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) > 0:
            summary_stats = filtered_df[numeric_cols].describe().round(2)
            st.dataframe(summary_stats, use_container_width=True)
        
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
                                st.plotly_chart(fig, use_container_width=True)

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
            st.dataframe(missing_df, use_container_width=True)
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
                st.plotly_chart(fig, use_container_width=True)

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
    """Generate executive summary report"""
    st.markdown("#### 🎯 Executive Summary Report")
    
    # Generate executive summary
    executive_summary = metrics_calc.generate_executive_summary()
    
    if executive_summary:
        # Brand health overview
        brand_health = executive_summary.get('brand_health', {})
        st.markdown(f"""
        **Brand Health Score:** {brand_health.get('raw_score', 'N/A')}/10 ({brand_health.get('status', 'Unknown')})
        
        **Key Metrics:**
        - Critical Issues: {executive_summary.get('key_metrics', {}).get('critical_issues', 0)}
        - Quick Wins: {executive_summary.get('key_metrics', {}).get('quick_wins', 0)}
        - Success Pages: {executive_summary.get('key_metrics', {}).get('success_pages', 0)}
        """)
        
        # Strategic recommendations
        if executive_summary.get('recommendations'):
            st.markdown("**Strategic Recommendations:**")
            for i, rec in enumerate(executive_summary['recommendations'], 1):
                st.markdown(f"{i}. {rec}")

def generate_persona_performance_report(master_df, metrics_calc):
    """Generate persona performance report"""
    st.markdown("#### 👥 Persona Performance Report")
    
    if 'persona_id' in master_df.columns and 'avg_score' in master_df.columns:
        persona_performance = master_df.groupby('persona_id')['avg_score'].agg(['mean', 'count']).round(2)
        persona_performance.columns = ['Average Score', 'Page Count']
        persona_performance = persona_performance.sort_values('Average Score', ascending=False)
        
        st.dataframe(persona_performance, use_container_width=True)
        
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
        
        st.dataframe(tier_performance, use_container_width=True)

def generate_success_stories_report(master_df, metrics_calc):
    """Generate success stories report"""
    st.markdown("#### 🌟 Success Stories Report")
    
    success_stories = metrics_calc.calculate_success_stories()
    
    if success_stories:
        st.markdown(f"**Found {len(success_stories)} success stories (score ≥ 7.7)**")
        
        for i, story in enumerate(success_stories[:5], 1):
            st.markdown(f"""
            **#{i} - {story.get('page_title', 'Unknown Page')}**
            - Score: {story['raw_score']:.1f}/10
            - Tier: {story.get('tier', 'Unknown')}
            """)

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

if __name__ == "__main__":
    main() 