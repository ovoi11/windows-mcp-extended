"""Tests for the network adapters service (NetworkAdapters)."""

from windows_mcp.system import network_adapters


class TestNetworkAdapters:
    def test_returns_text(self):
        result = network_adapters(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
