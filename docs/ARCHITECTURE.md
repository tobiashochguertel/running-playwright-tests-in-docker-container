# Architecture: Local Dev + Docker Testing

This document explains the architecture and design decisions behind running Playwright tests in Docker containers.

## 🎯 Design Goals

1. **Zero Local Setup**: Developers don't install Python, Playwright, or dependencies locally
2. **Headless Testing**: Browsers run headless in Docker—no UI interruptions on macOS
3. **Reproducibility**: `uv.lock` ensures identical environments across machines
4. **Fast Iteration**: Makefile provides quick commands for common tasks
5. **Multi-Language**: Structure allows easy addition of TypeScript, Java, Go examples
6. **CI/CD Ready**: Container-based tests run identically in local and CI environments

---

## 🏗️ System Architecture

### Local Development Machine (macOS)

```
┌────────────────────────────────────────────────┐
│ Developer's macOS Machine                      │
│                                                │
│ ┌─────────────────────────────────────────┐    │
│ │ Repository (Git)                        │    │
│ │ ├── examples/python-uv-3.13/            │    │
│ │ │   ├── Dockerfile                      │    │
│ │ │   ├── docker-compose.yml              │    │
│ │ │   ├── pyproject.toml                  │    │
│ │ │   ├── tests/                          │    │
│ │ │   │   ├── test_google.py              │    │
│ │ │   │   └── test_github.py              │    │
│ │ │   └── Makefile                        │    │
│ │ └── docs/                               │    │
│ │     ├── ARCHITECTURE.md (this file)     │    │
│ │     ├── BEST_PRACTICES.md               │    │
│ │     └── TROUBLESHOOTING.md              │    │
│ └─────────────────────────────────────────┘    │
│                    ↓                           │
│ ┌─────────────────────────────────────────┐    │
│ │ Developer Tools                         │    │
│ │ ├── VS Code / IDE                       │    │
│ │ ├── Docker Desktop                      │    │
│ │ ├── Docker Compose                      │    │
│ │ ├── make command                        │    │
│ │ └── Git                                 │    │
│ └─────────────────────────────────────────┘    │
│                    ↓                           │
│              make test                         │
│              (invokes Docker)                  │
└────────────────────────────────────────────────┘
```

### Docker Container Environment

```
┌───────────────────────────────────────────────┐
│ Docker Container                              │
│ (mcr.microsoft.com/playwright/python:v1.48)   │
│                                               │
│ ┌─────────────────────────────────────────┐   │
│ │ Base: Ubuntu 20.04 LTS                  │   │
│ │ ├── Chromium (latest)                   │   │
│ │ ├── Firefox (latest)                    │   │
│ │ ├── WebKit (latest)                     │   │
│ │ └── System dependencies                 │   │
│ └─────────────────────────────────────────┘   │
│                    ↓                          │
│ ┌─────────────────────────────────────────┐   │
│ │ Python Environment                      │   │
│ │ ├── Python 3.13.5 (installed)           │   │
│ │ ├── uv package manager                  │   │
│ │ └── /app/                               │   │
│ │     ├── pyproject.toml                  │   │
│ │     ├── uv.lock (frozen deps)           │   │
│ │     └── .venv/ (created by uv sync)     │   │
│ └─────────────────────────────────────────┘   │
│                    ↓                          │
│ ┌─────────────────────────────────────────┐   │
│ │ Installed Packages                      │   │
│ │ ├── playwright==1.48.0                  │   │
│ │ ├── pytest==8.0.0                       │   │
│ │ ├── pytest-asyncio==0.24.0              │   │
│ │ ├── pytest-html==4.1.0                  │   │
│ │ └── [other dependencies]                │   │
│ └─────────────────────────────────────────┘   │
│                    ↓                          │
│ ┌─────────────────────────────────────────┐   │
│ │ Test Execution                          │   │
│ │ ├── pytest discovers tests/             │   │
│ │ ├── Fixtures (conftest.py) setup        │   │
│ │ ├── Browsers launched (headless)        │   │
│ │ ├── Tests execute against real sites    │   │
│ │ └── Results & reports generated         │   │
│ └─────────────────────────────────────────┘   │
└───────────────────────────────────────────────┘
           ↓ (Volume Mounts - Bidirectional)
    ┌──────────────────────────────────┐
    │ Host Mac File System             │
    │ ├── test-results/                │
    │ ├── htmlreport/                  │
    │ └── tests/ (read-only mount)     │
    └──────────────────────────────────┘
```

