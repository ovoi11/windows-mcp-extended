"""Tests for the window list service (WindowList)."""

from windows_mcp.desktop import window_list


class TestWindowList:
    def test_returns_text(self):
        result = window_list(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
