#!/bin/bash

# Sopra Steria Brand Health Dashboard - Server Shutdown Script
# This script stops all three servers cleanly

echo "🛑 Stopping Sopra Steria Brand Health Dashboard servers..."

# Kill processes by PID if available
if [ -f "logs/fastapi.pid" ]; then
    FASTAPI_PID=$(cat logs/fastapi.pid)
    echo "🐍 Stopping FastAPI service (PID: $FASTAPI_PID)..."
    kill $FASTAPI_PID 2>/dev/null || true
    rm -f logs/fastapi.pid
fi

if [ -f "logs/express.pid" ]; then
    EXPRESS_PID=$(cat logs/express.pid)
    echo "🟢 Stopping Express API server (PID: $EXPRESS_PID)..."
    kill $EXPRESS_PID 2>/dev/null || true
    rm -f logs/express.pid
fi

if [ -f "logs/react.pid" ]; then
    REACT_PID=$(cat logs/react.pid)
    echo "⚛️  Stopping React frontend (PID: $REACT_PID)..."
    kill $REACT_PID 2>/dev/null || true
    rm -f logs/react.pid
fi

# Force kill any remaining processes on these ports
echo "🧹 Cleaning up any remaining processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo "✅ All servers stopped successfully!"
echo ""
echo "To restart all servers, run: ./start_all_servers.sh" 