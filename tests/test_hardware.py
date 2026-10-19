"""Tests for the hardware inventory service (HardwareInventory)."""

from windows_mcp.system import hardware_inventory


class TestHardwareInventory:
    def test_returns_text(self):
        result = hardware_inventory()
        assert isinstance(result, str)
        assert result.strip() != ""
