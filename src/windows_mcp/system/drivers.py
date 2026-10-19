"""Driver information — enumerate system drivers via CIM."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["list_drivers"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_SystemDriver | Select-Object Name,DisplayName,State,"
    "StartMode | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_drivers(
    name: str | None = None,
    limit: int = 50,
) -> str:
    """List system drivers with state and start mode."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _SCRIPT],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=90,
        )
    except FileNotFoundError:
        return "Error: powershell.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: driver query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        drv_name = (rec.get("Name") or "").strip()
        display = (rec.get("DisplayName") or "").strip()
        state = (rec.get("State") or "").strip()
        start = (rec.get("StartMode") or "").strip()
        if not drv_name and not display:
            continue
        if name and name.lower() not in drv_name.lower() and name.lower() not in display.lower():
            continue
        rows.append([drv_name, display, state, start])

    if not rows:
        return f"No drivers found{f' matching {name!r}' if name else ''}."
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "Display", "State", "Start"], tablefmt="simple")
    return f"System drivers ({len(rows)} shown):\n{table}"
