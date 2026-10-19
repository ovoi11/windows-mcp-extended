"""DiskIOStats tool — aggregate disk I/O counters."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import disk_io_stats


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DiskIOStats",
        description='Report aggregate disk I/O: read/write totals and current throughput (sampled over a short interval). Keywords: disk io, disk speed, read write speed, 磁盘IO, 磁盘读写. Read-only.',
        annotations=ToolAnnotations(
            title="DiskIOStats",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DiskIOStats-Tool")
    def disk_io_stats_tool(
        interval: float = 0.5,
        ctx: Context = None,
    ) -> str:
        return disk_io_stats(interval=interval)
