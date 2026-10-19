"""Tests for the driver info service (DriverInfo)."""

from windows_mcp.system import list_drivers


class TestDriverInfo:
    def test_list_returns_text(self):
        result = list_drivers(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_name_filter(self):
        result = list_drivers(name="__windows_mcp_no_such_driver__", limit=5)
        assert isinstance(result, str)
