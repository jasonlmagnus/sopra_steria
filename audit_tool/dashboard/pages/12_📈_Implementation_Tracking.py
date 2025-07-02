import streamlit as st
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from audit_tool.dashboard.components.perfect_styling_method import (
    apply_perfect_styling,
    create_main_header,
    create_section_header,
    create_metric_card,
    create_four_column_layout,
    create_divider
)

import pandas as pd
import plotly.express as px
import numpy as np

# Set page config
st.set_page_config(
    page_title="Brand Health Command Center - Implementation Tracking",
    page_icon="📈",
    layout="wide"
)

# Apply styling
apply_perfect_styling()

def main():
    # Create standardized page header
    create_main_header("📈 Implementation Tracking", "Monitor progress on strategic recommendations")
    
    # Sample implementation data for demonstration
    sample_data = {
        "Homepage Messaging": {"status": "completed", "progress": 100, "team": "Marketing"},
        "Navigation UX": {"status": "in_progress", "progress": 65, "team": "UX Team"},
        "Visual Brand Elements": {"status": "in_progress", "progress": 30, "team": "Design"},
        "Social Media Consistency": {"status": "not_started", "progress": 0, "team": "Social"},
        "Page Performance": {"status": "completed", "progress": 100, "team": "Tech"}
    }
    
    # Calculate metrics
    total_items = len(sample_data)
    completed = sum(1 for item in sample_data.values() if item["status"] == "completed")
    in_progress = sum(1 for item in sample_data.values() if item["status"] == "in_progress")
    avg_progress = np.mean([item["progress"] for item in sample_data.values()])
    
    # Display metrics
    create_section_header("Implementation Overview")
    
    col1, col2, col3, col4 = create_four_column_layout()
    
    with col1:
        create_metric_card(f"{total_items}", "📋 Total Items", status="info")
    
    with col2:
        completion_rate = (completed / total_items) * 100
        create_metric_card(f"{completion_rate:.1f}%", "✅ Completion Rate", 
                          status="success" if completion_rate >= 50 else "warning")
    
    with col3:
        create_metric_card(f"{avg_progress:.1f}%", "📈 Avg Progress", 
                          status="success" if avg_progress >= 70 else "warning")
    
    with col4:
        create_metric_card(f"{in_progress}", "🔄 In Progress", status="warning")
    
    create_divider()
    
    # Progress tracking table
    create_section_header("Detailed Progress")
    
    st.info("💡 This is a demonstration interface showing how implementation progress would be tracked.")
    
    # Convert to dataframe for display
    df_data = []
    for name, data in sample_data.items():
        df_data.append({
            "Initiative": name,
            "Status": data["status"].title(),
            "Progress": f"{data['progress']}%",
            "Team": data["team"]
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)
    
    # Progress visualization
    create_section_header("Progress Visualization")
    
    # Create progress chart
    names = list(sample_data.keys())
    progress_values = [item["progress"] for item in sample_data.values()]
    
    fig = px.bar(
        x=names,
        y=progress_values,
        title="Implementation Progress by Initiative",
        color=progress_values,
        color_continuous_scale="RdYlGn"
    )
    
    fig.update_layout(
        font=dict(family="Inter", size=12),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    create_divider()
    
    # Action items
    create_section_header("Next Actions")
    
    st.warning("⚠️ **Behind Schedule:** Visual Brand Elements (30% complete)")
    st.info("📅 **Starting Soon:** Social Media Consistency initiative")
    st.success("🎉 **Recently Completed:** Homepage Messaging and Page Performance")

if __name__ == "__main__":
    main() 