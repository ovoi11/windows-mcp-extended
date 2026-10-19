"""Process command lines — query Win32_Process for full command lines."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["list_process_command_lines"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_Process | Select-Object ProcessId,Name,ExecutablePath,"
    "CommandLine | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_process_command_lines(
    name: str | None = None,
    limit: int = 50,
) -> str:
    """List processes with executable path and full command line."""
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
        return "Error: process query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        pid = (rec.get("ProcessId") or "").strip()
        proc_name = (rec.get("Name") or "").strip()
        if not pid:
            continue
        if name and name.lower() not in proc_name.lower():
            continue
        cmdline = (rec.get("CommandLine") or "").strip() or "-"
        rows.append([pid, proc_name or "?", cmdline[:150]])

    if not rows:
        return f"No processes found{f' matching {name!r}' if name else ''}."
    rows.sort(key=lambda r: int(r[0]) if r[0].isdigit() else 0)
    rows = rows[:limit]
    table = tabulate(rows, headers=["PID", "Name", "Command Line"], tablefmt="simple")
    return f"进程命令行 ({len(rows)} shown):\n{table}"
