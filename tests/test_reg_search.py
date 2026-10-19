"""Tests for the registry search service (RegistrySearch)."""

from windows_mcp.system import search_registry


class TestRegistrySearch:
    def test_missing_keyword(self):
        assert "Error" in search_registry("")

    def test_returns_text(self):
        result = search_registry("windows", root="hkcu", limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
