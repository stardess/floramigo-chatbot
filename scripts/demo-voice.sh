#!/bin/bash
###############################################################################
# Floramigo Voice-Only Demo Launcher
#
# This script starts just the voice chatbot (requires API to be running separately).
#
# Usage: ./scripts/demo-voice.sh
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🎤 FLORAMIGO VOICE CHATBOT DEMO 🎤                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
fi

# Check OpenAI API key
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo -e "${RED}✗ Error: OPENAI_API_KEY not set${NC}"
    echo "  Voice chatbot requires OpenAI API key"
    echo "  Set it with: export OPENAI_API_KEY='sk-your-key-here'"
    exit 1
fi

# Check if API is running
echo -e "${BLUE}🔍 Checking if API is running...${NC}"
if ! curl -s http://localhost:8000/healthz > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠  API server not detected at http://localhost:8000${NC}"
    echo "   Voice chatbot will use OpenAI directly (may have limited plant context)"
    echo ""
    read -p "Continue? (Y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        echo "Start the API first with: ./scripts/demo-api.sh"
        exit 1
    fi
else
    echo -e "${GREEN}✓ API server detected${NC}"
fi

# Check dependencies
echo -e "${BLUE}📦 Checking voice dependencies...${NC}"
python -c "import openai, pyaudio, numpy" 2>/dev/null || {
    echo "Installing dependencies..."
    pip install -q openai pyaudio numpy requests
}
echo "✓ Dependencies OK"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}              VOICE CHATBOT READY                           ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "🎤 Wake Phrases:"
echo "   • 'Hey Floramigo'"
echo "   • 'Hey Flora'"
echo "   • 'Floramigo'"
echo ""
echo "💬 Example Questions:"
echo "   • 'How is my plant doing?'"
echo "   • 'Does my plant need water?'"
echo "   • 'What's the temperature?'"
echo "   • 'Should I fertilize?'"
echo ""
echo "🛑 To End:"
echo "   • Say 'goodbye' or 'bye'"
echo "   • Press Ctrl+C"
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Starting voice chatbot..."
echo ""

# Run voice chatbot
python client/floramigo-voice.py --api-url http://localhost:8000
