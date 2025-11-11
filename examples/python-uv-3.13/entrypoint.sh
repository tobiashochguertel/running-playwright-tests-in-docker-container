#!/bin/bash
set -e

# ============================================================================
# Playwright Test Entrypoint with UV and Diagnostics
# ============================================================================
# This script ensures all commands run through uv's virtual environment
# and provides colorful diagnostic output for debugging
#
# Environment Variables:
#   NO_COLORS         - Set to "1" or "true" to disable color output
#   BROWSER           - Browser to use (firefox, chromium, webkit)
#   DISPLAY           - X11 display number (default: :99)
#   XVFB_RESOLUTION   - Xvfb screen resolution (default: 1280x1024x24)
#   PYTEST_VERBOSE    - Pytest verbosity flag (default: -vv)
#   PYTEST_TRACEBACK  - Pytest traceback style (default: long)
# ============================================================================

# Initialize exit code
EXIT_CODE=0

# ============================================================================
# Color Configuration (using bash builtins for performance)
# ============================================================================
if [[ "${NO_COLORS:-0}" == "1" ]] || [[ "${NO_COLORS:-false}" == "true" ]]; then
  # Disable colors
  RED=''
  GREEN=''
  YELLOW=''
  BLUE=''
  CYAN=''
  BOLD=''
  NC=''
else
  # ANSI color codes (bash builtins)
  RED=$'\033[0;31m'
  GREEN=$'\033[0;32m'
  YELLOW=$'\033[1;33m'
  BLUE=$'\033[0;34m'
  CYAN=$'\033[0;36m'
  BOLD=$'\033[1m'
  NC=$'\033[0m' # No Color
fi

# ============================================================================
# Helper Functions (using bash builtins)
# ============================================================================

# Print with indentation (bash builtin printf)
print_indented() {
  local text="$1"
  printf "   %s\n" "$text"
}

# Print header
print_header() {
  printf "%s%s╔════════════════════════════════════════════════════════════════╗%s\n" "$CYAN" "$BOLD" "$NC"
  printf "%s%s║       Playwright Test Container - Environment Check           ║%s\n" "$CYAN" "$BOLD" "$NC"
  printf "%s%s╚════════════════════════════════════════════════════════════════╝%s\n" "$CYAN" "$BOLD" "$NC"
  printf "\n"
}

# Print section header
print_section() {
  local title="$1"
  printf "%s%s%s\n" "$BLUE" "$title" "$NC"
}

# ============================================================================
# Diagnostic Output
# ============================================================================
print_header

# Show Python version
print_section "🐍 Python Version:"
.venv/bin/python --version 2>&1 | while IFS= read -r line; do print_indented "$line"; done
printf "\n"

# Show uv version
print_section "📦 uv Version:"
uv --version 2>&1 | while IFS= read -r line; do print_indented "$line"; done
printf "\n"

# Show pytest version
print_section "🧪 pytest Version:"
.venv/bin/pytest --version 2>&1 | while IFS= read -r line; do print_indented "$line"; done
printf "\n"

# Show Playwright version
print_section "🎭 Playwright:"
.venv/bin/python -c "import playwright.sync_api; print('   Playwright installed (sync API available)')" 2>&1 || printf "   %s%sERROR: Playwright not installed%s\n" "$RED" "$BOLD" "$NC"
printf "\n"

# Check for browser (configurable via BROWSER env var)
BROWSER="${BROWSER:-firefox}"
print_section "🌐 Browser Installation Check (${BROWSER}):"
if .venv/bin/playwright install --list 2>&1 | grep -q "$BROWSER"; then
  printf "   %s✓ %s browser installed%s\n" "$GREEN" "$BROWSER" "$NC"
else
  printf "   %s✗ %s browser NOT installed%s\n" "$RED" "$BROWSER" "$NC"
  printf "   %sInstalling browser now...%s\n" "$YELLOW" "$NC"
  .venv/bin/playwright install "$BROWSER" --with-deps
fi
printf "\n"

# Show environment
print_section "🔧 Environment:"
print_indented "VIRTUAL_ENV: ${VIRTUAL_ENV:-(not set)}"
print_indented "PLAYWRIGHT_HEADLESS: ${PLAYWRIGHT_HEADLESS:-(not set)}"
print_indented "BROWSER: ${BROWSER}"
print_indented "DISPLAY: ${DISPLAY:-:99}"
print_indented "XVFB_RESOLUTION: ${XVFB_RESOLUTION:-1280x1024x24}"
print_indented "Working Directory: $(pwd)"
printf "\n"

