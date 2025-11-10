# Troubleshooting Guide

Common issues and solutions for running Playwright tests in Docker containers.

## 🐳 Docker-Related Issues

### Docker Daemon Not Running

**Error**: `Cannot connect to Docker daemon at unix:///var/run/docker.sock`

**Cause**: Docker Desktop not running on macOS

**Solution**:

```bash
# Start Docker Desktop (or via CLI if installed)
open /Applications/Docker.app

# Verify Docker is running
docker ps

# If still failing, restart Docker
osascript -e 'quit app "Docker"'
sleep 2
open /Applications/Docker.app
```

### Docker Image Build Fails

**Error**: `failed to solve with frontend dockerfile.v0: failed to read dockerfile`

**Cause**: Dockerfile path incorrect or file missing

**Solution**:

```bash
# Verify you're in correct directory
cd examples/python-uv-3.13
ls -la Dockerfile  # Should exist

# Try building with explicit path
docker build -f ./Dockerfile -t playwright:latest .

# Or use docker-compose
docker-compose build --no-cache
```

### Playwright Browsers Download Timeout

**Error**: `Failed to download Chromium/Firefox/WebKit`

**Cause**: Network timeout downloading browsers (~500MB)

**Solution**:

```bash
# Clear Docker cache and rebuild
make clean
make build  # Will re-download browsers

# If still failing, check network
docker run --rm alpine ping 8.8.8.8

# Try with increased Docker timeout
docker build --build-arg BUILDKIT_INLINE_CACHE=1 \
  --build-arg PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0 \
  -t playwright:latest .
```

### Out of Disk Space

**Error**: `no space left on device` during Docker build

**Cause**: Docker images/containers consuming disk

**Solution**:

```bash
# Check disk space
df -h

# Clean up Docker (aggressive)
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Remove all stopped containers
docker container prune

# Check Docker disk usage
docker system df
```

### Port Already in Use

**Error**: `bind: address already in use` (if using ports)

**Cause**: Another container using the port

**Solution**:

```bash
# Find which container uses port
lsof -i :5000  # Change 5000 to your port

# Stop conflicting container
docker-compose down

# Or stop all Docker containers
docker stop $(docker ps -q)
```

### Permission Denied Errors

**Error**: `permission denied while trying to connect to Docker daemon`

**Cause**: User not in docker group

**Solution**:

```bash
# Add your user to docker group (macOS usually not needed)
sudo dseditgroup -o edit -a $USER docker

# Or restart Docker Desktop to fix permissions
osascript -e 'quit app "Docker"'
sleep 2
open /Applications/Docker.app
```

---

## 📦 Dependency & Package Issues

### `uv sync` Fails

**Error**: `Failed to fetch dependencies` or `dependency resolution failed`

**Cause**: Network issue or incompatible Python version

**Solution**:

```bash
# Verify Python version in Dockerfile
# Should be 3.13+

# Force rebuild with fresh dependencies
make clean
make build

# Check if uv.lock is corrupted
rm uv.lock
make build  # Will regenerate uv.lock
```

### Module Not Found in Container

**Error**: `ModuleNotFoundError: No module named 'pytest'` or `'playwright'`

**Cause**: Dependencies not installed or uv sync not run

**Solution**:

```bash
# Rebuild Docker image (runs uv sync)
docker-compose build --no-cache

# Or manually sync inside container
docker-compose run --rm playwright uv sync

# Verify dependencies installed
docker-compose run --rm playwright pip list | grep pytest
```

### Version Conflicts

**Error**: `version conflict: X requires Y but you have Z`

**Cause**: Incompatible dependency versions

**Solution**:

```bash
# Clear and regenerate lock file
rm uv.lock
make build

# Or update specific package in pyproject.toml
# Edit pyproject.toml:
# [project]
# dependencies = [
#     "playwright>=1.48.0",  # Update version
# ]

# Then rebuild
make build
```

---

## 🧪 Test Execution Issues

### Tests Fail with "Page Did Not Navigate"

**Error**: `TimeoutError: Timeout 30000ms exceeded. waiting for function to return "true"`

**Cause**: Page load took too long or URL doesn't exist

**Solution**:

```python
# ✅ Use proper wait_until
await page.goto("https://example.com", wait_until="networkidle", timeout=60000)

# ✅ Check if URL is correct
print(f"Navigating to: {url}")

# ✅ Run test in verbose mode
make test-verbose

# ✅ Add screenshot for debugging
await page.screenshot(path="debug.png")
```

### Tests Fail with "Element Not Found"

**Error**: `TimeoutError: locator.click() has failed` or `locator.fill() timed out`

**Cause**: Selector doesn't match or element not visible

**Solution**:

