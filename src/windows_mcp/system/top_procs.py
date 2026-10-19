"""Top processes — CPU/memory ranking (snapshot)."""

from __future__ import annotations

__all__ = ["top_processes"]


def top_processes(by: str = "cpu", limit: int = 10) -> str:
    """List the top processes by CPU% or memory (RSS)."""
    import psutil
    from tabulate import tabulate

    by = by.lower()
    if by not in ("cpu", "memory"):
        return "Error: by must be 'cpu' or 'memory'."

    rows: list[list[str]] = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info"]):
        try:
            info = proc.info
            pid = info.get("pid")
            name = info.get("name") or "?"
            mem = info.get("memory_info")
            rss = mem.rss if mem else 0
            if by == "cpu":
                # cpu_percent is meaningless on first call; use one blocking call per proc.
                cpu = proc.cpu_percent(interval=None) or 0
            else:
                cpu = info.get("cpu_percent") or 0
            rows.append([str(pid), name, f"{cpu:.1f}", _fmt(rss)])
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue

    if by == "cpu":
        rows.sort(key=lambda r: float(r[2]), reverse=True)
    else:
        rows.sort(key=lambda r: _to_bytes(r[3]), reverse=True)

    rows = rows[: max(1, min(int(limit), 50))]
    table = tabulate(rows, headers=["PID", "Name", "CPU%", "RSS"], tablefmt="simple")
    return f"进程 TOP {len(rows)}（按{by}）:\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def _to_bytes(s: str) -> float:
    try:
        value, unit = s.split()
        value = float(value)
        return value * {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}[unit]
    except (ValueError, KeyError):
        return 0.0
