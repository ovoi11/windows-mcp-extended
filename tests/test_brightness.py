"""Tests for the brightness service (DisplayBrightness)."""

from windows_mcp.system import brightness_status


class TestDisplayBrightness:
    def test_returns_text(self):
        result = brightness_status()
        assert isinstance(result, str)
        assert result.strip() != ""
