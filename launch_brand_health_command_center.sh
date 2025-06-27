#!/bin/bash

# Brand Health Command Center Launch Script - PYTHON PROJECT
# Launches the strategic marketing decision engine (Streamlit/Python)
# This is a Python application, NOT Node.js

echo "🐍 PYTHON PROJECT - Brand Health Command Center"
echo "🎯 Launching Brand Health Command Center..."
echo "Strategic Marketing Decision Engine (Python/Streamlit)"
echo "======================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if required Python packages are installed
echo "📦 Checking Python dependencies..."
echo "   (This is a Python project using pip, not npm)"
python -c "import streamlit, pandas, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required Python packages. Installing from requirements.txt..."
    pip install -r requirements.txt
fi

# Check if audit data exists
if [ ! -d "audit_outputs" ] || [ -z "$(ls -A audit_outputs)" ]; then
    echo "⚠️  No audit data found in audit_outputs/"
    echo "💡 You can either:"
    echo "   1. Run an audit first using the 'Run Audit' tab"
    echo "   2. Place existing audit data in audit_outputs/[persona_name]/"
    echo ""
fi

echo "🔄 Killing any existing Streamlit processes..."
pkill -f streamlit || true
sleep 2

echo "🚀 Starting Brand Health Command Center..."
echo ""
echo "📊 Dashboard will be available at:"
echo "   Executive Dashboard: http://localhost:8509"
echo ""
echo "🎯 Features:"
echo "   ✅ Strategic brand assessment (Distinct/Resonating/Converting)"
echo "   ✅ Executive KPI dashboard with critical issue alerts"
echo "   ✅ Tier performance analysis with experience data"
echo "   ✅ Top improvement opportunities with impact scoring"
echo "   ✅ Success stories and best practice identification"
echo "   ✅ AI-powered strategic recommendations"
echo ""
echo "📋 Navigation:"
echo "   • Executive Dashboard - Strategic overview (You'll start here)"
echo "   • Persona Insights - How personas feel and act"
echo "   • Content Matrix - Performance across pillars & page types"
echo "   • Opportunity & Impact - Prioritized improvement opportunities"
echo "   • Success Library - High-performing pages to emulate"
echo "   • Run Audit - Create new brand audits"
echo "   • Reports & Export - Share insights and deep-dive data"
echo ""

# Launch the Python Streamlit application from root directory (so data paths work correctly)
echo "🐍 Starting Python Streamlit application..."
streamlit run audit_tool/dashboard/brand_health_command_center.py --server.port 8509

echo ""
echo "🎯 Python Brand Health Command Center stopped." 