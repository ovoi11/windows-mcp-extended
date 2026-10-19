"""Tests for the installed apps service (InstalledApps)."""

from windows_mcp.system import list_apps


class TestInstalledApps:
    def test_list_returns_text(self):
        result = list_apps(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_name_filter(self):
        result = list_apps(name="__windows_mcp_no_such_app__", limit=5)
        assert isinstance(result, str)
        assert "No applications" in result or "没有" in result

    def test_include_hidden_flag(self):
        result = list_apps(limit=5, include_hidden=True)
        assert isinstance(result, str)
