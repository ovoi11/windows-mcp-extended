"""Tests for the firewall rules service (FirewallRules)."""

from windows_mcp.system import firewall_rules


class TestFirewallRules:
    def test_invalid_action(self):
        assert "Error" in firewall_rules(action="bogus")  # type: ignore[arg-type]

    def test_returns_text(self):
        result = firewall_rules(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
