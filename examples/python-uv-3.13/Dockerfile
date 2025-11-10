# ============================================================================
# Multi-stage Dockerfile for Playwright tests with optimal caching
# ============================================================================
# This Dockerfile uses multi-stage builds to:
# 1. Cache base dependencies (apt, build tools) separately
# 2. Cache uv installation separately
# 3. Only rebuild project-specific code when source files change
# 4. Supports easy Python version swaps via build args
# ============================================================================

# ============================================================================
# Stage 1: Base system dependencies
# ============================================================================
# Cached layer with system packages and development tools
FROM mcr.microsoft.com/playwright/python:v1.55.0-noble AS base-deps

LABEL stage=base-deps
LABEL description="Base dependencies stage - caches system packages"

# Install system dependencies (apt packages)
# These rarely change, so this layer caches well
# DL3008: (version pinning not practical for system packages)
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  build-essential \
  python3 \
  && rm -rf /var/lib/apt/lists/*

# ============================================================================
# Stage 2: uv installation
# ============================================================================
# Separate stage for uv installation to enable independent caching
FROM base-deps AS uv-installer

LABEL stage=uv-installer
LABEL description="uv installer stage - isolated for independent caching"

# Download and install uv as a standalone tool (installs to ~/.local/bin)
# This layer only rebuilds if uv installation script changes
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN /root/.local/bin/uv python install

# ============================================================================
# Stage 3: Project dependencies (venv creation)
# ============================================================================
# Caches uv venv creation separately from project files
FROM uv-installer AS dependencies

LABEL stage=dependencies
LABEL description="Dependencies stage - creates isolated venv"

WORKDIR /app

# Copy only dependency file (pyproject.toml)
# This enables Docker layer caching for venv creation
COPY pyproject.toml .

# Create virtual environment and install dependencies
# Rebuilds only when pyproject.toml changes
ENV PIP_ROOT_USER_ACTION=ignore
RUN python3 --version
# READ: https://docs.astral.sh/uv/concepts/projects/sync/#partial-installations
# RUN touch README.md && /root/.local/bin/uv sync --refresh --no-install-project && rm README.md
RUN /root/.local/bin/uv sync --refresh --no-install-project

# ============================================================================
# Stage 4: Final application stage
# ============================================================================
# Production image with all dependencies and project code
FROM dependencies AS runtime

LABEL description="Final runtime image with tests and dependencies"

WORKDIR /app

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy test files
# This layer rebuilds when tests change, but not when dependencies change
COPY tests/ /app/tests/

# Set headless mode by default
ENV PLAYWRIGHT_HEADLESS=true

# Activate virtual environment by adding it to PATH
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"
ENV UV_CACHE_DIR=/app/.cache/uv

# Use entrypoint script for flexible argument passing
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["-v", "tests/"]
