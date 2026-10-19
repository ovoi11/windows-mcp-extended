"""Tests for the locale service (LocaleInfo)."""

from windows_mcp.system import locale_info


class TestLocaleInfo:
    def test_returns_text(self):
        result = locale_info()
        assert isinstance(result, str)
        assert result.strip() != ""
