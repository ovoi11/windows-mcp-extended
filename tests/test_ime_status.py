"""Tests for the IME status service (ImeStatus)."""

from windows_mcp.system import ime_status


class TestImeStatus:
    def test_returns_layout(self):
        result = ime_status()
        assert isinstance(result, str)
        assert "键盘布局" in result

    def test_has_language_id(self):
        result = ime_status()
        assert "语言 ID" in result
