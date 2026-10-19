"""Tests for the file watcher service (WatchFile)."""

import os

from windows_mcp.monitor import clear_file_baseline, watch_path


class TestWatchFile:
    def setup_method(self):
        clear_file_baseline()

    def test_missing_path(self):
        result = watch_path(r"C:\__windows_mcp_no_such_dir__", duration=1)
        assert "Error" in result

    def test_invalid_duration(self):
        result = watch_path(os.getcwd(), duration=0)
        assert "Error" in result

    def test_establishes_baseline(self):
        # Duration is short; the first call just records a baseline.
        result = watch_path(os.getcwd(), duration=1, recursive=False)
        assert "基线" in result

    def test_clear_baseline(self):
        assert "已清除" in clear_file_baseline()
