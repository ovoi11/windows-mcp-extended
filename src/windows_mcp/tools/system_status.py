"""SystemStatus tool — CPU, memory, disk, battery and uptime summary."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import system_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="SystemStatus",
        description='Summarize system health. Keywords: system status, cpu usage, memory usage, disk space, battery, uptime, hardware info. Returns CPU load, logical core count, memory used/total, C: disk usage, battery state and boot/uptime. Read-only.',
        annotations=ToolAnnotations(
            title="SystemStatus",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "SystemStatus-Tool")
    def system_status_tool(ctx: Context = None) -> str:
        return system_status()
