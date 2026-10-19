"""RecentFiles tool — recently opened documents."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import recent_files


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="RecentFiles",
        description='List recently opened documents (from the RecentDocs registry). Keywords: recent files, recent documents, recently opened, 最近文档, 最近打开. Read-only.',
        annotations=ToolAnnotations(
            title="RecentFiles",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "RecentFiles-Tool")
    def recent_files_tool(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        return recent_files(limit=limit)
