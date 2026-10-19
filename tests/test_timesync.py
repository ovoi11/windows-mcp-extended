"""Tests for the time sync service (TimeSyncInfo)."""

from windows_mcp.system import time_sync_status


class TestTimeSyncInfo:
    def test_returns_text(self):
        result = time_sync_status()
        assert isinstance(result, str)
        assert result.strip() != ""
