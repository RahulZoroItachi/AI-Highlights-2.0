#!/bin/bash

echo "🚀 Starting AI Hybrid V1 Development Server..."
echo ""

# Function to kill background jobs on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down server..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Load environment variables to get the port
if [ -f "backend/.env" ]; then
    export $(grep -v '^#' backend/.env | grep 'PORT=' | xargs)
elif [ -f ".env" ]; then
    export $(grep -v '^#' .env | grep 'PORT=' | xargs)
fi

# Use PORT from .env or default to 5005
PORT=${PORT:-5005}

# Check if Flask dependencies are installed
if ! python3 -c "import flask, flask_cors" 2>/dev/null; then
    echo "📦 Installing Flask dependencies..."
    cd backend
    pip3 install -r api_requirements.txt
    cd ..
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
fi

# Start the unified server
echo "🚀 Starting Unified Server..."
cd backend
python3 api_server.py &
SERVER_PID=$!
cd ..

echo ""
echo "✅ Server is running!"
echo ""
echo "📋 Access Points:"
echo "  🌐 Application UI:  http://localhost:${PORT}"
echo "  🔧 API Base:        http://localhost:${PORT}/api/"
echo "  📊 Health Check:    http://localhost:${PORT}/api/health"
echo "  ⚙️ Configuration:   http://localhost:${PORT}/config.js"
echo ""
echo "💡 Usage:"
echo "  1. Open http://localhost:${PORT} in your browser"
echo "  2. Use the Settings tab to configure API keys"
echo "  3. Configure your scenarios and run analysis"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Wait for background job
wait
