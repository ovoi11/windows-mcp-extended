"""FirewallRules tool — query Windows Firewall rules."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import firewall_rules


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="FirewallRules",
        description='Query Windows Firewall rules. Keywords: firewall rule, allow rule, block rule, inbound, outbound, 防火墙规则. Optional filters: name (substring), direction (in/out), action (allow/block). Read-only; never modifies rules.',
        annotations=ToolAnnotations(
            title="FirewallRules",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "FirewallRules-Tool")
    def firewall_rules_tool(
        name: str | None = None,
        direction: str | None = None,
        action: Literal["allow", "block"] | None = None,
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return firewall_rules(name=name, direction=direction, action=action, limit=limit)