---

## 🔄 Workflow: Local Dev to Test Execution

### Step 1: Developer Edits Tests Locally

```
Developer edits tests/test_google.py in VS Code
            ↓
Git watches for changes (no action)
```

### Step 2: Developer Runs Make Command

```
$ cd examples/python-uv-3.13
$ make test
            ↓
make reads Makefile
            ↓
Makefile runs: docker-compose run --rm playwright pytest -v tests/
            ↓
Docker Compose reads docker-compose.yml
```

### Step 3: Docker Compose Orchestrates Container

```
Docker Compose:
  1. Checks if image exists (if not: calls `docker build`)
  2. Starts container from image
  3. Mounts volumes:
     - tests/ (read-only from host)
     - test-results/ (write from container)
     - htmlreport/ (write from container)
  4. Sets environment: PLAYWRIGHT_HEADLESS=true
  5. Runs command: pytest -v tests/
```

### Step 4: Container Executes Tests

```
Inside Container:
  1. pytest discovers tests/ directory
  2. conftest.py fixtures execute:
     - browser fixture: Launches Chromium (headless)
     - context fixture: Creates new context
     - page fixture: Creates new page
  3. Test execution:
     - test_google.py runs 4 tests
     - test_github.py runs 5 tests
  4. Results collected
  5. HTML report generated
```

### Step 5: Results Flow Back to Host

```
Container writes:
  - test-results/*.json
  - htmlreport/report.html
            ↓
Volume mounts copy to:
  - Mac's test-results/
  - Mac's htmlreport/
            ↓
Developer can:
  - View HTML report: make report
  - Parse JSON for CI: test-results/
  - Commit results to Git
```

---

## 🗂️ File Dependency Map

```
Dockerfile (Base Image Definition)
    ↓
    Defines: Python 3.13, uv, system packages
    Used by: docker-compose.yml

docker-compose.yml (Service Orchestration)
    ├── Extends: Dockerfile
    ├── Defines: volumes, environment, working directory
    └── Called by: Makefile targets

pyproject.toml (Dependency Definition)
    ├── Lists: pytest, playwright, pytest-asyncio, pytest-html
    ├── Defines: pytest configuration
    ├── Locked by: uv.lock (frozen versions)
    └── Used by: Dockerfile (uv sync --frozen)

uv.lock (Frozen Dependencies)
    ├── Generated from: pyproject.toml
    ├── Contains: Exact versions of all transitive dependencies
    ├── Used by: Dockerfile (uv sync --frozen)
    └── Ensures: Reproducible builds across machines

conftest.py (Test Fixtures)
    ├── Defines: browser, context, page fixtures
    ├── Scope: Session, Function scoped
    ├── Used by: test_google.py, test_github.py
    └── Dependency: Playwright

test_google.py (Test Implementation)
    ├── Uses: page fixture from conftest.py
    ├── Tests: google.de homepage
    ├── Runs in: pytest (from pyproject.toml config)
    └── Browser: Chromium (from Dockerfile's base image)

test_github.py (Test Implementation)
    ├── Uses: page fixture from conftest.py
    ├── Tests: github.com homepage
    ├── Runs in: pytest (from pyproject.toml config)
    └── Browser: Chromium (from Dockerfile's base image)

Makefile (Developer Interface)
    ├── Command: make build → docker-compose build
    ├── Command: make test → docker-compose run
    ├── Command: make report → open htmlreport/report.html
    └── Reads: docker-compose.yml, pyproject.toml
```

---

## 🔌 Technology Stack Layers

### Layer 1: Host Machine

- macOS / Linux
- Docker Desktop
- `make` command-line tool
- Git

