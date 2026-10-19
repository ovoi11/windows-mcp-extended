"""ServiceControl tool — manage Windows services."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import control_service, list_services


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ServiceControl",
        description='Manage Windows services. Keywords: service, start service, stop service, restart service, Windows service status, SCM. Use mode="list" to enumerate services (optionally filtered by name substring and running/stopped state). Use mode="control" with action="start|stop|restart" to change a service\'s state. Starting, stopping or restarting a service is a system-affecting action: prefer the exact service name; if the target is unknown, list first. Changes require administrator rights and may disrupt other software — obtain permission before controlling a service that is not clearly requested.',
        annotations=ToolAnnotations(
            title="ServiceControl",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ServiceControl-Tool")
    def service_control_tool(
        mode: Literal["list", "control"],
        action: Literal["start", "stop", "restart"] | None = None,
        name: str | None = None,
        state: Literal["running", "stopped"] | None = None,
        limit: int = 50,
        ctx: Context = None,
    ) -> str:
        if mode == "list":
            return list_services(name=name, state=state, limit=limit)
        if mode == "control":
            if not name:
                return "Error: name is required for control mode."
            if not action:
                return "Error: action (start|stop|restart) is required for control mode."
            return control_service(name, action)
        return 'Error: mode must be "list" or "control".'
