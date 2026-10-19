"""NetworkAdapters tool — physical NIC details."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import network_adapters


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetworkAdapters",
        description='List physical network adapters: name, connection ID, interface type, MAC address, link speed and enabled state. Keywords: network adapter, mac address, nic, network card, 网卡, mac地址. Read-only.',
        annotations=ToolAnnotations(
            title="NetworkAdapters",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetworkAdapters-Tool")
    def network_adapters_tool(
        limit: int = 15,
        ctx: Context = None,
    ) -> str:
        return network_adapters(limit=limit)
