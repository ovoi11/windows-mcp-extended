"""Time sync status — Windows Time service state (w32tm, read-only)."""

from __future__ import annotations

import subprocess

__all__ = ["time_sync_status"]

_CREATE_NO_WINDOW = 0x08000000


def time_sync_status() -> str:
    """Report the Windows Time service synchronization status."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["w32tm.exe", "/query", "/status"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return "Error: w32tm.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: w32tm timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    if proc.returncode != 0:
        return f"Error querying time sync: {(err or text).strip()}"

    rows: list[list[str]] = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        rows.append([key, value])

    if not rows:
        return f"时间同步状态:\n{text}"
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"时间同步状态:\n{table}"
