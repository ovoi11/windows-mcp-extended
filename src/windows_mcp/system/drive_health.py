"""Drive health — physical disk health/status via Get-PhysicalDisk."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["drive_health"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-PhysicalDisk | Select-Object DeviceId,FriendlyName,MediaType,"
    "HealthStatus,OperationalStatus,Size | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def drive_health(limit: int = 10) -> str:
    """List physical disks with health status."""
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
        return "Error: disk query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        device = (rec.get("DeviceId") or "").strip()
        if not device:
            continue
        size = (rec.get("Size") or "").strip()
        rows.append(
            [
                device,
                (rec.get("FriendlyName") or "").strip()[:40] or "-",
                (rec.get("MediaType") or "").strip() or "-",
                (rec.get("HealthStatus") or "").strip() or "-",
                (rec.get("OperationalStatus") or "").strip() or "-",
                _fmt(int(size)) if size and size.isdigit() else "-",
            ]
        )

    if not rows:
        return "未找到物理磁盘信息（可能需要管理员权限）。"
    rows = rows[: max(1, min(int(limit), 30))]
    table = tabulate(
        rows,
        headers=["ID", "Name", "Media", "Health", "Op Status", "Size"],
        tablefmt="simple",
    )
    return f"物理磁盘健康 ({len(rows)}):\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} EB"
