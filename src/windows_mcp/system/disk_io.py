"""Disk I/O — aggregate disk throughput counters (psutil)."""

from __future__ import annotations

__all__ = ["disk_io_stats"]


def disk_io_stats(interval: float = 0.5) -> str:
    """Report aggregate disk I/O: totals and current throughput."""
    import psutil
    from tabulate import tabulate

    before = psutil.disk_io_counters()
    if before is None:
        return "磁盘 I/O 计数器不可用。"
    import time

    time.sleep(max(0.1, min(interval, 5.0)))
    after = psutil.disk_io_counters()
    if after is None:
        return "磁盘 I/O 计数器不可用。"
    elapsed = interval
    rows = [
        ["读总量", _fmt(after.read_bytes)],
        ["写总量", _fmt(after.write_bytes)],
        ["当前读速率", f"{_fmt((after.read_bytes - before.read_bytes) / elapsed)}/s"],
        ["当前写速率", f"{_fmt((after.write_bytes - before.write_bytes) / elapsed)}/s"],
        ["读次数", f"{after.read_count:,}"],
        ["写次数", f"{after.write_count:,}"],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"磁盘 I/O:\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
