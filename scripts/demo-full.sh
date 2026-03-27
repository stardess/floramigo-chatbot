#!/bin/bash
###############################################################################
# Floramigo Full System Demo Launcher
#
# This script starts the complete Floramigo system:
# - FastAPI backend server
# - Voice chatbot with wake word detection
# - Sample sensor data generation
#
# Usage: ./scripts/demo-full.sh
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║           🌿 FLORAMIGO FULL SYSTEM DEMO 🌿                  ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}⚠  Virtual environment not activated${NC}"
    if [ -d "venv" ]; then
        echo "   Activating venv..."
        source venv/bin/activate
    else
        echo -e "${RED}Error: venv not found. Run: python -m venv venv${NC}"
        exit 1
    fi
fi

# Check OpenAI API key
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo -e "${YELLOW}⚠  OPENAI_API_KEY not set${NC}"
    echo "   Voice features will be limited"
    echo "   Set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check dependencies
echo -e "${BLUE}📦 Checking dependencies...${NC}"
python -c "import fastapi" 2>/dev/null || {
    echo "Installing API dependencies..."
    pip install -q -r requirements-api.txt
}
python -c "import openai" 2>/dev/null || {
    echo "Installing core dependencies..."
    pip install -q -r requirements-core.txt
}
echo "✓ Dependencies OK"

# Create data directory if needed
mkdir -p data logs

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    
    # Kill background processes
    if [ ! -z "$API_PID" ]; then
        echo "   Stopping API server (PID: $API_PID)..."
        kill $API_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$DATA_PID" ]; then
        echo "   Stopping data generator (PID: $DATA_PID)..."
        kill $DATA_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
    exit 0
}

# Trap Ctrl+C and cleanup
trap cleanup SIGINT SIGTERM

# Start API server
echo -e "\n${BLUE}🚀 Starting API server...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!
echo "   API server started (PID: $API_PID)"
echo "   Logs: logs/api.log"

# Wait for API to be ready
echo -en "${BLUE}⏳ Waiting for API to be ready${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

# Test API
echo -e "${BLUE}🧪 Testing API...${NC}"
HEALTH=$(curl -s http://localhost:8000/healthz)
if [[ "$HEALTH" == *"ok"* ]]; then
    echo "✓ API is healthy"
else
    echo -e "${RED}✗ API health check failed${NC}"
    cleanup
    exit 1
fi

# Ingest sample telemetry
echo -e "\n${BLUE}📊 Ingesting sample sensor data...${NC}"
curl -s -X POST http://localhost:8000/ingest/telemetry \
    -H "Content-Type: application/json" \
    -d '{
      "temperature": 24.5,
      "humidity": 45,
      "moisture_pct": 38,
      "light_raw": 180,
      "plant_name": "Basil"
    }' > /dev/null
echo "✓ Sample data ingested"

# Show current status
echo -e "\n${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}                    SYSTEM READY                            ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📍 API Endpoints:"
echo "   • API Docs:      http://localhost:8000/docs"
echo "   • Health Check:  http://localhost:8000/healthz"
echo "   • Ask Question:  POST http://localhost:8000/ask"
echo ""
echo "🎤 Voice Chatbot:"
echo "   Starting in 3 seconds..."
echo ""
echo "💡 Tips:"
echo "   • Say 'Hey Floramigo' or 'Hey Flora' to activate"
echo "   • Ask about plant status, watering, care tips"
echo "   • Say 'goodbye' to end conversation"
echo "   • Press Ctrl+C to exit completely"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

sleep 3

# Start voice chatbot (foreground)
echo -e "\n${BLUE}🎤 Starting voice chatbot...${NC}\n"
python client/floramigo-voice.py --api-url http://localhost:8000

# Cleanup will be called by trap
