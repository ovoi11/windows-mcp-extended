"""Tests for the drive health service (DriveSmartInfo)."""

from windows_mcp.system import drive_health


class TestDriveSmartInfo:
    def test_returns_text(self):
        result = drive_health(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
