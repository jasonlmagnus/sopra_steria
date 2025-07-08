#!/bin/bash

# Sopra Steria Brand Health Dashboard - Multi-Server Startup Script
# This script starts all three required servers for the React application

echo "🚀 Starting Sopra Steria Brand Health Dashboard..."
echo "This will start 3 servers:"
echo "  • FastAPI Service (Port 8000) - Python backend"
echo "  • Express API Server (Port 3000) - Node.js middleware"  
echo "  • React Frontend (Port 5173) - Vite dev server"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes on these ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

sleep 2

# Start FastAPI service
echo "🐍 Starting FastAPI service on port 8000..."
python3 -m fastapi_service.server > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "FastAPI PID: $FASTAPI_PID"

# Wait for FastAPI to start
sleep 3

# Start Express API server
echo "🟢 Starting Express API server on port 3000..."
cd api
npm start > ../logs/express.log 2>&1 &
EXPRESS_PID=$!
echo "Express PID: $EXPRESS_PID"
cd ..

# Wait for Express to start
sleep 3

# Start React frontend
echo "⚛️  Starting React frontend on port 5173..."
cd web
npm run dev > ../logs/react.log 2>&1 &
REACT_PID=$!
echo "React PID: $REACT_PID"
cd ..

# Save PIDs for cleanup
echo "$FASTAPI_PID" > logs/fastapi.pid
echo "$EXPRESS_PID" > logs/express.pid
echo "$REACT_PID" > logs/react.pid

echo ""
echo "✅ All servers started successfully!"
echo ""
echo "🌐 Access your application at:"
echo "  • React Frontend: http://localhost:5173"
echo "  • Express API: http://localhost:3000"
echo "  • FastAPI Service: http://localhost:8000"
echo ""
echo "📋 Server Status:"
echo "  • FastAPI Service: PID $FASTAPI_PID"
echo "  • Express API: PID $EXPRESS_PID"  
echo "  • React Frontend: PID $REACT_PID"
echo ""
echo "📝 Logs are available in the logs/ directory"
echo "  • FastAPI: logs/fastapi.log"
echo "  • Express: logs/express.log"
echo "  • React: logs/react.log"
echo ""
echo "🛑 To stop all servers, run: ./stop_all_servers.sh"
echo ""
echo "Press Ctrl+C to stop monitoring (servers will continue running)"

# Monitor the processes
while true; do
    sleep 5
    if ! kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "❌ FastAPI service stopped unexpectedly"
        echo "Check logs/fastapi.log for details"
        break
    fi
    if ! kill -0 $EXPRESS_PID 2>/dev/null; then
        echo "❌ Express API server stopped unexpectedly"
        echo "Check logs/express.log for details"
        break
    fi
    if ! kill -0 $REACT_PID 2>/dev/null; then
        echo "❌ React frontend stopped unexpectedly"
        echo "Check logs/react.log for details"
        break
    fi
done 