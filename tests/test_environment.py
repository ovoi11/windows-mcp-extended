"""Tests for the environment variable service (EnvironmentVariables).

NOTE: 待测试点 — set/delete with scope="user" mutate the real HKCU\\Environment,
so tests cover the read-only paths and validation only.
"""

from windows_mcp.system import delete_environment, list_environment, set_environment


class TestEnvironmentVariables:
    def test_list_user(self):
        result = list_environment(scope="user")
        assert isinstance(result, str)

    def test_list_process(self):
        result = list_environment(scope="process")
        assert isinstance(result, str)
        assert "进程环境变量" in result

    def test_set_requires_name(self):
        assert "Error" in set_environment("", "v")

    def test_delete_requires_name(self):
        assert "Error" in delete_environment("")

    def test_process_scope_roundtrip(self):
        # Process-scope set/delete is safe: it only mutates this process.
        assert "已设置" in set_environment("__WINDOWS_MCP_TEST_VAR__", "1", scope="process")
        assert "已删除" in delete_environment("__WINDOWS_MCP_TEST_VAR__", scope="process")
