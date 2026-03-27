#!/bin/bash
###############################################################################
# Floramigo API-Only Demo Launcher
#
# This script starts just the FastAPI backend and provides curl examples.
#
# Usage: ./scripts/demo-api.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🌿 FLORAMIGO API DEMO 🌿                             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
fi

# Create directories
mkdir -p data logs

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}🧹 Stopping API server...${NC}"
    if [ ! -z "$API_PID" ]; then
        kill $API_PID 2>/dev/null || true
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start API
echo -e "${BLUE}🚀 Starting API server...${NC}"
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload > logs/api.log 2>&1 &
API_PID=$!

# Wait for ready
echo -en "${BLUE}⏳ Waiting for API${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
done

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}              API SERVER RUNNING                            ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "📍 Endpoints:"
echo "   • Docs:  http://localhost:8000/docs"
echo "   • API:   http://localhost:8000"
echo ""
echo "🧪 Try these commands:"
echo ""
echo "# 1. Health check"
echo "curl http://localhost:8000/healthz"
echo ""
echo "# 2. Ingest sensor data"
echo "curl -X POST http://localhost:8000/ingest/telemetry \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"temperature\": 24.5, \"humidity\": 45, \"moisture_pct\": 38}'"
echo ""
echo "# 3. Get current readings"
echo "curl http://localhost:8000/ingest/current"
echo ""
echo "# 4. Ask a question"
echo "curl -X POST http://localhost:8000/ask \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"message\": \"How is my plant doing?\"}'"
echo ""
echo "# 5. Get diagnosis"
echo "curl http://localhost:8000/diagnose"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Keep running
wait $API_PID
