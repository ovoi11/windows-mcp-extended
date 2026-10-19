"""Tests for the domain membership service (DomainMembership)."""

from windows_mcp.system import domain_membership


class TestDomainMembership:
    def test_returns_text(self):
        result = domain_membership()
        assert isinstance(result, str)
        assert result.strip() != ""
