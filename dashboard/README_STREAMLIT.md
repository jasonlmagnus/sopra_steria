# 🎯 Sopra Steria Website Audit - Streamlit Dashboard

An interactive dashboard for analyzing website audit results across different personas and content categories.

## 🚀 Quick Start

### Option 1: Automated Setup with Virtual Environment (Recommended)

```bash
cd dashboard
./setup_venv.sh
./run_dashboard.sh
```

### Option 2: Manual Setup with Virtual Environment

```bash
cd dashboard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate dashboard data (if not already done)
python dashboard_analysis.py

# Run the dashboard
streamlit run streamlit_dashboard.py
```

### Option 3: System-wide Installation (Not Recommended)

```bash
cd dashboard

# Install dependencies globally
pip3 install -r requirements.txt

# Generate dashboard data (if not already done)
python3 dashboard_analysis.py

# Run the dashboard
streamlit run streamlit_dashboard.py
```

## 📁 File Structure

```
dashboard/
├── 🎯 streamlit_dashboard.py     # Main dashboard application
├── 📊 dashboard_data.json        # Processed audit data (1.3MB)
├── 📋 dashboard_report.md        # Static analysis report
├── 🔧 dashboard_analysis.py      # Data processing script
├── 📖 README_STREAMLIT.md        # This documentation
├── 🚀 run_dashboard.sh          # Automated run script
├── ⚙️ setup_venv.sh             # Virtual environment setup
├── 📦 requirements.txt          # Python dependencies
├── 📈 dashboard_recommendations.md # Implementation guide
├── 📄 otto_audit.csv            # Original audit data
└── 📁 venv/                     # Virtual environment (created automatically)
```

## 🔧 Virtual Environment Benefits

### **Why Use Virtual Environment:**

- ✅ **Isolated Dependencies**: No conflicts with system Python packages
- ✅ **Reproducible Setup**: Consistent environment across different machines
- ✅ **Easy Cleanup**: Remove entire `venv` folder to uninstall
- ✅ **Version Control**: Specific package versions guaranteed

### **Virtual Environment Commands:**

```bash
# Activate (run from dashboard directory)
source venv/bin/activate

# Deactivate (when done)
deactivate

# Remove environment (if needed)
rm -rf venv
```

## 📊 Dashboard Features

### **Executive Summary**

- **Key Metrics**: Total evaluations, average scores, URLs analyzed
- **Performance Alerts**: Critical and moderate performance indicators
- **Top Insights**: Best and worst performing personas

### **Interactive Visualizations**

#### 1. **Persona Comparison Radar Chart**

- Multi-dimensional comparison across 6 metrics:
  - Headlines effectiveness
  - Content relevance
  - Pain point recognition
  - Value proposition clarity
  - Trust signals
  - CTA appropriateness

#### 2. **Category Performance Analysis**

- Horizontal bar chart showing content category performance
- Color-coded by performance level (Red < 2.0, Orange < 3.0, Green ≥ 3.0)
- Critical and good performance thresholds marked

#### 3. **Score Distribution**

- Histogram showing overall score distribution
- Average score line for reference
- Helps identify performance patterns

#### 4. **Persona vs Category Heatmap**

- Matrix view of persona performance across categories
- Color-coded for easy identification of strengths/weaknesses
- Interactive hover for detailed scores

### **Filtering & Interactivity**

#### **Sidebar Filters**

- **Persona Selection**: Choose specific personas to analyze
- **Category Selection**: Focus on particular content types
- **Score Range**: Filter by performance levels (0-5 scale)

#### **Real-time Updates**

- All visualizations update automatically based on filters
- Metrics recalculate dynamically
- Export filtered data as CSV

### **Detailed Analysis**

#### **Top/Bottom Performers**

- **Top 5 URLs**: Best performing content by score
- **Bottom 5 URLs**: Content needing immediate attention
- Includes category, persona, and score information

#### **Action Items & Quick Wins**

- **Impact Potential Analysis**: Categories with high improvement opportunity
- **Quick Wins Identification**: Low-hanging fruit for optimization
- **Specific Recommendations**: Targeted improvement suggestions

#### **Raw Data Access**

- Toggle to show complete evaluation dataset
- Download filtered data as CSV
- Timestamp-based file naming

## 🎨 Dashboard Layout

