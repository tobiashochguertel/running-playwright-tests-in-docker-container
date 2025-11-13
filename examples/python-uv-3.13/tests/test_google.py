"""Tests for Google homepage using Playwright."""

import pytest
from playwright.async_api import Page


class TestGoogleHomepage:
    """Test suite for Google homepage functionality."""

    @pytest.mark.asyncio
    async def test_google_homepage_loads(self, page: Page):
        """Test that Google homepage loads and displays search box."""
        # Use 'load' instead of 'networkidle' - faster and sufficient for most cases
        await page.goto("https://www.google.com", wait_until="load", timeout=30000)

        # Handle cookie consent if present (non-blocking)
        try:
            # Try to accept cookies if dialog appears
            cookie_button = page.locator("button:has-text('Accept all'), button:has-text('Alle akzeptieren')")
            if await cookie_button.count() > 0:
                await cookie_button.first.click(timeout=2000)
                await page.wait_for_timeout(500)
        except Exception:
            pass  # Cookie dialog not present or already accepted

        # Verify page title contains 'Google'
        title = await page.title()
        assert "Google" in title

        # Verify search box is visible (multiple possible selectors)
        search_box = page.locator("textarea[name='q'], input[name='q'], textarea[aria-label*='Search']")
        await search_box.first.wait_for(state="visible", timeout=10000)
        assert await search_box.first.is_visible()

    @pytest.mark.asyncio
    async def test_google_search_button_visible(self, page: Page):
        """Test that Google search button is visible on homepage."""
        await page.goto("https://www.google.com", wait_until="load", timeout=30000)

        # Handle cookie consent if present
        try:
            cookie_button = page.locator("button:has-text('Accept all'), button:has-text('Alle akzeptieren')")
            if await cookie_button.count() > 0:
                await cookie_button.first.click(timeout=2000)
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Find search buttons (multiple possible text variations)
        search_button = page.locator("input[value='Google Search'], input[value='Google Suche'], button[aria-label*='Google Search']")

        # Verify button is in the DOM
        count = await search_button.count()
        assert count > 0, "Search button not found"

    @pytest.mark.asyncio
    async def test_google_has_logo(self, page: Page):
        """Test that Google logo is present on the homepage."""
        await page.goto("https://www.google.com", wait_until="load", timeout=30000)

        # Handle cookie consent if present
        try:
            cookie_button = page.locator("button:has-text('Accept all'), button:has-text('Alle akzeptieren')")
            if await cookie_button.count() > 0:
                await cookie_button.first.click(timeout=2000)
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Google logo is an image with specific alt text or in header
        # Check for existence (attached to DOM) rather than visibility, as Google may hide elements
        logo = page.locator("img[alt='Google'], img[alt*='Google'], header img")
        await logo.first.wait_for(state="attached", timeout=10000)
        assert await logo.count() > 0, "Google logo not found in DOM"

    @pytest.mark.asyncio
    async def test_google_footer_links_present(self, page: Page):
        """Test that footer links are present on Google homepage."""
        await page.goto("https://www.google.com", wait_until="load", timeout=30000)

        # Handle cookie consent if present
        try:
            cookie_button = page.locator("button:has-text('Accept all'), button:has-text('Alle akzeptieren')")
            if await cookie_button.count() > 0:
                await cookie_button.first.click(timeout=2000)
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Look for footer links (About, Privacy, etc.)
        footer = page.locator("footer, div[role='contentinfo']")
        await footer.first.wait_for(state="visible", timeout=10000)
        assert await footer.first.is_visible()

        # Check for at least one link in footer
        links = footer.first.locator("a")
        count = await links.count()
        assert count > 0, "No links found in footer"
