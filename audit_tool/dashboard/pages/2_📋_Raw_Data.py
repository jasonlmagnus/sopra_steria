#!/usr/bin/env python3
"""
Raw Data Page
Explore and export the underlying audit data
"""

import streamlit as st
import pandas as pd
import json
import sys
from pathlib import Path
from io import BytesIO

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def convert_df_to_csv(df):
    """Convert DataFrame to CSV for download"""
    return df.to_csv(index=False).encode('utf-8')

def convert_df_to_json(df):
    """Convert DataFrame to JSON for download"""
    return df.to_json(orient='records', indent=2).encode('utf-8')

def main():
    st.title("📋 Raw Data Explorer")
    
    # Check if we have global state
    if 'run_data' not in st.session_state:
        st.error("Please select a run from the home page first.")
        st.info("👈 Use the sidebar to select an audit run")
        return
    
    gateway = st.session_state['gateway']
    run_data = st.session_state['run_data']
    
    # Get filtered data
    filtered_data = gateway.get_filtered_data(
        run_data,
        st.session_state['persona_filter'],
        st.session_state['score_filter'],
        st.session_state['tier_filter']
    )
    
    if filtered_data.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Data overview
    st.markdown("### 📊 Data Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Records", len(filtered_data))
    
    with col2:
        st.metric("Unique Pages", len(filtered_data['page_id'].unique()))
    
    with col3:
        st.metric("Criteria Types", len(filtered_data['criterion_id'].unique()))
    
    with col4:
        st.metric("Performance Tiers", len(filtered_data['tier'].unique()))
    
    # Data filtering and exploration
    st.markdown("### 🔍 Data Explorer")
    
    # Additional filters for data exploration
    col1, col2 = st.columns(2)
    
    with col1:
        # Criterion filter
        available_criteria = sorted(filtered_data['criterion_id'].unique())
        selected_criteria = st.multiselect(
            "Filter by Criteria:",
            available_criteria,
            default=available_criteria[:5] if len(available_criteria) > 5 else available_criteria,
            help="Select specific criteria to focus on"
        )
    
    with col2:
        # Descriptor filter
        available_descriptors = filtered_data['descriptor'].unique()
        selected_descriptors = st.multiselect(
            "Filter by Performance:",
            available_descriptors,
            default=available_descriptors,
            help="Filter by performance level"
        )
    
    # Apply additional filters
    if selected_criteria:
        display_data = filtered_data[filtered_data['criterion_id'].isin(selected_criteria)]
    else:
        display_data = filtered_data
    
    if selected_descriptors:
        display_data = display_data[display_data['descriptor'].isin(selected_descriptors)]
    
    # Data table with sorting and filtering
    st.markdown("### 📋 Data Table")
    
    # Column selection
    available_columns = list(display_data.columns)
    default_columns = ['url_slug', 'tier', 'criterion_id', 'raw_score', 'descriptor']
    
    selected_columns = st.multiselect(
        "Select columns to display:",
        available_columns,
        default=[col for col in default_columns if col in available_columns],
        help="Choose which columns to show in the table"
    )
    
    if selected_columns:
        table_data = display_data[selected_columns].copy()
        
        # Format the data for better display
        if 'raw_score' in table_data.columns:
            table_data['raw_score'] = table_data['raw_score'].round(2)
        
        if 'url_slug' in table_data.columns:
            # Make URL slugs more readable
            table_data['url_slug'] = table_data['url_slug'].str.replace('_', ' ').str.title()
        
        if 'criterion_id' in table_data.columns:
            # Make criterion IDs more readable
            table_data['criterion_id'] = table_data['criterion_id'].str.replace('_', ' ').str.title()
        
        # Display the table
        st.dataframe(
            table_data,
            use_container_width=True,
            height=400
        )
        
        # Table statistics
        st.markdown("#### 📈 Table Statistics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Rows displayed:** {len(table_data)}")
            st.write(f"**Total rows:** {len(filtered_data)}")
        
        with col2:
            if 'raw_score' in table_data.columns:
                st.write(f"**Average score:** {table_data['raw_score'].mean():.2f}")
                st.write(f"**Score range:** {table_data['raw_score'].min():.1f} - {table_data['raw_score'].max():.1f}")
        
        with col3:
            if 'descriptor' in table_data.columns:
                pass_rate = (table_data['descriptor'] == 'PASS').mean() * 100
                st.write(f"**Pass rate:** {pass_rate:.1f}%")
                st.write(f"**Most common:** {table_data['descriptor'].mode().iloc[0] if not table_data['descriptor'].mode().empty else 'N/A'}")
    
    # Export section
    st.markdown("### 📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Export
        csv_data = convert_df_to_csv(display_data)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"audit_data_{st.session_state['selected_run']}.csv",
            mime="text/csv",
            help="Download filtered data as CSV file"
        )
    
    with col2:
        # JSON Export
        json_data = convert_df_to_json(display_data)
        st.download_button(
            label="📋 Download as JSON",
            data=json_data,
            file_name=f"audit_data_{st.session_state['selected_run']}.json",
            mime="application/json",
            help="Download filtered data as JSON file"
        )
    
    with col3:
        # Parquet Export (if needed)
        if st.button("💾 Export to Parquet", help="Save filtered data as Parquet file"):
            output_path = f"audit_data_export_{st.session_state['selected_run']}.parquet"
            display_data.to_parquet(output_path)
            st.success(f"Data exported to {output_path}")
    
    # Data quality checks
    st.markdown("### 🔍 Data Quality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Missing Data Analysis")
        missing_data = display_data.isnull().sum()
        missing_pct = (missing_data / len(display_data) * 100).round(2)
        
        missing_df = pd.DataFrame({
            'Column': missing_data.index,
            'Missing Count': missing_data.values,
            'Missing %': missing_pct.values
        })
        
        missing_df = missing_df[missing_df['Missing Count'] > 0]
        
        if not missing_df.empty:
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.success("✅ No missing data found!")
    
    with col2:
        st.markdown("#### 📈 Score Distribution")
        if 'raw_score' in display_data.columns:
            score_stats = display_data['raw_score'].describe()
            
            st.write(f"**Count:** {score_stats['count']:.0f}")
            st.write(f"**Mean:** {score_stats['mean']:.2f}")
            st.write(f"**Std:** {score_stats['std']:.2f}")
            st.write(f"**Min:** {score_stats['min']:.2f}")
            st.write(f"**25%:** {score_stats['25%']:.2f}")
            st.write(f"**50%:** {score_stats['50%']:.2f}")
            st.write(f"**75%:** {score_stats['75%']:.2f}")
            st.write(f"**Max:** {score_stats['max']:.2f}")
        else:
            st.info("Score column not available in current selection")
    
    # Advanced analysis
    st.markdown("### 🔬 Advanced Analysis")
    
    with st.expander("📊 Correlation Analysis", expanded=False):
        numeric_columns = display_data.select_dtypes(include=['float64', 'int64']).columns
        
        if len(numeric_columns) > 1:
            corr_matrix = display_data[numeric_columns].corr()
            st.dataframe(corr_matrix.round(3), use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation analysis")
    
    with st.expander("🏷️ Categorical Analysis", expanded=False):
        categorical_columns = display_data.select_dtypes(include=['object']).columns
        
        for col in categorical_columns:
            if col in display_data.columns:
                st.markdown(f"**{col.replace('_', ' ').title()}:**")
                value_counts = display_data[col].value_counts()
                st.write(value_counts.to_dict())
                st.markdown("---")
    
    # Raw manifest data
    st.markdown("### 📋 Run Manifest")
    
    with st.expander("View Run Metadata", expanded=False):
        manifest = run_data['manifest']
        st.json(manifest)
    
    # Data schema information
    st.markdown("### 📝 Data Schema")
    
    with st.expander("View Data Types and Schema", expanded=False):
        schema_info = pd.DataFrame({
            'Column': display_data.columns,
            'Data Type': display_data.dtypes.astype(str),
            'Non-Null Count': display_data.count(),
            'Null Count': display_data.isnull().sum(),
            'Unique Values': display_data.nunique()
        })
        
        st.dataframe(schema_info, use_container_width=True)

if __name__ == "__main__":
    main() 