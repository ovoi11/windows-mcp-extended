"""Tests for the mapped drives service (MappedDrives)."""

from windows_mcp.system import mapped_drives


class TestMappedDrives:
    def test_returns_text(self):
        result = mapped_drives()
        assert isinstance(result, str)
        assert result.strip() != ""
