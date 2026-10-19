"""InstalledUpdates tool — list installed Windows updates."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_updates


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="InstalledUpdates",
        description='List installed Windows updates (hotfixes). Keywords: windows update, installed updates, hotfix, patches, KB, 已安装更新, 补丁. Returns hotfix ID, description, install date and installer. Read-only.',
        annotations=ToolAnnotations(
            title="InstalledUpdates",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "InstalledUpdates-Tool")
    def installed_updates_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_updates(limit=limit)
