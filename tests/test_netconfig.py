"""Tests for the network config service (NetworkConfig)."""

from windows_mcp.system import network_config


class TestNetworkConfig:
    def test_returns_text(self):
        result = network_config(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
