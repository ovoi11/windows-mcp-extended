"""Tests for the process command line service (ProcessCommandLine)."""

from windows_mcp.system import list_process_command_lines


class TestProcessCommandLine:
    def test_returns_text(self):
        result = list_process_command_lines(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_name_filter(self):
        result = list_process_command_lines(name="__windows_mcp_no_such_proc__", limit=5)
        assert isinstance(result, str)
