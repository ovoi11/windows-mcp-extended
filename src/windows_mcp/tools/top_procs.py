"""TopProcesses tool — highest CPU/memory consumers."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import top_processes


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="TopProcesses",
        description='List the top processes by CPU percent or memory usage (RSS). Keywords: top processes, highest cpu, highest memory, task manager, 进程占用. by="cpu" (default) or "memory". Read-only.',
        annotations=ToolAnnotations(
            title="TopProcesses",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "TopProcesses-Tool")
    def top_processes_tool(
        by: Literal["cpu", "memory"] = "cpu",
        limit: int = 10,
        ctx: Context = None,
    ) -> str:
        return top_processes(by=by, limit=limit)
