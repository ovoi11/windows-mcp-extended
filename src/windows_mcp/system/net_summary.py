"""Network connection summary — TCP/UDP state counts (netstat)."""

from __future__ import annotations

import subprocess

__all__ = ["network_connection_summary"]

_CREATE_NO_WINDOW = 0x08000000


def network_connection_summary() -> str:
    """Count TCP/UDP connections by protocol and state."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["netstat.exe", "-ano"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=120,
        )
    except FileNotFoundError:
        return "Error: netstat.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: netstat timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    states: dict[str, int] = {}
    counts = {"TCP": 0, "UDP": 0}
    for line in text.splitlines():
        upper = line.strip().upper()
        if upper.startswith("TCP"):
            counts["TCP"] += 1
            parts = line.split()
            if len(parts) >= 4:
                state = parts[3]
                states[state] = states.get(state, 0) + 1
        elif upper.startswith("UDP"):
            counts["UDP"] += 1

    rows = [
        ["TCP 连接", str(counts["TCP"])],
        ["UDP 连接", str(counts["UDP"])],
        ["总计", str(counts["TCP"] + counts["UDP"])],
    ]
    for state in sorted(states, key=lambda s: -states[s]):
        rows.append([f"  {state}", str(states[state])])
    table = tabulate(rows, headers=["连接类型", "数量"], tablefmt="simple")
    return f"网络连接统计:\n{table}"
