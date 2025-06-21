#!/bin/bash

echo "🚀 Launching Brand Audit Dashboard..."
echo ""
echo "🔧 Two Dashboard Options Available:"
echo ""
echo "1. 🏃 AUDIT RUNNER (Port 8504)"
echo "   ✅ Run new brand audits"
echo "   ✅ Upload personas and URLs"
echo "   ✅ Monitor audit progress"
echo "   ✅ View audit results"
echo ""
echo "2. 📊 ANALYSIS DASHBOARD (Port 8505)"
echo "   ✅ Executive summary with critical issues"
echo "   ✅ AI-powered strategic insights"
echo "   ✅ Performance overview with charts"
echo "   ✅ Evidence explorer with search"
echo "   ✅ Multi-persona analysis"
echo "   ✅ Advanced data export"
echo ""

# Kill any existing instances
lsof -ti:8504 | xargs kill -9 2>/dev/null || true
lsof -ti:8505 | xargs kill -9 2>/dev/null || true

echo "🚀 Starting both dashboards..."
echo ""

# Launch audit runner in background
echo "Starting Audit Runner on http://localhost:8504"
streamlit run audit_tool/dashboard/audit_runner_dashboard.py --server.port 8504 &

# Wait a moment
sleep 2

# Launch analysis dashboard
echo "Starting Analysis Dashboard on http://localhost:8505"
echo ""
echo "🎯 Analysis Dashboard Features:"
echo "   • Executive Summary - Critical issues and tier analysis"
echo "   • AI Strategic Insights - Priority recommendations"
echo "   • Performance Overview - Charts and metrics"
echo "   • Evidence Explorer - Search AI rationale"
echo ""
streamlit run audit_tool/dashboard/main_dashboard.py --server.port 8505 