```python
# ✅ Verify selector exists
locator = page.locator("input[name='search']")
count = await locator.count()
print(f"Found {count} elements with selector")

# ✅ Check if element is visible
if await locator.is_visible():
    print("Element is visible")
else:
    print("Element is NOT visible")
    await page.screenshot(path="debug.png")

# ✅ Use more specific selector
# Instead of: page.locator("button")
# Use: page.locator("button:has-text('Search')")

# ✅ Wait for element
await page.wait_for_selector("input[name='search']", timeout=10000)
```

### Tests Timeout

**Error**: `Timeout 30000ms exceeded`

**Cause**: Page load too slow or network issues

**Solution**:

```python
# ✅ Increase timeout
await page.goto("https://example.com", timeout=60000)  # 60 seconds

# ✅ Use networkidle instead of load
await page.goto("https://example.com", wait_until="networkidle")

# ✅ Check network inside container
docker-compose run --rm playwright bash -c "ping -c 3 example.com"

# ✅ Run locally to compare
# If test works locally but fails in Docker, it's likely network
```

### Tests Fail Intermittently (Flaky)

**Error**: Test passes sometimes, fails other times

**Cause**: Race conditions or timing issues

**Solution**:

```python
# ❌ DON'T use sleep()
time.sleep(2)  # Flaky!

# ✅ DO use Playwright's built-in waiting
await page.wait_for_url("**/success")  # Wait for URL change
await page.wait_for_selector(".results")  # Wait for element
await page.wait_for_function("() => document.ready")  # Wait for condition

# ✅ Use wait_until for page loads
await page.goto(url, wait_until="networkidle")

# ✅ Re-run test to verify
make test-single FILE=tests/test_google.py::TestGoogleHomepage::test_google_homepage_loads
```

### Assertion Errors Not Clear

**Error**: `AssertionError` with minimal output

**Solution**:

```python
# ✅ Add assertion messages
count = await page.locator("nav a").count()
assert count > 0, f"Expected at least 1 nav link, found {count}"

# ✅ Use descriptive assertions
assert await search_box.is_visible(), "Search box should be visible"

# ✅ Run verbose mode
make test-verbose

# Output shows full traceback
```

---

## 🌐 Network & Site-Specific Issues

### Cannot Access External Websites

**Error**: `net::ERR_NAME_NOT_RESOLVED` or connection refused

**Cause**: Network issue or Docker network misconfiguration

**Solution**:

```bash
# Test network from inside container
docker-compose run --rm playwright bash
ping google.com
exit

# If ping works but tests fail, check:
# 1. URL is correct
# 2. Site requires authentication
# 3. Site blocks bots

# Bypass bot detection (risky, some sites don't like)
# Add user agent:
context = await browser.new_context(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
)
```

### Site Blocks Playwright

**Error**: `403 Forbidden` or `401 Unauthorized`

**Cause**: Some sites detect and block Playwright

**Solution**:

```python
# ✅ Add stealth plugin
# Install: pip install playwright-stealth
# Use: from playwright_stealth import stealth

# ✅ Or use randomized user-agent
import random
user_agents = [
    "Mozilla/5.0 ...",
    "Chrome/120.0 ...",
]
context = await browser.new_context(
    user_agent=random.choice(user_agents)
)

# ✅ Add delays between requests
await page.wait_for_timeout(1000)  # 1 second delay

# ⚠️ Check site's robots.txt and terms of service
```

### Site Requires Authentication

**Error**: `401 Unauthorized` or redirected to login

**Cause**: Tests accessing protected pages

**Solution**:

```python
# ✅ Create fixture for authenticated page
@pytest.fixture
async def authenticated_page(page: Page) -> Page:
    await page.goto("https://example.com/login")
    await page.fill("input[name='email']", "user@example.com")
    await page.fill("input[name='password']", "password123")
    await page.click("button[type='submit']")

    # Wait for redirect to authenticated page
    await page.wait_for_url("**/dashboard")

    yield page

# ✅ Use environment variables for credentials
import os
email = os.getenv("TEST_USER_EMAIL")
password = os.getenv("TEST_USER_PASSWORD")
```

### SSL/Certificate Errors

**Error**: `ERR_CERT_AUTHORITY_INVALID`

**Cause**: Self-signed certificate or certificate issue

**Solution**:

```python
# ✅ Ignore HTTPS errors (use only for testing!)
context = await browser.new_context(
    ignore_https_errors=True
)

# ✅ Or disable SSL verification (less secure)
# Not recommended for production tests
```

---

## 📊 HTML Report Issues

### HTML Report Won't Generate

**Error**: `htmlreport/` directory empty or missing `report.html`

**Cause**: pytest-html not installed or configuration issue

**Solution**:

```bash
# Verify pytest-html installed
docker-compose run --rm playwright pip list | grep pytest-html

# Check pyproject.toml configuration
cat pyproject.toml | grep -A 5 "pytest.ini_options"

# Should have:
# addopts = "-v --html=htmlreport/report.html --self-contained-html"

# Manually generate report
make test
make report  # Opens the HTML
```

