# Sopra Steria Website Audit & Journey Analysis

A comprehensive audit and analysis platform for evaluating Sopra Steria's digital presence across multiple personas and user journeys.

## 🎯 Project Overview

This repository contains a complete website audit system that combines:

- **Quantitative Analysis**: 10,964+ evaluations across 5 personas and 76 URLs
- **Qualitative Journey Mapping**: Deep-dive persona journey analysis
- **Interactive Dashboard**: Streamlit-based visualization and insights platform
- **Strategic Recommendations**: Actionable insights with implementation roadmaps

## 📊 Dashboard Features

### Core Analytics

- **Executive Summary**: KPIs, performance alerts, and key metrics
- **Persona Analysis**: Radar charts comparing 6 key metrics across personas
- **Category Performance**: Color-coded performance analysis by content type
- **Score Distribution**: Statistical analysis of evaluation patterns
- **Heatmap Visualization**: Persona vs category performance matrix

### Advanced Insights

- **🎯 Strategic Insights**: Critical priority actions and quick wins roadmap
- **👥 Persona Journeys**: Journey inconsistency analysis and recommendations
- **🏆 Competitive Analysis**: Partnership leverage opportunities and success patterns
- **🚨 Critical Issues**: Specific problems with exact quotes and examples
- **✅ What Works**: Concrete examples of successful content with detailed justifications
- **⚡ Quick Wins**: Specific improvement opportunities with measurable impact potential
- **⚠️ Audit Methodology Issues**: Brand positioning evaluation problems and solutions

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git

### Installation & Launch

```bash
# Clone the repository
git clone https://github.com/jasonlmagnus/sopra_steria.git
cd sopra_steria

# Build and launch dashboard (automated setup)
cd dashboard
./build_dashboard.sh

# Launch dashboard (for subsequent runs)
./launch_dashboard.sh
```

The dashboard will automatically:

- Create virtual environment
- Install dependencies
- Process data files
- Extract concrete findings
- Generate strategic insights
- Launch Streamlit interface

Access the dashboard at: `http://localhost:8501`

## 📁 Repository Structure

```
sopra_steria/
├── dashboard/                          # Main dashboard application
│   ├── streamlit_dashboard.py         # Primary dashboard interface
│   ├── dashboard_analysis.py          # Data processing engine
│   ├── concrete_findings_extractor.py # Findings extraction system
│   ├── strategic_insights.py          # Strategic analysis generator
│   ├── build_dashboard.sh             # Automated setup script
│   ├── launch_dashboard.sh            # Dashboard launcher
│   ├── requirements.txt               # Python dependencies
│   └── README_STREAMLIT.md           # Detailed dashboard documentation
├── personas/                          # Persona definitions and analysis
├── prompts/                          # Analysis prompts and frameworks
├── data/                             # Supporting data files
└── README.md                         # This file
```

## 🎭 Persona Analysis

### Evaluated Personas

1. **IT Executive Public Sector** - Government digital transformation leaders
2. **Financial Services Leader** - Banking and finance IT decision makers
3. **Chief Data Officer** - Data strategy and governance executives
4. **Operations Transformation Executive** - Operational efficiency leaders
5. **Cross-Sector IT Director** - Multi-industry technology leaders

### Journey Analysis Available

- **P1: BENELUX Public Sector IT Executive** - Complete 5-stage journey mapping
  - Discovery & Initial Awareness
  - Industry & Solution Exploration
  - Deep Solution Research
  - Content & Insight Consumption
  - Decision & Contact Consideration

## 📈 Key Findings

### Performance Overview

- **Overall Average Score**: 1.90/5 (Critical level)
- **Best Performer**: Cross-Sector IT Director (2.22/5)
- **Worst Performer**: Chief Data Officer (1.69/5)
- **Quick Win Opportunity**: Social Media optimization (1.11/5)

### Critical Issues Identified

- **753 Critical Issues** with specific examples and justifications
- **Brand Positioning Problems**: Inappropriate persona-specific evaluation of inspirational messaging
- **Content Gaps**: Limited government-specific adaptation and context
- **Navigation Issues**: Difficulty finding relevant information by persona

