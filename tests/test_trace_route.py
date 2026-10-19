"""Tests for the trace route service (TraceRoute).

NOTE: 待测试点 — sends real ICMP probes; tests cover validation only.
"""

from windows_mcp.system import trace_route


class TestTraceRoute:
    def test_missing_host(self):
        assert "Error" in trace_route("")

    def test_localhost(self):
        result = trace_route("127.0.0.1", max_hops=5)
        assert isinstance(result, str)
        assert result.strip() != ""
