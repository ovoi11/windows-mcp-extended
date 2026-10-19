"""InstalledApps tool — enumerate installed applications."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_apps


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="InstalledApps",
        description='List installed applications from the Windows Uninstall registry keys. Keywords: installed programs, installed apps, software list, uninstall list. Supports optional name-substring filter and limit. include_hidden=True also lists entries with bracketed or KB-prefixed display names. Read-only.',
        annotations=ToolAnnotations(
            title="InstalledApps",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "InstalledApps-Tool")
    def installed_apps_tool(
        name: str | None = None,
        limit: int = 50,
        include_hidden: bool = False,
        ctx: Context = None,
    ) -> str:
        return list_apps(name=name, limit=limit, include_hidden=include_hidden)
