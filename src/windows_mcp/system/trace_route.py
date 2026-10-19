"""Trace route — hop-by-hop path to a host (tracert, read-only)."""

from __future__ import annotations

import subprocess

__all__ = ["trace_route"]

_CREATE_NO_WINDOW = 0x08000000


def trace_route(host: str, max_hops: int = 20) -> str:
    """Trace the network path to a host (tracert)."""
    from tabulate import tabulate

    if not host:
        return "Error: host is required."
    max_hops = max(1, min(int(max_hops), 60))
    try:
        proc = subprocess.run(
            ["tracert.exe", "-d", "-h", str(max_hops), "-w", "2000", host],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=180,
        )
    except FileNotFoundError:
        return "Error: tracert.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: tracert timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    rows: list[list[str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2 or not parts[0].isdigit():
            continue
        hop = parts[0]
        tail = " ".join(parts[1:])[:100]
        rows.append([hop, tail])

    if not rows:
        return f"无法跟踪 {host}: {text.strip()}"
    table = tabulate(rows, headers=["Hop", "Response(s)"], tablefmt="simple")
    return f"路由跟踪 {host}:\n{table}"
