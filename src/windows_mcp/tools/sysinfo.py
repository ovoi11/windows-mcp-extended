"""SystemInfo tool — hardware, OS and manufacturer summary."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import system_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="SystemInfo",
        description='Summarize machine hardware and OS information. Keywords: system info, hardware, motherboard, cpu model, ram size, os version, 系统信息, 电脑配置. Returns manufacturer, model, CPU name/clock, logical cores, physical memory, OS caption/version/architecture. Read-only.',
        annotations=ToolAnnotations(
            title="SystemInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "SystemInfo-Tool")
    def system_info_tool(ctx: Context = None) -> str:
        return system_info()