```
┌─────────────────────────────────────────────────────────────┐
│                    🎯 SOPRA STERIA AUDIT DASHBOARD          │
├─────────────────────────────────────────────────────────────┤
│ SIDEBAR FILTERS     │ MAIN CONTENT AREA                     │
│ ├── Personas        │ ┌─── Executive Summary ───┐           │
│ ├── Categories      │ │ Metrics | Alerts | Insights │       │
│ └── Score Range     │ └─────────────────────────────┘       │
│                     │                                       │
│                     │ ┌─── Performance Analysis ───┐        │
│                     │ │ Radar | Bar | Dist | Heat  │        │
│                     │ └─────────────────────────────┘       │
│                     │                                       │
│                     │ ┌─── Detailed Analysis ───┐           │
│                     │ │ Top/Bottom | Quick Wins  │          │
│                     │ └─────────────────────────────┘       │
│                     │                                       │
│                     │ ┌─── Raw Data Export ───┐             │
│                     │ │ Table View | Download  │             │
│                     │ └─────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 📈 Key Insights from Your Data

### **Critical Performance Alert** 🚨

- **Overall Average**: 1.90/5 (Critical level)
- **Total Evaluations**: 270 across 5 personas
- **URLs Analyzed**: 76 unique URLs

### **Persona Performance Ranking**

1. **Cross-Sector IT Director**: 2.22/5 (Best)
2. **IT Executive (Public Sector)**: 1.96/5
3. **Operations Transformation Executive**: 1.92/5
4. **Financial Services Leader**: 1.77/5
5. **Chief Data Officer**: 1.69/5 (Needs Attention)

### **Content Category Performance**

- **Best**: External News (Merger) - 2.71/5
- **Worst**: Social Media Profile - 1.11/5
- **Quick Win**: Social Media optimization opportunity

## 🔧 Technical Requirements

### **System Requirements**

- Python 3.7 or higher
- 4GB RAM minimum (8GB recommended)
- Modern web browser (Chrome, Firefox, Safari, Edge)

### **Dependencies**

```
streamlit>=1.28.0    # Interactive web app framework
pandas>=1.5.0        # Data manipulation and analysis
plotly>=5.15.0       # Interactive visualizations
numpy>=1.24.0        # Numerical computing
```

### **Data Files Required**

- `otto_audit.csv` - Original audit data
- `dashboard_data.json` - Processed data (auto-generated)

## 🎯 Usage Scenarios

### **Executive Presentation**

1. Navigate to dashboard directory: `cd dashboard`
2. Run: `./run_dashboard.sh`
3. Open dashboard in presentation mode (F11)
4. Focus on Executive Summary section
5. Export specific data for follow-up discussions

### **Detailed Analysis**

1. Use persona filters to focus on specific audiences
2. Analyze radar charts for multi-dimensional insights
3. Identify quick wins from Action Items section
4. Export filtered data for deeper analysis

### **Progress Tracking**

1. Re-run `python dashboard_analysis.py` with updated data
2. Compare performance metrics over time
3. Track improvement in specific categories
4. Monitor persona-specific optimizations

## 🚀 Advanced Features

### **Custom Analysis**

- Filter combinations for specific insights
- Export capabilities for external analysis
- Real-time metric calculations

### **Performance Optimization**

- Cached data loading for faster performance
- Efficient filtering and aggregation
- Responsive design for all screen sizes

### **Data Export Options**

- CSV export with timestamps
- Filtered data preservation
- Complete evaluation text included

## 🔍 Troubleshooting

### **Common Issues**

#### Dashboard won't start

```bash
cd dashboard

# Check if you're in the right directory
ls -la streamlit_dashboard.py

# Set up virtual environment
./setup_venv.sh

# Run dashboard
./run_dashboard.sh
```

#### Virtual environment issues

```bash
# Remove and recreate virtual environment
rm -rf venv
./setup_venv.sh
```

#### Data not loading

```bash
# Regenerate dashboard data
source venv/bin/activate
python dashboard_analysis.py

# Check file exists
ls -la dashboard_data.json
```

#### Performance issues

- Close other browser tabs
- Restart the dashboard
- Check system memory usage

### **Browser Compatibility**

- **Recommended**: Chrome, Firefox (latest versions)
- **Supported**: Safari, Edge
- **Not supported**: Internet Explorer

## 📊 Dashboard URLs

Once running, access the dashboard at:

- **Local**: http://localhost:8501
- **Network**: http://[your-ip]:8501 (for sharing)

## 🎨 Customization

### **Styling**

- Custom CSS in `streamlit_dashboard.py`
- Color schemes for performance levels
- Responsive layout design

### **Metrics**

- Modify scoring thresholds in code
- Add new visualization types
- Customize alert conditions

## 📝 Next Steps

1. **Navigate to dashboard directory**: `cd dashboard`
2. **Set up environment**: `./setup_venv.sh` (first time only)
3. **Run dashboard**: `./run_dashboard.sh`
4. **Review Current Performance**: Use Executive Summary
5. **Identify Quick Wins**: Check Action Items section
6. **Plan Improvements**: Export data for detailed planning
7. **Track Progress**: Re-run analysis after optimizations
8. **Share Insights**: Use presentation mode for stakeholders

---

**Quick Commands:**

```bash
# First time setup
cd dashboard
./setup_venv.sh

# Run dashboard
./run_dashboard.sh

# Manual activation (if needed)
source venv/bin/activate
streamlit run streamlit_dashboard.py

# Deactivate when done
deactivate
```

**Support**: For issues or questions, refer to the troubleshooting section above.
