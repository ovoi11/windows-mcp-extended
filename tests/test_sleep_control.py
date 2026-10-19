"""Tests for the sleep prevention service (PreventSleep)."""

from windows_mcp.system import (
    disable_sleep_prevention,
    enable_sleep_prevention,
    get_sleep_prevention_status,
)


class TestSleepControl:
    def test_enable_disable_roundtrip(self):
        disable_sleep_prevention()
        assert "未启用" in get_sleep_prevention_status()
        enable_sleep_prevention()
        assert "已启用" in get_sleep_prevention_status()
        disable_sleep_prevention()
        assert "未启用" in get_sleep_prevention_status()

    def test_enable_with_display(self):
        disable_sleep_prevention()
        enable_sleep_prevention(keep_display=True)
        status = get_sleep_prevention_status()
        assert "已启用" in status
        assert "显示器常亮" in status
        disable_sleep_prevention()
