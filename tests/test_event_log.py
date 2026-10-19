"""Tests for the event log service (EventLogReader).

NOTE: 待测试点 — reading the Security log may require administrator rights;
tests cover parameter validation and the Application/System log read paths only.
"""

from windows_mcp.system import read_event_log


class TestEventLogReader:
    def test_invalid_log_name(self):
        result = read_event_log(log="NotALog")
        assert "Error" in result

    def test_system_log_read(self):
        result = read_event_log(log="System", max_events=3)
        # Either returns events or a readable error — never crashes.
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_application_log_level_filter(self):
        result = read_event_log(log="Application", max_events=5, level="error")
        assert isinstance(result, str)

    def test_source_filter(self):
        result = read_event_log(log="System", max_events=5, source="xyz")
        assert isinstance(result, str)
