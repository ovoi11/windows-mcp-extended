"""BrowserExtensions tool — installed browser extensions."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import browser_extensions


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="BrowserExtensions",
        description='List installed Edge/Chrome browser extensions with names and versions. Keywords: browser extensions, chrome extensions, edge extensions, suspicious extension, 浏览器扩展. Read-only; useful for security reviews.',
        annotations=ToolAnnotations(
            title="BrowserExtensions",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "BrowserExtensions-Tool")
    def browser_extensions_tool(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        return browser_extensions(limit=limit)
