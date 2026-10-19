"""RegistrySearch tool — search registry keys/values by keyword."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import search_registry


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="RegistrySearch",
        description='Search the Windows registry for keys or values whose name contains a keyword. Keywords: registry search, find registry key, find registry value, 注册表搜索. Searches HKCU\\Software or HKLM\\Software (bounded walk, depth-limited). Read-only.',
        annotations=ToolAnnotations(
            title="RegistrySearch",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "RegistrySearch-Tool")
    def registry_search_tool(
        keyword: str,
        root: Literal["hklm", "hkcu"] = "hkcu",
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return search_registry(keyword=keyword, root=root, limit=limit)
