"""Tests for the USB history service (USBDeviceHistory)."""

from windows_mcp.system import usb_device_history


class TestUsbDeviceHistory:
    def test_returns_text(self):
        result = usb_device_history(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
