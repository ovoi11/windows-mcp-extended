"""Tests for the system info service (SystemInfo)."""

from windows_mcp.system import system_info


class TestSystemInfo:
    def test_returns_text(self):
        result = system_info()
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_has_os_row(self):
        result = system_info()
        assert "操作系统" in result or "Error" in result
