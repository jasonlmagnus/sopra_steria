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
    st.title("👥 Persona Comparison")
    
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
    
    # Check if we have multiple personas
    if summary['total_personas'] < 2:
        st.info("📊 Only one persona found. Upload additional personas to enable comparison analysis.")
        return
    
    st.markdown(f"### 📊 Comparing {summary['total_personas']} Personas")
    
    # Persona Performance Overview
    persona_summary = filtered_df.groupby('persona_id').agg({
        'raw_score': ['mean', 'std', 'count', 'min', 'max'],
        'page_id': 'nunique',
        'criterion_id': 'nunique'
    }).round(2)
    persona_summary.columns = ['Avg Score', 'Std Dev', 'Evaluations', 'Min Score', 'Max Score', 'Pages', 'Criteria']
    persona_summary = persona_summary.sort_values('Avg Score', ascending=False)
    
    # Performance comparison chart
    st.markdown("#### 📈 Performance Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart of average scores
        fig_bar = px.bar(
            x=persona_summary.index,
            y=persona_summary['Avg Score'],
            title="Average Score by Persona",
            labels={'x': 'Persona', 'y': 'Average Score'},
            color=persona_summary['Avg Score'],
            color_continuous_scale='RdYlGn',
            text=persona_summary['Avg Score']
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_bar.update_layout(showlegend=False, yaxis=dict(range=[0, 10]))
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Score distribution comparison
        fig_box = px.box(
            filtered_df,
            x='persona_id',
            y='raw_score',
            title="Score Distribution by Persona"
        )
        fig_box.update_layout(xaxis_title="Persona", yaxis_title="Score")
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Detailed comparison table
    st.markdown("#### 📋 Detailed Performance Metrics")
    
    # Add performance indicators
    persona_summary['Status'] = persona_summary['Avg Score'].apply(
        lambda x: '🟢 Excellent' if x >= 8.0 else '🟡 Good' if x >= 4.0 else '🔴 Needs Work'
    )
    
    st.dataframe(persona_summary, use_container_width=True)
    
    # Criteria-level comparison
    st.markdown("#### 🎯 Criteria Performance Comparison")
    
    # Create criteria heatmap
    criteria_comparison = filtered_df.pivot_table(
        index='criterion_id',
        columns='persona_id',
        values='raw_score',
        aggfunc='mean'
    ).round(2)
    
    if not criteria_comparison.empty:
        # Display as heatmap
        fig_heatmap = px.imshow(
            criteria_comparison.values,
            labels=dict(x="Persona", y="Criteria", color="Score"),
            x=criteria_comparison.columns,
            y=[c.replace('_', ' ').title() for c in criteria_comparison.index],
            color_continuous_scale='RdYlGn',
            aspect="auto",
            title="Criteria Performance Heatmap"
        )
        fig_heatmap.update_layout(height=max(400, len(criteria_comparison) * 25))
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Show top differences
        st.markdown("#### 🔍 Biggest Performance Differences")
        
        if len(criteria_comparison.columns) >= 2:
            # Calculate variance across personas for each criterion
            criteria_variance = criteria_comparison.var(axis=1).sort_values(ascending=False)
            top_differences = criteria_variance.head(5)
            
            for criterion, variance in top_differences.items():
                with st.expander(f"📊 {criterion.replace('_', ' ').title()} (Variance: {variance:.2f})"):
                    criterion_data = criteria_comparison.loc[criterion]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        best_persona = criterion_data.idxmax()
                        worst_persona = criterion_data.idxmin()
                        st.metric("Best Performer", f"{best_persona}: {criterion_data[best_persona]:.1f}")
                        st.metric("Worst Performer", f"{worst_persona}: {criterion_data[worst_persona]:.1f}")
                    
                    with col2:
                        # Show specific examples for this criterion
                        criterion_examples = filtered_df[filtered_df['criterion_id'] == criterion]
                        if not criterion_examples.empty:
                            best_example = criterion_examples.loc[criterion_examples['raw_score'].idxmax()]
                            worst_example = criterion_examples.loc[criterion_examples['raw_score'].idxmin()]
                            
                            st.markdown("**Best Example:**")
                            st.write(f"• Page: {best_example['url_slug'].replace('_', ' ').title()}")
                            st.write(f"• Score: {best_example['raw_score']:.1f}/10")
                            
                            st.markdown("**Worst Example:**")
                            st.write(f"• Page: {worst_example['url_slug'].replace('_', ' ').title()}")
                            st.write(f"• Score: {worst_example['raw_score']:.1f}/10")
    
    # Experience comparison (if available)
    if summary.get('has_experience_data') and datasets['experience'] is not None:
        st.markdown("#### 👤 Experience Data Comparison")
        
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
        
        st.dataframe(exp_comparison, use_container_width=True)
    
    # Export comparison data
    st.markdown("#### 📥 Export Comparison Data")
    
    if st.button("📊 Generate Comparison Report"):
        # Create comprehensive comparison report
        report_content = f"# Persona Comparison Report\n\n"
        report_content += f"**Personas Analyzed:** {summary['total_personas']}\n"
        report_content += f"**Total Pages:** {summary['total_pages']}\n"
        report_content += f"**Total Evaluations:** {summary['total_evaluations']}\n\n"
        
        report_content += "## Performance Summary\n\n"
        for persona, data in persona_summary.iterrows():
            report_content += f"### {persona}\n"
            report_content += f"- **Average Score:** {data['Avg Score']:.1f}/10\n"
            report_content += f"- **Pages Analyzed:** {int(data['Pages'])}\n"
            report_content += f"- **Score Range:** {data['Min Score']:.1f} - {data['Max Score']:.1f}\n"
            report_content += f"- **Status:** {data['Status']}\n\n"
        
        if summary.get('has_experience_data'):
            report_content += "## Experience Data Summary\n\n"
            for persona, data in exp_comparison.iterrows():
                report_content += f"### {persona}\n"
                report_content += f"- **Positive Sentiment:** {data['Positive Sentiment %']:.1f}%\n"
                report_content += f"- **High Engagement:** {data['High Engagement %']:.1f}%\n"
                report_content += f"- **High Conversion:** {data['High Conversion %']:.1f}%\n\n"
        
        st.download_button(
            "📥 Download Comparison Report",
            report_content,
            "persona_comparison_report.md",
            "text/markdown"
        )

if __name__ == "__main__":
    main() 