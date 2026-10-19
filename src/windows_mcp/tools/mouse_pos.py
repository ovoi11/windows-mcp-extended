"""MousePosition tool — current cursor coordinates."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.desktop.mouse_pos import mouse_position


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="MousePosition",
        description='Report the current mouse cursor position in screen coordinates (and virtual desktop size). Keywords: mouse position, cursor location, where is the mouse, 鼠标位置. Read-only; does not move the cursor.',
        annotations=ToolAnnotations(
            title="MousePosition",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "MousePosition-Tool")
    def mouse_position_tool(ctx: Context = None) -> str:
        return mouse_position()
