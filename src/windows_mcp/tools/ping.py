"""NetworkLatency tool — ping a host."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import ping_host


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetworkLatency",
        description='Ping a host and report RTT and packet loss. Keywords: ping, latency, network delay, packet loss, 网络延迟. Sends `count` ICMP echo requests (default 4) with a per-packet timeout. Read-only; sends ICMP traffic to the given host.',
        annotations=ToolAnnotations(
            title="NetworkLatency",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetworkLatency-Tool")
    def network_latency_tool(
        host: str,
        count: int = 4,
        timeout_ms: int = 2000,
        ctx: Context = None,
    ) -> str:
        return ping_host(host=host, count=count, timeout_ms=timeout_ms)
