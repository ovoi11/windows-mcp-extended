"""DriverInfo tool — enumerate system drivers."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_drivers


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DriverInfo",
        description='List Windows system drivers with state and start mode. Keywords: driver list, device driver, kernel driver, driver status. Supports optional name-substring filter. Read-only.',
        annotations=ToolAnnotations(
            title="DriverInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DriverInfo-Tool")
    def driver_info_tool(
        name: str | None = None,
        limit: int = 50,
        ctx: Context = None,
    ) -> str:
        return list_drivers(name=name, limit=limit)
