"""Tests for the network shares service (NetworkShares)."""

from windows_mcp.system import list_shares


class TestNetworkShares:
    def test_returns_text(self):
        result = list_shares(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
