"""ProcessIOStats tool — per-process I/O counters."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import process_io_stats


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessIOStats",
        description='List processes with the highest cumulative I/O (read/write bytes). Keywords: process io, disk usage by process, io stats, 进程IO. Read-only.',
        annotations=ToolAnnotations(
            title="ProcessIOStats",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessIOStats-Tool")
    def process_io_stats_tool(
        limit: int = 10,
        ctx: Context = None,
    ) -> str:
        return process_io_stats(limit=limit)
