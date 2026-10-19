"""ActiveWindowInfo tool — foreground window details."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.desktop.active_window import active_window_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ActiveWindowInfo",
        description='Report the foreground (active) window: handle, title, PID and owning process. Keywords: active window, foreground window, current window title, 当前窗口. Read-only.',
        annotations=ToolAnnotations(
            title="ActiveWindowInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ActiveWindowInfo-Tool")
    def active_window_info_tool(ctx: Context = None) -> str:
        return active_window_info()