### Success Patterns

- **124 Best Practices** with concrete examples
- **Strong European Heritage**: Sovereignty positioning aligns with values
- **Proven Scale**: £300m+ government contracts demonstrate capability
- **Comprehensive Expertise**: 3,000+ cybersecurity specialists

## 🛠️ Technical Architecture

### Dashboard Technology Stack

- **Frontend**: Streamlit with custom CSS styling
- **Visualization**: Plotly for interactive charts and graphs
- **Data Processing**: Pandas for analysis and manipulation
- **Backend**: Python with caching for performance optimization

### Data Processing Pipeline

1. **Raw Data Ingestion**: CSV audit data processing
2. **Score Extraction**: Regex-based numerical score extraction
3. **Findings Analysis**: Natural language processing for insights
4. **Strategic Pattern Recognition**: Cross-persona trend analysis
5. **Visualization Generation**: Interactive chart and graph creation

## 📋 Usage Examples

### Dashboard Navigation

```python
# Filter by persona
persona_filter = "IT Executive Public Sector"

# Filter by score range
score_range = (1.0, 3.0)  # Critical to moderate performance

# Export findings
download_csv_data()  # Available in dashboard interface
```

### Command Line Operations

```bash
# Rebuild all data and insights
./build_dashboard.sh

# Launch with specific port
streamlit run streamlit_dashboard.py --server.port 8502

# Check dashboard status
ps aux | grep streamlit
```

## 🔧 Configuration

### Environment Variables

- `STREAMLIT_SERVER_PORT`: Dashboard port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Server address (default: localhost)

### Data Sources

- Primary audit data: `otto_audit.csv` (excluded from repository)
- Processed data: Generated automatically during build process
- Journey analysis: Markdown files in persona directories

## 🤝 Contributing

### Development Setup

```bash
# Create development environment
python -m venv dev_env
source dev_env/bin/activate  # On Windows: dev_env\Scripts\activate
pip install -r dashboard/requirements.txt

# Run in development mode
streamlit run dashboard/streamlit_dashboard.py --server.runOnSave true
```

### Adding New Personas

1. Create persona directory in `personas/`
2. Add journey analysis markdown files
3. Update dashboard persona filters
4. Regenerate insights with `./build_dashboard.sh`

## 📊 Performance Metrics

### Dashboard Performance

- **Load Time**: <3 seconds for initial dashboard load
- **Data Processing**: ~30 seconds for complete rebuild
- **Memory Usage**: ~200MB for full dataset
- **Concurrent Users**: Supports multiple simultaneous users

### Analysis Coverage

- **10,964 Total Evaluations** across all personas and URLs
- **1,386 Concrete Findings** extracted and categorized
- **270 Individual Category Scores** for detailed analysis
- **5 Complete Journey Stages** mapped for government persona

## 🔒 Security & Privacy

### Data Protection

- Sensitive audit data excluded from repository via `.gitignore`
- No personal or confidential information in tracked files
- Local processing only - no external data transmission

### Access Control

- Dashboard runs locally by default
- Network access configurable via Streamlit settings
- No authentication required for local development use

## 📞 Support & Contact

### Documentation

- **Dashboard Guide**: `dashboard/README_STREAMLIT.md`
- **Technical Details**: `dashboard/README_DASHBOARD.md`
- **Strategic Insights**: Available in dashboard interface

### Troubleshooting

```bash
# Common issues and solutions
./build_dashboard.sh  # Rebuilds everything from scratch
./launch_dashboard.sh --help  # Shows available options
```

## 🟢 Node Example

This repository now includes a small Node.js script located in `node_scripts/`.
You can run it to verify Node is configured correctly:

```bash
cd node_scripts
npm install
npm run hello
```

## 📄 License

This project is proprietary and confidential. All rights reserved.

---

**Last Updated**: January 2025  
**Version**: 2.0  
**Maintainer**: Jason Magnus
