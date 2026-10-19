"""Process I/O — per-process IO counters (psutil)."""

from __future__ import annotations

__all__ = ["process_io_stats"]


def process_io_stats(limit: int = 10) -> str:
    """List processes with the highest cumulative I/O (read/write bytes)."""
    import psutil
    from tabulate import tabulate

    rows: list[list[str]] = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            io = proc.io_counters()
            rows.append(
                [
                    str(proc.info["pid"]),
                    proc.info["name"] or "?",
                    _fmt(io.read_bytes),
                    _fmt(io.write_bytes),
                ]
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue

    if not rows:
        return "无法读取进程 I/O 统计。"
    rows.sort(key=lambda r: _to_bytes(r[2]) + _to_bytes(r[3]), reverse=True)
    rows = rows[: max(1, min(int(limit), 30))]
    table = tabulate(rows, headers=["PID", "Name", "Read", "Write"], tablefmt="simple")
    return f"进程 I/O TOP {len(rows)}:\n{table}"


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
