# Start from Microsoft's official Playwright image (browsers included)
# Uses Python 3.12+ with Ubuntu 24.04 (noble) for Python 3.13+ support
FROM mcr.microsoft.com/playwright/python:v1.48.0-noble

# Note: This image comes with Python 3.12 pre-installed
# For Python 3.13, use: mcr.microsoft.com/playwright/python:v1.48.0-jammy
# The noble image (Ubuntu 24.04) has better Python 3.13 support

WORKDIR /app

# Install curl for downloading uv standalone
RUN apt-get update && apt-get install -y --no-install-recommends \
  curl \
  build-essential \
  python3-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml .

# Download and install uv as a standalone tool (installs to ~/.local/bin)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies using the installed uv
RUN /root/.local/bin/uv sync --refresh

# Link system-installed playwright to venv so tests can import it
# System Python has playwright pre-installed in base image
# We create a symlink so venv can access it without reinstalling (avoids greenlet compilation)
RUN mkdir -p /app/.venv/lib/python3.12/site-packages && \
  python_site_packages=$(python3 -c "import site; print(site.getsitepackages()[0])") && \
  venv_site_packages="/app/.venv/lib/python3.12/site-packages" && \
  ln -sf "$python_site_packages/playwright" "$venv_site_packages/playwright" && \
  ln -sf "$python_site_packages/playwright-"*.dist-info "$venv_site_packages/" 2>/dev/null || true

# Copy test files and entrypoint script
COPY tests/ /app/tests/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set headless mode by default
ENV PLAYWRIGHT_HEADLESS=true

# Activate virtual environment by adding it to PATH
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:/root/.local/bin:$PATH"
ENV UV_CACHE_DIR=/app/.cache/uv

# Use entrypoint script for flexible argument passing
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["-v", "tests/"]
