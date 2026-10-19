"""Tests for the process detail service (ProcessDetail)."""

from windows_mcp.system import process_detail


class TestProcessDetail:
    def test_needs_pid_or_name(self):
        assert "Error" in process_detail()

    def test_invalid_pid(self):
        result = process_detail(pid=999999999)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_current_process(self):
        import os

        result = process_detail(pid=os.getpid())
        assert "进程详情" in result
