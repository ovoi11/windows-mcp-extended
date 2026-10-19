"""Tests for the remote desktop service (RemoteDesktopStatus)."""

from windows_mcp.system import remote_desktop_status


class TestRemoteDesktopStatus:
    def test_returns_text(self):
        result = remote_desktop_status()
        assert isinstance(result, str)
        assert result.strip() != ""
