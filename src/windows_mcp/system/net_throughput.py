"""Network throughput — live upload/download rates (sampled)."""

from __future__ import annotations

import time

__all__ = ["network_throughput"]


def network_throughput(interval: float = 1.0) -> str:
    """Sample network counters to report live download/upload rates."""
    import psutil
    from tabulate import tabulate

    before = psutil.net_io_counters()
    if before is None:
        return "网络计数器不可用。"
    time.sleep(max(0.2, min(interval, 5.0)))
    after = psutil.net_io_counters()
    if after is None:
        return "网络计数器不可用。"
    elapsed = interval

    rows = [
        ["下载速率", f"{_fmt((after.bytes_recv - before.bytes_recv) / elapsed)}/s"],
        ["上传速率", f"{_fmt((after.bytes_sent - before.bytes_sent) / elapsed)}/s"],
        ["累计接收", _fmt(after.bytes_recv)],
        ["累计发送", _fmt(after.bytes_sent)],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"网络吞吐量（{elapsed:.1f}s 采样）:\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
