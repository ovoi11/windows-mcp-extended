"""ProcessPriority tool — read and set process priority classes."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_priorities, set_priority


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessPriority",
        description='Read or set Windows process priority classes. Keywords: process priority, priority class, high priority, background process, task priority. Use mode="list" to show priorities of running processes, mode="set" with pid and priority (idle|below|normal|above|high — REALTIME is intentionally not exposed) to change one. Changing priority affects system responsiveness — obtain permission before adjusting processes that were not explicitly requested.',
        annotations=ToolAnnotations(
            title="ProcessPriority",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessPriority-Tool")
    def process_priority_tool(
        mode: Literal["list", "set"] = "list",
        pid: int | None = None,
        priority: Literal["idle", "below", "normal", "above", "high"] | None = None,
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        if mode == "list":
            return list_priorities(limit=limit)
        if mode == "set":
            if not pid:
                return "Error: pid is required for set mode."
            if not priority:
                return "Error: priority is required for set mode."
            return set_priority(pid, priority)
        return "Error: unknown mode."
