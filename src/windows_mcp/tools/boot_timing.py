"""BootTiming tool — last boot duration."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import boot_timing


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="BootTiming",
        description='Report the last boot duration and current uptime. Keywords: boot time, startup time, how long to boot, 启动耗时, 开机时间. Read-only.',
        annotations=ToolAnnotations(
            title="BootTiming",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "BootTiming-Tool")
    def boot_timing_tool(ctx: Context = None) -> str:
        return boot_timing()
