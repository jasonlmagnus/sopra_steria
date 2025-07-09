# Sopra Steria Website Audit & Journey Analysis (Hybrid Python/Node.js Project)

This repository contains a comprehensive audit and analysis platform for evaluating Sopra Steria's digital presence. The project is currently undergoing a phased migration to a hybrid architecture.

- **Backend**: Python for data science, AI analysis, and scraping.
- **API**: Node.js (Express/TypeScript) to serve data.
- **Frontend**: React (Vite/TypeScript) for the interactive dashboard.

**For AI Agents:** See `CODEX_IMMEDIATE_TASKS.md` for current priorities and `AGENTS.MD` for detailed guidelines.

**For Migration Status:** Refer to `node_refactor.md` for the detailed migration plan and current status.

## 🚀 Quick Start (Hybrid Development)

### Prerequisites

- Python 3.10+
- Node.js 22+
- Git

### Installation & Launch

```bash
# Clone the repository
git clone https://github.com/jasonlmagnus/sopra_steria.git
cd sopra_steria

# Run the unified setup script for both Python & Node environments
./setup_codex.sh

# To launch the React frontend (once implemented):
cd web
pnpm dev

# To launch the Node.js API (once implemented):
cd api
pnpm start

# Test the API endpoint
curl http://localhost:3000/api/hello
# {"message":"Hello from API"}

# New endpoint to list generated HTML reports
curl http://localhost:3000/api/reports
# {"reports": ["report.html", ...]}

# To launch the Python FastAPI service
cd fastapi_service
python server.py

# Test the FastAPI endpoint
curl http://localhost:8000/hello
# {"message":"Hello from FastAPI"}
```

### Configure PNPM Registry

To install Node dependencies from the public npm registry, run:

```bash
pnpm config set registry https://registry.npmjs.org
pnpm install --registry https://registry.npmjs.org
```

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

### Social Media Backfill Utility

The audit tool includes a specialized utility for managing social media platform data:

**Location**: `audit_tool/social_media_backfill.py`

**Features**:

- Adds missing social media platform entries (Instagram, Facebook, Twitter/X)
- Updates scores based on master social media audit findings
- Validates current state and provides detailed reporting
- Creates automatic backups before any changes

**Usage**:

```bash
# Navigate to audit tool directory
cd audit_tool

# Check current social media data state
python social_media_backfill.py --check

# Add missing social media platforms to CSV
python social_media_backfill.py --add-platforms

# Update social media scores from master audit
python social_media_backfill.py --update-scores

# Complete backfill process (recommended)
python social_media_backfill.py --full-backfill
```

### Gap Analysis Tool

The project includes a dynamic gap analysis tool for validating React component functionality and detecting missing features:

**Location**: `audit_tool/gap_analyzer.py`

**Features**:

- **Component Validation**: Checks React components for expected features
- **API Endpoint Testing**: Validates API connectivity and response codes
- **Routing Verification**: Ensures proper component integration
- **Data Consistency Checks**: Verifies required data files exist
- **Health Scoring**: Provides overall dashboard health assessment
- **Regression Prevention**: Automatically detects when features are accidentally removed

**Usage**:

```bash
# Run gap analysis (from project root)
python audit_tool/gap_analyzer.py

# Generate detailed JSON report
python audit_tool/gap_analyzer.py --output gap_report.json

# Test with different API base URL
python audit_tool/gap_analyzer.py --api-base http://localhost:8000
```

**Integration with CI/CD**:

```bash
# Example CI/CD usage
python audit_tool/gap_analyzer.py
if [ $? -ne 0 ]; then
  echo "Critical gaps detected! Failing build."
  exit 1
fi
```

**Health Scoring**:
- **90-100%**: Excellent - Dashboard is in great shape
- **70-89%**: Good - Minor improvements needed  
- **50-69%**: Fair - Several issues need attention
- **<50%**: Poor - Significant issues require immediate attention

For detailed documentation, see `audit_tool/README_gap_analyzer.md`

**Supported Platforms**:

- **LinkedIn**: `/company/soprasteria-benelux/` (6.8/10 average score)
- **Instagram**: `@soprasteria_bnl` (6.2/10 average score)
- **Facebook**: `/soprasteriabenelux/` (2.8/10 average score)
- **Twitter/X**: `@SopraSteria_Bnl` (1.2/10 average score)

**Persona-Specific Scoring**:

- P1 (C-Suite): LinkedIn 8.0, Instagram 7.0, Facebook 4.0, Twitter 2.0
- P2 (Tech Leaders): LinkedIn 8.0, Instagram 6.0, Facebook 3.0, Twitter 1.0
- P3 (Programme): LinkedIn 6.0, Instagram 8.0, Facebook 2.0, Twitter 1.0
- P4 (Cybersecurity): LinkedIn 5.0, Instagram 3.0, Facebook 3.0, Twitter 1.0
- P5 (Tech Influencers): LinkedIn 7.0, Instagram 7.0, Facebook 2.0, Twitter 1.0

### Social Media Dashboard Integration

The Social Media Analysis dashboard (`8_🔍_Social_Media_Analysis.py`) has been successfully migrated from static markdown to live CSV data:

**✅ Migration Benefits**:

- **Live Data**: Real-time access to updated social media scores from unified audit data
- **Dynamic Analytics**: Interactive filtering by platform and persona
- **Comprehensive Insights**: Automated generation of key insights and recommendations
- **Executive Summary**: High-level metrics including health status and critical issues
- **Action Plans**: Prioritized recommendations with timelines and expected impact

**📊 Current Platform Performance** (Live from CSV):

- **LinkedIn**: 6.5/10 (⚠️ Moderate) - Strongest platform with professional content
- **Instagram**: 6.2/10 (⚠️ Moderate) - Strong visual storytelling, needs technical depth
- **Facebook**: 2.8/10 (🚨 Critical) - Requires comprehensive strategy improvement
- **Twitter/X**: 1.2/10 (🚨 Critical) - Platform abandonment, immediate revival needed

**🎯 Key Features**:

- **Platform Performance Matrix**: Persona-specific scores for each social media platform
- **Interactive Heatmaps**: Visual representation of platform-persona performance
- **Actionable Recommendations**: High/medium priority actions with timelines
- **Executive Metrics**: Critical issues, success cases, and quick win opportunities

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

## 📄 License

This project is proprietary and confidential. All rights reserved.

---

**Last Updated**: January 2025  
**Version**: 2.0  
**Maintainer**: Jason Magnus
