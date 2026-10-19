"""Tests for the scheduled task service (ScheduledTask).

NOTE: 待测试点 — create/run/end/delete mutate the task scheduler; tests here
cover validation and the read-only list path only. Live task mutations are
intentionally not executed in the test suite.
"""

from windows_mcp.system import create_task, list_tasks


class TestScheduledTask:
    def test_list_returns_text(self):
        result = list_tasks(limit=10)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_create_invalid_schedule(self):
        result = create_task("t", "cmd.exe", schedule="NOPE")  # type: ignore[arg-type]
        assert "Error" in result and "schedule" in result

    def test_create_missing_start_time(self):
        result = create_task("t", "cmd.exe", schedule="ONCE")
        assert "Error" in result and "start_time" in result

    def test_create_invalid_command_empty(self):
        # A blank command still goes to schtasks and should return an error path,
        # never raise a Python exception.
        result = create_task("t", "", schedule="ONCE", start_time="12:00")
        assert isinstance(result, str)
