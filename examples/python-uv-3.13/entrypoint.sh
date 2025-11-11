#!/bin/bash
set -e

# ============================================================================
# Playwright Test Entrypoint with UV and Diagnostics
# ============================================================================
# This script ensures all commands run through uv's virtual environment
# and provides colorful diagnostic output for debugging
# ============================================================================

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
# MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Print header
echo -e "${CYAN}${BOLD}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║       Playwright Test Container - Environment Check           ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Show Python version
echo -e "${BLUE}🐍 Python Version:${NC}"
.venv/bin/python --version 2>&1 | sed 's/^/   /'
echo ""

# Show uv version
echo -e "${BLUE}📦 uv Version:${NC}"
uv --version 2>&1 | sed 's/^/   /'
echo ""

# Show pytest version
echo -e "${BLUE}🧪 pytest Version:${NC}"
.venv/bin/pytest --version 2>&1 | sed 's/^/   /'
echo ""

# Show Playwright version
echo -e "${BLUE}🎭 Playwright:${NC}"
.venv/bin/python -c "import playwright.sync_api; print('   Playwright installed (sync API available)')" 2>&1 || echo "   ${RED}ERROR: Playwright not installed${NC}"
echo ""

# Check for Chromium browser
echo -e "${BLUE}🌐 Browser Installation Check:${NC}"
if .venv/bin/playwright show-browsers 2>&1 | grep -q "chromium"; then
  echo -e "   ${GREEN}✓ Chromium browser installed${NC}"
else
  echo -e "   ${RED}✗ Chromium browser NOT installed${NC}"
  echo -e "   ${YELLOW}Installing browsers now...${NC}"
  .venv/bin/playwright install chromium --with-deps
fi
echo ""

# Show environment
echo -e "${BLUE}🔧 Environment:${NC}"
echo -e "   VIRTUAL_ENV: ${VIRTUAL_ENV:-${YELLOW}(not set)${NC}}"
echo -e "   PLAYWRIGHT_HEADLESS: ${PLAYWRIGHT_HEADLESS:-${YELLOW}(not set)${NC}}"
echo -e "   Working Directory: $(pwd)"
echo ""

# Check if tests directory exists
if [ -d "/app/tests" ]; then
  test_count=$(find /app/tests -name "test_*.py" -o -name "*_test.py" | wc -l | tr -d ' ')
  echo -e "${GREEN}✓ Tests directory found: ${test_count} test files${NC}"
else
  echo -e "${RED}✗ Tests directory not found at /app/tests${NC}"
  exit 1
fi
echo ""

echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}Starting Xvfb and test execution...${NC}"
echo -e "${CYAN}${BOLD}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Start Xvfb (virtual framebuffer X server) in the background
# Required for Chromium to run in headless mode on ARM64
echo -e "${BLUE}🖥️  Starting Xvfb on display :99...${NC}"
Xvfb :99 -screen 0 1280x1024x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
export DISPLAY=:99

# Wait for Xvfb to be ready
sleep 2
echo -e "${GREEN}✓ Xvfb ready (PID: $XVFB_PID)${NC}"
echo ""

# Execute command directly from venv (not through 'uv run')
# Note: 'uv run' requires module structure, but this is a test-only project
if [ $# -eq 0 ]; then
  .venv/bin/pytest
  EXIT_CODE=$?
else
  # Check if first argument is pytest-related
  if [[ "$1" == "pytest"* ]] || [[ "$1" == "-"* ]]; then
    # Run pytest directly from venv
    .venv/bin/pytest "$@"
    EXIT_CODE=$?
  else
    # For other commands, try to run from venv
    .venv/bin/"$*"
    EXIT_CODE=$?
  fi
fi

# Clean up Xvfb
kill $XVFB_PID 2>/dev/null || true
exit $EXIT_CODE
