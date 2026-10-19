"""Tests for the keyboard layouts service (KeyboardLayouts)."""

from windows_mcp.system import list_keyboard_layouts


class TestKeyboardLayouts:
    def test_returns_text(self):
        result = list_keyboard_layouts()
        assert isinstance(result, str)
        assert result.strip() != ""
