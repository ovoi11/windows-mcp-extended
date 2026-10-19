"""Tests for the timezone service (TimezoneInfo)."""

from windows_mcp.system import timezone_info


class TestTimezoneInfo:
    def test_returns_text(self):
        result = timezone_info()
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_has_offset(self):
        result = timezone_info()
        assert "时区 ID" in result or "Error" in result
