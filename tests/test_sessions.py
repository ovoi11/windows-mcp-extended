"""Tests for the session info service (SessionInfo)."""

from windows_mcp.system import session_info


class TestSessionInfo:
    def test_returns_text(self):
        result = session_info(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
