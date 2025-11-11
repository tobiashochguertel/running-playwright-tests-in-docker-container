# Playwright Docker Test Container (Python + uv)

A production-ready Docker container for running Playwright tests with Python 3.13, optimized for **flexibility**, **performance**, and **developer experience**. Built with [uv](https://github.com/astral-sh/uv) for fast dependency management.

## 🎯 Features

- **🚀 Fast Builds**: Multi-stage Docker build with optimized layer caching
- **🌐 Browser Flexibility**: Choose Firefox (default), Chromium, WebKit, or all browsers via build args
- **🐍 Modern Python**: Python 3.13 managed by uv (configurable version)
- **🎨 Configurable Display**: Xvfb with customizable resolution and display number
- **📊 Test Customization**: Control pytest verbosity and traceback style via environment variables
- **🎭 Headless Ready**: Xvfb for headless browser testing (ARM64 compatible)
- **📦 Volume Support**: Mount tests and results directories for easy development
- **🔧 Developer Friendly**: go-task automation, docker-compose profiles, detailed diagnostics
- **🚫 Accessibility**: NO_COLORS support for terminals that don't support ANSI colors
- **⚡ Performance**: Bash builtins instead of external commands, conditional UV cache refresh

---

## 📋 Table of Contents

- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Build Arguments](#-build-arguments)
- [Environment Variables](#-environment-variables)
- [Browser Variants](#-browser-variants)
- [Using go-task](#-using-go-task-recommended)
- [Using docker-compose](#-using-docker-compose)
- [Using Docker CLI](#-using-docker-cli)
- [Using Makefile](#-using-makefile-legacy)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [CI/CD Integration](#-cicd-integration)

---

## 📋 Prerequisites

- Docker & Docker Compose installed
- **Optional**: [go-task](https://taskfile.dev/) for task automation (`brew install go-task`)
- **Optional**: `make` for legacy commands (`brew install make`)
- macOS/Linux/WSL2 with bash or zsh

> **Note:** You do NOT need Python, `uv`, or Playwright installed locally—everything runs in Docker!

---

## 🚀 Quick Start

### Option 1: go-task (Recommended)

```bash
# Install go-task (if not already installed)
brew install go-task  # macOS
# or: https://taskfile.dev/installation/

# Navigate to example directory
cd running-playwright-tests-in-docker-container/examples/python-uv-3.13

# List all available tasks
task --list

# Build and run tests with Firefox (default)
task test:firefox

# Build and test all browser variants
task test:all
```

### Option 2: docker-compose

```bash
# Build and run with Firefox (default)
docker-compose up

# Build with Chromium
BROWSER=chromium docker-compose build
docker-compose up

# Run with custom environment
docker-compose run --rm -e PYTEST_VERBOSE=-vvv playwright
```

### Option 3: Docker CLI

```bash
# Build Firefox variant
docker build --build-arg BROWSER=firefox -t playwright:firefox .

# Run tests
docker run --rm \
  -v "$(pwd)/test-results:/app/test-results" \
  -v "$(pwd)/htmlreport:/app/htmlreport" \
  playwright:firefox
```

### Option 4: Makefile (Legacy)

```bash
# Build and test
make build
make test

# View HTML report
make report
```

---

## 🏗️ Build Arguments

Configure the Docker image at build time:

| Argument           | Default  | Options                          | Description                        |
| ------------------ | -------- | -------------------------------- | ---------------------------------- |
| `PYTHON_VERSION`   | `3.13`   | Any valid Python version         | Python version to install via uv   |
| `BROWSER`          | `firefox`| `firefox`, `chromium`, `webkit`, `all` | Browser(s) to install        |
| `UV_CACHE_REFRESH` | `false`  | `true`, `false`                  | Force uv to refresh dependency cache |

### Examples

```bash
# Build with Python 3.12 and Chromium
docker build \
  --build-arg PYTHON_VERSION=3.12 \
  --build-arg BROWSER=chromium \
  -t playwright:custom .

# Build with all browsers
docker build --build-arg BROWSER=all -t playwright:all .

# Force dependency refresh
task build:refresh
```

---

## ⚙️ Environment Variables

Configure runtime behavior with environment variables:

### Display Configuration

| Variable          | Default         | Description                           |
| ----------------- | --------------- | ------------------------------------- |
| `DISPLAY`         | `:99`           | X11 display number for Xvfb           |
| `XVFB_RESOLUTION` | `1280x1024x24`  | Xvfb screen resolution (WxHxD format) |

### Pytest Configuration

| Variable             | Default | Options                    | Description                    |
| -------------------- | ------- | -------------------------- | ------------------------------ |
| `PYTEST_VERBOSE`     | `-vv`   | `-v`, `-vv`, `-vvv`, etc.  | Pytest verbosity level         |
| `PYTEST_TRACEBACK`   | `long`  | `short`, `long`, `native`  | Traceback style for failures   |

### Browser Configuration

| Variable              | Default  | Options                           | Description                |
| --------------------- | -------- | --------------------------------- | -------------------------- |
| `BROWSER`             | `firefox`| `firefox`, `chromium`, `webkit`   | Browser to use (if `all` built) |
| `PLAYWRIGHT_HEADLESS` | `true`   | `true`, `false`                   | Run browser in headless mode |

### Output Configuration

| Variable    | Default | Options            | Description                      |
| ----------- | ------- | ------------------ | -------------------------------- |
| `NO_COLORS` | `0`     | `0`, `1`, `false`, `true` | Disable ANSI colors in output |

### Examples

```bash
# Extra verbose with no colors
docker-compose run --rm \
  -e PYTEST_VERBOSE=-vvv \
  -e NO_COLORS=1 \
  playwright

# Custom display configuration
docker-compose run --rm \
  -e DISPLAY=:100 \
  -e XVFB_RESOLUTION=1920x1080x24 \
  playwright
```

---

## � Project Structure

```text
python-uv-3.13/
├── Dockerfile              # Multi-stage Docker build (4 stages)
├── entrypoint.sh           # Container entrypoint (bash builtins, configurable)
├── pyproject.toml          # Python dependencies (uv format)
├── docker-compose.yml      # Docker Compose with service profiles
├── Taskfile.yml            # go-task automation (27 tasks)
├── Makefile                # Legacy commands
├── pytest.ini              # Pytest configuration
├── tests/                  # Test files
│   ├── conftest.py         # Pytest fixtures
│   ├── conftest_function_scope.py  # Function-scoped fixtures
│   ├── test_google.py      # Example test (google.de)
│   └── test_github.py      # Example test (github.com)
├── test-results/           # Pytest JSON results (volume mount)
└── htmlreport/             # HTML test reports (volume mount)
```

---

## 🔧 Multi-Stage Build Architecture

The `Dockerfile` uses a 4-stage multi-stage build for optimal caching:

1. **base-deps** (`FROM ubuntu:24.04`): Install system dependencies (curl, Xvfb, etc.)
2. **uv-installer**: Install uv and Python 3.13 via `uv python install`
3. **dependencies**: Install Python dependencies and Playwright browsers
4. **runtime**: Final lightweight image with entrypoint

### Key Points

- **No Python on your system**: Everything runs in the container
- **Headless Mode**: Xvfb provides virtual display (no interruptions)
- **Volume Mounts**: Test files mounted as read-only for live editing
- **Artifact Preservation**: Test results and HTML reports accessible from host
- **PATH Persistence**: uv and venv binaries in both interactive and non-interactive shells

---

## 🌐 Browser Variants

### Firefox (Default) - ARM64 Recommended ✅

Best ARM64 compatibility, recommended for most use cases.

```bash
# go-task
task build:firefox
task run:firefox

# docker-compose
BROWSER=firefox docker-compose build
docker-compose up

# Docker CLI
docker build --build-arg BROWSER=firefox -t playwright:firefox .
docker run --rm playwright:firefox
```

### Chromium

Google Chrome's open-source foundation.

```bash
# go-task
task build:chromium
task run:chromium

# docker-compose
docker-compose --profile chromium up

# Docker CLI
docker build --build-arg BROWSER=chromium -t playwright:chromium .
docker run --rm playwright:chromium
```

### WebKit

Safari's rendering engine.

```bash
# go-task
task build:webkit
task run:webkit

# docker-compose
docker-compose --profile webkit up

# Docker CLI
docker build --build-arg BROWSER=webkit -t playwright:webkit .
docker run --rm playwright:webkit
```

### All Browsers

Install all three browsers (larger image size: ~2.5GB vs ~1.5GB for single).

```bash
# go-task
task build:all-browsers
BROWSER=chromium task run:all  # Specify browser at runtime

# docker-compose
docker-compose --profile all up

# Docker CLI
docker build --build-arg BROWSER=all -t playwright:all .
docker run --rm -e BROWSER=chromium playwright:all
```

---

## 🔧 Using go-task (Recommended)

[go-task](https://taskfile.dev/) provides convenient automation for common workflows.

### Installation

```bash
# macOS
brew install go-task

# Linux
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# Windows
choco install go-task

# Or download binary from: https://taskfile.dev/installation/
```

### Available Tasks (27 total)

```bash
# List all tasks
task --list

# Build tasks
task build:firefox          # Build Firefox variant
task build:chromium         # Build Chromium variant
task build:webkit           # Build WebKit variant
task build:all-browsers     # Build all-in-one image
task build:all              # Build all variants
task build:refresh          # Build with UV cache refresh

# Run tasks (auto-build if needed)
task run:firefox            # Run Firefox tests
task run:chromium           # Run Chromium tests
task run:webkit             # Run WebKit tests
task run:all                # Run all variants sequentially

# Test tasks (build + run)
task test:firefox           # Build and test Firefox
task test:chromium          # Build and test Chromium
task test:webkit            # Build and test WebKit
task test:all               # Build and test all variants

# Custom environment tasks
task test:verbose           # Run with -vvv output
task test:no-colors         # Run with NO_COLORS=1
task test:custom-display    # Run with custom display settings

# Development tasks
task shell:firefox          # Interactive bash shell (Firefox)
task shell:chromium         # Interactive bash shell (Chromium)
task inspect BROWSER=firefox # Show browser installation details

# Cleanup tasks
task clean                  # Remove built images
task clean:reports          # Remove test results/reports
task clean:all              # Remove images + reports

# Information tasks
task list-images            # List all built images
task size                   # Show image sizes
task help                   # Show detailed help
```

### Examples

```bash
# Quick test cycle
task test:firefox

# Build all variants and test
task build:all
task run:all

# Development workflow
task shell:firefox
# Inside container: .venv/bin/pytest tests/test_google.py

# Clean up everything
task clean:all
```

---

## 🐳 Using docker-compose

### Basic Commands

```bash
# Build and run default (Firefox)
docker-compose up

# Build specific variant
BROWSER=chromium docker-compose build

# Run with custom environment
docker-compose run --rm -e PYTEST_VERBOSE=-vvv playwright

# Use specific browser profile
docker-compose --profile chromium up
docker-compose --profile webkit up
docker-compose --profile all up
```

### Service Profiles

The docker-compose.yml includes profiles for different browser variants:

```bash
# Default (no profile): Firefox
docker-compose up

# Chromium profile
docker-compose --profile chromium up

# WebKit profile
docker-compose --profile webkit up

# All browsers profile
docker-compose --profile all up
```

### Environment File (.env)

Create a `.env` file for persistent configuration:

```bash
# .env file
PYTHON_VERSION=3.13
BROWSER=firefox
UV_CACHE_REFRESH=false

# Runtime configuration
PYTEST_VERBOSE=-vv
PYTEST_TRACEBACK=long
NO_COLORS=0
DISPLAY=:99
XVFB_RESOLUTION=1280x1024x24
PLAYWRIGHT_HEADLESS=true
```

Then simply run:

```bash
docker-compose up
```

---

## 🛠️ Using Docker CLI

### Build

```bash
# Basic build
docker build -t playwright:firefox .

# With build arguments
docker build \
  --build-arg PYTHON_VERSION=3.13 \
  --build-arg BROWSER=chromium \
  --build-arg UV_CACHE_REFRESH=false \
  -t playwright:chromium .

# Multiple tags
docker build \
  --build-arg BROWSER=firefox \
  -t playwright:firefox \
  -t playwright:latest \
  -t playwright:firefox-py3.13 \
  .
```

### Run

```bash
# Basic run
docker run --rm playwright:firefox

# With volume mounts
docker run --rm \
  -v "$(pwd)/test-results:/app/test-results" \
  -v "$(pwd)/htmlreport:/app/htmlreport" \
  playwright:firefox

# With environment variables
docker run --rm \
  -e PYTEST_VERBOSE=-vvv \
  -e PYTEST_TRACEBACK=long \
  -e NO_COLORS=0 \
  playwright:firefox

# Override pytest command
docker run --rm playwright:firefox tests/test_google.py
docker run --rm playwright:firefox -vv --tb=short tests/

# Interactive shell
docker run --rm -it --entrypoint /bin/bash playwright:firefox
```

---

## 📚 Using Makefile (Legacy)

The Makefile provides backward compatibility with the original commands:

```bash
make help               # Show all available commands
make build              # Build Docker image (Firefox)
make test               # Run all tests (headless)
make test-verbose       # Run with verbose output
make test-single        # Run specific test file
make report             # Generate & open HTML report
make shell              # Open interactive shell in container
make clean              # Remove containers & cache
```

### Examples

```bash
# Run all tests
make test

# Run with verbose output
make test-verbose

# Run specific test file
make test-single FILE=tests/test_google.py

# Open interactive shell
make shell
```

**Note:** Makefile uses Firefox browser only. For other browsers, use go-task or docker-compose.

---

## 🧪 Test Examples

### test_google.py

Tests the Google homepage (google.de):

- ✅ Homepage loads successfully
- ✅ Search box is visible
- ✅ Google logo is displayed
- ✅ Footer links are present

### test_github.py

Tests the GitHub homepage:

- ✅ Homepage loads successfully
- ✅ Navigation menu is visible
- ✅ Search box is available
- ✅ GitHub logo is displayed
- ✅ Sign in button is visible
- ✅ Footer is rendered

---

## 📊 Configuration Details

### `pyproject.toml`

Defines project metadata and dependencies:

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "playwright>=1.48.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-html>=4.1.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
addopts = "-v --tb=short --html=htmlreport/report.html"
```

### `docker-compose.yml`

Orchestrates the container with:

- **Build args**: `PYTHON_VERSION`, `BROWSER`, `UV_CACHE_REFRESH`
- **Environment variables**: All 8+ configurable options
- **Service profiles**: firefox (default), chromium, webkit, all
- **Volumes**: Mount tests (ro), test-results, htmlreport

### `conftest.py`

Provides pytest fixtures for async browser testing:

- **browser fixture**: Browser instance (session-scoped, configurable via $BROWSER)
- **context fixture**: Browser context with 1280x720 viewport
- **page fixture**: New page for each test (function-scoped)

---

## 🎨 Customization

### Custom pytest Configuration

Edit `pyproject.toml` to customize pytest behavior:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
# Customize output format
addopts = """
  -v                             # Verbose output
  --tb=long                      # Long traceback format
  --strict-markers               # Strict marker checking
  --html=htmlreport/report.html  # HTML report
  --self-contained-html          # Embed assets in HTML
  --maxfail=3                    # Stop after 3 failures
"""
```

### Custom Browsers

Modify `tests/conftest.py` to use different browsers:

```python
import os
import pytest
from playwright.async_api import async_playwright

@pytest.fixture(scope="session")
async def browser():
    browser_name = os.environ.get("BROWSER", "firefox")
    async with async_playwright() as p:
        if browser_name == "chromium":
            browser = await p.chromium.launch(headless=True)
        elif browser_name == "webkit":
            browser = await p.webkit.launch(headless=True)
        else:  # firefox
            browser = await p.firefox.launch(headless=True)

        yield browser
        await browser.close()
```

### Custom Xvfb Settings

Override in docker-compose.yml or runtime:

```yaml
environment:
  DISPLAY: ":99"
  XVFB_RESOLUTION: "1920x1080x24"  # Full HD
```

Or via Docker CLI:

```bash
docker run --rm \
  -e DISPLAY=:99 \
  -e XVFB_RESOLUTION=1920x1080x24 \
  playwright:firefox
```

### Custom entrypoint

Override the entrypoint for debugging:

```bash
# Skip entrypoint, use bash
docker run --rm -it --entrypoint /bin/bash playwright:firefox

# Inside container:
Xvfb :99 -screen 0 1280x1024x24 &
export DISPLAY=:99
.venv/bin/pytest tests/
```

---

## 🔬 Development

### Interactive Development

```bash
# Open interactive shell with go-task
task shell:firefox

# Or with docker-compose
docker-compose run --rm --entrypoint /bin/bash playwright

# Inside container
.venv/bin/pytest tests/test_google.py -vv
.venv/bin/pytest tests/ --lf  # Run last failed
.venv/bin/pytest tests/ -k "github"  # Run tests matching "github"
```

### Adding Dependencies

1. Edit `pyproject.toml`:

```toml
[project]
dependencies = [
    "playwright>=1.48.0",
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-html>=4.1.0",
    "requests>=2.31.0",  # Add new dependency
]
```

2. Rebuild image:

```bash
task build:firefox
# Or
docker-compose build
```

### Debugging Tests

```bash
# Run with pytest debugger
docker run --rm -it playwright:firefox tests/test_google.py --pdb

# Run with verbose output and full tracebacks
docker run --rm -e PYTEST_VERBOSE=-vvv -e PYTEST_TRACEBACK=long playwright:firefox

# Use go-task verbose preset
task test:verbose
```

### Checking Environment

```bash
# Inside container, check Python environment
task shell:firefox

# Then run:
which python
python --version
uv --version
playwright --version
pytest --version

# Check browser installations
task inspect BROWSER=firefox
# Or manually:
ls -la /root/.cache/ms-playwright/

# Check environment variables
env | grep -E 'DISPLAY|XVFB|PYTEST|BROWSER'
```

---

## 📤 Output & Artifacts

### Test Results

- **Location**: `test-results/` directory
- **Contents**: Screenshots, traces, videos (if configured)
- **Mounted as**: Docker volume from host

### HTML Report

- **Location**: `htmlreport/report.html`
- **Generated by**: pytest-html plugin
- **Self-contained**: Embeds CSS/JS for offline viewing

### Viewing Reports

```bash
# macOS
open htmlreport/report.html

# Linux
xdg-open htmlreport/report.html

# Windows
start htmlreport/report.html

# Or use Python HTTP server
cd htmlreport && python -m http.server 8000
# Then open: http://localhost:8000/report.html
```

### CI/CD Artifacts

Configure your CI system to upload test results:

```yaml
# GitHub Actions
- name: Upload Test Results
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: playwright-results
    path: |
      test-results/
      htmlreport/
```

---

## 🧪 Testing Your Own Websites

### For Public Websites

Edit test files and change the URL:

```python
# tests/test_mysite.py
import pytest

@pytest.mark.asyncio
async def test_homepage(page):
    await page.goto("https://example.com", wait_until="networkidle")
    assert await page.title() == "Example Domain"
```

### For Local Apps

Use `host.docker.internal` to access your Mac/Windows localhost:

```python
# Test local app running on port 3000
await page.goto("http://host.docker.internal:3000", wait_until="networkidle")
```

Or set via environment variable in `docker-compose.yml`:

```yaml
environment:
  TEST_BASE_URL: http://host.docker.internal:3000
```

Then in your tests:

```python
import os

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:3000")

@pytest.mark.asyncio
async def test_homepage(page):
    await page.goto(BASE_URL, wait_until="networkidle")
```

### For Docker Compose Networks

If your app runs in a Docker Compose network:

```yaml
# docker-compose.yml
services:
  playwright:
    # ... playwright config ...
    networks:
      - app-network

  myapp:
    # ... your app config ...
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

Then reference by service name:

```python
await page.goto("http://myapp:3000", wait_until="networkidle")
```

---

## 🐛 Troubleshooting

### Browser Installation Issues

**Issue**: "Browser executable not found" or "chromium not found"

**Cause**: Playwright browser not installed or BROWSER env var mismatch.

**Solutions**:

```bash
# 1. Verify BROWSER environment variable
task inspect BROWSER=firefox

# 2. Rebuild with correct browser
task build:chromium

# 3. Check browser installation in container
task shell:firefox
ls -la /root/.cache/ms-playwright/

# 4. Manually install browser
docker run --rm -it --entrypoint /bin/bash playwright:firefox
playwright install firefox
```

### Xvfb Display Issues

**Issue**: "Cannot open display :99" or "Xvfb not starting"

**Cause**: Display server conflicts or incorrect configuration.

**Solutions**:

```bash
# 1. Check Xvfb is running (inside container)
ps aux | grep Xvfb

# 2. Use custom display number
docker run --rm -e DISPLAY=:100 playwright:firefox

# 3. Check for port conflicts
task test:custom-display

# 4. Restart container
docker-compose down && docker-compose up
```

### Permission Denied on Volumes

**Issue**: "Permission denied" writing to test-results/ or htmlreport/

**Cause**: Docker volume permissions mismatch.

**Solutions**:

```bash
# 1. Make directories writable
chmod -R 777 test-results htmlreport

# 2. Or change ownership
sudo chown -R $USER:$USER test-results htmlreport

# 3. Or create with correct permissions
mkdir -p test-results htmlreport
chmod 755 test-results htmlreport
```

### Tests Run But No Output Files

**Issue**: Tests complete successfully but no files in test-results/ or htmlreport/

**Cause**: Volume mount not configured or pytest config issue.

**Solutions**:

```bash
# 1. Verify volume mounts
docker inspect <container_id> | grep -A 10 Mounts

# 2. Check pytest configuration
cat pyproject.toml | grep -A 5 pytest

# 3. Run with explicit output
docker run --rm \
  -v "$(pwd)/test-results:/app/test-results" \
  -v "$(pwd)/htmlreport:/app/htmlreport" \
  playwright:firefox

# 4. Use go-task (volumes pre-configured)
task test:firefox
```

### ModuleNotFoundError: playwright

**Issue**: "ModuleNotFoundError: No module named 'playwright'"

**Cause**: Virtual environment not activated or dependencies not installed.

**Solutions**:

```bash
# 1. Rebuild image (installs dependencies)
task build:firefox

# 2. Verify uv sync completed during build
docker build --progress=plain -t playwright:firefox .

# 3. Inside container, check installation
task shell:firefox
.venv/bin/python -c "import playwright; print(playwright.__version__)"
```

### Colors Not Displaying

**Issue**: Colored output not showing in terminal

**Cause**: Color codes disabled by CI environment or NO_COLORS=1

**Solutions**:

```bash
# Enable colors explicitly
docker run --rm -e NO_COLORS=0 playwright:firefox

# Or use go-task (colors enabled by default)
task test:firefox

# Disable colors if causing issues
task test:no-colors
```

### Build Fails with "uv not found"

**Issue**: Build fails at Stage 3 with "uv: command not found"

**Cause**: PATH not persisted from Stage 2 to Stage 3

**Solutions**:

```bash
# 1. Ensure using latest Dockerfile (includes PATH exports)
git pull

# 2. Clear build cache and rebuild
docker builder prune
task build:refresh

# 3. Verify multi-stage COPY worked
docker build --progress=plain -t playwright:firefox .
# Look for: "COPY --from=uv-installer /root/.local /root/.local"
```

### Tests Slow on ARM64 (Apple Silicon)

**Issue**: Tests run significantly slower on ARM64 machines

**Cause**: Browser binary architecture mismatch (x86_64 emulation)

**Solutions**:

```bash
# 1. Use Firefox (best ARM64 support)
task build:firefox

# 2. Avoid Chromium/WebKit on ARM64 (emulated)
# Use Firefox for local development

# 3. For CI, use amd64 runners (GitHub Actions, GitLab CI)
# GitHub Actions: runs-on: ubuntu-latest (amd64)
# GitLab CI: tags: [amd64]
```

### Network Errors (Page did not navigate)

**Issue**: Tests fail with "Page did not navigate" or timeout errors

**Cause**: Network issue, DNS resolution failure, or site structure changed

**Solutions**:

```bash
# 1. Run with verbose output
task test:verbose

# 2. Test DNS resolution inside container
task shell:firefox
ping -c 3 google.com
curl -I https://google.de

# 3. Increase timeout in tests
# In your test file:
await page.goto("https://example.com", timeout=60000)  # 60 seconds

# 4. Check for proxy or VPN interference
```

---

## � CI/CD Integration

### GitHub Actions (Basic)

```yaml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: docker build -t playwright:firefox .

      - name: Run Tests
        run: |
          docker run --rm \
            -v $PWD/test-results:/app/test-results \
            -v $PWD/htmlreport:/app/htmlreport \
            playwright:firefox

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-results
          path: |
            test-results/
            htmlreport/
```

### GitHub Actions (Matrix Strategy)

```yaml
name: Playwright Tests (Multi-Browser)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [firefox, chromium, webkit]
        python-version: ["3.13", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker Image
        run: |
          docker build \
            --build-arg PYTHON_VERSION=${{ matrix.python-version }} \
            --build-arg BROWSER=${{ matrix.browser }} \
            -t playwright:${{ matrix.browser }}-py${{ matrix.python-version }} \
            .

      - name: Run Tests
        run: |
          docker run --rm \
            -v $PWD/test-results:/app/test-results \
            -v $PWD/htmlreport:/app/htmlreport \
            playwright:${{ matrix.browser }}-py${{ matrix.python-version }}

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: results-${{ matrix.browser }}-py${{ matrix.python-version }}
          path: |
            test-results/
            htmlreport/
```

### GitLab CI

```yaml
stages:
  - test

variables:
  DOCKER_DRIVER: overlay2

test:firefox:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build --build-arg BROWSER=firefox -t playwright:firefox .
    - docker run --rm -v $PWD/test-results:/app/test-results playwright:firefox
  artifacts:
    when: always
    paths:
      - test-results/
      - htmlreport/
    expire_in: 30 days

test:chromium:
  stage: test
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker build --build-arg BROWSER=chromium -t playwright:chromium .
    - docker run --rm -v $PWD/test-results:/app/test-results playwright:chromium
  artifacts:
    when: always
    paths:
      - test-results/
      - htmlreport/
    expire_in: 30 days
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    environment {
        BROWSER = 'firefox'
        PYTHON_VERSION = '3.13'
    }

    stages {
        stage('Build') {
            steps {
                sh '''
                    docker build \
                        --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
                        --build-arg BROWSER=${BROWSER} \
                        -t playwright:${BROWSER} .
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    docker run --rm \
                        -v ${WORKSPACE}/test-results:/app/test-results \
                        -v ${WORKSPACE}/htmlreport:/app/htmlreport \
                        playwright:${BROWSER}
                '''
            }
        }
    }

    post {
        always {
            publishHTML([
                reportDir: 'htmlreport',
                reportFiles: 'report.html',
                reportName: 'Playwright Test Report'
            ])
            archiveArtifacts artifacts: 'test-results/**, htmlreport/**'
        }
    }
}
```

---

## 📚 Further Reading

### Official Documentation

- **Playwright Python**: <https://playwright.dev/python/>
- **uv Package Manager**: <https://docs.astral.sh/uv/>
- **pytest Documentation**: <https://docs.pytest.org/>
- **Docker Multi-Stage Builds**: <https://docs.docker.com/build/building/multi-stage/>
- **go-task**: <https://taskfile.dev/>

### Playwright Resources

- **Playwright Selectors**: <https://playwright.dev/python/docs/selectors>
- **Playwright Best Practices**: <https://playwright.dev/python/docs/best-practices>
- **Playwright CI/CD**: <https://playwright.dev/python/docs/ci>
- **Playwright Trace Viewer**: <https://playwright.dev/python/docs/trace-viewer>

### Docker Resources

- **Dockerfile Best Practices**: <https://docs.docker.com/develop/dev-best-practices/>
- **Docker Compose Profiles**: <https://docs.docker.com/compose/profiles/>
- **Docker Build Arguments**: <https://docs.docker.com/engine/reference/builder/#arg>

### Testing Resources

- **pytest Fixtures**: <https://docs.pytest.org/en/stable/fixture.html>
- **pytest Markers**: <https://docs.pytest.org/en/stable/mark.html>
- **pytest Plugins**: <https://docs.pytest.org/en/stable/plugins.html>

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Test your changes: `task test:all`
4. Commit following [Conventional Commits](https://www.conventionalcommits.org/)
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/running-playwright-tests-in-docker-container.git
cd running-playwright-tests-in-docker-container/examples/python-uv-3.13

# Install go-task (if not already installed)
brew install go-task  # macOS

# Build and test
task test:firefox
```

---

## ✨ Next Steps

1. **Add more tests** to `tests/` for other websites or your app
2. **Customize pytest configuration** in `pyproject.toml` for your needs
3. **Integrate with CI/CD** using GitHub Actions, GitLab CI, or Jenkins
4. **Try parallel execution** with `pytest-xdist` for faster runs
5. **Add screenshots/videos** to HTML reports for better debugging
6. **Experiment with different browsers** (chromium, webkit, all)
7. **Configure custom Xvfb settings** for different screen resolutions
8. **Create custom fixtures** in `conftest.py` for your test needs

---

## 🤝 Need Help?

- Check [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) in the docs folder
- See [BEST_PRACTICES.md](../../docs/BEST_PRACTICES.md) for advanced usage
- Review [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) for system design

---

## 📄 License

This example is part of the `running-playwright-tests-in-docker-container` project.

See the [main repository](../../) for license details.

---

**Last Updated**: January 2025
**Maintained By**: @tobiashochguertel
**Project**: running-playwright-tests-in-docker-container

---

**Ready to run your first test?** Try `task test:firefox` now! 🚀