### Layer 2: Container Orchestration

- Docker (containerization)
- Docker Compose 3.9 (multi-service setup, though single service here)

### Layer 3: Base Image

- Microsoft's official Playwright image (mcr.microsoft.com/playwright/python:v1.48.0-focal)
- Pre-installed: Chromium, Firefox, WebKit
- Pre-installed: System dependencies for browsers

### Layer 4: Python Environment

- Python 3.13.5
- `uv` package manager
- Virtual environment created by `uv sync`

### Layer 5: Testing Framework

- pytest 8.0.0+ (test runner)
- pytest-asyncio 0.24.0+ (async test support)
- pytest-html 4.1.0+ (HTML reporting)

### Layer 6: Browser Automation

- Playwright 1.48.0+ (browser control)
- Async/await API for non-blocking operations

---

## 🚀 Execution Flow: From Command to Test Results

```
Developer Types:
  $ make test

↓ Makefile rule executed:
  test:
    docker-compose run --rm playwright pytest -v tests/

↓ Docker Compose resolves:
  1. Read docker-compose.yml
  2. Find service "playwright"
  3. Check if image exists
  4. If not: build from Dockerfile
  5. Start container
  6. Mount volumes
  7. Set environment variables
  8. Run entrypoint: pytest

↓ Container boots:
  1. Base image loads (Ubuntu + Playwright browsers)
  2. Python 3.13 loads
  3. Dependencies resolved from uv.lock
  4. Virtual environment activated

↓ pytest starts (entrypoint command):
  1. Discover test files in tests/
  2. Load conftest.py
  3. Register fixtures

↓ Fixture initialization:
  1. browser fixture: Launch Chromium (headless)
  2. context fixture: Create browser context (1280x720)
  3. page fixture: Create page instance

↓ Test execution:
  1. test_google.py::TestGoogleHomepage::test_google_homepage_loads()
     - Navigate to google.de
     - Wait for network idle
     - Assert page title contains "Google"
     - Assert search box visible
  2. ... (3 more Google tests)
  3. test_github.py::TestGitHubHomepage::test_github_homepage_loads()
     - Navigate to github.com
     - Wait for network idle
     - Assert page title
     - Assert navigation visible
  4. ... (4 more GitHub tests)

↓ Results collection:
  1. pytest gathers assertions
  2. HTML report plugin captures results
  3. Snapshots of failures (if any)

↓ Output generation:
  1. JSON report: test-results/pytest.json
  2. HTML report: htmlreport/report.html
  3. Console output: pytest summary

↓ Volume mount sync:
  1. Container outputs → Mac's filesystem
  2. test-results/ populated
  3. htmlreport/ populated
  4. Console logs visible to developer

↓ Container exits:
  Docker Compose removes container (--rm flag)
  Files remain on host

↓ Developer continues:
  $ make report
  → Opens htmlreport/report.html in browser
  → Can inspect test results, failures, screenshots
```

---

## 🔐 Isolation & Security

### Container Isolation

- **Process Isolation**: Tests run in separate process namespace
- **Filesystem Isolation**: `/app` directory isolated from host system
- **Network Isolation**: Container has its own network interface
- **User Isolation**: Runs as non-root user inside container

### Volume Mount Strategy

