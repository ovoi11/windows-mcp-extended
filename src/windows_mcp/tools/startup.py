"""StartupManager tool — manage user auto-run (Run key) entries."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import add_startup, list_startup, remove_startup


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="StartupManager",
        description='Manage the current user\'s auto-run programs (HKCU Run key). Keywords: startup, autorun, boot program, run at login, startup item. Use mode="list" to enumerate entries, mode="add" with name and command to register an auto-run entry (overwrites same name), mode="remove" with name to delete one. Adding or removing startup entries changes system state — obtain permission before modifying entries that were not explicitly requested.',
        annotations=ToolAnnotations(
            title="StartupManager",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "StartupManager-Tool")
    def startup_manager_tool(
        mode: Literal["list", "add", "remove"],
        name: str | None = None,
        command: str | None = None,
        ctx: Context = None,
    ) -> str:
        if mode == "list":
            return list_startup()
        if not name:
            return "Error: name is required for add/remove modes."
        if mode == "add":
            if not command:
                return "Error: command is required for add mode."
            return add_startup(name, command)
        if mode == "remove":
            return remove_startup(name)
        return "Error: unknown mode."
