# ============================================================================
# Multi-stage Dockerfile for Playwright tests with optimal caching
# ============================================================================
# This Dockerfile uses multi-stage builds to:
# 1. Start with clean Ubuntu 24.04 (no pre-installed Playwright/Python)
# 2. Cache uv installation separately
# 3. Let uv manage Python version (3.13+) via pyproject.toml
# 4. Cache Python dependencies separately from test code
# 5. Install Playwright browsers in dependencies stage for caching
# ============================================================================

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

# Verify installation
RUN curl --version && echo "✓ curl installed"

# ============================================================================
# Stage 2: uv installation
# ============================================================================
# Install uv and let it manage Python version
FROM base-deps AS uv-installer

LABEL stage=uv-installer
LABEL description="uv installer - manages Python version per project"

# Download and install uv as a standalone tool (installs to ~/.local/bin)
# This layer only rebuilds if uv installation script changes
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for subsequent stages
ENV PATH="/root/.local/bin:$PATH"

# Verify uv installation
RUN uv --version && echo "✓ uv installed"

# Let uv install Python 3.13+ (will be determined by pyproject.toml)
# This creates a managed Python installation
WORKDIR /tmp
RUN echo '[project]' > pyproject.toml && \
  echo 'name = "temp"' >> pyproject.toml && \
  echo 'version = "0.1.0"' >> pyproject.toml && \
  echo 'requires-python = ">=3.13"' >> pyproject.toml && \
  uv python install && \
  rm pyproject.toml

# Verify Python installation
RUN uv python list && echo "✓ Python managed by uv"

# ============================================================================
# Stage 3: Project dependencies (venv + Playwright browsers)
# ============================================================================
# Install dependencies and Playwright browsers - heavy caching stage
FROM uv-installer AS dependencies

LABEL stage=dependencies
LABEL description="Dependencies + Playwright browsers - heavily cached"

WORKDIR /app

# Copy only dependency file (pyproject.toml)
# This enables Docker layer caching for dependency installation
COPY pyproject.toml .

# Create virtual environment and install Python dependencies
# Rebuilds only when pyproject.toml changes
ENV PIP_ROOT_USER_ACTION=ignore
RUN echo "📦 Installing Python dependencies..." && \
  uv sync --no-install-project && \
  echo "✓ Python dependencies installed"

# Activate venv for subsequent commands
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"

# Show installed Python version
RUN python --version && echo "✓ Python ready"

# Install Playwright browsers (Chromium) - this is the heavy part
# We do this in dependencies stage so it's cached
RUN echo "🌐 Installing Playwright Chromium browser..." && \
  uv run playwright install chromium --with-deps && \
  echo "✓ Chromium installed"

# Verify browser installation
RUN echo "🔍 Verifying browser installation..." && \
  uv run playwright show-browsers && \
  echo "✓ Browser verification complete"

# ============================================================================
# Stage 4: Final runtime stage
# ============================================================================
# Lightweight final stage - only adds test files
FROM dependencies AS runtime

LABEL description="Final runtime - tests only (dependencies cached)"

WORKDIR /app

# Copy entrypoint script (diagnostic and uv wrapper)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy test files and configuration
# This layer rebuilds when tests change, but dependencies are cached
COPY tests/ /app/tests/
COPY pytest.ini /app/pytest.ini

# Verify tests were copied
RUN echo "📋 Test files:" && \
  find /app/tests -name "*.py" -type f && \
  echo "✓ Tests copied successfully"

# Environment configuration
ENV PLAYWRIGHT_HEADLESS=true
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"
ENV UV_CACHE_DIR=/app/.cache/uv

# Create output directories
RUN mkdir -p /app/test-results /app/htmlreport

# Health check - verify pytest and playwright are accessible
RUN echo "🏥 Health check..." && \
  uv run pytest --version && \
  uv run python -c "import playwright; print(f'Playwright {playwright.__version__}')" && \
  echo "✓ Health check passed"

# Use diagnostic entrypoint that enforces uv execution
ENTRYPOINT ["/app/entrypoint.sh"]

# Default: run all tests with verbose output
# Override with: docker-compose run --rm playwright pytest -vv tests/test_google.py
CMD ["-vv", "--tb=short", "tests/"]