# Check if tests directory exists
if [[ -d "/app/tests" ]]; then
  test_count=0
  while IFS= read -r -d '' _; do
    ((test_count++))
  done < <(find /app/tests \( -name "test_*.py" -o -name "*_test.py" \) -print0 2>/dev/null)
  printf "%s✓ Tests directory found: %d test files%s\n" "$GREEN" "$test_count" "$NC"
else
  printf "%s✗ Tests directory not found at /app/tests%s\n" "$RED" "$NC"
  exit 1
fi
printf "\n"

printf "%s%s════════════════════════════════════════════════════════════════%s\n" "$CYAN" "$BOLD" "$NC"
printf "%s%sStarting Xvfb and test execution...%s\n" "$GREEN" "$BOLD" "$NC"
printf "%s%s════════════════════════════════════════════════════════════════%s\n" "$CYAN" "$BOLD" "$NC"
printf "\n"

# Start Xvfb (virtual framebuffer X server) in the background
# Required for browsers to run in headless mode
# Configurable via DISPLAY and XVFB_RESOLUTION environment variables
DISPLAY="${DISPLAY:-:99}"
XVFB_RESOLUTION="${XVFB_RESOLUTION:-1280x1024x24}"

printf "%s🖥️  Starting Xvfb on display %s with resolution %s...%s\n" "$BLUE" "$DISPLAY" "$XVFB_RESOLUTION" "$NC"
Xvfb "$DISPLAY" -screen 0 "$XVFB_RESOLUTION" -ac +extension GLX +render -noreset &
XVFB_PID=$!
export DISPLAY

# Wait for Xvfb to be ready using xdpyinfo (more reliable than sleep)
XVFB_TIMEOUT=10
XVFB_ELAPSED=0
while ! xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; do
  if [[ "$XVFB_ELAPSED" -ge "$XVFB_TIMEOUT" ]]; then
    printf "%s✗ Xvfb failed to start within %d seconds%s\n" "$RED" "$XVFB_TIMEOUT" "$NC"
    exit 1
  fi
  sleep 0.5
  ((XVFB_ELAPSED++))
done

printf "%s✓ Xvfb ready (PID: %d)%s\n" "$GREEN" "$XVFB_PID" "$NC"
printf "\n"

# Execute command directly from venv (not through 'uv run')
# Note: 'uv run' requires module structure, but this is a test-only project
# Build pytest command using environment variables for configuration
if [[ $# -eq 0 ]]; then
  # Build default pytest command from environment variables
  PYTEST_CMD=(.venv/bin/pytest)

  # Add verbosity flag if set (e.g., PYTEST_VERBOSE=-vv)
  if [[ -n "${PYTEST_VERBOSE:-}" ]]; then
    PYTEST_CMD+=("$PYTEST_VERBOSE")
  fi

  # Add traceback style if set (e.g., PYTEST_TRACEBACK=long)
  if [[ -n "${PYTEST_TRACEBACK:-}" ]]; then
    PYTEST_CMD+=("--tb=$PYTEST_TRACEBACK")
  fi

  # Add default test directory
  PYTEST_CMD+=(tests/)

  # Execute pytest command
  "${PYTEST_CMD[@]}"
  EXIT_CODE=$?
else
  # Check if first argument is pytest-related
  if [[ "$1" == "pytest"* ]] || [[ "$1" == "-"* ]]; then
    # Run pytest directly from venv with provided arguments
    .venv/bin/pytest "$@"
    EXIT_CODE=$?
  else
    # For other commands, try to run from venv
    .venv/bin/"$*"
    EXIT_CODE=$?
  fi
fi

# Clean up Xvfb (check if PID exists and process is running)
if [[ -n "${XVFB_PID:-}" ]] && kill -0 "$XVFB_PID" 2>/dev/null; then
  kill "$XVFB_PID" 2>/dev/null || true
  printf "%s✓ Xvfb stopped (PID: %d)%s\n" "$GREEN" "$XVFB_PID" "$NC"
fi

exit "$EXIT_CODE"
