"""Process detail — deep diagnostic metrics for a single process."""

from __future__ import annotations

__all__ = ["process_detail"]


def process_detail(pid: int | None = None, name: str | None = None) -> str:
    """Report detailed metrics for one process (by pid or name)."""
    import psutil
    from tabulate import tabulate

    if pid is None and name is None:
        return "Error: provide either pid or name."

    target: psutil.Process | None = None
    try:
        if pid is not None:
            target = psutil.Process(pid)
        else:
            for p in psutil.process_iter(["pid", "name"]):
                if p.info["name"] and p.info["name"].lower() == name.lower():
                    target = p
                    break
            if target is None:
                return f'No process matching "{name}" found.'
    except psutil.NoSuchProcess:
        return f"No process with PID {pid} found."

    try:
        info = target.as_dict(
            attrs=[
                "pid", "name", "exe", "cmdline", "create_time", "num_threads",
                "num_handles", "status", "memory_info", "cpu_percent", "username",
            ]
        )
    except (psutil.NoSuchProcess, psutil.AccessDenied, OSError) as e:
        return f"Error reading process detail: {e}."

    mem = info.get("memory_info") or None
    rows: list[list[str]] = [
        ["PID", str(info.get("pid", "?"))],
        ["名称", info.get("name") or "?"],
        ["状态", info.get("status") or "?"],
        ["线程数", str(info.get("num_threads", "-"))],
        ["句柄数", str(info.get("num_handles", "-"))],
        ["CPU%", f"{info.get('cpu_percent') or 0:.1f}%"],
        ["内存(RSS)", _fmt(mem.rss) if mem else "-"],
        ["内存(VMS)", _fmt(mem.vms) if mem else "-"],
        ["用户", info.get("username") or "-"],
        ["启动时间", _fmt_time(info.get("create_time"))],
        ["可执行文件", str(info.get("exe") or "-")[:120]],
    ]
    cmdline = info.get("cmdline")
    if cmdline:
        rows.append(["命令行", " ".join(str(x) for x in cmdline)[:200]])

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"进程详情 (PID {info.get('pid', '?')}):\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _fmt_time(ts: float | None) -> str:
    if not ts:
        return "-"
    import datetime

    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
