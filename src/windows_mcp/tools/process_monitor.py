"""ProcessMonitor tool — snapshot, diff and watch process activity."""

from typing import Literal

from mcp.types import ToolAnnotations

from windows_mcp.infrastructure import with_analytics
from windows_mcp.monitor import (
    clear_baseline,
    diff_processes,
    snapshot_processes,
    watch_processes,
)
from fastmcp import Context


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessMonitor",
        description='Monitor process activity on the machine. Keywords: process events, what started, what exited, watch processes, new process, process diff. mode="snapshot" captures the current process table and stores it as the baseline. mode="diff" compares the current processes against the last baseline and reports started/stopped processes. mode="watch" polls for start/stop events for a given duration (0-300s). mode="clear" drops the stored baseline.',
        annotations=ToolAnnotations(
            title="ProcessMonitor",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessMonitor-Tool")
    def process_monitor_tool(
        mode: Literal["snapshot", "diff", "watch", "clear"] = "snapshot",
        duration: float = 10.0,
        interval: float = 0.5,
        limit: int = 50,
        sort_by: Literal["memory", "name", "pid"] = "memory",
        ctx: Context = None,
    ) -> str:
        if mode == "snapshot":
            return snapshot_processes(limit=limit, sort_by=sort_by)
        elif mode == "diff":
            return diff_processes()
        elif mode == "watch":
            return watch_processes(duration=duration, interval=interval)
        elif mode == "clear":
            return clear_baseline()
        return 'Error: mode 必须是 "snapshot"、"diff"、"watch" 或 "clear"。'
