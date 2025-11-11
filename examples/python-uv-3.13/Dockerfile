# ============================================================================
# Multi-stage Dockerfile for Playwright tests with optimal caching
# ============================================================================
# This Dockerfile uses multi-stage builds to:
# 1. Start with clean Ubuntu 24.04 (no pre-installed Playwright/Python)
# 2. Cache uv installation separately
# 3. Let uv manage Python version (3.13 specifically) via direct installation
# 4. Cache Python dependencies separately from test code
# 5. Install Playwright browsers in dependencies stage for caching
# 6. Support multiple browser variants via build arguments
# ============================================================================

# Build arguments for customization
ARG PYTHON_VERSION=3.13
ARG BROWSER=firefox
ARG UV_CACHE_REFRESH=false

# ============================================================================
# Stage 1: Base system dependencies
# ============================================================================
# Clean Ubuntu base with only curl and build-essential
FROM ubuntu:24.04 AS base-deps

LABEL stage=base-deps
LABEL description="Base Ubuntu with minimal system packages"

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install only essential system dependencies
# Let uv manage Python installation
# DL3008: (version pinning not practical for system packages)
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  build-essential \
  && rm -rf /var/lib/apt/lists/*

# Verify installation with version output
RUN echo "==> curl version:" && \
  curl --version && \
  echo "✓ curl installed"

# ============================================================================
# Stage 2: uv installation and Python setup
# ============================================================================
# Install uv and specific Python version
FROM base-deps AS uv-installer

LABEL stage=uv-installer
LABEL description="uv installer - manages Python version"

# Pass build args to this stage
ARG PYTHON_VERSION

# Download and install uv as a standalone tool (installs to ~/.local/bin)
# This layer only rebuilds if uv installation script changes
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for subsequent stages and persist it in shell rc files
ENV PATH="/root/.local/bin:$PATH"

# Persist PATH in shell rc files for interactive sessions (docker exec, etc.)
# This ensures uv is available in any shell session, not just during build
RUN echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc && \
  echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.profile && \
  echo '# uv (Python package manager)' >> /root/.bashrc

# Verify uv installation and show version
RUN echo "==> uv version:" && \
  uv --version && \
  echo "✓ uv installed"

# Install specific Python version using uv's direct installation command
# This is more reliable than using a dummy pyproject.toml
# See: https://docs.astral.sh/uv/guides/install-python/#installing-a-specific-version
RUN echo "==> Installing Python ${PYTHON_VERSION}..." && \
  uv python install "${PYTHON_VERSION}" && \
  echo "✓ Python ${PYTHON_VERSION} installation complete"

# Verify Python installation and show installed versions
RUN echo "==> Installed Python versions:" && \
  uv python list && \
  echo "✓ Python managed by uv"

# ============================================================================
# Stage 3: Project dependencies (venv + Playwright browsers)
# ============================================================================
# Install dependencies and Playwright browsers - heavy caching stage
FROM uv-installer AS dependencies

LABEL stage=dependencies
LABEL description="Dependencies + Playwright browsers - heavily cached"

# Pass build args to this stage
ARG BROWSER
ARG UV_CACHE_REFRESH

WORKDIR /app

# Copy only dependency file (pyproject.toml)
# This enables Docker layer caching for dependency installation
# TODO: Consider splitting dependencies into separate file for better caching
# when only pytest/ruff/mypy config changes
COPY pyproject.toml .

# Create virtual environment and install Python dependencies
# Use --refresh flag if UV_CACHE_REFRESH=true to refresh existing venv
# This allows build cache reuse with dependency updates
ENV PIP_ROOT_USER_ACTION=ignore
RUN echo "📦 Installing Python dependencies..." && \
  if [ "${UV_CACHE_REFRESH}" = "true" ]; then \
  echo "  (using --refresh to update existing cache)" && \
  uv sync --no-install-project --refresh; \
  else \
  uv sync --no-install-project; \
  fi && \
  echo "✓ Python dependencies installed"

# Activate venv for subsequent commands and persist in shell rc files
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"

# Persist venv PATH in shell rc files for interactive sessions
RUN echo 'export VIRTUAL_ENV="/app/.venv"' >> /root/.bashrc && \
  echo 'export PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"' >> /root/.bashrc && \
  echo '# Python virtual environment' >> /root/.bashrc

# Show installed Python version with full details
RUN echo "==> Python version details:" && \
  python --version && \
  echo "==> Python executable location:" && \
  command -v python && \
  echo "✓ Python ready"

# Install Playwright browsers based on build argument
# Support: firefox, chromium, webkit, or "all" for all browsers
# Default: firefox (better ARM64/Apple Silicon compatibility)
RUN echo "🎭 Installing Playwright browser(s): ${BROWSER}..." && \
  if [ "${BROWSER}" = "all" ]; then \
  echo "  Installing all browsers (firefox, chromium, webkit)..." && \
  .venv/bin/playwright install --with-deps; \
  else \
  echo "  Installing ${BROWSER}..." && \
  .venv/bin/playwright install "${BROWSER}" --with-deps; \
  fi && \
  echo "✓ Browser installation complete"

# Verify browser installation
RUN echo "==> Installed browsers:" && \
  .venv/bin/playwright install --list && \
  echo "✓ Browser verification complete"

# ============================================================================
# Stage 4: Final runtime stage
# ============================================================================
# Lightweight final stage - only adds test files
FROM dependencies AS runtime

LABEL description="Final runtime - tests only (dependencies cached)"

# Pass build args to final stage for runtime configuration
ARG BROWSER

WORKDIR /app

# Copy entrypoint script (diagnostic and uv wrapper)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy test files
# This layer rebuilds when tests change, but dependencies are cached
# Note: pytest config is in pyproject.toml (already copied in dependencies stage)
# NOTE: For development, mount tests as volume instead: -v ./tests:/app/tests:ro
COPY tests/ /app/tests/

# Verify tests were copied
RUN echo "📋 Test files:" && \
  find /app/tests -name "*.py" -type f && \
  echo "✓ Tests copied successfully"

# Environment configuration
# These can be overridden via docker-compose.yml or docker run -e
ENV PLAYWRIGHT_HEADLESS=true
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"
ENV UV_CACHE_DIR=/app/.cache/uv

# Xvfb configuration (can be overridden)
ENV DISPLAY=:99
ENV XVFB_RESOLUTION=1280x1024x24

# Pytest configuration (can be overridden)
ENV PYTEST_VERBOSE=-vv
ENV PYTEST_TRACEBACK=long

# Browser configuration (matches build arg)
ENV BROWSER=${BROWSER}

# Create output directories
# These will be mounted as volumes in docker-compose.yml
RUN mkdir -p /app/test-results /app/htmlreport

# Declare volumes for documentation
# These directories are intended to be mounted from host
VOLUME ["/app/tests", "/app/test-results", "/app/htmlreport"]

# Health check - verify pytest and playwright are accessible
# Note: Use .venv/bin directly since project doesn't have module structure
RUN echo "🏥 Health check..." && \
  .venv/bin/pytest --version && \
  .venv/bin/python -c "import playwright.sync_api; print('Playwright installed')" && \
  echo "✓ Health check passed"

# Use diagnostic entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default: run all tests with configurable verbosity
# Reads PYTEST_VERBOSE and PYTEST_TRACEBACK env vars
# Override with: docker-compose run --rm playwright pytest -vv tests/test_google.py
CMD ["tests/"]
