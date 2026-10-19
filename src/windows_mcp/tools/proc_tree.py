"""ProcessTree tool — parent/child process relationships."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import process_tree


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessTree",
        description='Render the running process tree (parent -> children) as an indented list. Keywords: process tree, parent process, child process, process hierarchy, 进程树. Read-only.',
        annotations=ToolAnnotations(
            title="ProcessTree",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessTree-Tool")
    def process_tree_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return process_tree(limit=limit)
