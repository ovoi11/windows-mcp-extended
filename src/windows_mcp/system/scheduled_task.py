"""Windows scheduled task management — list, run, end, delete and create tasks."""

from __future__ import annotations

import subprocess
from typing import Literal

__all__ = ["list_tasks", "run_task", "end_task", "delete_task", "create_task"]

_CREATE_NO_WINDOW = 0x08000000

_SCHEDULE_TYPES = ("ONLOGON", "ONSTART", "ONCE", "DAILY")


def _schtasks(args: list[str]) -> tuple[int, str]:
    """Run schtasks.exe and return (exit_code, decoded output)."""
    cmd = ["schtasks.exe", *args]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return -1, "schtasks.exe not found on this system."
    except subprocess.TimeoutExpired:
        return -1, "schtasks.exe timed out."
    out = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    return proc.returncode, (out + err).strip()


def list_tasks(limit: int = 50) -> str:
    """List scheduled tasks via schtasks /query (CSV, no header)."""
    code, text = _schtasks(["/query", "/fo", "CSV", "/nh"])
    if code != 0:
        return f"Error querying scheduled tasks: {text}"
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 3:
            continue
        task_name = parts[0].strip().strip('"')
        next_run = parts[1].strip().strip('"')
        status = parts[2].strip().strip('"')
        rows.append([task_name, next_run, status])
    if not rows:
        return "No scheduled tasks found."
    from tabulate import tabulate

    rows = rows[:limit]
    table = tabulate(rows, headers=["Task", "Next Run", "Status"], tablefmt="simple")
    return f"Scheduled tasks ({len(rows)} shown):\n{table}"


def run_task(name: str) -> str:
    """Run a scheduled task on demand."""
    code, text = _schtasks(["/run", "/tn", name])
    if code != 0:
        return f"Error running task {name!r}: {text}"
    return f"Task {name!r}: run requested."


def end_task(name: str) -> str:
    """Stop a running scheduled task."""
    code, text = _schtasks(["/end", "/tn", name])
    if code != 0:
        return f"Error ending task {name!r}: {text}"
    return f"Task {name!r}: end requested."


def delete_task(name: str) -> str:
    """Delete a scheduled task (force, no prompt)."""
    code, text = _schtasks(["/delete", "/tn", name, "/f"])
    if code != 0:
        return f"Error deleting task {name!r}: {text}"
    return f"Task {name!r}: deleted."


def create_task(
    name: str,
    command: str,
    schedule: Literal["ONLOGON", "ONSTART", "ONCE", "DAILY"] = "ONCE",
    args: str | None = None,
    start_time: str | None = None,
) -> str:
    """Create a scheduled task.

    schedule: ONLOGON (at user logon), ONSTART (at system start), ONCE or DAILY.
    start_time: HH:mm for ONCE/DAILY (24h format).
    """
    if schedule not in _SCHEDULE_TYPES:
        return f"Error: schedule must be one of {_SCHEDULE_TYPES}."
    task_cmd = [f'"{command}"'] + ([args] if args else [])
    sch = ["/create", "/tn", name, "/tr", " ".join(task_cmd), "/sc", schedule, "/f"]
    if schedule in ("ONCE", "DAILY"):
        if not start_time:
            return "Error: start_time (HH:mm) is required for ONCE/DAILY schedules."
        sch += ["/st", start_time]
    code, text = _schtasks(sch)
    if code != 0:
        return f"Error creating task {name!r}: {text}"
    return f"Task {name!r}: created (schedule={schedule})."
