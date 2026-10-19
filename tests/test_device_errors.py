"""Tests for the device errors service (HardwareDeviceErrors)."""

from windows_mcp.system import device_errors


class TestDeviceErrors:
    def test_returns_text(self):
        result = device_errors(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
