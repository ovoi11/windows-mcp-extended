"""WakeSourceInfo tool — last wake source and wake timers."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import wake_source_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="WakeSourceInfo",
        description='Report the last wake source (powercfg /lastwake) and pending wake timers (/waketimers). Keywords: wake source, why did the pc wake, wake timer, 唤醒来源. Read-only.',
        annotations=ToolAnnotations(
            title="WakeSourceInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "WakeSourceInfo-Tool")
    def wake_source_info_tool(ctx: Context = None) -> str:
        return wake_source_info()
