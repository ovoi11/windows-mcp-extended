"""DriveSmartInfo tool — physical disk health status."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import drive_health


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DriveSmartInfo",
        description='List physical disks with health status, media type, operational status and size. Keywords: disk health, smart status, hard drive health, ssd health, 硬盘健康. Read-only.',
        annotations=ToolAnnotations(
            title="DriveSmartInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DriveSmartInfo-Tool")
    def drive_smart_info_tool(
        limit: int = 10,
        ctx: Context = None,
    ) -> str:
        return drive_health(limit=limit)
