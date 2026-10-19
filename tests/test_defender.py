"""Tests for the Defender status service (WindowsDefenderStatus)."""

from windows_mcp.system import defender_status


class TestDefenderStatus:
    def test_returns_text(self):
        result = defender_status()
        assert isinstance(result, str)
        assert result.strip() != ""
