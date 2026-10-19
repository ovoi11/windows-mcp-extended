"""Tests for the programs-by-size service (InstalledProgramsBySize)."""

from windows_mcp.system import programs_by_size


class TestProgramsBySize:
    def test_returns_text(self):
        result = programs_by_size(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
