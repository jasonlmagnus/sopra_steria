#!/bin/bash

echo "🚀 Starting Sopra Steria Website Audit Dashboard"
echo "================================================"

# Check if we're in the dashboard directory
if [ ! -f "streamlit_dashboard.py" ]; then
    echo "❌ Please run this script from the dashboard directory"
    echo "Current directory: $(pwd)"
    echo "Expected files: streamlit_dashboard.py, requirements.txt"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    ./setup_venv.sh
    if [ $? -ne 0 ]; then
        echo "❌ Failed to set up virtual environment"
        exit 1
    fi
else
    echo "✅ Virtual environment found"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    echo "Try running: ./setup_venv.sh"
    exit 1
fi

echo "✅ Virtual environment activated"

# Check if dashboard data exists
if [ ! -f "dashboard_data.json" ]; then
    echo "📊 Generating dashboard data..."
    python dashboard_analysis.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Dashboard data generated"
    else
        echo "❌ Failed to generate dashboard data"
        echo "Please ensure otto_audit.csv exists and run dashboard_analysis.py manually"
        exit 1
    fi
else
    echo "✅ Dashboard data found"
fi

echo ""
echo "🎯 Starting Streamlit Dashboard..."
echo "Dashboard will open in your browser at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo "When done, run 'deactivate' to exit the virtual environment"
echo ""

# Run Streamlit
streamlit run streamlit_dashboard.py 