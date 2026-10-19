"""Tests for the bluetooth devices service (BluetoothDevices)."""

from windows_mcp.system import bluetooth_devices


class TestBluetoothDevices:
    def test_returns_text(self):
        result = bluetooth_devices(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
