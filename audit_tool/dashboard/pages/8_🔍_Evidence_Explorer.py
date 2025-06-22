#!/usr/bin/env python3
"""
Evidence Explorer Page
Search through AI rationale and detailed evidence
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    st.title("🔍 Evidence & Rationale Explorer")
    
    # Check if we have data
    if 'datasets' not in st.session_state or st.session_state['datasets'] is None:
        st.error("No audit data found. Please ensure data is loaded from the main dashboard.")
        return
    
    datasets = st.session_state['datasets']
    summary = st.session_state['summary']
    filtered_df = datasets['criteria']
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Search interface
    st.markdown("### 🔍 Search AI Rationale & Evidence")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input(
            "Search through AI explanations:",
            placeholder="Enter keywords to search through AI rationale...",
            help="Search for specific terms in the AI's reasoning and evidence"
        )
    
    with col2:
        min_score_filter = st.slider("Minimum score:", 0.0, 10.0, 0.0, 0.5)
    
    with col3:
        max_results = st.selectbox("Max results:", [10, 25, 50, 100], index=1)
    
    # Advanced filters
    with st.expander("🔧 Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'criterion_id' in filtered_df.columns:
                unique_criteria = filtered_df['criterion_id'].dropna().astype(str).unique()
                selected_criteria = st.multiselect(
                    "Filter by criteria:",
                    options=sorted(unique_criteria),
                    help="Select specific criteria to focus on"
                )
            else:
                selected_criteria = []
        
        with col2:
            if 'url_slug' in filtered_df.columns:
                unique_pages = filtered_df['url_slug'].dropna().astype(str).unique()
                selected_pages = st.multiselect(
                    "Filter by pages:",
                    options=sorted(unique_pages),
                    format_func=lambda x: str(x).replace('_', ' ').title(),
                    help="Select specific pages to analyze"
                )
            else:
                selected_pages = []
        
        with col3:
            score_range = st.select_slider(
                "Score range:",
                options=["All", "Critical (0-4)", "Good (4-7)", "Excellent (7-10)"],
                value="All",
                help="Filter by performance level"
            )
    
    # Apply filters
    display_df = filtered_df.copy()
    
    # Apply search filter
    if search_query and 'evidence' in display_df.columns:
        display_df = display_df[
            display_df['evidence'].str.contains(search_query, case=False, na=False)
        ]
    
    # Apply score filter
    display_df = display_df[display_df['raw_score'] >= min_score_filter]
    
    # Apply criteria filter
    if selected_criteria:
        display_df = display_df[display_df['criterion_id'].isin(selected_criteria)]
    
    # Apply page filter
    if selected_pages:
        display_df = display_df[display_df['url_slug'].isin(selected_pages)]
    
    # Apply score range filter
    if score_range == "Critical (0-4)":
        display_df = display_df[display_df['raw_score'] < 4.0]
    elif score_range == "Good (4-7)":
        display_df = display_df[(display_df['raw_score'] >= 4.0) & (display_df['raw_score'] < 7.0)]
    elif score_range == "Excellent (7-10)":
        display_df = display_df[display_df['raw_score'] >= 7.0]
    
    # Limit results
    display_df = display_df.head(max_results)
    
    # Results summary
    if display_df.empty:
        st.warning("No evidence found matching your search criteria.")
        st.info("💡 Try broadening your search terms or adjusting the filters.")
        return
    
    st.success(f"Found {len(display_df)} evaluations matching your criteria")
    
    # Sort options
    col1, col2 = st.columns([1, 1])
    with col1:
        sort_by = st.selectbox(
            "Sort by:",
            ["Score (Low to High)", "Score (High to Low)", "Page Name", "Criteria Name"],
            index=0
        )
    
    with col2:
        view_mode = st.radio(
            "View mode:",
            ["Detailed Cards", "Compact Table"],
            horizontal=True
        )
    
    # Apply sorting
    if sort_by == "Score (Low to High)":
        display_df = display_df.sort_values('raw_score', ascending=True)
    elif sort_by == "Score (High to Low)":
        display_df = display_df.sort_values('raw_score', ascending=False)
    elif sort_by == "Page Name":
        display_df = display_df.sort_values('url_slug', ascending=True)
    elif sort_by == "Criteria Name":
        display_df = display_df.sort_values('criterion_id', ascending=True)
    
    # Display results
    if view_mode == "Detailed Cards":
        st.markdown("### 📋 Detailed Evidence Cards")
        
        for idx, row in display_df.iterrows():
            # Color code based on score
            if row['raw_score'] >= 8.0:
                card_color = "success"
                score_emoji = "🟢"
            elif row['raw_score'] >= 4.0:
                card_color = "warning"
                score_emoji = "🟡"
            else:
                card_color = "error"
                score_emoji = "🔴"
            
            page_name = str(row.get('url_slug', 'Unknown')).replace('_', ' ').title()
            criterion_name = str(row.get('criterion_id', 'Unknown')).replace('_', ' ').title()
            
            with st.container():
                st.markdown(f"""
                <div style="border-left: 4px solid {'#22c55e' if card_color == 'success' else '#eab308' if card_color == 'warning' else '#ef4444'}; 
                            padding: 1rem; margin: 1rem 0; background-color: #f8f9fa; border-radius: 0.5rem;">
                    <h4>{score_emoji} {page_name} - {criterion_name}</h4>
                    <p><strong>Score:</strong> {row['raw_score']:.1f}/10</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Evidence/Rationale
                if pd.notna(row.get('evidence')):
                    st.markdown("**🤖 AI Evidence:**")
                    evidence = str(row['evidence'])
                    if search_query:
                        # Highlight search terms
                        highlighted = evidence.replace(
                            search_query, 
                            f"**{search_query}**"
                        )
                        st.markdown(highlighted)
                    else:
                        st.markdown(evidence)
                else:
                    st.markdown("*No evidence available*")
                
                # Additional details
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'tier' in row and pd.notna(row['tier']):
                        st.markdown(f"**Tier:** {row['tier']}")
                with col2:
                    if 'persona_id' in row and pd.notna(row['persona_id']):
                        st.markdown(f"**Persona:** {row['persona_id']}")
                with col3:
                    if 'url' in row and pd.notna(row['url']):
                        st.markdown(f"[🔗 View Page]({row['url']})")
                
                st.markdown("---")
    
    else:  # Compact Table
        st.markdown("### 📊 Evidence Summary Table")
        
        # Prepare table data
        table_data = display_df.copy()
        
        # Format columns for display
        if 'url_slug' in table_data.columns:
            table_data['Page'] = table_data['url_slug'].apply(lambda x: str(x).replace('_', ' ').title())
        if 'criterion_id' in table_data.columns:
            table_data['Criterion'] = table_data['criterion_id'].apply(lambda x: str(x).replace('_', ' ').title())
        
        # Add score indicators
        table_data['Status'] = table_data['raw_score'].apply(
            lambda x: '🟢 Excellent' if x >= 8.0 else '🟡 Good' if x >= 4.0 else '🔴 Needs Work'
        )
        
        # Truncate rationale for table view
        if 'evidence' in table_data.columns:
            table_data['Evidence Summary'] = table_data['evidence'].apply(
                lambda x: str(x)[:100] + "..." if pd.notna(x) and len(str(x)) > 100 else str(x)
            )
        
        # Select columns for display
        display_columns = ['Page', 'Criterion', 'raw_score', 'Status']
        if 'Evidence Summary' in table_data.columns:
            display_columns.append('Evidence Summary')
        if 'persona_id' in table_data.columns:
            display_columns.append('persona_id')
        
        # Rename columns
        column_config = {
            'raw_score': 'Score',
            'persona_id': 'Persona'
        }
        
        st.dataframe(
            table_data[display_columns].rename(columns=column_config),
            use_container_width=True,
            hide_index=True
        )
    
    # Export functionality
    st.markdown("### 📥 Export Evidence")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export to CSV"):
            # Prepare export data
            export_data = display_df.copy()
            if 'url_slug' in export_data.columns:
                export_data['Page Name'] = export_data['url_slug'].apply(lambda x: str(x).replace('_', ' ').title())
            if 'criterion_id' in export_data.columns:
                export_data['Criterion Name'] = export_data['criterion_id'].apply(lambda x: str(x).replace('_', ' ').title())
            
            csv_data = export_data.to_csv(index=False).encode('utf-8')
            st.download_button(
                "💾 Download Evidence CSV",
                csv_data,
                "evidence_export.csv",
                "text/csv"
            )
    
    with col2:
        if st.button("📝 Export Rationale Report"):
            # Create detailed rationale report
            report_content = f"# Evidence & Rationale Report\n\n"
            report_content += f"**Search Query:** {search_query or 'All'}\n"
            report_content += f"**Results Found:** {len(display_df)}\n"
            report_content += f"**Generated:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for idx, row in display_df.iterrows():
                page_name = str(row.get('url_slug', 'Unknown')).replace('_', ' ').title()
                criterion_name = str(row.get('criterion_id', 'Unknown')).replace('_', ' ').title()
                
                report_content += f"## {page_name} - {criterion_name}\n"
                report_content += f"**Score:** {row['raw_score']:.1f}/10\n\n"
                
                if pd.notna(row.get('evidence')):
                    report_content += f"**AI Rationale:**\n{row['evidence']}\n\n"
                
                if 'url' in row and pd.notna(row['url']):
                    report_content += f"**URL:** {row['url']}\n\n"
                
                report_content += "---\n\n"
            
            st.download_button(
                "📋 Download Rationale Report",
                report_content,
                "rationale_report.md",
                "text/markdown"
            )

if __name__ == "__main__":
    main() 