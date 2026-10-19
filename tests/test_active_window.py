"""Tests for the active window service (ActiveWindowInfo)."""

from windows_mcp.desktop import active_window_info


class TestActiveWindowInfo:
    def test_returns_text(self):
        result = active_window_info()
        assert isinstance(result, str)
        assert result.strip() != ""
