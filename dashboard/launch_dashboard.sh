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
