"""Tests for the Windows license service (WindowsLicenseInfo)."""

from windows_mcp.system import windows_license_info


class TestWindowsLicenseInfo:
    def test_returns_text(self):
        result = windows_license_info()
        assert isinstance(result, str)
        assert result.strip() != ""
