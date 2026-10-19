"""Port-process map — listening ports and owning processes (netstat -ano)."""

from __future__ import annotations

import re
import subprocess

__all__ = ["port_process_map"]

_CREATE_NO_WINDOW = 0x08000000

_LINE_RE = re.compile(
    r"^\s*(TCP|UDP)\s+"
    r"(\S+)\s+"
    r"(\S+)\s+"
    r"(LISTENING|ESTABLISHED|TIME_WAIT|CLOSE_WAIT|SYN_SENT|\*)?\s*"
    r"(\d+)?\s*$",
    re.IGNORECASE,
)


def port_process_map(protocol: str | None = None, port: int | None = None, limit: int = 30) -> str:
    """Map listening/active network ports to owning processes (netstat -ano)."""
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
    proc_names: dict[int, str] = {}
    rows: list[list[str]] = []

    for line in text.splitlines():
        if not line.strip():
            continue
        upper = line.strip().upper()
        proto = "TCP" if upper.startswith("TCP") else "UDP" if upper.startswith("UDP") else None
        if proto is None:
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[1]
        remote = parts[2]
        state = parts[3] if proto == "TCP" else "-"
        pid_s = parts[-1]
        if not pid_s.isdigit():
            continue
        pid = int(pid_s)
        host_port = local.rsplit(":", 1)[-1]
        if port is not None and not local.endswith(f":{port}") and host_port != str(port):
            continue
        if protocol and proto != protocol.upper():
            continue
        if pid not in proc_names:
            proc_names[pid] = _lookup_name(pid)
        rows.append([proto, local, remote, state, str(pid), proc_names[pid]])

    if not rows:
        return "未找到匹配的端口映射。"
    rows.sort(key=lambda r: r[0])
    rows = rows[: max(1, min(int(limit), 100))]
    table = tabulate(
        rows,
        headers=["Proto", "Local", "Remote", "State", "PID", "Process"],
        tablefmt="simple",
    )
    return f"端口→进程映射 ({len(rows)} shown):\n{table}"


def _lookup_name(pid: int) -> str:
    try:
        import psutil

        return psutil.Process(pid).name()
    except Exception:
        return "-"
