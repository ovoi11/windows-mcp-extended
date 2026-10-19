"""Tests for the recent files service (RecentFiles)."""

from windows_mcp.system import recent_files


class TestRecentFiles:
    def test_returns_text(self):
        result = recent_files(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
