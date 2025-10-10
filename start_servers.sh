#!/bin/bash

echo "🚀 Starting AI Hybrid V1 Development Servers..."
echo ""

# Function to kill background jobs on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if Flask dependencies are installed
if ! python3 -c "import flask, flask_cors" 2>/dev/null; then
    echo "📦 Installing Flask dependencies..."
    cd backend
    pip3 install -r api_requirements.txt
    cd ..
fi

# Start API server in background
echo "🔧 Starting API Server (Port 5000)..."
cd backend
python3 api_server.py &
API_PID=$!
cd ..

# Wait a moment for API to start
sleep 2

# Start frontend server in background
echo "🌐 Starting Frontend Server (Port 8000)..."
cd frontend
python3 -m http.server 8000 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers are running!"
echo ""
echo "📋 Access Points:"
echo "  🌐 Frontend UI:    http://localhost:8000"
echo "  🔧 API Server:     http://localhost:5000"
echo "  📊 Health Check:   http://localhost:5000/api/health"
echo ""
echo "💡 Usage:"
echo "  1. Open http://localhost:8000 in your browser"
echo "  2. Configure your scenarios in the UI"
echo "  3. Click 'Save Configuration' to update inputs.json automatically"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"
echo ""

# Wait for background jobs
wait
