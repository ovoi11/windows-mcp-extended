"""ScheduledTask tool — manage Windows scheduled tasks."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import create_task, delete_task, end_task, list_tasks, run_task


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ScheduledTask",
        description='Manage Windows scheduled tasks. Keywords: scheduled task, task scheduler, schtasks, autorun task, startup program. Use mode="list" to enumerate tasks. Use mode="run" / mode="end" / mode="delete" with a task name. Use mode="create" with a task name, command (and optional args), schedule (ONLOGON/ONSTART/ONCE/DAILY) and start_time (HH:mm for ONCE/DAILY). Creating or deleting tasks changes system state: obtain permission before creating or deleting a task that was not explicitly requested.',
        annotations=ToolAnnotations(
            title="ScheduledTask",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ScheduledTask-Tool")
    def scheduled_task_tool(
        mode: Literal["list", "run", "end", "delete", "create"],
        name: str | None = None,
        command: str | None = None,
        schedule: Literal["ONLOGON", "ONSTART", "ONCE", "DAILY"] = "ONCE",
        args: str | None = None,
        start_time: str | None = None,
        limit: int = 50,
        ctx: Context = None,
    ) -> str:
        if mode == "list":
            return list_tasks(limit=limit)
        if not name:
            return "Error: name is required for this mode."
        if mode == "run":
            return run_task(name)
        if mode == "end":
            return end_task(name)
        if mode == "delete":
            return delete_task(name)
        if mode == "create":
            if not command:
                return "Error: command is required for create mode."
            return create_task(
                name, command, schedule=schedule, args=args, start_time=start_time
            )
        return "Error: unknown mode."
