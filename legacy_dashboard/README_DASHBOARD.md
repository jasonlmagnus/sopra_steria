# Sopra Steria Website Audit Dashboard

## Overview
This interactive dashboard provides comprehensive analysis of Sopra Steria's website performance across 5 key personas and multiple content categories, with specific actionable examples and recommendations.

## Features

### 📖 Methodology
- Complete audit framework explanation
- Scoring criteria and persona profiles
- Performance thresholds and interpretation guide

### 📊 Performance Overview
- Executive summary with key metrics
- Persona performance radar charts
- Category performance analysis

### 💡 Actionable Examples (NEW)
- **Specific good vs bad examples** with detailed justifications
- **Real URLs and content** that scored high or low
- **Concrete recommendations** for improvement
- **Quick wins** with clear implementation paths

### 🎯 Strategic Insights
- Critical priority actions with evidence
- Quick wins implementation roadmap
- Recommendation themes analysis

### 👥 Persona Journeys
- Journey consistency analysis
- Persona-specific strengths and weaknesses
- Performance variance identification

### 🏆 Competitive Analysis
- Success patterns and best practices
- Partnership leverage opportunities
- Competitive positioning insights

### 📈 Detailed Analytics
- Score distributions and correlations
- Persona vs category heatmaps
- Statistical analysis

### 📋 Raw Data
- Column-by-column analysis
- Persona-specific narratives
- Data export functionality

## Quick Start

### First Time Setup
```bash
./build_dashboard.sh
```

### Launch Dashboard
```bash
./launch_dashboard.sh
```

The dashboard will open at http://localhost:8501

## Data Sources
- **Raw Data**: otto_audit.csv (10,964 evaluations)
- **Processed Data**: dashboard_data.json
- **Strategic Insights**: strategic_narrative.json

## Key Insights Available

### ✅ What's Working
- Specific examples of high-performing content (≥3.5/5)
- Success patterns and replication strategies
- Best practice identification

### ❌ What's Not Working  
- Concrete examples of failing content (≤2.0/5)
- Detailed justifications for poor performance
- Specific improvement recommendations

### ⚡ Quick Wins
- Moderate-scoring content with clear improvement paths
- Implementation priorities and impact potential
- Resource-efficient optimization opportunities

## Technical Details

### Dependencies
- Python 3.8+
- Streamlit
- Pandas
- Plotly
- NumPy

### File Structure
```
dashboard/
├── build_dashboard.sh          # Complete build script
├── launch_dashboard.sh         # Dashboard launcher
├── streamlit_dashboard.py      # Main dashboard application
├── dashboard_analysis.py       # Data processing
├── strategic_insights.py       # Strategic analysis
├── otto_audit.csv             # Raw audit data
├── dashboard_data.json         # Processed data
├── strategic_narrative.json    # Strategic insights
└── venv/                      # Virtual environment
```

### Data Processing Pipeline
1. **Raw Data Extraction** - Processes otto_audit.csv
2. **Score Extraction** - Extracts numerical scores from evaluation text
3. **Example Extraction** - Identifies specific good/bad examples with justifications
4. **Strategic Analysis** - Generates insights and recommendations
5. **Dashboard Integration** - Consolidates all data for interactive visualization

## Troubleshooting

### Dashboard Won't Start
```bash
# Rebuild everything
./build_dashboard.sh
```

### Missing Data
```bash
# Reprocess data
source venv/bin/activate
python dashboard_analysis.py
python strategic_insights.py
```

### Port Issues
If port 8501 is busy, Streamlit will automatically use the next available port (8502, 8503, etc.)

## Support
For issues or questions, check the console output for detailed error messages.
