"""Pytest configuration with FUNCTION-SCOPED fixtures (testing hypothesis)."""

import pytest
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


@pytest.fixture
async def browser():
    """Create and manage a browser instance for EACH TEST (function scope).

    This avoids session-scoped async fixture issues with pytest-asyncio.
    """
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            headless=True,
            timeout=30000,  # 30 second browser launch timeout
        )
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser):
    """Create a new browser context for each test."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
    )
    context.set_default_navigation_timeout(20000)  # 20 seconds
    context.set_default_timeout(10000)  # 10 seconds for other actions

    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext):
    """Create a new page for each test."""
    page = await context.new_page()
    yield page
    await page.close()
