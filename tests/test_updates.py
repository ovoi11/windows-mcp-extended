"""Tests for the installed updates service (InstalledUpdates)."""

from windows_mcp.system import list_updates


class TestInstalledUpdates:
    def test_returns_text(self):
        result = list_updates(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
