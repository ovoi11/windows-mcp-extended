"""Tests for the page file service (PageFileInfo)."""

from windows_mcp.system import pagefile_info


class TestPageFileInfo:
    def test_returns_text(self):
        result = pagefile_info()
        assert isinstance(result, str)
        assert result.strip() != ""
