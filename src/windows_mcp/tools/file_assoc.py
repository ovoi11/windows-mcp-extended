"""FileAssociations tool — query file extension associations."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_associations


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="FileAssociations",
        description='Query Windows file extension associations. Keywords: file association, open with, default program, extension mapping, .txt opens with. Pass an extension (e.g. "txt" or ".txt") to filter, or leave empty to list all. Read-only; never modifies associations.',
        annotations=ToolAnnotations(
            title="FileAssociations",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "FileAssociations-Tool")
    def file_associations_tool(
        extension: str | None = None,
        limit: int = 50,
        ctx: Context = None,
    ) -> str:
        return list_associations(extension=extension, limit=limit)
