"""EventLogReader tool — read Windows event logs."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import read_event_log


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="EventLogReader",
        description='Read recent entries from a Windows event log. Keywords: event log, event viewer, system log, application log, security log, crash, error history. Reads the most recent events from the Application, Security or System log with optional level (error/warning/info) and source-name filters. Read-only; some logs may require administrator rights.',
        annotations=ToolAnnotations(
            title="EventLogReader",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "EventLogReader-Tool")
    def event_log_reader_tool(
        log: Literal["Application", "Security", "System"] = "System",
        max_events: int = 20,
        level: Literal["error", "warning", "info"] | None = None,
        source: str | None = None,
        ctx: Context = None,
    ) -> str:
        return read_event_log(log=log, max_events=max_events, level=level, source=source)
