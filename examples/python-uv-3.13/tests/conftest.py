"""Pytest configuration and fixtures for Playwright tests."""

import pytest
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


@pytest.fixture(scope="session")
async def browser() -> Browser:
    """Create and manage a browser instance for the test session.

    Configured with Docker-optimized settings:
    - --no-sandbox: Required for Docker root user execution
    - --disable-setuid-sandbox: Prevents sandboxing issues in containers
    - --disable-dev-shm-usage: Prevents shared memory issues in Docker
    - --disable-gpu: Disables GPU acceleration (not needed for headless)
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                # Essential for Docker environments
                "--no-sandbox",
                "--disable-setuid-sandbox",
                # Prevent shared memory issues
                "--disable-dev-shm-usage",
                # Performance optimizations for headless
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-extensions",
            ],
            # Set reasonable timeout for browser launch (30 seconds)
            timeout=30000,
        )
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> BrowserContext:
    """Create a new browser context for each test.

    Configured with reasonable timeouts for Docker environment.
    """
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        # Set default navigation timeout (20 seconds)
        # Individual tests can override if needed
    )
    # Set default timeout for actions in this context
    context.set_default_navigation_timeout(20000)  # 20 seconds
    context.set_default_timeout(10000)  # 10 seconds for other actions

    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> Page:
    """Create a new page for each test."""
    page = await context.new_page()
    yield page
    await page.close()
