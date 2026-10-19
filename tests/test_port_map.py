"""Tests for the port-process map service (PortProcessMap)."""

from windows_mcp.system import port_process_map


class TestPortProcessMap:
    def test_returns_text(self):
        result = port_process_map(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_port_filter(self):
        result = port_process_map(port=135, limit=5)
        assert isinstance(result, str)
