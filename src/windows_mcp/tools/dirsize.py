"""DirectorySize tool — measure folder disk footprint."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import directory_size


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DirectorySize",
        description='Measure the disk footprint of a folder. Keywords: folder size, directory size, disk usage, which folder is big, 目录大小. Returns the total size and top-level children (depth controls how many levels of children are listed). Read-only.',
        annotations=ToolAnnotations(
            title="DirectorySize",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DirectorySize-Tool")
    def directory_size_tool(
        path: str,
        depth: int = 1,
        ctx: Context = None,
    ) -> str:
        return directory_size(path=path, depth=depth)
