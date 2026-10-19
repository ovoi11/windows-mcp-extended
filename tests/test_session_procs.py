"""Tests for the session processes service (SessionProcesses)."""

from windows_mcp.system import session_processes


class TestSessionProcesses:
    def test_returns_text(self):
        result = session_processes(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
