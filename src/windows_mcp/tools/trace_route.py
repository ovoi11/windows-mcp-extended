"""TraceRoute tool — hop-by-hop path to a host."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import trace_route


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="TraceRoute",
        description='Trace the network path to a host (tracert, without DNS reverse lookups). Keywords: tracert, traceroute, route trace, network path, 路由跟踪. Sends ICMP probes to the given host. Read-only.',
        annotations=ToolAnnotations(
            title="TraceRoute",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "TraceRoute-Tool")
    def trace_route_tool(
        host: str,
        max_hops: int = 20,
        ctx: Context = None,
    ) -> str:
        return trace_route(host=host, max_hops=max_hops)
