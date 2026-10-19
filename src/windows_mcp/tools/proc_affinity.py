"""ProcessAffinity tool — CPU affinity of a process."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import process_affinity


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessAffinity",
        description='Report the CPU affinity mask of a process: which logical CPUs it is allowed to run on. Keywords: cpu affinity, processor affinity, process cores, CPU 亲和性. Read-only; never changes affinity.',
        annotations=ToolAnnotations(
            title="ProcessAffinity",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessAffinity-Tool")
    def process_affinity_tool(
        pid: int,
        ctx: Context = None,
    ) -> str:
        return process_affinity(pid=pid)
