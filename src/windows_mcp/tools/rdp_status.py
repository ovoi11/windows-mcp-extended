"""RemoteDesktopStatus tool — RDP configuration."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import remote_desktop_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="RemoteDesktopStatus",
        description='Report whether Remote Desktop is enabled and its listening port. Keywords: remote desktop, rdp, rdp enabled, 远程桌面. Read-only.',
        annotations=ToolAnnotations(
            title="RemoteDesktopStatus",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "RemoteDesktopStatus-Tool")
    def remote_desktop_status_tool(ctx: Context = None) -> str:
        return remote_desktop_status()
