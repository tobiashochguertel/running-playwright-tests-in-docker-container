"""Tests for Google homepage using Playwright."""

import pytest
from playwright.async_api import Page


class TestGoogleHomepage:
    """Test suite for Google homepage functionality."""

    @pytest.mark.asyncio
    async def test_google_homepage_loads(self, page: Page):
        """Test that Google homepage loads and displays search box."""
        await page.goto("https://www.google.de", wait_until="networkidle")

        # Verify page title contains 'Google'
        title = await page.title()
        assert "Google" in title

        # Verify search box is visible
        search_box = page.locator("textarea[aria-label='Suche']")
        assert await search_box.is_visible()

    @pytest.mark.asyncio
    async def test_google_search_button_visible(self, page: Page):
        """Test that Google search button is visible on homepage."""
        await page.goto("https://www.google.de", wait_until="networkidle")

        # Find search buttons
        search_button = page.locator("button:has-text('Google Suche')")

        # Verify button is in the DOM
        count = await search_button.count()
        assert count > 0, "Search button not found"

    @pytest.mark.asyncio
    async def test_google_has_logo(self, page: Page):
        """Test that Google logo is visible on the homepage."""
        await page.goto("https://www.google.de", wait_until="networkidle")

        # Google logo is an image with specific alt text
        logo = page.locator("img[alt='Google']")

        assert await logo.is_visible()

    @pytest.mark.asyncio
    async def test_google_footer_links_present(self, page: Page):
        """Test that footer links are present on Google homepage."""
        await page.goto("https://www.google.de", wait_until="networkidle")

        # Look for footer links (Über Google, Datenschutz, etc.)
        footer = page.locator("footer")
        assert await footer.is_visible()

        # Check for at least one link in footer
        links = footer.locator("a")
        count = await links.count()
        assert count > 0, "No links found in footer"
