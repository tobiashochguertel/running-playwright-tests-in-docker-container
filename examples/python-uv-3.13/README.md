# Python 3.13+ with `uv` + Playwright + Docker

A minimal, production-ready example for running Playwright tests in Docker using **Python 3.13+**, **`uv` package manager**, and **pytest**.

## 🎯 What This Example Does

✅ Runs Playwright tests in **headless mode** inside Docker
✅ Tests **real websites** (Google, GitHub) — no local app needed
✅ Uses `uv` for **fast, reproducible** dependency management
✅ Provides **Makefile** for quick commands
✅ Generates **HTML reports** with screenshots
✅ Zero interruptions on your macOS dev machine

---

## 📋 Prerequisites

- Docker & Docker Compose installed
- `make` command available (macOS: `brew install make`)
- macOS/Linux with bash or zsh

> **Note:** You do NOT need Python, `uv`, or Playwright installed locally—everything runs in Docker!

---

## 🚀 Quick Start

### 1. Navigate to This Example

```bash
cd running-playwright-tests-in-docker-container/examples/python-uv-3.13
```

### 2. Build Docker Image

```bash
make build
```

This builds a Docker image with Python 3.13, `uv`, Playwright, and all dependencies.

### 3. Run Tests

```bash
make test
```

Tests run **headless** in the container—no browser windows on your Mac!

### 4. View Results

```bash
make report
```

Opens an HTML report with test results in your browser.

---

## 📁 Project Structure

```text
python-uv-3.13/
├── Dockerfile              # Python 3.13 + uv + Playwright
├── docker-compose.yml      # Docker Compose orchestration
├── pyproject.toml          # uv dependencies & pytest config
├── uv.lock                 # Locked dependency versions
├── Makefile                # Quick commands
├── .gitignore              # Git ignore rules
├── tests/
│   ├── conftest.py         # pytest fixtures & setup
│   ├── test_google.py      # Google homepage tests
│   └── test_github.py      # GitHub homepage tests
└── README.md               # This file
```

---

## 📚 Available Commands

```bash
make help               # Show all available commands
make build              # Build Docker image
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

---

## 🔧 How It Works

### Dockerfile Breakdown

The `Dockerfile` does the following:

1. **Starts from Microsoft's official Playwright image** with pre-installed browsers (Chromium, Firefox, WebKit)
2. **Installs Python 3.13** explicitly for the latest Python features
3. **Installs `uv`** for fast, reproducible dependency management
4. **Copies and locks dependencies** using `uv sync --frozen`
5. **Copies test files** into the container
6. **Sets `PLAYWRIGHT_HEADLESS=true`** to run browsers headless (no UI)
7. **Uses pytest as entrypoint** with sensible defaults

### Key Points

- **No Python on your Mac**: Everything runs in the container
- **Headless Mode**: Browsers run without UI, no interruptions
- **Volume Mounts**: Test files mounted as read-only for live editing
- **Artifact Preservation**: Test results, HTML reports mounted for access from host

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

- **dependencies**: playwright, pytest, pytest-asyncio, pytest-html
- **pytest config**: asyncio mode, test discovery, HTML reporting

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

Orchestrates the container:

- **volumes**: Mount test files, capture results
- **environment**: Set `PLAYWRIGHT_HEADLESS=true`
- **working_dir**: Set to `/app` for correct paths

### `conftest.py`

Provides pytest fixtures for async browser testing:

- **browser fixture**: Chromium browser instance (session-scoped)
- **context fixture**: Browser context with 1280x720 viewport
- **page fixture**: New page for each test

---

## 📊 Output & Artifacts

### Test Results

After `make test`, results appear in:

- **Console**: Real-time test output
- **`test-results/`**: JSON report for CI/CD integration
- **`htmlreport/`**: Interactive HTML report with screenshots

### Viewing Reports

```bash
# Auto-open HTML report
make report

# Or manually
open htmlreport/report.html
```

---

## 🧪 Testing Your Own Websites

To test your own website or local app:

### For Public Websites

Edit test files and change the URL:

```python
# Instead of google.de
await page.goto("https://example.com", wait_until="networkidle")
```

### For Local Apps

Use `host.docker.internal` to access your Mac's localhost:

```python
# Test local app running on port 3000
await page.goto("http://host.docker.internal:3000", wait_until="networkidle")
```

Or set via environment variable in `docker-compose.yml`:

```yaml
environment:
  TEST_BASE_URL: http://host.docker.internal:3000
```

---

## 🐛 Troubleshooting

### Tests fail with "Page did not navigate"

**Cause**: Network issue or site structure changed.
**Fix**: Run with verbose output:

```bash
make test-verbose
```

### Docker image build fails

**Cause**: Network timeout downloading Playwright browsers.
**Fix**: Rebuild with no cache:

```bash
make clean
make build
```

### Permission denied errors

**Cause**: Docker socket permissions.
**Fix**: Ensure Docker is running:

```bash
docker ps
```

### Module not found errors in container

**Cause**: Dependencies not properly synced.
**Fix**: Rebuild the image:

```bash
make build
```

---

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests in Docker
        run: |
          cd examples/python-uv-3.13
          make build
          make test
```

---

## 📚 Further Reading

- **[Playwright Python Docs](https://playwright.dev/python/)** — API reference & best practices
- **[pytest Documentation](https://docs.pytest.org/)** — Test fixtures, markers, plugins
- **[`uv` Documentation](https://docs.astral.sh/uv/)** — Package manager usage
- **[Docker Compose Docs](https://docs.docker.com/compose/)** — Container orchestration
- **[async/await in Python](https://docs.python.org/3/library/asyncio.html)** — Async programming

---

## ✨ Next Steps

1. **Add more tests** to `tests/` for other websites or your app
2. **Customize Dockerfile** if you need additional system packages
3. **Integrate with CI/CD** using GitHub Actions, GitLab CI, or Jenkins
4. **Try parallel execution** with `pytest-xdist` for faster runs
5. **Add screenshots** to HTML reports for better debugging

---

## 🤝 Need Help?

- Check [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md) in the docs folder
- See [BEST_PRACTICES.md](../../docs/BEST_PRACTICES.md) for advanced usage
- Review [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) for system design

---

**Ready to run your first test?** Try `make test` now! 🚀
