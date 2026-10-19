"""Tests for the firewall status service (FirewallStatus)."""

from windows_mcp.system import firewall_status


class TestFirewallStatus:
    def test_returns_text(self):
        result = firewall_status()
        assert isinstance(result, str)
        assert result.strip() != ""
