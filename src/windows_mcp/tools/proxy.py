"""ProxySettings tool — system proxy configuration."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import proxy_settings


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProxySettings",
        description='Report the current user/IE proxy and WinHTTP proxy settings. Keywords: proxy, proxy server, proxy settings, http proxy, 代理设置. Read-only; never changes proxy configuration.',
        annotations=ToolAnnotations(
            title="ProxySettings",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProxySettings-Tool")
    def proxy_settings_tool(ctx: Context = None) -> str:
        return proxy_settings()
