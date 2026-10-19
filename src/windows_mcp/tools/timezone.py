"""TimezoneInfo tool — report the current time zone."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import timezone_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="TimezoneInfo",
        description='Report the current Windows time zone. Keywords: timezone, time zone, UTC offset, DST, daylight saving. Returns zone ID, display name, UTC offset and daylight-saving state. Read-only.',
        annotations=ToolAnnotations(
            title="TimezoneInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "TimezoneInfo-Tool")
    def timezone_info_tool(ctx: Context = None) -> str:
        return timezone_info()
