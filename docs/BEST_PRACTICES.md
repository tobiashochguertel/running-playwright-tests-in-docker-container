# Best Practices for Docker + Playwright Testing

This document provides best practices for writing, organizing, and running Playwright tests in Docker containers.

## 🎯 Core Principles

1. **Test Real Behavior**: Test user-visible actions, not implementation details
2. **Keep Tests Fast**: Use `wait_until="networkidle"` for page loads, avoid arbitrary sleeps
3. **Isolate Tests**: Each test should be independent and runnable in any order
4. **Use Fixtures**: Leverage pytest fixtures for setup/teardown
5. **Mock External Services**: Don't rely on external APIs in tests (use local servers if needed)
6. **Clear Naming**: Test names should describe what they verify
7. **Deterministic Results**: Same test run should produce identical results

---

## 🧪 Test Organization & Naming

### ✅ Good Test Names

```python
# Test file naming
test_google.py          # Tests Google functionality
test_authentication.py  # Tests auth flow

# Test class naming
class TestGoogleHomepage:      # Describes what is being tested
class TestGitHubNavigation:    # Clear subject

# Test method naming
def test_google_homepage_loads(self, page):
    # Clear: what does it test? expected outcome?

def test_search_box_is_visible(self, page):
    # Clear: verifiable action

def test_user_can_login_with_valid_credentials(self, page):
    # Clear: user action, context, expected result
```

### ❌ Avoid These Names

```python
# Vague names
def test_stuff(self, page):
def test_page(self, page):
def test_elements(self, page):

# Implementation-focused names
def test_click_selector_3_times(self, page):
def test_xpath_exists(self, page):
def test_javascript_returns_value(self, page):
```

### 📁 Project Structure

```
examples/python-uv-3.13/tests/
├── conftest.py              # Shared fixtures
├── test_google.py           # Google tests (4 related tests)
├── test_github.py           # GitHub tests (5 related tests)
└── [future_tests]
    └── test_yoursite.py     # New website tests
```

---

## 🔧 Fixture Best Practices

### Use Class-Scoped Fixtures for Shared Resources

```python
# ✅ GOOD: Session scope for browser (reused across tests)
@pytest.fixture(scope="session")
async def browser() -> Browser:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()

# ❌ BAD: Function scope creates new browser for every test
@pytest.fixture(scope="function")
async def browser() -> Browser:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()  # Slow! Creates 100 browsers for 100 tests
```

### Use Function-Scoped Fixtures for Test Isolation

```python
# ✅ GOOD: New page for each test (isolation)
@pytest.fixture
async def page(context: BrowserContext) -> Page:
    page = await context.new_page()
    yield page
    await page.close()  # Clean up after each test

# ✅ GOOD: New context for each test (isolation, but shares browser)
@pytest.fixture
async def context(browser: Browser) -> BrowserContext:
    context = await browser.new_context(viewport={"width": 1280, "height": 720})
    yield context
    await context.close()
```

### Use Fixtures for Common Setup

```python
# ✅ GOOD: Fixture provides pre-configured page
@pytest.fixture
async def logged_in_page(page: Page) -> Page:
    await page.goto("https://example.com/login")
    await page.fill("input[name='email']", "user@example.com")
    await page.fill("input[name='password']", "password123")
    await page.click("button[type='submit']")
    await page.wait_for_url("https://example.com/dashboard")
    yield page

# Usage in test
async def test_dashboard_shows_user_data(self, logged_in_page: Page):
    # Already logged in, ready to test
    assert "Dashboard" in await logged_in_page.title()
```

---

## 🧪 Test Writing Patterns

### Use Async/Await Consistently

```python
# ✅ GOOD: Async pattern for non-blocking operations
class TestGoogleHomepage:
    async def test_homepage_loads(self, page: Page):
        await page.goto("https://www.google.de", wait_until="networkidle")
        title = await page.title()
        assert "Google" in title

# ❌ BAD: Mixing sync and async (confusing)
def test_homepage_loads(self, page: Page):
    page.goto("https://www.google.de")  # Won't work without await
```

### Use `wait_until` for Reliable Page Loads

```python
# ✅ GOOD: Wait for network idle (most reliable)
await page.goto("https://example.com", wait_until="networkidle")

# ✅ GOOD: Wait for specific content (also reliable)
await page.goto("https://example.com", wait_until="domcontentloaded")

# ❌ BAD: Arbitrary sleep (flaky and slow)
await page.goto("https://example.com")
await asyncio.sleep(3)  # What if page takes 5 seconds?
```

### Use Specific Locators

