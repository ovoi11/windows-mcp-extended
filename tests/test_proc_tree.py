"""Tests for the process tree service (ProcessTree)."""

from windows_mcp.system import process_tree


class TestProcessTree:
    def test_returns_text(self):
        result = process_tree(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
