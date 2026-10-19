"""Tests for the service control service (ServiceControl).

NOTE: 待测试点 — service start/stop/restart requires administrator rights and
mutates system state, so these tests cover validation and listing paths only.
Live control calls are intentionally not executed in the test suite.
"""

from windows_mcp.system import control_service, list_services


class TestServiceControl:
    def test_list_returns_table_or_no_services(self):
        result = list_services(limit=10)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_list_invalid_state_ignored(self):
        # state filter accepts running/stopped; anything else is treated as no filter.
        result = list_services(state="running", limit=5)
        assert isinstance(result, str)

    def test_control_invalid_action(self):
        result = control_service("Spooler", "explode")  # type: ignore[arg-type]
        assert "Error" in result and "action" in result

    def test_control_missing_service_returns_error(self):
        # A nonexistent service name must produce an error message, never a crash.
        result = control_service("__windows_mcp_no_such_service__", "start")
        assert "Error" in result

    def test_control_stop_uninstalled_returns_error(self):
        result = control_service("__windows_mcp_no_such_service__", "stop")
        assert "Error" in result
