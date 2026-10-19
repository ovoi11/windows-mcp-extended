"""Tests for the crash report service (CrashReportList)."""

from windows_mcp.system import crash_report_list


class TestCrashReportList:
    def test_returns_text(self):
        result = crash_report_list(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
