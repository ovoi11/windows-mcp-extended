"""PortProcessMap tool — listening ports to owning processes."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import port_process_map


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="PortProcessMap",
        description='Map network ports to owning processes (netstat -ano): protocol, local/remote address, state, PID and process name. Keywords: port, listening port, which process uses port, netstat, 端口占用. Optional filters: protocol (TCP/UDP) and port. Read-only.',
        annotations=ToolAnnotations(
            title="PortProcessMap",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "PortProcessMap-Tool")
    def port_process_map_tool(
        protocol: str | None = None,
        port: int | None = None,
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return port_process_map(protocol=protocol, port=port, limit=limit)
