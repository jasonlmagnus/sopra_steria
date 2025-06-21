#!/bin/bash

# Sopra Steria Website Audit Dashboard - Complete Build Script
# This script sets up everything needed for the dashboard with actionable examples

echo "🚀 Building Sopra Steria Website Audit Dashboard"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "otto_audit.csv" ]; then
    echo "❌ Error: otto_audit.csv not found. Please run this script from the dashboard directory."
    exit 1
fi

# Step 1: Set up virtual environment
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Step 2: Install dependencies
echo "📦 Installing dependencies..."
pip install -q streamlit pandas plotly numpy

# Step 3: Process audit data and extract concrete findings
echo "📊 Processing audit data and extracting concrete findings..."
if python dashboard_analysis.py; then
    echo "✅ Dashboard data processed successfully"
else
    echo "❌ Error processing dashboard data"
    exit 1
fi

if python concrete_findings_extractor.py; then
    echo "✅ Concrete findings extracted successfully"
else
    echo "❌ Error extracting concrete findings"
    exit 1
fi

if python strategic_insights.py; then
    echo "✅ Strategic insights generated successfully"
else
    echo "❌ Error generating strategic insights"
    exit 1
fi

# Step 4: Verify all required files exist
echo "🔍 Verifying dashboard files..."

required_files=(
    "streamlit_dashboard.py"
    "dashboard_analysis.py"
    "concrete_findings_extractor.py"
    "strategic_insights.py"
    "dashboard_data.json"
    "concrete_findings.json"
    "concrete_insights.json"
    "requirements.txt"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -eq 0 ]; then
    echo "✅ All required files present"
else
    echo "❌ Missing files:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

# Step 6: Create launch script
echo "📝 Creating launch script..."
cat > launch_dashboard.sh << 'EOF'
#!/bin/bash

# Sopra Steria Website Audit Dashboard - Launch Script
# This script launches the dashboard with all dependencies

echo "🚀 Starting Sopra Steria Website Audit Dashboard"
echo "================================================"

# Check if we're in the right directory
if [ ! -f "streamlit_dashboard.py" ]; then
    echo "❌ Error: streamlit_dashboard.py not found."
    echo "📁 Current directory: $(pwd)"
    echo "💡 Please run this script from the dashboard directory:"
    echo "   cd dashboard && ./launch_dashboard.sh"
    echo ""
    echo "🔍 Available files in current directory:"
    ls -la
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run build_dashboard.sh first:"
    echo "   ./build_dashboard.sh"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Check if required data files exist
if [ ! -f "dashboard_data.json" ]; then
    echo "❌ Dashboard data not found. Running data processing..."
    python dashboard_analysis.py
fi

if [ ! -f "concrete_findings.json" ]; then
    echo "❌ Concrete findings not found. Extracting concrete findings..."
    python concrete_findings_extractor.py
fi

echo "✅ Dashboard data found"

# Launch Streamlit dashboard
echo "🎯 Starting Streamlit Dashboard..."
echo "Dashboard will open in your browser at http://localhost:8501"
echo "Press Ctrl+C to stop the dashboard"
echo "When done, run 'deactivate' to exit the virtual environment"
echo ""

# Start the dashboard
streamlit run streamlit_dashboard.py
EOF

chmod +x launch_dashboard.sh

# Step 7: Create README with instructions
echo "📚 Creating documentation..."
cat > README_DASHBOARD.md << 'EOF'
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
EOF

echo "✅ Documentation created"

# Step 8: Final verification
echo ""
echo "🎉 Dashboard build completed successfully!"
echo ""
echo "📊 Summary:"
echo "- Virtual environment: ✅ Ready"
echo "- Dependencies: ✅ Installed"
echo "- Data processing: ✅ Complete"
echo "- Strategic insights: ✅ Generated"
echo "- Actionable examples: ✅ Integrated"
echo "- Launch script: ✅ Created"
echo "- Documentation: ✅ Ready"
echo ""
echo "🚀 To start the dashboard:"
echo "   ./launch_dashboard.sh"
echo ""
echo "📚 For detailed information:"
echo "   cat README_DASHBOARD.md"
echo ""
echo "🎯 Dashboard Features:"
echo "   • Specific good vs bad examples with justifications"
echo "   • Real URLs and content analysis"
echo "   • Concrete improvement recommendations"
echo "   • Quick wins with implementation paths"
echo "   • Complete strategic insights"
echo ""

deactivate 