"""Network shares — enumerate shared folders (Win32_Share)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["list_shares"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_Share | Select-Object Name,Path,Description,Type | "
    "ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_shares(limit: int = 30) -> str:
    """List shared folders on this machine."""
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
        return "Error: share query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        if not name:
            continue
        path = (rec.get("Path") or "").strip()
        desc = (rec.get("Description") or "").strip()
        share_type = (rec.get("Type") or "").strip()
        rows.append([name, path or "-", desc or "-", share_type])

    if not rows:
        return "没有共享文件夹。"
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "Path", "Description", "Type"], tablefmt="simple")
    return f"共享文件夹 ({len(rows)}):\n{table}"