```python
# ✅ GOOD: Specific, maintainable locators
search_box = page.locator("input[aria-label='Search']")
button = page.locator("button:has-text('Submit')")
logo = page.locator("img[alt='Company Logo']")

# ⚠️ ACCEPTABLE: CSS selectors (faster but less maintainable)
search_box = page.locator(".search-input")

# ❌ BAD: XPath (slow, brittle)
search_box = page.locator("//*[@id='main']/div[1]/input")

# ❌ BAD: Index-based (fragile)
buttons = page.locator("button")
buttons.nth(0).click()  # What if new button added?
```

### Verify Visibility Before Interaction

```python
# ✅ GOOD: Check visibility first
search_box = page.locator("input[name='search']")
assert await search_box.is_visible()
await search_box.fill("Playwright")

# ✅ GOOD: Use Playwright's built-in waiting
await search_box.click()  # Automatically waits for clickable

# ❌ BAD: Assume visibility
search_box = page.locator("input[name='search']")
await search_box.fill("Playwright")  # Might fail silently
```

### Handle Async Operations Properly

```python
# ✅ GOOD: Await navigation promise
async def test_search_works(self, page: Page):
    await page.goto("https://www.google.de", wait_until="networkidle")
    search_box = page.locator("textarea[aria-label='Suche']")

    # Wait for navigation while typing and clicking
    await asyncio.gather(
        page.wait_for_url("**/?q=*"),
        search_box.fill("Playwright"),
        page.locator("button:has-text('Google Suche')").click()
    )

    # Now verify search results
    results = page.locator("a[data-sokoban-feature='serp-results']")
    assert await results.count() > 0

# ❌ BAD: Not waiting for navigation
search_box = page.locator("textarea[aria-label='Suche']")
await search_box.fill("Playwright")
await page.locator("button:has-text('Google Suche')").click()
# Page might still be loading!
```

---

## 🐛 Error Handling & Debugging

### Use Verbose Assertions

```python
# ✅ GOOD: Clear assertion messages
elements = page.locator("nav a")
count = await elements.count()
assert count > 0, f"Expected at least 1 navigation link, found {count}"

# ❌ BAD: Unhelpful assertion message
assert count > 0  # Why did it fail? How many were there?
```

### Add Debugging Context

```python
# ✅ GOOD: Capture page state on failure
async def test_search_results_display(self, page: Page):
    await page.goto("https://www.google.de", wait_until="networkidle")
    search_box = page.locator("textarea[aria-label='Suche']")

    try:
        assert await search_box.is_visible()
    except AssertionError:
        # Capture page state for debugging
        await page.screenshot(path="debug_screenshot.png")
        print("Page content:", await page.content())
        raise

# ✅ GOOD: Use pytest fixtures for screenshots
@pytest.fixture
async def take_screenshot(page: Page):
    def _take_screenshot(name: str):
        return page.screenshot(path=f"screenshots/{name}.png")
    return _take_screenshot

async def test_something(self, page: Page, take_screenshot):
    # ... test code ...
    await take_screenshot("before_click")
    await element.click()
    await take_screenshot("after_click")
```

### Test Both Happy Path & Error Cases

```python
# ✅ GOOD: Test both success and failure
class TestSearch:
    async def test_valid_search_returns_results(self, page: Page):
        # Happy path
        await page.goto("https://example.com")
        await page.fill("input[name='q']", "valid query")
        await page.click("button[type='submit']")

        results = page.locator(".result")
        assert await results.count() > 0

    async def test_empty_search_shows_error(self, page: Page):
        # Error case
        await page.goto("https://example.com")
        await page.click("button[type='submit']")  # No input filled

        error_msg = page.locator(".error-message")
        assert await error_msg.is_visible()
```

---

## 🐳 Docker Best Practices

### Use .gitignore to Exclude Docker Artifacts

```
# .gitignore example
__pycache__/
*.pyc
.pytest_cache/
test-results/
htmlreport/
.venv/
.vscode/
.idea/
.DS_Store
```

### Optimize Docker Image Size

```dockerfile
# ✅ GOOD: Single RUN command (fewer layers)
RUN apt-get update && apt-get install -y \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    && rm -rf /var/lib/apt/lists/*  # Clean up

# ❌ BAD: Multiple RUN commands (unnecessary layers)
RUN apt-get update
RUN apt-get install -y python3.13
RUN apt-get install -y python3.13-dev
RUN rm -rf /var/lib/apt/lists/*
```

### Use --rm Flag in Docker Compose

```yaml
# ✅ GOOD: Auto-remove container after execution
docker-compose run --rm playwright pytest

# ❌ BAD: Containers pile up
docker-compose run playwright pytest  # Leaves stopped containers
```

### Set Resource Limits

```yaml
# ✅ GOOD: Docker Compose with resource limits
services:
  playwright:
    image: ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 📊 Performance Optimization

### Use Session-Scoped Browser

```python
# ✅ GOOD: Browser reused (fast)
@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser

# Result: 100 tests = 1 browser launch (~5 seconds)
```

### Parallelize Tests

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with 4 workers
pytest -n 4 tests/

# Result: 100 tests → ~25 tests/worker
```