- **tests/**: Mounted as `:ro` (read-only)
  - Prevents accidental modification from container
  - Direct live editing possible from macOS

- **test-results/**, **htmlreport/**: Mounted read-write
  - Container writes results back to host
  - Developer can inspect, commit, or process results

### Environment Variables

- `PLAYWRIGHT_HEADLESS=true` ensures headless mode
- Can be extended for CI/CD (e.g., `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=false`)

---

## 📊 Reproducibility Guarantees

### Exact Version Pinning

**uv.lock** freezes exact versions:

```
pytest==8.0.0 (not >=8.0.0)
playwright==1.48.0 (not 1.48.x)
```

### Python Version

**Dockerfile** explicitly installs Python 3.13.5 (not just 3.13)

### System Dependencies

**Base Image** (mcr.microsoft.com/playwright/python:v1.48.0) includes:

- Exact Chromium, Firefox, WebKit versions
- Exact system libraries (libc, GCC, etc.)

### Result

✅ Same test run on:

- Developer's Mac
- CI/CD (GitHub Actions, GitLab CI)
- Team member's machine
- Docker Hub / Container registry
- Production environment (if needed)

**All produce identical results** ✓

---

## 🎯 Design Patterns Used

### 1. Fixture Pattern (pytest)

```python
@pytest.fixture(scope="session")
async def browser():
    # Shared browser instance for all tests
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()
```

**Benefit**: Reusable setup/teardown, lifecycle management

### 2. Context Manager Pattern (Playwright)

```python
async with async_playwright() as p:
    browser = await p.chromium.launch()
    # Use browser
    # Auto cleanup when exiting 'with' block
```

**Benefit**: Guaranteed cleanup, exception safety

### 3. Layer Pattern (Docker)

```dockerfile
FROM base_image          # Layer 1: Browsers, system libs
RUN install python      # Layer 2: Python 3.13
RUN install uv          # Layer 3: Package manager
RUN uv sync             # Layer 4: Dependencies
COPY tests /app/tests   # Layer 5: Test files
```

**Benefit**: Docker caching, faster rebuilds, clear responsibility

### 4. Volume Mount Pattern (Docker Compose)

```yaml
volumes:
  - ./tests:/app/tests:ro          # Read-only input
  - ./htmlreport:/app/htmlreport   # Write output
```

**Benefit**: Live code editing, result extraction, bidirectional communication

### 5. Makefile Pattern

```makefile
build:
 docker-compose build

test:
 docker-compose run --rm playwright pytest -v tests/
```

**Benefit**: Consistent interface, discoverability, documentation

---

## 🔧 Configuration Management

### Environment Configuration

| Variable | Value | Purpose |
|----------|-------|---------|
| `PLAYWRIGHT_HEADLESS` | `true` | Run browsers without UI |
| `PYTHONUNBUFFERED` | `1` | Real-time logging output |
| `PYTEST_ASYNCIO_MODE` | `auto` | Automatic async test handling |

### pytest Configuration

From `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --tb=short --html=htmlreport/report.html --self-contained-html"
```

### Makefile Configuration

From `Makefile`:

```makefile
COMPOSE_FILE := docker-compose.yml
SERVICE := playwright
DOCKER_COMPOSE := docker-compose -f $(COMPOSE_FILE)
```

---

## 🚨 Error Handling & Debugging

### Container Won't Start

1. Check Docker status: `docker ps`
2. Rebuild: `make clean && make build`
3. View logs: `docker logs -f <container_id>`

### Tests Fail with Network Error

1. Check Docker network: `docker network ls`
2. Verify Internet access: `docker exec -it <container> ping google.com`
3. Use verbose mode: `make test-verbose`

### HTML Report Won't Generate

1. Check volume mounts: `docker-compose config --volumes`
2. Verify permissions: `ls -la htmlreport/`
3. Rebuild pytest config in pyproject.toml

---

## 📈 Scalability & Extensions

### Current Limits

- Single service in Docker Compose (can add more)
- Single Python version (can create multi-version matrix)
- Real website testing (can add database, mock servers)

### Future Enhancements

1. **Matrix Testing**: Python 3.12, 3.13, 3.14
2. **Multiple Browsers**: Chrome, Firefox, Safari (via WebKit)
3. **Parallel Execution**: `pytest-xdist` for faster runs
4. **Coverage Reports**: `pytest-cov` integration
5. **Database Testing**: PostgreSQL, MongoDB containers
6. **Mock Servers**: LocalStack for AWS testing
7. **Performance Profiling**: `pytest-benchmark` for metrics
8. **Visual Regression**: Percy, Applitools integration

---

## 🔗 Related Documentation

- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** — Testing patterns and configuration guidelines
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Common issues and solutions
- **[Python Example README](../examples/python-uv-3.13/README.md)** — Quick start guide

---

**Last Updated**: January 2025
**For**: running-playwright-tests-in-docker-container repository
