"""Pytest configuration and fixtures for Playwright tests."""

import pytest
from playwright.async_api import async_playwright, Browser, Page, BrowserContext


@pytest.fixture(scope="session")
async def browser() -> Browser:
    """Create and manage a browser instance for the test session."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        yield browser
        await browser.close()


@pytest.fixture
async def context(browser: Browser) -> BrowserContext:
    """Create a new browser context for each test."""
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
    )
    yield context
    await context.close()


@pytest.fixture
async def page(context: BrowserContext) -> Page:
    """Create a new page for each test."""
    page = await context.new_page()
    yield page
    await page.close()
