"""NetworkConnectionSummary tool — connection counts by state."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import network_connection_summary


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetworkConnectionSummary",
        description='Count TCP/UDP connections by protocol and TCP state (LISTENING, ESTABLISHED, etc). Keywords: connection count, tcp connections, netstat summary, 连接统计. Read-only.',
        annotations=ToolAnnotations(
            title="NetworkConnectionSummary",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetworkConnectionSummary-Tool")
    def network_connection_summary_tool(ctx: Context = None) -> str:
        return network_connection_summary()
