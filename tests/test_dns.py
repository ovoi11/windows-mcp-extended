"""Tests for the DNS lookup service (DnsLookup)."""

from windows_mcp.system import dns_lookup


class TestDnsLookup:
    def test_missing_host(self):
        assert "Error" in dns_lookup("")

    def test_localhost_resolves(self):
        result = dns_lookup("localhost")
        assert isinstance(result, str)
        assert result.strip() != ""
