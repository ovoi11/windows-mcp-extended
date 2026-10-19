"""TimeSyncInfo tool — Windows Time service synchronization status."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import time_sync_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="TimeSyncInfo",
        description='Report the Windows Time service synchronization status. Keywords: time sync, clock sync, w32tm, ntp status, 时间同步. Returns source, stratum, last successful sync time and offset. Read-only; does not resync the clock.',
        annotations=ToolAnnotations(
            title="TimeSyncInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "TimeSyncInfo-Tool")
    def time_sync_info_tool(ctx: Context = None) -> str:
        return time_sync_status()
