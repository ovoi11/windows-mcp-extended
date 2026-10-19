"""Tests for the system status service (SystemStatus)."""

from windows_mcp.system import system_status


class TestSystemStatus:
    def test_returns_summary(self):
        result = system_status()
        assert isinstance(result, str)
        assert "CPU" in result

    def test_has_memory_row(self):
        result = system_status()
        assert "内存" in result

    def test_has_uptime_row(self):
        result = system_status()
        assert "开机时间" in result
