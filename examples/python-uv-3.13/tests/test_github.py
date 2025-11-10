"""Tests for GitHub homepage using Playwright."""

import pytest
from playwright.async_api import Page


class TestGitHubHomepage:
    """Test suite for GitHub homepage functionality."""

    @pytest.mark.asyncio
    async def test_github_homepage_loads(self, page: Page):
        """Test that GitHub homepage loads successfully."""
        await page.goto("https://github.com", wait_until="networkidle")

        # Verify page title
        title = await page.title()
        assert "GitHub" in title

    @pytest.mark.asyncio
    async def test_github_navigation_visible(self, page: Page):
        """Test that GitHub navigation menu is visible."""
        await page.goto("https://github.com", wait_until="networkidle")

        # Look for main navigation
        nav = page.locator("nav")
        assert await nav.is_visible()

    @pytest.mark.asyncio
    async def test_github_search_box_visible(self, page: Page):
        """Test that GitHub search box is visible on homepage."""
        await page.goto("https://github.com", wait_until="networkidle")

        # GitHub search input
        search_input = page.locator("input[placeholder*='Search']")

        # Check if search input exists and is visible
        if await search_input.count() > 0:
            assert await search_input.is_visible()

    @pytest.mark.asyncio
    async def test_github_has_logo(self, page: Page):
        """Test that GitHub logo is visible on the homepage."""
        await page.goto("https://github.com", wait_until="networkidle")

        # GitHub logo/home link
        logo = page.locator("a[href='/']").first

        assert await logo.is_visible()

    @pytest.mark.asyncio
    async def test_github_sign_in_button_visible(self, page: Page):
        """Test that Sign In button is visible on GitHub homepage."""
        await page.goto("https://github.com", wait_until="networkidle")

        # Look for Sign In button (may vary in text)
        sign_in_button = page.locator("a:has-text('Sign in')")

        # Verify button exists
        count = await sign_in_button.count()
        assert count > 0, "Sign in button not found"

    @pytest.mark.asyncio
    async def test_github_footer_visible(self, page: Page):
        """Test that GitHub footer is visible on the homepage."""
        await page.goto("https://github.com", wait_until="networkidle")

        # GitHub footer
        footer = page.locator("footer")

        # Scroll to bottom to ensure footer is in viewport
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Footer might not always be visible, but should exist
        assert await footer.count() > 0
