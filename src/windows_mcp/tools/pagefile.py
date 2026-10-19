"""PageFileInfo tool — page file and virtual memory usage."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import pagefile_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="PageFileInfo",
        description='Report page file usage and virtual memory totals. Keywords: pagefile, virtual memory, swap, 虚拟内存, 页面文件. Returns per-page-file allocated/used/peak MB and total virtual memory. Read-only.',
        annotations=ToolAnnotations(
            title="PageFileInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "PageFileInfo-Tool")
    def pagefile_info_tool(ctx: Context = None) -> str:
        return pagefile_info()
