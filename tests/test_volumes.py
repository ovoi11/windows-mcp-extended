"""Tests for the storage volumes service (StorageVolumes)."""

from windows_mcp.system import list_volumes


class TestStorageVolumes:
    def test_returns_text(self):
        result = list_volumes()
        assert isinstance(result, str)
        assert result.strip() != ""
