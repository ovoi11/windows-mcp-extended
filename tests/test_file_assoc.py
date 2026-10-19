"""Tests for the file association service (FileAssociations)."""

from windows_mcp.system import list_associations


class TestFileAssociations:
    def test_list_returns_text(self):
        result = list_associations(limit=10)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_extension_filter(self):
        result = list_associations(extension="txt", limit=5)
        assert isinstance(result, str)

    def test_dotted_extension(self):
        result = list_associations(extension=".txt", limit=5)
        assert isinstance(result, str)

    def test_missing_extension(self):
        result = list_associations(extension="__windows_mcp_no_such_ext__", limit=5)
        assert isinstance(result, str)
