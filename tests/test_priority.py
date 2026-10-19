"""Tests for the process priority service (ProcessPriority).

NOTE: 待测试点 — set_priority mutates a live process; tests cover the
read-only list path and validation only.
"""

from windows_mcp.system import list_priorities, set_priority


class TestProcessPriority:
    def test_list_returns_text(self):
        result = list_priorities(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_set_invalid_priority(self):
        result = set_priority(1, "realtime")  # type: ignore[arg-type]
        assert "Error" in result

    def test_set_missing_pid(self):
        result = set_priority(99999999, "normal")
        assert "No process" in result or "Error" in result
