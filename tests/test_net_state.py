"""Tests for the network state service (NetState).

NOTE: 待测试点 — connection enumeration may be restricted without
administrator rights; tests cover the format contract and the stats path.
"""

from windows_mcp.monitor import list_connections, net_stats


class TestNetState:
    def test_connections_returns_text(self):
        result = list_connections(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_connections_state_filter(self):
        result = list_connections(state="LISTEN", limit=5)
        assert isinstance(result, str)

    def test_stats_returns_adapters(self):
        result = net_stats()
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_negative_limit_safe(self):
        result = list_connections(limit=-1)
        assert isinstance(result, str)
