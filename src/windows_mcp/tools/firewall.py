"""FirewallStatus tool — Windows Firewall profile states."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import firewall_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="FirewallStatus",
        description='Report Windows Defender Firewall profile states. Keywords: firewall status, firewall on/off, inbound rule, outbound rule, 防火墙. Returns per-profile enable state and inbound/outbound default action. Read-only; never changes firewall rules.',
        annotations=ToolAnnotations(
            title="FirewallStatus",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "FirewallStatus-Tool")
    def firewall_status_tool(ctx: Context = None) -> str:
        return firewall_status()
