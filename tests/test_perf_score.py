"""Tests for the WinSAT score service (SystemPerformanceScore)."""

from windows_mcp.system import system_performance_score


class TestSystemPerformanceScore:
    def test_returns_text(self):
        result = system_performance_score()
        assert isinstance(result, str)
        assert result.strip() != ""
