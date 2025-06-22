#!/usr/bin/env python3
"""
AI Strategic Insights Page
AI-powered analysis and strategic recommendations
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add audit_tool to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

def main():
    st.title("💡 AI Strategic Insights")
    
    # Check if we have data
    if 'datasets' not in st.session_state or st.session_state['datasets'] is None:
        st.error("No audit data found. Please ensure data is loaded from the main dashboard.")
        return
    
    datasets = st.session_state.get('datasets', {})
    summary = st.session_state['summary']
    master_df = st.session_state['master_df']
    filtered_df = master_df  # Use master_df directly since it contains all the data
    
    if filtered_df.empty:
        st.warning("No data matches the current filters.")
        return
    
    # AI-Generated Strategic Summary
    st.markdown("### 🧠 AI Analysis Summary")
    
    # Calculate key metrics for AI analysis
    avg_score = filtered_df['avg_score'].mean()
    total_pages = filtered_df['page_id'].nunique()
    critical_issues = len(filtered_df[filtered_df['avg_score'] < 4.0])
    excellent_examples = len(filtered_df[filtered_df['avg_score'] >= 8.0])
    
    # Generate AI insights based on data patterns
    if avg_score >= 7.5:
        insight_level = "🟢 **Strong Brand Performance**"
        strategic_focus = "optimization and differentiation"
    elif avg_score >= 5.5:
        insight_level = "🟡 **Solid Foundation with Growth Opportunities**"
        strategic_focus = "targeted improvements and consistency"
    else:
        insight_level = "🔴 **Critical Brand Health Issues**"
        strategic_focus = "immediate remediation and strategic overhaul"
    
    st.markdown(f"""
    **Overall Assessment:** {insight_level}
    
    **Strategic Recommendation:** Based on analysis of {total_pages} pages across multiple personas, 
    your brand audit reveals an average performance score of {avg_score:.1f}/10. The data suggests 
    focusing on {strategic_focus} to maximize brand impact.
    
    **Key Findings:**
    - {excellent_examples} pages demonstrate excellence and should be used as templates
    - {critical_issues} areas require immediate attention to prevent brand damage
    - Persona experience data shows {'strong' if summary.get('has_experience_data') else 'limited'} engagement patterns
    """)
    
    # Top Strategic Priorities
    st.markdown("### 🎯 Top Strategic Priorities")
    
    # Find worst performing criteria with highest impact
    # Use the correct column name based on our data structure
    criterion_col = 'criterion_code' if 'criterion_code' in filtered_df.columns else 'criterion_id'
    
    if criterion_col not in filtered_df.columns:
        st.error("❌ Criteria analysis requires proper column structure")
        return
    
    # Use the correct score column name
    score_col = 'avg_score'  # Use avg_score from unified data
    
    criteria_analysis = filtered_df.groupby(criterion_col).agg({
        score_col: ['mean', 'count'],
        'page_id': 'nunique'
    }).round(2)
    criteria_analysis.columns = ['avg_score', 'evaluations', 'pages_affected']
    criteria_analysis['impact_score'] = (10 - criteria_analysis['avg_score']) * criteria_analysis['pages_affected']
    criteria_analysis['priority'] = criteria_analysis['impact_score'].rank(ascending=False, method='dense')
    
    top_priorities = criteria_analysis.sort_values('impact_score', ascending=False).head(5)
    
    for i, (criterion, data) in enumerate(top_priorities.iterrows(), 1):
        priority_color = "🔴" if i <= 2 else "🟡" if i <= 4 else "🟢"
        
        with st.expander(f"{priority_color} Priority #{i}: {criterion.replace('_', ' ').title()}", expanded=i<=2):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Current Score", f"{data['avg_score']:.1f}/10")
                st.metric("Pages Affected", int(data['pages_affected']))
            
            with col2:
                st.metric("Impact Score", f"{data['impact_score']:.1f}")
                improvement_potential = (8.0 - data['avg_score']) * data['pages_affected']
                st.metric("Improvement Potential", f"{improvement_potential:.1f}")
            
            with col3:
                # Get specific examples for this criterion
                criterion_examples = filtered_df[filtered_df[criterion_col] == criterion].sort_values(score_col)
                
                if not criterion_examples.empty:
                    worst_example = criterion_examples.iloc[0]
                    st.markdown("**Worst Performing Page:**")
                    st.write(f"• {worst_example['url_slug'].replace('_', ' ').title()}")
                    st.write(f"• Score: {worst_example['avg_score']:.1f}/10")
                    
                    if len(criterion_examples) > 1:
                        best_example = criterion_examples.iloc[-1]
                        st.markdown("**Best Example:**")
                        st.write(f"• {best_example['url_slug'].replace('_', ' ').title()}")
                        st.write(f"• Score: {best_example['avg_score']:.1f}/10")
            
            # AI-generated specific recommendations
            st.markdown("**🤖 AI Recommendation:**")
            if data['avg_score'] < 4.0:
                st.error(f"**CRITICAL:** This criterion is failing across {int(data['pages_affected'])} pages. Immediate action required to prevent brand damage.")
            elif data['avg_score'] < 6.0:
                st.warning(f"**IMPROVE:** Focus on optimizing this criterion across {int(data['pages_affected'])} pages for significant brand impact.")
            else:
                st.info(f"**OPTIMIZE:** Fine-tune this criterion across {int(data['pages_affected'])} pages to achieve excellence.")
    
    # Experience-Based Insights (if available)
    if summary.get('has_experience_data') and 'overall_sentiment' in filtered_df.columns:
        st.markdown("### 👥 Persona Experience Insights")
        
        experience_df = filtered_df  # Use master_df since it contains experience data
        
        # Sentiment analysis
        sentiment_breakdown = experience_df['overall_sentiment'].value_counts()
        engagement_breakdown = experience_df['engagement_level'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Sentiment Analysis:**")
            for sentiment, count in sentiment_breakdown.items():
                pct = (count / len(experience_df)) * 100
                color = "🟢" if sentiment == "Positive" else "🔴" if sentiment == "Negative" else "🟡"
                st.write(f"{color} {sentiment}: {count} pages ({pct:.1f}%)")
        
        with col2:
            st.markdown("**Engagement Analysis:**")
            for engagement, count in engagement_breakdown.items():
                pct = (count / len(experience_df)) * 100
                color = "🟢" if engagement == "High" else "🔴" if engagement == "Low" else "🟡"
                st.write(f"{color} {engagement}: {count} pages ({pct:.1f}%)")
        
        # AI insights on experience data
        positive_pct = (sentiment_breakdown.get('Positive', 0) / len(experience_df)) * 100
        high_engagement_pct = (engagement_breakdown.get('High', 0) / len(experience_df)) * 100
        
        st.markdown("**🤖 Experience Analysis:**")
        if positive_pct >= 70 and high_engagement_pct >= 60:
            st.success("**EXCELLENT:** Strong positive sentiment and high engagement indicate effective brand communication.")
        elif positive_pct >= 50 and high_engagement_pct >= 40:
            st.warning("**GOOD:** Decent engagement but room for improvement in emotional connection and user experience.")
        else:
            st.error("**CRITICAL:** Low sentiment and engagement suggest fundamental issues with brand messaging and user experience.")
    
    # Quick Wins Analysis
    st.markdown("### ⚡ Quick Wins Identified")
    
    # Find pages with mixed performance (some high, some low scores)
    page_variance = filtered_df.groupby('url_slug').agg({
        'avg_score': ['mean', 'std', 'min', 'max', 'count']
    }).round(2)
    page_variance.columns = ['avg_score', 'std_score', 'min_score', 'max_score', 'criteria_count']
    
    # Quick wins are pages with high variance (some criteria doing well, others poorly)
    quick_wins = page_variance[
        (page_variance['std_score'] > 2.0) & 
        (page_variance['max_score'] >= 7.0) & 
        (page_variance['min_score'] <= 4.0)
    ].sort_values('std_score', ascending=False).head(3)
    
    if not quick_wins.empty:
        for page, data in quick_wins.iterrows():
            with st.expander(f"⚡ Quick Win: {page.replace('_', ' ').title()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Average Score", f"{data['avg_score']:.1f}/10")
                    st.metric("Score Range", f"{data['min_score']:.1f} - {data['max_score']:.1f}")
                
                with col2:
                    st.metric("Variance", f"{data['std_score']:.1f}")
                    st.metric("Criteria Count", int(data['criteria_count']))
                
                # Show specific failing criteria for this page
                page_criteria = filtered_df[filtered_df['url_slug'] == page].sort_values('avg_score')
                failing_criteria = page_criteria[page_criteria['avg_score'] <= 4.0]
                
                if not failing_criteria.empty:
                    st.markdown("**🎯 Focus Areas:**")
                    for _, criterion in failing_criteria.iterrows():
                        st.write(f"• **{criterion[criterion_col].replace('_', ' ').title()}**: {criterion['avg_score']:.1f}/10")
                        if pd.notna(criterion['evidence']):
                            st.write(f"  *{criterion['evidence'][:100]}...*")
    else:
        st.info("No obvious quick wins identified. Focus on systematic improvements across priority criteria.")
    
    # Export Strategic Insights
    st.markdown("### 📄 Export Strategic Report")
    
    if st.button("Generate Strategic Insights Report"):
        # Create comprehensive strategic report
        report_content = f"""# Strategic Brand Audit Insights Report

## Executive Summary
- **Overall Score**: {avg_score:.1f}/10
- **Pages Analyzed**: {total_pages}
- **Critical Issues**: {critical_issues}
- **Excellence Examples**: {excellent_examples}

## Top Strategic Priorities
"""
        
        for i, (criterion, data) in enumerate(top_priorities.iterrows(), 1):
            report_content += f"""
### Priority #{i}: {criterion.replace('_', ' ').title()}
- **Current Score**: {data['avg_score']:.1f}/10
- **Pages Affected**: {int(data['pages_affected'])}
- **Impact Score**: {data['impact_score']:.1f}
"""
        
        st.download_button(
            "📥 Download Strategic Report",
            report_content,
            "strategic_insights_report.md",
            "text/markdown"
        )

if __name__ == "__main__":
    main() 