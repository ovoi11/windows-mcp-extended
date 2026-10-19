"""Tests for the network connection summary service (NetworkConnectionSummary)."""

from windows_mcp.system import network_connection_summary


class TestNetworkConnectionSummary:
    def test_returns_text(self):
        result = network_connection_summary()
        assert isinstance(result, str)
        assert result.strip() != ""
