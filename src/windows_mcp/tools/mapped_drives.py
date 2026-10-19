"""MappedDrives tool — network drive mappings."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import mapped_drives


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="MappedDrives",
        description='List network drive mappings (net use). Keywords: mapped drives, network drives, drive letters, 网络驱动器, 映射盘. Does not reveal credentials. Read-only.',
        annotations=ToolAnnotations(
            title="MappedDrives",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "MappedDrives-Tool")
    def mapped_drives_tool(ctx: Context = None) -> str:
        return mapped_drives()
