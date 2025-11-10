# Running Playwright Tests in Docker Container

Great question! Yes, absolutely-you can run Playwright tests in a Docker container to keep your macOS workflow uninterrupted. Here's a comprehensive approach:

## Overview

**Problem:** Browser windows from local Playwright tests interrupt your work.
**Solution:** Containerize Playwright tests with headless browsers running in Docker while you continue developing on your Mac.

---

## Architecture: Local Dev + Remote Test Container

```text
+-----------------------------------------+
|         macOS Host Machine              |
|  +----------------------------------+   |
|  |  Your IDE/Editor (VSCode, etc.)  |   |
|  |  + Your App Dev Work             |   |
|  +----------------------------------+   |
|                                         |
|  +----------------------------------+   |
|  |   pytest (local or remote)       |   |
|  |   Triggers tests -> Docker API   |   |
|  +----------------------------------+   |
+-----------------------------------------+
           v (Docker socket/API)
+-----------------------------------------+
|    Docker Container (Linux)             |
|  +----------------------------------+   |
|  |  Python 3.13+                    |   |
|  |  Playwright + Chromium/Firefox   |   |
|  |  pytest running headless         |   |
|  |  (No browser UI interruptions)   |   |
|  +----------------------------------+   |
+-----------------------------------------+
```

---

## Step 1: Dockerfile Setup

Create a `Dockerfile.tests` for your Python 3.13+ Playwright environment:

```dockerfile name=Dockerfile.tests
FROM mcr.microsoft.com/playwright/python:v1.48.0-focal

# Use Python 3.13+
RUN apt-get update && \
    apt-get install -y python3.13 python3.13-dev python3.13-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set Python 3.13 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1

WORKDIR /app

# Copy requirements
COPY requirements-test.txt .

# Install dependencies
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install -r requirements-test.txt

# Copy test files
COPY tests/ /app/tests/
COPY src/ /app/src/  # if needed

# Set headless mode by default
ENV PLAYWRIGHT_HEADLESS=true

ENTRYPOINT ["pytest"]
CMD ["-v", "tests/"]
```

---

## Step 2: requirements-test.txt

```text name=requirements-test.txt
pytest>=8.0.0
pytest-playwright>=0.5.0
playwright>=1.48.0
python-dotenv>=1.0.0
```

---

## Step 3: docker-compose.yml (Recommended)

Simplifies repeated test runs and environment management:

```yaml name=docker-compose.yml
version: '3.9'

services:
  playwright-tests:
    build:
      context: .
      dockerfile: Dockerfile.tests
    container_name: playwright-tests-runner
    environment:
      PLAYWRIGHT_HEADLESS: "true"
      # Pass your app's URL if testing remote
      TEST_BASE_URL: http://host.docker.internal:3000
    volumes:
      - ./tests:/app/tests:ro
      - ./src:/app/src:ro
      - ./test-results:/app/test-results
      - ./htmlreport:/app/htmlreport
    ports:
      - "8080:8080"  # for reports if needed
```

---

## Step 4: Playwright Configuration (pytest)

Ensure your `pytest.ini` or `pyproject.toml` is configured for headless:

```ini name=pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    e2e: end-to-end tests
    unit: unit tests
addopts = -v --tb=short --strict-markers
```

Or in `pyproject.toml`:

```toml name=pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
markers = ["e2e", "unit"]
addopts = "-v --tb=short"
```

And in your **playwright.ini** or fixture setup:

```python name=tests/conftest.py
import pytest
from playwright.async_api import async_playwright

@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        # Headless by default; override only if needed
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()

@pytest.fixture
async def page(browser):
    context = await browser.new_context()
    page = await context.new_page()
    yield page
    await page.close()
    await context.close()
```

---

## Step 5: Run Tests in Docker

### **Option A: One-off Test Run**

```bash
docker-compose run --rm playwright-tests pytest -v tests/
```

### **Option B: Persistent Container (Watch Mode)**

```bash
docker-compose up --build playwright-tests
```

### **Option C: Run Specific Tests**

```bash
docker-compose run --rm playwright-tests pytest -v tests/test_login.py::test_user_login
```

### **Option D: Generate HTML Report**

```bash
docker-compose run --rm playwright-tests pytest \
  --html=htmlreport/report.html \
  --self-contained-html \
  tests/
```

---

## Step 6: macOS Host Integration (Optional but Useful)

### **Makefile for Quick Commands**

```makefile name=Makefile
.PHONY: test test-watch test-report test-debug build-tests

build-tests:
 docker-compose build --no-cache playwright-tests

test:
 docker-compose run --rm playwright-tests pytest -v tests/

test-watch:
 docker-compose run --rm playwright-tests pytest -v tests/ --tb=short

test-report:
 docker-compose run --rm playwright-tests pytest \
   --html=htmlreport/report.html \
   --self-contained-html \
   tests/

test-debug:
 docker-compose run -it playwright-tests pytest -vv --pdb tests/

clean:
 docker-compose down
 rm -rf htmlreport test-results
```

**Usage:**

```bash
make build-tests
make test          # Run once
make test-watch    # Run with output
make test-report   # Generate HTML report
```

---

## Step 7: Testing Against Local App

If your app runs locally on `localhost:3000`, Docker containers can reach it via `host.docker.internal`:

```python name=tests/test_app.py
import pytest
from playwright.async_api import Page

@pytest.mark.asyncio
async def test_homepage(page: Page):
    # Docker will resolve host.docker.internal to your Mac's IP
    await page.goto("http://host.docker.internal:3000")
    assert await page.title()
```

Or set via env variable in `docker-compose.yml`:

```yaml
environment:
  TEST_BASE_URL: http://host.docker.internal:3000
```

---

## Step 8: CI/CD Bonus (GitHub Actions)

Run the same tests in CI without modification:

```yaml name=.github/workflows/test.yml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Playwright tests in Docker
        run: |
          docker-compose -f docker-compose.yml run --rm playwright-tests
```

---

## Key Benefits

| Benefit                  | Why                                                      |
|--------------------------|----------------------------------------------------------|
| **Zero interruptions**   | Headless browsers run in container, no UI popups         |
| **Isolated environment** | Consistent Python 3.13+ + Playwright version across team |
| **Local dev intact**     | Your Mac stays responsive-develop freely                 |
| **Reproducible tests**   | Same Docker image = same results everywhere              |
| **Easy CI/CD**           | Use exact same `docker-compose` in GitHub Actions        |
| **Logs & artifacts**     | Mount volumes for test reports & screenshots             |

---

## References

- **Playwright Python Docs:** <https://playwright.dev/python/>
- **Microsoft Playwright Docker Image:** <https://hub.docker.com/_/microsoft-playwright>
- **Docker Compose Reference:** <https://docs.docker.com/compose/compose-file/>
- **pytest-playwright:** <https://github.com/microsoft/playwright-pytest>
- **pytest Documentation:** <https://docs.pytest.org/>

---

Ready to set this up? Let me know if you hit any issues with the Docker build, environment variables, or test execution! [rocket]
