"""Process priority — read and set Windows process priority classes."""

from __future__ import annotations

from typing import Literal

__all__ = ["list_priorities", "set_priority"]

# REALTIME is intentionally excluded: it can starve the system.
_PRIORITY_ALIASES: dict[str, int] = {
    "idle": 64,          # IDLE_PRIORITY_CLASS
    "below": 16384,      # BELOW_NORMAL_PRIORITY_CLASS
    "normal": 32,        # NORMAL_PRIORITY_CLASS
    "above": 32768,      # ABOVE_NORMAL_PRIORITY_CLASS
    "high": 128,         # HIGH_PRIORITY_CLASS
}
_PRIORITY_NAMES = {v: k for k, v in _PRIORITY_ALIASES.items()}


def _class_name(value: int) -> str:
    return _PRIORITY_NAMES.get(value, str(value))


def list_priorities(limit: int = 20) -> str:
    """List running processes with their priority class."""
    import psutil
    from tabulate import tabulate

    rows: list[list[str]] = []
    for p in psutil.process_iter(["pid", "name"]):
        try:
            proc = psutil.Process(p.info["pid"])
            nice = proc.nice()
            rows.append([p.info["pid"], p.info["name"] or "Unknown", _class_name(nice)])
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue
    if not rows:
        return "没有可显示的进程。"
    rows.sort(key=lambda r: r[1].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["PID", "Name", "Priority"], tablefmt="simple")
    return f"进程优先级 ({len(rows)} shown):\n{table}"


def set_priority(pid: int, priority: Literal["idle", "below", "normal", "above", "high"]) -> str:
    """Set a process's priority class (REALTIME is not exposed)."""
    import psutil

    if priority not in _PRIORITY_ALIASES:
        return f"Error: priority must be one of {tuple(_PRIORITY_ALIASES)}."
    try:
        proc = psutil.Process(pid)
        proc_name = proc.name()
        proc.nice(_PRIORITY_ALIASES[priority])
    except psutil.NoSuchProcess:
        return f"No process with PID {pid} found."
    except psutil.AccessDenied:
        return f"Access denied setting priority for PID {pid} (try as administrator)."
    except OSError as e:
        return f"Error setting priority for PID {pid}: {e}."
    return f"PID {pid} ({proc_name}) priority set to {priority}."
