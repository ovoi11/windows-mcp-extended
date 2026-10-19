"""Tests for the disk I/O service (DiskIOStats)."""

from windows_mcp.system import disk_io_stats


class TestDiskIOStats:
    def test_returns_text(self):
        result = disk_io_stats(interval=0.2)
        assert isinstance(result, str)
        assert result.strip() != ""
