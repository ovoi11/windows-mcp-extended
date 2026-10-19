"""Tests for the elevation / UAC service (ElevationControl)."""

from windows_mcp.system import (
    check_elevation_status,
    elevate_process,
    verify_process_elevation,
)


class TestElevation:
    def test_status_returns_uac_line(self):
        result = check_elevation_status()
        assert "UAC" in result
        assert "提权状态" in result or "无法读取" in result

    def test_verify_missing_args(self):
        assert "Error" in verify_process_elevation()

    def test_verify_missing_process(self):
        result = verify_process_elevation(name="__no_such_process_xyz__")
        assert "Error" in result

    def test_elevate_missing_path(self):
        assert "Error" in elevate_process(r"C:\does\not\exist.exe")

    def test_elevate_missing_args_param(self):
        # No path => error before any ShellExecute call.
        assert "Error" in elevate_process("")
