"""Process activity monitoring service — snapshot, diff and watch modes.

Reuses psutil (already a dependency of this project) for process enumeration.
State (baseline snapshot) lives module-scoped so successive MCP tool calls can
diff against the previous observation.
"""

from __future__ import annotations

import time
from typing import Optional

import psutil

__all__ = ["snapshot_processes", "diff_processes", "watch_processes", "clear_baseline"]

_baseline: Optional[dict[int, tuple[str, float]]] = None


def _collect() -> dict[int, tuple[str, float]]:
    """Return {pid: (name, create_time)} for all visible processes."""
    procs: dict[int, tuple[str, float]] = {}
    for p in psutil.process_iter(["pid", "name", "create_time"]):
        try:
            info = p.info
            procs[info["pid"]] = (info["name"] or "Unknown", info["create_time"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procs


def _fmt_time(ts: float) -> str:
    return time.strftime("%H:%M:%S", time.localtime(ts))


def snapshot_processes(limit: int = 50, sort_by: str = "memory") -> str:
    """Return the current process snapshot as a table and store it as the baseline."""
    global _baseline
    import psutil as _ps

    procs = []
    for p in _ps.process_iter(["pid", "name", "create_time", "memory_info"]):
        try:
            info = p.info
            mem_mb = (
                info["memory_info"].rss / (1024 * 1024) if info["memory_info"] else 0
            )
            procs.append(
                {
                    "pid": info["pid"],
                    "name": info["name"] or "Unknown",
                    "created": _fmt_time(info["create_time"]),
                    "mem_mb": round(mem_mb, 1),
                }
            )
        except (_ps.NoSuchProcess, _ps.AccessDenied):
            continue
    sort_key = {
        "memory": lambda x: x["mem_mb"],
        "name": lambda x: x["name"].lower(),
        "pid": lambda x: x["pid"],
    }
    procs.sort(key=sort_key.get(sort_by, sort_key["memory"]), reverse=(sort_by != "name"))
    procs = procs[:limit]

    _baseline = _collect()
    if not procs:
        return "当前无可见进程。"
    from tabulate import tabulate

    table = tabulate(
        [[p["pid"], p["name"], p["created"], f"{p['mem_mb']:.1f} MB"] for p in procs],
        headers=["PID", "Name", "Created", "Memory"],
        tablefmt="simple",
    )
    return f"进程快照已记录为基线（{len(procs)} 个，共 {len(_baseline)} 个可见进程）:\n{table}"


def diff_processes() -> str:
    """Compare the current process set against the stored baseline."""
    global _baseline
    if _baseline is None:
        return "Error: 尚无基线。请先调用 snapshot（mode='snapshot'）建立基线。"

    current = _collect()
    started = [(pid, name) for pid, (name, _) in current.items() if pid not in _baseline]
    stopped = [
        (pid, name) for pid, (name, _) in _baseline.items() if pid not in current
    ]
    _baseline = current

    from tabulate import tabulate

    lines = [f"进程变化（基线 {len(_baseline)} 个 → 当前 {len(current)} 个）:", ""]
    if started:
        started.sort(key=lambda x: x[0])
        lines.append(f"新增进程（{len(started)}）:")
        lines.append(
            tabulate(started, headers=["PID", "Name"], tablefmt="simple")
        )
        lines.append("")
    if stopped:
        stopped.sort(key=lambda x: x[0])
        lines.append(f"退出进程（{len(stopped)}）:")
        lines.append(
            tabulate(stopped, headers=["PID", "Name"], tablefmt="simple")
        )
        lines.append("")
    if not started and not stopped:
        lines.append("无进程启动或退出。")
    return "\n".join(lines)


def watch_processes(duration: float = 10.0, interval: float = 0.5) -> str:
    """Watch for process start/stop events for *duration* seconds."""
    global _baseline
    if duration <= 0 or duration > 300:
        return "Error: duration 必须在 0~300 秒之间。"
    if interval <= 0:
        return "Error: interval 必须大于 0。"

    from tabulate import tabulate

    events: list[list[str]] = []
    seen = _collect()
    deadline = time.monotonic() + duration
    while time.monotonic() < deadline:
        current = _collect()
        for pid, (name, _) in current.items():
            if pid not in seen:
                events.append([_fmt_time(time.time()), "started", str(pid), name])
        for pid, (name, _) in seen.items():
            if pid not in current:
                events.append([_fmt_time(time.time()), "stopped", str(pid), name])
        seen = current
        time.sleep(interval)

    _baseline = seen
    if not events:
        return f"监控 {duration:.1f} 秒：未观察到进程启动或退出。"
    return (
        f"监控 {duration:.1f} 秒，观察到 {len(events)} 个事件:\n"
        + tabulate(events, headers=["Time", "Event", "PID", "Name"], tablefmt="simple")
    )


def clear_baseline() -> str:
    """Drop the stored baseline."""
    global _baseline
    _baseline = None
    return "进程监控基线已清除。"
