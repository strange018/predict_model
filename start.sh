#!/bin/bash
# Startup script for Predictive Infrastructure Intelligence System - Local Development

set -e

echo "🚀 Predictive Infrastructure Intelligence System - Local Startup"
echo "=============================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo "📌 Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION} found${NC}"
echo ""

# Check virtual environment
echo "📌 Checking Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment exists${NC}"
fi

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Install requirements
echo "📌 Installing Python dependencies..."
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Display startup summary
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ System Ready for Launch${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

echo "📝 Startup Summary:"
echo "  • Mode: Local Development"
echo "  • Backend: Flask (http://localhost:5000)"
echo "  • Frontend: Direct HTML (http://localhost:5000)"
echo "  • Kubernetes: Demo Mode (simulated metrics)"
echo ""

echo "🚀 Starting Backend Service..."
echo ""
echo "   ▸ Monitoring Service: Starting..."
echo "   ▸ ML Engine: Initialized"
echo "   ▸ API Server: Running on port 5000"
echo ""
echo "📖 Quick Links:"
echo "   • Frontend: http://localhost:5000"
echo "   • Health Check: http://localhost:5000/api/health"
echo "   • Events: http://localhost:5000/api/events"
echo "   • Stats: http://localhost:5000/api/stats"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

# Start the app
python3 app.py