### Report Opens but Shows No Results

**Error**: `htmlreport/report.html` opens but no test data

**Cause**: Tests didn't actually run or results weren't captured

**Solution**:

```bash
# Re-run tests with verbose output
make test-verbose

# Check volume mounts
docker-compose config --volumes

# Verify report path
ls -la htmlreport/
file htmlreport/report.html

# If file is empty, pytest-html not collecting results
# Check addopts in pyproject.toml
```

### Report Shows All Tests as Passed But They Failed

**Error**: Report shows "5 passed" but test output showed failures

**Cause**: HTML report cached or tests interrupted

**Solution**:

```bash
# Delete old report
rm htmlreport/report.html

# Clean pytest cache
rm -rf .pytest_cache

# Rebuild and rerun
make clean
make build
make test
```

---

## 🛠️ Debugging Techniques

### Enable Verbose Output

```bash
# Very verbose output
make test-verbose

# Or directly:
docker-compose run --rm playwright pytest -vv --tb=long tests/
```

### Run Single Test

```bash
# Run one test file
make test-single FILE=tests/test_google.py

# Or directly:
docker-compose run --rm playwright \
  pytest tests/test_google.py::TestGoogleHomepage::test_google_homepage_loads -vv
```

### Capture Screenshots on Failure

```python
@pytest.fixture
async def take_screenshot(page: Page):
    def _screenshot(name: str):
        page.screenshot(path=f"screenshots/{name}.png")
    return _screenshot

async def test_something(self, page: Page, take_screenshot):
    try:
        await page.goto("https://example.com")
        # ... test code
    except Exception as e:
        await take_screenshot("failure")
        raise
```

### Check Container Logs

```bash
# View Docker logs
docker-compose logs playwright

# Tail logs (follow)
docker-compose logs -f playwright

# Get last 100 lines
docker-compose logs --tail 100 playwright
```

### Interactive Container Shell

```bash
# Open bash in container
make shell

# Or directly:
docker-compose run --rm playwright bash

# Inside container:
python -c "import playwright; print(playwright.__version__)"
python -c "import pytest; print(pytest.__version__)"
python -m pytest --version
```

### Inspect Network Traffic

```bash
# From inside container
docker-compose run --rm playwright bash

# Inside container, install curl and test
apt-get update && apt-get install -y curl
curl -v https://google.de

# Check if external URLs are accessible
curl https://github.com
```

---

## 🚀 Advanced Troubleshooting

### Check Docker Image Layers

```bash
# See image history
docker history playwright:latest

# Or inspect with dive (requires installation)
dive playwright:latest
```

### Debug pytest Configuration

```bash
# Show pytest config
docker-compose run --rm playwright pytest --co -q

# Show all markers
docker-compose run --rm playwright pytest --markers

# Show fixtures
docker-compose run --rm playwright pytest --fixtures
```

### Profile Test Performance

```bash
# Add pytest-profiling
pip install pytest-profiling

# Run with profiling
docker-compose run --rm playwright pytest --profile tests/

# Check profile results
cat prof/combined.prof
```

### Memory Leak Detection

```bash
# Install memory-profiler
pip install memory-profiler

# Run with memory profiling
docker-compose run --rm playwright python -m memory_profiler tests/test_google.py
```

---

## 📞 Getting More Help

### Before Asking for Help

1. ✅ Run with verbose output: `make test-verbose`
2. ✅ Check Docker logs: `docker-compose logs playwright`
3. ✅ Verify Docker is running: `docker ps`
4. ✅ Read error messages carefully (scroll up!)
5. ✅ Try rebuilding: `make clean && make build`
6. ✅ Search existing issues on GitHub

### When Reporting Issues

Include:

- ✅ Your macOS version (`sw_vers`)
- ✅ Docker version (`docker --version`)
- ✅ Docker Compose version (`docker-compose --version`)
- ✅ Full error output (with verbose flag)
- ✅ Steps to reproduce
- ✅ Screenshot or screen recording if visual

### Useful Commands for Reporting

```bash
# Get system info
sw_vers
docker --version
docker-compose --version
python --version

# Get Docker info
docker info
docker-compose config

# Get test output
make test-verbose 2>&1 | tee output.txt  # Save to file
```

---

## 🔗 Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design and Docker setup
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)** — Testing patterns and best practices
- **[Python Example README](../examples/python-uv-3.13/README.md)** — Quick start guide
- **[Playwright GitHub Issues](https://github.com/microsoft/playwright/issues)** — Community issues
- **[Docker Documentation](https://docs.docker.com/)** — Docker reference

---

**Last Updated**: January 2025
**For**: running-playwright-tests-in-docker-container repository
