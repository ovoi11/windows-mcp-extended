"""Tests for the auto-logon service (AutoLogonCheck)."""

from windows_mcp.system import auto_logon_check


class TestAutoLogonCheck:
    def test_returns_text(self):
        result = auto_logon_check()
        assert isinstance(result, str)
        assert result.strip() != ""
