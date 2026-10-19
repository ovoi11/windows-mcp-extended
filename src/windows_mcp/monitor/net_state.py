"""Network state — active TCP/UDP connections and adapter statistics."""

from __future__ import annotations

from typing import Literal

__all__ = ["list_connections", "net_stats"]


def list_connections(
    state: str | None = None,
    limit: int = 20,
) -> str:
    """List active network connections with owning process names."""
    import socket

    import psutil
    from tabulate import tabulate

    try:
        conns = psutil.net_connections(kind="all")
    except (psutil.AccessDenied, PermissionError):
        return "Error: access denied enumerating connections (try as administrator)."

    rows = []
    for c in conns:
        if state and state.upper() != (c.status or "").upper():
            continue
        local = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
        remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "-"
        proc_name = "-"
        if c.pid:
            try:
                proc_name = psutil.Process(c.pid).name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_name = f"pid {c.pid}"
        kind = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
        rows.append([kind, local, remote, c.status or "-", c.pid or "-", proc_name])

    if not rows:
        return f"No connections found{f' in state {state}' if state else ''}."
    rows.sort(key=lambda r: (r[2] != "-", r[0], r[2]))
    rows = rows[:limit]
    table = tabulate(rows, headers=["Proto", "Local", "Remote", "State", "PID", "Process"], tablefmt="simple")
    return f"Network connections ({len(rows)} shown of {len(conns)}):\n{table}"


def net_stats() -> str:
    """Summarize network adapter status and traffic counters."""
    import psutil
    from tabulate import tabulate

    io = psutil.net_io_counters(pernic=True)
    rows = []
    for name, stats in psutil.net_if_stats().items():
        counters = io.get(name)
        rx = counters.bytes_recv if counters else 0
        tx = counters.bytes_sent if counters else 0
        rows.append(
            [
                name,
                "up" if stats.isup else "down",
                f"{stats.speed} Mbps" if stats.speed else "-",
                _fmt_bytes(rx),
                _fmt_bytes(tx),
            ]
        )
    if not rows:
        return "No network adapters found."
    table = tabulate(rows, headers=["Adapter", "State", "Speed", "RX", "TX"], tablefmt="simple")
    return f"Network adapters ({len(rows)}):\n{table}"


def _fmt_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
