"""Tests for the browser extensions service (BrowserExtensions)."""

from windows_mcp.system import browser_extensions


class TestBrowserExtensions:
    def test_returns_text(self):
        result = browser_extensions(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
