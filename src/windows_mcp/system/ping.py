"""Network latency — ping a host and report RTT/loss."""

from __future__ import annotations

import re
import subprocess

__all__ = ["ping_host"]

_CREATE_NO_WINDOW = 0x08000000
_AVG_RE = re.compile(r"平均\s*=\s*(\d+)ms|Average\s*=\s*(\d+)ms", re.IGNORECASE)
_LOSS_RE = re.compile(r"\((\d+)%?\s*丢失\)|\((\d+)%\s*loss\)", re.IGNORECASE)


def ping_host(host: str, count: int = 4, timeout_ms: int = 2000) -> str:
    """Ping a host and report minimum/average/maximum RTT and packet loss."""
    from tabulate import tabulate

    if not host:
        return "Error: host is required."
    count = max(1, min(int(count), 20))
    try:
        proc = subprocess.run(
            ["ping.exe", "-n", str(count), "-w", str(timeout_ms), host],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return "Error: ping.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: ping timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    avg = None
    m = _AVG_RE.search(text)
    if m:
        avg = m.group(1) or m.group(2)
    loss = None
    m = _LOSS_RE.search(text)
    if m:
        loss = m.group(1) or m.group(2)

    if proc.returncode != 0 and avg is None:
        first = next((l for l in text.splitlines() if l.strip()), text)
        return f"无法 ping 通 {host}: {first.strip()}"

    rows = [
        ["主机", host],
        ["包数", str(count)],
    ]
    if avg is not None:
        rows.append(["平均 RTT", f"{avg} ms"])
    if loss is not None:
        rows.append(["丢包", f"{loss}%"])
    if avg is None:
        rows.append(["平均 RTT", "未知（无应答）"])
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"Ping {host}:\n{table}"
