#!/usr/bin/env python3
"""
Persona Comparison Page
Compare performance across different personas
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    """Main persona comparison page"""
    st.set_page_config(page_title="Persona Comparison", page_icon="👥", layout="wide")
    
    # Get data from session state
    if 'master_df' not in st.session_state:
        st.error("❌ No data available. Please go to the main dashboard first to load data.")
        return
    
    master_df = st.session_state['master_df']
    datasets = st.session_state.get('datasets', {})
    summary = st.session_state.get('summary', {})
    
    st.title("👥 Persona Comparison Analysis")
    st.markdown("### Compare performance across different personas")
    
    # Check if we have persona data
    if 'persona_id' not in master_df.columns:
        st.warning("⚠️ No persona data available for comparison")
        st.info("Persona comparison requires data with persona_id column")
        return
    
    # Check number of personas
    unique_personas = master_df['persona_id'].nunique()
    if unique_personas < 2:
        st.warning("⚠️ Need at least 2 personas for comparison analysis")
        st.info(f"Currently have {unique_personas} persona(s) in the dataset")
        return
    
    # Check if we have data
    if 'datasets' not in st.session_state or st.session_state['datasets'] is None:
        st.error("No audit data found. Please ensure data is loaded from the main dashboard.")
        return
    
    filtered_df = datasets['criteria']
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    # Persona Performance Overview
    persona_summary = filtered_df.groupby('persona_id').agg({
        'avg_score': ['mean', 'std', 'count', 'min', 'max'],
        'page_id': 'nunique',
        'criterion_id': 'nunique'
    }).round(2)
    
    # Flatten column names
    persona_summary.columns = ['Avg Score', 'Std Dev', 'Evaluations', 'Min Score', 'Max Score', 'Pages', 'Criteria']
    
    # Add status column
    persona_summary['Status'] = persona_summary['Avg Score'].apply(
        lambda x: '🟢 Excellent' if x >= 8.0 else '🟡 Good' if x >= 6.0 else '🔴 Needs Work'
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Persona Performance Summary")
        st.dataframe(persona_summary, use_container_width=True)
    
    with col2:
        st.subheader("📈 Performance Comparison")
        
        # Create performance comparison chart
        fig = px.bar(
            x=persona_summary.index,
            y=persona_summary['Avg Score'],
            color=persona_summary['Avg Score'],
            color_continuous_scale='RdYlGn',
            title="Average Score by Persona"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed criteria comparison
    st.subheader("🎯 Criteria Performance Comparison")
    
    # Create criteria comparison matrix
    criteria_comparison = filtered_df.pivot_table(
        values='avg_score',
        index='criterion_id',
        columns='persona_id',
        aggfunc='mean'
    ).round(2)
    
    if not criteria_comparison.empty:
        # Display as heatmap
        fig_heatmap = px.imshow(
            criteria_comparison.values,
            x=criteria_comparison.columns,
            y=[c.replace('_', ' ').title() for c in criteria_comparison.index],
            color_continuous_scale='RdYlGn',
            aspect='auto',
            title="Criteria Performance Heatmap"
        )
        fig_heatmap.update_layout(height=max(400, len(criteria_comparison) * 25))
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Show detailed table
        st.dataframe(criteria_comparison, use_container_width=True)
        
        # Performance insights
        if len(criteria_comparison.columns) >= 2:
            st.subheader("🔍 Key Insights")
            
            # Find best and worst performing criteria for each persona
            for persona in criteria_comparison.columns:
                persona_data = criteria_comparison[persona].dropna()
                if not persona_data.empty:
                    best_criterion = persona_data.idxmax()
                    worst_criterion = persona_data.idxmin()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**{persona} - Best Performance:**")
                        st.success(f"• {best_criterion.replace('_', ' ').title()}: {persona_data[best_criterion]:.1f}/10")
                    
                    with col2:
                        st.markdown(f"**{persona} - Needs Improvement:**")
                        st.warning(f"• {worst_criterion.replace('_', ' ').title()}: {persona_data[worst_criterion]:.1f}/10")
        
        # Criterion deep dive
        st.subheader("🔬 Criterion Deep Dive")
        
        unique_criteria = criteria_comparison.index.tolist()
        selected_criterion = st.selectbox(
            "Select criterion for detailed analysis:",
            unique_criteria,
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        if selected_criterion:
            criterion_examples = filtered_df[filtered_df['criterion_id'] == selected_criterion]
            
            if not criterion_examples.empty:
                st.markdown(f"#### Analysis for: {selected_criterion.replace('_', ' ').title()}")
                
                # Show best and worst examples
                best_example = criterion_examples.loc[criterion_examples['avg_score'].idxmax()]
                worst_example = criterion_examples.loc[criterion_examples['avg_score'].idxmin()]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**🏆 Best Example:**")
                    st.write(f"• **Page:** {best_example['url_slug'].replace('_', ' ').title()}")
                    st.write(f"• **Persona:** {best_example['persona_id']}")
                    st.write(f"• Score: {best_example['avg_score']:.1f}/10")
                    st.write(f"• **Rationale:** {best_example['rationale'][:200]}...")
                
                with col2:
                    st.markdown("**⚠️ Needs Improvement:**")
                    st.write(f"• **Page:** {worst_example['url_slug'].replace('_', ' ').title()}")
                    st.write(f"• **Persona:** {worst_example['persona_id']}")
                    st.write(f"• Score: {worst_example['avg_score']:.1f}/10")
                    st.write(f"• **Rationale:** {worst_example['rationale'][:200]}...")
    
    # Experience comparison (if available)
    if summary.get('has_experience_data') and datasets['experience'] is not None:
        st.subheader("👥 Experience Comparison")
        
        experience_df = datasets['experience']
        
        # Experience metrics by persona
        exp_comparison = experience_df.groupby('persona_id').agg({
            'overall_sentiment': lambda x: (x == 'Positive').sum() / len(x) * 100,
            'engagement_level': lambda x: (x == 'High').sum() / len(x) * 100,
            'conversion_likelihood': lambda x: (x == 'High').sum() / len(x) * 100
        }).round(1)
        exp_comparison.columns = ['Positive Sentiment %', 'High Engagement %', 'High Conversion %']
        
        # Display experience comparison
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_sent = px.bar(
                x=exp_comparison.index,
                y=exp_comparison['Positive Sentiment %'],
                title="Positive Sentiment by Persona",
                color=exp_comparison['Positive Sentiment %'],
                color_continuous_scale='RdYlGn'
            )
            fig_sent.update_layout(showlegend=False)
            st.plotly_chart(fig_sent, use_container_width=True)
        
        with col2:
            fig_eng = px.bar(
                x=exp_comparison.index,
                y=exp_comparison['High Engagement %'],
                title="High Engagement by Persona",
                color=exp_comparison['High Engagement %'],
                color_continuous_scale='RdYlGn'
            )
            fig_eng.update_layout(showlegend=False)
            st.plotly_chart(fig_eng, use_container_width=True)
        
        with col3:
            fig_conv = px.bar(
                x=exp_comparison.index,
                y=exp_comparison['High Conversion %'],
                title="High Conversion by Persona",
                color=exp_comparison['High Conversion %'],
                color_continuous_scale='RdYlGn'
            )
            fig_conv.update_layout(showlegend=False)
            st.plotly_chart(fig_conv, use_container_width=True)
        
        # Experience summary table
        st.dataframe(exp_comparison, use_container_width=True)
    
    # Export options
    st.subheader("📥 Export Comparison Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        persona_csv = persona_summary.to_csv().encode('utf-8')
        st.download_button(
            "📊 Download Persona Summary",
            persona_csv,
            "persona_comparison.csv",
            "text/csv"
        )
    
    with col2:
        if not criteria_comparison.empty:
            criteria_csv = criteria_comparison.to_csv().encode('utf-8')
            st.download_button(
                "🎯 Download Criteria Matrix",
                criteria_csv,
                "criteria_comparison.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main() 