"""NetworkThroughput tool — live network rates."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import network_throughput


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetworkThroughput",
        description='Sample network counters to report live download/upload rates and totals. Keywords: network speed, throughput, download speed, upload speed, 网速, 带宽. Read-only.',
        annotations=ToolAnnotations(
            title="NetworkThroughput",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetworkThroughput-Tool")
    def network_throughput_tool(
        interval: float = 1.0,
        ctx: Context = None,
    ) -> str:
        return network_throughput(interval=interval)
