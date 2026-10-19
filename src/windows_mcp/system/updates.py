"""Installed updates — enumerate Windows hotfixes (Get-HotFix)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["list_updates"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-HotFix | Select-Object HotFixID,Description,InstalledOn,InstalledBy | "
    "ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_updates(limit: int = 30) -> str:
    """List installed Windows updates (hotfixes)."""
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
        return "Error: update query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        hotfix = (rec.get("HotFixID") or "").strip()
        if not hotfix:
            continue
        desc = (rec.get("Description") or "").strip()
        installed_on = (rec.get("InstalledOn") or "").strip()
        installed_by = (rec.get("InstalledBy") or "").strip()
        rows.append([hotfix, desc[:40] or "-", installed_on or "-", installed_by or "-"])

    if not rows:
        return "未找到已安装的更新记录。"
    rows.sort(key=lambda r: r[0].lower(), reverse=True)
    rows = rows[:limit]
    table = tabulate(rows, headers=["HotFix", "Description", "Installed On", "By"], tablefmt="simple")
    return f"已安装更新 ({len(rows)} shown):\n{table}"
