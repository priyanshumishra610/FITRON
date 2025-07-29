#!/bin/bash

# FITRON AI Coach Chatbot - Quick Start Script
# This script sets up and starts the FITRON chatbot

set -e

echo "🏋️‍♂️ FITRON AI Coach Chatbot - Quick Start"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    print_error "Please run this script from the backend directory"
    exit 1
fi

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    print_error "Python 3.8+ is required. Found: $python_version"
    exit 1
fi
print_success "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f "env.example" ]; then
        cp env.example .env
        print_success ".env file created from template"
        print_warning "Please edit .env file with your configuration"
    else
        print_error "env.example not found. Please create .env file manually"
        exit 1
    fi
fi

# Check if Ollama is installed
print_status "Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    print_warning "Ollama not found. Installing..."
    curl -fsSL https://ollama.ai/install.sh | sh
    print_success "Ollama installed"
else
    print_success "Ollama found"
fi

# Start Ollama if not running
print_status "Starting Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    ollama serve &
    sleep 3
    print_success "Ollama service started"
else
    print_success "Ollama service already running"
fi

# Check if required model is available
print_status "Checking Ollama models..."
MODEL_NAME=${MODEL_NAME:-"gemma"}
if ! ollama list | grep -q "$MODEL_NAME"; then
    print_warning "Model $MODEL_NAME not found. Downloading..."
    ollama pull "$MODEL_NAME"
    print_success "Model $MODEL_NAME downloaded"
else
    print_success "Model $MODEL_NAME found"
fi

# Check MongoDB
print_status "Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    print_warning "MongoDB not found. Please install MongoDB:"
    echo "  macOS: brew install mongodb-community"
    echo "  Ubuntu: sudo apt install mongodb"
    echo "  Windows: Download from mongodb.com"
    echo ""
    print_warning "Starting without MongoDB (some features may not work)"
else
    # Try to start MongoDB if not running
    if ! pgrep -x "mongod" > /dev/null; then
        print_status "Starting MongoDB..."
        mongod --dbpath /tmp/mongodb --fork --logpath /tmp/mongodb.log
        sleep 2
        print_success "MongoDB started"
    else
        print_success "MongoDB already running"
    fi
fi

# Run health check
print_status "Running health check..."
python3 -c "
import asyncio
import httpx
import sys

async def health_check():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get('http://localhost:8000/api/v1/chatbot/health', timeout=5)
            if response.status_code == 200:
                print('✅ Health check passed')
                return True
            else:
                print('❌ Health check failed')
                return False
    except Exception as e:
        print(f'❌ Health check error: {e}')
        return False

if __name__ == '__main__':
    result = asyncio.run(health_check())
    sys.exit(0 if result else 1)
" || {
    print_warning "Health check failed - server may not be running yet"
}

# Start the server
print_status "Starting FITRON AI Coach Chatbot..."
echo ""
echo "🚀 Server starting on http://localhost:8000"
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🧪 Test the chatbot: python test_chatbot.py"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 