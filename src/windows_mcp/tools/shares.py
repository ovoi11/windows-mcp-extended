"""NetworkShares tool — enumerate shared folders."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_shares


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="NetworkShares",
        description='List shared folders on this machine. Keywords: network share, shared folder, smb share, 共享文件夹. Returns name, path, description and share type. Read-only.',
        annotations=ToolAnnotations(
            title="NetworkShares",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "NetworkShares-Tool")
    def network_shares_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_shares(limit=limit)
