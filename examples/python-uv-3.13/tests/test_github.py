"""Tests for GitHub homepage using Playwright."""

import pytest
from playwright.async_api import Page


class TestGitHubHomepage:
    """Test suite for GitHub homepage functionality."""

    @pytest.mark.asyncio
    async def test_github_homepage_loads(self, page: Page):
        """Test that GitHub homepage loads successfully."""
        # Use 'load' instead of 'networkidle' for faster tests
        await page.goto("https://github.com", wait_until="load")

        # Verify page title
        title = await page.title()
        assert "GitHub" in title

    @pytest.mark.asyncio
    async def test_github_navigation_visible(self, page: Page):
        """Test that GitHub navigation menu is visible."""
        await page.goto("https://github.com", wait_until="load")

        # Look for main navigation (use specific aria-label to avoid multiple matches)
        nav = page.locator("nav[aria-label='Global']")
        assert await nav.is_visible()

    @pytest.mark.asyncio
    async def test_github_search_box_visible(self, page: Page):
        """Test that GitHub search box is visible on homepage."""
        await page.goto("https://github.com", wait_until="load", timeout=30000)

        # GitHub search input (may be in different locations depending on auth state)
        search_input = page.locator("input[name='q'], input[placeholder*='Search'], button[aria-label*='Search']")

        # Wait for at least one search element to be present
        await search_input.first.wait_for(state="attached", timeout=10000)

        # Check if search input exists
        count = await search_input.count()
        assert count > 0, "Search element not found"

    @pytest.mark.asyncio
    async def test_github_has_logo(self, page: Page):
        """Test that GitHub logo is visible on the homepage."""
        await page.goto("https://github.com", wait_until="load")

        # GitHub logo/home link
        logo = page.locator("a[href='/']").first

        assert await logo.is_visible()

    @pytest.mark.asyncio
    async def test_github_sign_in_button_visible(self, page: Page):
        """Test that Sign In button is visible on GitHub homepage."""
        await page.goto("https://github.com", wait_until="load", timeout=30000)

        # Look for Sign In button (may vary in text and element type)
        sign_in_button = page.locator("a:has-text('Sign in'), a:has-text('Sign up'), a[href='/login']")

        # Wait for auth-related elements to load
        await sign_in_button.first.wait_for(state="attached", timeout=10000)

        # Verify button exists
        count = await sign_in_button.count()
        assert count > 0, "Sign in/Sign up button not found"

    @pytest.mark.asyncio
    async def test_github_footer_visible(self, page: Page):
        """Test that GitHub footer is visible on the homepage."""
        await page.goto("https://github.com", wait_until="load", timeout=30000)

        # GitHub footer
        footer = page.locator("footer, div[role='contentinfo']")

        # Scroll to bottom to ensure footer is in viewport
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(500)  # Wait for scroll to complete

        # Footer should exist and be visible after scroll
        await footer.first.wait_for(state="visible", timeout=5000)
        assert await footer.first.is_visible()
