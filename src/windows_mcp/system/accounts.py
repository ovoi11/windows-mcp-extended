"""User accounts — list local accounts and the current user (CIM)."""

from __future__ import annotations

import csv
import io
import os
import subprocess

__all__ = ["list_accounts"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_UserAccount -Filter \"LocalAccount=True\" | "
    "Select-Object Name,FullName,Disabled,SID | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_accounts(limit: int = 30) -> str:
    """List local user accounts and mark the current user."""
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
        return "Error: account query timed out."

    text = _decode(proc.stdout or b"")
    current = os.environ.get("USERNAME", "")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        full = (rec.get("FullName") or "").strip()
        disabled = (rec.get("Disabled") or "").strip()
        sid = (rec.get("SID") or "").strip()
        if not name:
            continue
        marker = "← 当前用户" if name.lower() == current.lower() else ""
        rows.append([name, full or "-", "禁用" if disabled.lower() == "true" else "启用", sid, marker])

    if not rows:
        return "未找到本地用户账户。"
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "FullName", "State", "SID", ""], tablefmt="simple")
    return f"本地用户账户 ({len(rows)}):\n{table}"
