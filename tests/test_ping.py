"""Tests for the ping service (NetworkLatency).

NOTE: 待测试点 — sends real ICMP traffic; tests cover validation and localhost.
"""

from windows_mcp.system import ping_host


class TestNetworkLatency:
    def test_missing_host(self):
        assert "Error" in ping_host("")

    def test_localhost(self):
        result = ping_host("127.0.0.1", count=1, timeout_ms=500)
        assert isinstance(result, str)
        assert result.strip() != ""
