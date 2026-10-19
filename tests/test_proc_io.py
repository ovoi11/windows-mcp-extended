"""Tests for the process I/O service (ProcessIOStats)."""

from windows_mcp.system import process_io_stats


class TestProcessIOStats:
    def test_returns_text(self):
        result = process_io_stats(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
