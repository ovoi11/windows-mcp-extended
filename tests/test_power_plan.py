"""Tests for the power plan service (PowerPlan).

NOTE: 待测试点 — set_active_plan switches the live power scheme; tests cover
the read-only paths and GUID validation only.
"""

from windows_mcp.system import get_active_plan, list_plans, set_active_plan


class TestPowerPlan:
    def test_list_returns_text(self):
        result = list_plans()
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_active_returns_text(self):
        result = get_active_plan()
        assert isinstance(result, str)
        assert "当前电源方案" in result or "Error" in result

    def test_set_invalid_guid(self):
        result = set_active_plan("not-a-guid")
        assert "Error" in result
