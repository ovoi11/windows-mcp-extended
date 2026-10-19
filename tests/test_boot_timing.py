"""Tests for the boot timing service (BootTiming)."""

from windows_mcp.system import boot_timing


class TestBootTiming:
    def test_returns_text(self):
        result = boot_timing()
        assert isinstance(result, str)
        assert result.strip() != ""
