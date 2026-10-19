"""Tests for the Wi-Fi service (WifiManager)."""

from windows_mcp.system import wifi_networks, wifi_status


class TestWifiManager:
    def test_status_returns_text(self):
        result = wifi_status()
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_scan_returns_text(self):
        result = wifi_networks(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_scan_limit_safe(self):
        result = wifi_networks(limit=0)
        assert isinstance(result, str)
