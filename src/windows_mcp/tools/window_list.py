"""WindowList tool — enumerate visible top-level windows."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.desktop.window_list import window_list


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="WindowList",
        description='List visible top-level windows with their PID and title. Keywords: open windows, window list, window title, 窗口列表, 打开的窗口. Read-only.',
        annotations=ToolAnnotations(
            title="WindowList",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "WindowList-Tool")
    def window_list_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return window_list(limit=limit)
