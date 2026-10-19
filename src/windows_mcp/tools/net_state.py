"""NetState tool — network connections and adapter statistics."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.monitor import list_connections, net_stats


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetState",
        description='Inspect network state. Keywords: network connections, listening ports, open ports, TCP, UDP, adapter status, bandwidth, RX, TX. Use mode="connections" to list active TCP/UDP connections (optionally filtered by state such as LISTEN or ESTABLISHED) with owning process names. Use mode="stats" to summarize adapter up/down status, link speed and traffic counters. Read-only.',
        annotations=ToolAnnotations(
            title="NetState",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetState-Tool")
    def net_state_tool(
        mode: Literal["connections", "stats"] = "connections",
        state: str | None = None,
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        if mode == "stats":
            return net_stats()
        return list_connections(state=state, limit=limit)
