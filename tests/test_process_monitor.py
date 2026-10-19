"""Tests for the process monitor service (ProcessMonitor)."""

from windows_mcp.monitor import (
    clear_baseline,
    diff_processes,
    snapshot_processes,
    watch_processes,
)


class TestProcessMonitor:
    def setup_method(self):
        clear_baseline()

    def test_snapshot_establishes_baseline(self):
        result = snapshot_processes(limit=5)
        assert "进程快照" in result

    def test_diff_without_baseline(self):
        clear_baseline()
        result = diff_processes()
        assert "Error" in result and "基线" in result

    def test_diff_after_snapshot(self):
        snapshot_processes(limit=5)
        result = diff_processes()
        # Either reports changes or reports none — never an error.
        assert "Error" not in result

    def test_watch_invalid_duration(self):
        assert "Error" in watch_processes(duration=0)
        assert "Error" in watch_processes(duration=301)

    def test_clear(self):
        snapshot_processes(limit=5)
        assert "已清除" in clear_baseline()
        assert "Error" in diff_processes()
