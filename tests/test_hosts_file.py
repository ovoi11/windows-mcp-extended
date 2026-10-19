"""Tests for the hosts file service (HostsFile)."""

from windows_mcp.system import read_hosts


class TestHostsFile:
    def test_read_returns_text(self):
        result = read_hosts()
        assert isinstance(result, str)
        assert result.strip() != ""
