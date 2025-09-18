#!/bin/bash

# MIRAGE v2 - Quick Start Web Interface
# Start the web interface for testing and validation

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 MIRAGE v2 - Web Interface Quick Start${NC}"
echo "=============================================="

# Check if .env file exists
if [[ ! -f ".env" ]]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [[ -f ".env.template" ]]; then
        cp .env.template .env
        echo -e "${YELLOW}📝 Please edit .env file and add your GEMINI_API_KEY${NC}"
        echo -e "${YELLOW}   Then run this script again.${NC}"
        exit 1
    else
        echo -e "${YELLOW}❌ .env.template not found. Please create .env file manually.${NC}"
        exit 1
    fi
fi

# Check if GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=your_key_here" .env; then
    echo -e "${YELLOW}⚠️  GEMINI_API_KEY not configured in .env file${NC}"
    echo -e "${YELLOW}   Please add your Gemini API key to .env file${NC}"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo -e "${GREEN}✅ Environment configured${NC}"

# Create necessary directories
mkdir -p data/raw_documents data/embeddings data/processed logs

echo -e "${GREEN}✅ Directories created${NC}"

# Install dependencies if needed
if [[ ! -d ".venv" ]]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -e .
    echo -e "${GREEN}✅ Dependencies installed${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
    source .venv/bin/activate
fi

echo ""
echo -e "${BLUE}🌐 Starting MIRAGE v2 Web Interface...${NC}"
echo ""
echo -e "${GREEN}📋 Available at:${NC}"
echo -e "   • Main Interface: http://127.0.0.1:8000"
echo -e "   • API Endpoints: http://127.0.0.1:8000/api/"
echo -e "   • Health Check: http://127.0.0.1:8000/health"
echo -e "   • WebSocket: ws://127.0.0.1:8000/ws"
echo ""
echo -e "${GREEN}🎯 Features:${NC}"
echo -e "   • Upload pharmaceutical documents"
echo -e "   • AI-powered query processing"
echo -e "   • Human-in-the-Loop validation"
echo -e "   • Real-time monitoring"
echo -e "   • Document management"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo "=============================================="

# Start the web interface
python scripts/start_web_interface.py
