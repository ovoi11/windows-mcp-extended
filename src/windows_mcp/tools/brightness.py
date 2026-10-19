"""DisplayBrightness tool — read screen brightness (read-only)."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import brightness_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DisplayBrightness",
        description='Report the current display brightness percentage. Keywords: brightness, screen brightness, 亮度. Reads via WMI (WmiMonitorBrightness); works on laptops and many desktops. Read-only; does not change brightness.',
        annotations=ToolAnnotations(
            title="DisplayBrightness",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DisplayBrightness-Tool")
    def display_brightness_tool(ctx: Context = None) -> str:
        return brightness_status()
