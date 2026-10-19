"""Session processes — map processes to logon sessions (CIM)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["session_processes"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_Process | Group-Object SessionId | "
    "Select-Object Name,Count | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def session_processes(limit: int = 15) -> str:
    """Count running processes per logon session (session ID)."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _SCRIPT],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=120,
        )
    except FileNotFoundError:
        return "Error: powershell.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: session query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        sid = (rec.get("Name") or "").strip()
        count = (rec.get("Count") or "").strip()
        if sid.isdigit():
            rows.append([sid, count])

    if not rows:
        return "无法读取会话进程统计。"
    rows.sort(key=lambda r: int(r[0]))
    rows = rows[: max(1, min(int(limit), 30))]
    table = tabulate(rows, headers=["Session ID", "Processes"], tablefmt="simple")
    return f"会话进程统计 ({len(rows)}):\n{table}"
