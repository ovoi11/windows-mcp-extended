"""Tests for the mouse position service (MousePosition)."""

from windows_mcp.desktop import mouse_position


class TestMousePosition:
    def test_returns_text(self):
        result = mouse_position()
        assert isinstance(result, str)
        assert result.strip() != ""
