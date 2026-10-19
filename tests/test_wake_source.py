"""Tests for the wake source service (WakeSourceInfo)."""

from windows_mcp.system import wake_source_info


class TestWakeSourceInfo:
    def test_returns_text(self):
        result = wake_source_info()
        assert isinstance(result, str)
        assert result.strip() != ""
