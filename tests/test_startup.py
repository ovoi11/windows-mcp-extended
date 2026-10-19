"""Tests for the startup manager service (StartupManager).

NOTE: 待测试点 — add/remove mutate the real HKCU Run key, so tests cover the
read-only list path and parameter validation only.
"""

from windows_mcp.system import add_startup, list_startup, remove_startup


class TestStartupManager:
    def test_list_returns_text(self):
        result = list_startup()
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_add_requires_name_and_command(self):
        assert "Error" in add_startup("", "cmd.exe")
        assert "Error" in add_startup("name", "")

    def test_remove_missing_name(self):
        result = remove_startup("")
        assert "不存在" in result or "Error" in result
