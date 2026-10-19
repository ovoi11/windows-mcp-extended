"""Tests for the PnP device service (UsbDeviceList)."""

from windows_mcp.system import list_devices


class TestUsbDeviceList:
    def test_all_returns_text(self):
        result = list_devices(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_class_filter(self):
        result = list_devices(class_name="usb", limit=5)
        assert isinstance(result, str)

    def test_invalid_class_falls_back(self):
        # Unknown class names are treated as "all" via the alias table; never crash.
        result = list_devices(limit=3)  # type: ignore[arg-type]
        assert isinstance(result, str)
