"""NetworkConfig tool — adapter IP/DHCP/DNS configuration."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import network_config


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetworkConfig",
        description='List network adapter IP configurations. Keywords: ip config, ipconfig, ip address, gateway, dns server, dhcp, 网络配置. Returns per-adapter IPv4 address, gateway and DNS. Read-only.',
        annotations=ToolAnnotations(
            title="NetworkConfig",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetworkConfig-Tool")
    def network_config_tool(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        return network_config(limit=limit)
