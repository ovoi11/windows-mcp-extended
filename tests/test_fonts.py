"""Tests for the installed fonts service (InstalledFonts)."""

from windows_mcp.system import installed_fonts


class TestInstalledFonts:
    def test_returns_text(self):
        result = installed_fonts(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
