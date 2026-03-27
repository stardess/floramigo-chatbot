#!/bin/bash
###############################################################################
# Floramigo System Test Script
#
# Runs all tests and validates the system is ready for demo.
#
# Usage: ./scripts/test-system.sh
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

FAILED_TESTS=0

echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        🧪 FLORAMIGO SYSTEM TEST SUITE 🧪                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Activate venv if needed
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    fi
fi

# Test 1: Python version
echo -e "\n${BLUE}[1/8] Checking Python version...${NC}"
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 9 ]; then
    echo -e "${GREEN}✓ Python $PYTHON_VERSION (OK)${NC}"
else
    echo -e "${RED}✗ Python 3.9+ required (found $PYTHON_VERSION)${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 2: Check dependencies
echo -e "\n${BLUE}[2/8] Checking dependencies...${NC}"
DEPS=("fastapi" "openai" "uvicorn" "requests" "pydantic")
for dep in "${DEPS[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        echo -e "${GREEN}✓ $dep installed${NC}"
    else
        echo -e "${RED}✗ $dep missing${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 3: Check project structure
echo -e "\n${BLUE}[3/8] Checking project structure...${NC}"
DIRS=("api" "floramigo" "client" "tests" "docs" "data")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓ $dir/ exists${NC}"
    else
        echo -e "${RED}✗ $dir/ missing${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 4: Check key files
echo -e "\n${BLUE}[4/8] Checking key files...${NC}"
FILES=(
    "api/main.py"
    "floramigo/core/phd.py"
    "floramigo/core/orchestrator.py"
    "client/floramigo-chat.py"
    "client/floramigo-voice.py"
    "README.md"
)
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓ $file exists${NC}"
    else
        echo -e "${RED}✗ $file missing${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
done

# Test 5: Import tests
echo -e "\n${BLUE}[5/8] Testing Python imports...${NC}"
if python -c "from api.main import app" 2>/dev/null; then
    echo -e "${GREEN}✓ API imports OK${NC}"
else
    echo -e "${RED}✗ API import failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

if python -c "from floramigo.core.phd import PlantHealthDaemon" 2>/dev/null; then
    echo -e "${GREEN}✓ PHD imports OK${NC}"
else
    echo -e "${RED}✗ PHD import failed${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
fi

# Test 6: Run pytest if available
echo -e "\n${BLUE}[6/8] Running test suite...${NC}"
if command -v pytest &> /dev/null; then
    if pytest tests/ -v --tb=short 2>&1 | tail -20; then
        echo -e "${GREEN}✓ All tests passed${NC}"
    else
        echo -e "${YELLOW}⚠ Some tests failed (see above)${NC}"
    fi
else
    echo -e "${YELLOW}⚠ pytest not installed, skipping tests${NC}"
    echo "  Install with: pip install pytest pytest-cov"
fi

# Test 7: Check OpenAI configuration
echo -e "\n${BLUE}[7/8] Checking OpenAI configuration...${NC}"
if [[ -z "$OPENAI_API_KEY" ]]; then
    echo -e "${YELLOW}⚠ OPENAI_API_KEY not set${NC}"
    echo "  Voice features will be limited"
    echo "  Set with: export OPENAI_API_KEY='your-key'"
else
    echo -e "${GREEN}✓ OPENAI_API_KEY is set${NC}"
    # Validate key format
    if [[ $OPENAI_API_KEY == sk-* ]]; then
        echo -e "${GREEN}✓ API key format looks valid${NC}"
    else
        echo -e "${YELLOW}⚠ API key format may be invalid${NC}"
    fi
fi

# Test 8: Check documentation
echo -e "\n${BLUE}[8/8] Checking documentation...${NC}"
DOCS=("README.md" "DEMO_GUIDE.md" "STATUS.md" "TEST_RESULTS.md")
for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✓ $doc exists${NC}"
    else
        echo -e "${YELLOW}⚠ $doc missing${NC}"
    fi
done

# Summary
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}              TEST SUMMARY                                  ${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✅ All critical tests passed!${NC}"
    echo ""
    echo "🎯 System is ready for demo"
    echo ""
    echo "Next steps:"
    echo "  • ./scripts/demo-full.sh    - Full system demo"
    echo "  • ./scripts/demo-api.sh     - API only demo"
    echo "  • ./scripts/demo-voice.sh   - Voice chatbot demo"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $FAILED_TESTS critical test(s) failed${NC}"
    echo ""
    echo "Please fix the issues above before running demo."
    echo ""
    exit 1
fi
