"""Tests for the recycle bin service (RecycleBinInfo)."""

from windows_mcp.system import recycle_bin_info


class TestRecycleBinInfo:
    def test_returns_text(self):
        result = recycle_bin_info()
        assert isinstance(result, str)
        assert result.strip() != ""
