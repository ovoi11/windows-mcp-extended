"""ProcessDetail tool — deep metrics for a single process."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import process_detail


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessDetail",
        description='Report deep diagnostic metrics for one process (by pid or name): status, threads, handles, CPU%, RSS/VMS memory, user, start time, executable path and command line. Keywords: process detail, process info, threads, handles, memory usage of process, 进程详情. Read-only.',
        annotations=ToolAnnotations(
            title="ProcessDetail",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessDetail-Tool")
    def process_detail_tool(
        pid: int | None = None,
        name: str | None = None,
        ctx: Context = None,
    ) -> str:
        return process_detail(pid=pid, name=name)
