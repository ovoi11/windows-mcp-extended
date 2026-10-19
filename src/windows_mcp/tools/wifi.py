"""WifiManager tool — Wi-Fi connection state and nearby networks."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import wifi_networks, wifi_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="WifiManager",
        description='Inspect Wi-Fi state. Keywords: wifi, wi-fi, wireless, ssid, network scan, signal strength. Use mode="status" to report the current adapter state and active connection, mode="scan" to list nearby networks with authentication, encryption and signal. Read-only; does not connect or disconnect.',
        annotations=ToolAnnotations(
            title="WifiManager",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "WifiManager-Tool")
    def wifi_manager_tool(
        mode: Literal["status", "scan"] = "status",
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        if mode == "scan":
            return wifi_networks(limit=limit)
        return wifi_status()
