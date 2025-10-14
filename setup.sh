#!/bin/bash

echo "🚀 Setting up AI Hybrid Analysis Platform..."
echo ""

# Check Python version
python_version=$(python3 --version 2>/dev/null || echo "Python not found")
echo "📍 $python_version"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.9+ and try again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment."
        exit 1
    fi
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies."
    exit 1
fi

# Setup environment file
if [ ! -f "backend/.env" ]; then
    echo "⚙️ Setting up environment configuration..."
    cp env.template backend/.env
    echo "✅ Created backend/.env from template"
    echo ""
    echo "📝 IMPORTANT: Edit backend/.env with your API keys:"
    echo "   - THOUGHTSPOT_BASE_URL"
    echo "   - THOUGHTSPOT_AUTH_TOKEN" 
    echo "   - CLAUDE_API_KEY"
else
    echo "✅ Environment file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: ./start_servers.sh"
echo "3. Open: http://localhost:5005 in your browser"
echo ""
echo "💡 Need help? Check the README.md file"