### Use Appropriate Viewport Size

```python
# ✅ GOOD: Standard viewport (fast, representative)
context = await browser.new_context(
    viewport={"width": 1280, "height": 720}
)

# ⚠️ CAUTION: Mobile viewport (slower, more data)
context = await browser.new_context(
    device="iPhone 12"  # Includes realistic network throttling
)
```

---

## 🚀 CI/CD Integration Best Practices

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: |
          cd examples/python-uv-3.13
          docker-compose build --no-cache

      - name: Run tests
        run: |
          cd examples/python-uv-3.13
          docker-compose run --rm playwright pytest -v

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: examples/python-uv-3.13/htmlreport/
```

### Use Matrix Strategy for Multiple Versions

```yaml
# Test across Python versions
strategy:
  matrix:
    python-version: ['3.12', '3.13', '3.14']

steps:
  - run: |
      docker build \
        --build-arg PYTHON_VERSION=${{ matrix.python-version }} \
        -t playwright:${{ matrix.python-version }} \
        .
```

### Fail Fast on Critical Tests

```yaml
# Mark critical tests
@pytest.mark.critical
async def test_login_works(self, page: Page):
    # This test must pass before other tests
    pass

# Run in CI
pytest -m critical tests/
pytest -m "not critical" tests/
```

---

## 📝 Documentation Best Practices

### Document Test Purpose

```python
# ✅ GOOD: Clear docstring
async def test_google_search_button_visible(self, page: Page):
    """
    Verify that the Google search button is visible on the homepage.

    This test ensures the search button is discoverable and clickable
    for users, which is critical for search functionality.
    """
    await page.goto("https://www.google.de", wait_until="networkidle")
    button = page.locator("button:has-text('Google Suche')")
    assert await button.is_visible()

# ❌ BAD: No explanation
async def test_button_visible(self, page: Page):
    await page.goto("https://www.google.de")
    button = page.locator("button")
    assert button  # What button? Why?
```

### Document Assumptions

```python
# ✅ GOOD: Clear assumptions
async def test_logged_in_user_sees_dashboard(self, page: Page):
    """
    Assumes user is already logged in.

    This test verifies dashboard content for authenticated users.
    For login tests, see test_authentication.py
    """
    await page.goto("https://example.com/dashboard")
    title = page.locator("h1:has-text('Dashboard')")
    assert await title.is_visible()
```

---

## 🔒 Security Best Practices

### Don't Store Credentials in Tests

```python
# ❌ BAD: Hardcoded credentials
await page.fill("input[name='password']", "admin123")

# ✅ GOOD: Use environment variables
import os
password = os.getenv("TEST_PASSWORD")
await page.fill("input[name='password']", password)
```

### Use .gitignore for Sensitive Files

```
# Don't commit these
.env
.env.local
secrets/
test-credentials.json
```

### Clean Up Test Data

```python
# ✅ GOOD: Clean up after test
@pytest.fixture
async def test_user(page: Page):
    # Create test user
    user_id = await create_test_user()
    yield user_id
    # Clean up
    await delete_test_user(user_id)
```

---

## 🎓 Common Mistakes & How to Avoid Them

### Mistake 1: Flaky Tests with Arbitrary Sleeps

```python
# ❌ BAD: Flaky (race condition)
await page.click("button")
time.sleep(2)
assert await page.title() == "New Page"

# ✅ GOOD: Reliable (waits properly)
await page.click("button")
await page.wait_for_url("**/new-page")
assert await page.title() == "New Page"
```

### Mistake 2: Tightly Coupled to Implementation

```python
# ❌ BAD: Implementation detail (breaks when HTML changes)
form = page.locator("div[class='login-form-container-wrapper-main']")

# ✅ GOOD: User-facing (resilient to HTML changes)
form = page.locator("form:has-text('Login')")
```

### Mistake 3: Not Waiting for Elements

```python
# ❌ BAD: Element might not exist yet
buttons = page.locator("button")
button = buttons.first
await button.click()

# ✅ GOOD: Wait for element to be actionable
button = page.locator("button:first")
await button.click()  # Built-in waiting
```

### Mistake 4: Shared State Between Tests

```python
# ❌ BAD: Tests depend on each other
class TestSequence:
    async def test_1_create_item(self, page: Page):
        # Creates item

    async def test_2_verify_item_exists(self, page: Page):
        # Depends on test_1 running first!

# ✅ GOOD: Independent tests
class TestItem:
    async def test_create_and_verify_item(self, page: Page):
        # Both create and verify in one test
        # Or use fixtures to isolate
```

---

## 🔗 Related Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design and Docker setup
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Common issues and solutions
- **[Playwright Docs](https://playwright.dev/python/)** — Official API reference

---

**Last Updated**: January 2025
**For**: running-playwright-tests-in-docker-container repository
