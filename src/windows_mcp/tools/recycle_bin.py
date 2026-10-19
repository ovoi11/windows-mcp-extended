"""RecycleBinInfo tool — recycle bin size and item count."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import recycle_bin_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="RecycleBinInfo",
        description='Report the recycle bin total size and item count. Keywords: recycle bin, trash, 回收站. Read-only; does not empty or modify the bin.',
        annotations=ToolAnnotations(
            title="RecycleBinInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "RecycleBinInfo-Tool")
    def recycle_bin_info_tool(ctx: Context = None) -> str:
        return recycle_bin_info()
