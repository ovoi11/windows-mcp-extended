"""Printers — enumerate installed printers (Get-Printer)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["list_printers"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-Printer | Select-Object Name,DriverName,PortName,Shared,Published | "
    "ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_printers(limit: int = 30) -> str:
    """List installed printers."""
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
        return "Error: printer query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        if not name:
            continue
        driver = (rec.get("DriverName") or "").strip()
        port = (rec.get("PortName") or "").strip()
        shared = (rec.get("Shared") or "").strip()
        shared_mark = "共享" if shared.lower() == "true" else ""
        rows.append([name, driver or "-", port or "-", shared_mark])

    if not rows:
        return "未找到打印机。"
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "Driver", "Port", ""], tablefmt="simple")
    return f"打印机 ({len(rows)}):\n{table}"
