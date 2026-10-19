"""Tests for the network throughput service (NetworkThroughput)."""

from windows_mcp.system import network_throughput


class TestNetworkThroughput:
    def test_returns_text(self):
        result = network_throughput(interval=0.2)
        assert isinstance(result, str)
        assert result.strip() != ""
