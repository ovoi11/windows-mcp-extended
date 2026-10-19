"""PreventSleep tool — keep the system awake during long-running tasks."""

from typing import Literal

from mcp.types import ToolAnnotations

from windows_mcp.infrastructure import with_analytics
from windows_mcp.system import (
    disable_sleep_prevention,
    enable_sleep_prevention,
    get_sleep_prevention_status,
)
from fastmcp import Context


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="PreventSleep",
        description='Prevent the Windows system from entering sleep while the MCP server is running. Keywords: keep awake, prevent sleep, no sleep, stay awake, power settings. mode="enable" blocks system sleep (optionally keep the display on with keep_display=True). mode="disable" clears the block. mode="status" reports whether sleep prevention is active. The block auto-clears when the server exits.',
        annotations=ToolAnnotations(
            title="PreventSleep",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "PreventSleep-Tool")
    def prevent_sleep_tool(
        mode: Literal["enable", "disable", "status"] = "status",
        keep_display: bool = False,
        ctx: Context = None,
    ) -> str:
        if mode == "enable":
            return enable_sleep_prevention(keep_display=keep_display)
        elif mode == "disable":
            return disable_sleep_prevention()
        return get_sleep_prevention_status()
