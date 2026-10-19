"""ImeStatus tool — query the active keyboard layout / input language."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import ime_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ImeStatus",
        description='Query the active Windows keyboard layout and input language. Keywords: IME, input method, keyboard layout, input language, 输入法, 键盘布局. Returns the layout KLID, display language name and language ID for the current session. Read-only; does not switch layouts or alter input.',
        annotations=ToolAnnotations(
            title="ImeStatus",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ImeStatus-Tool")
    def ime_status_tool(ctx: Context = None) -> str:
        return ime_status()
