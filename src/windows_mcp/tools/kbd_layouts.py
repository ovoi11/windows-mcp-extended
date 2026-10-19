"""KeyboardLayouts tool — list installed keyboard layouts."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_keyboard_layouts


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="KeyboardLayouts",
        description='List installed Windows keyboard layouts with KLID, layout name/file, and mark which ones are preloaded for the current user. Keywords: keyboard layouts, input methods, keyboard languages, IME list. Read-only.',
        annotations=ToolAnnotations(
            title="KeyboardLayouts",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "KeyboardLayouts-Tool")
    def keyboard_layouts_tool(ctx: Context = None) -> str:
        return list_keyboard_layouts()
