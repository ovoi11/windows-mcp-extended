"""Bluetooth devices — paired/enumerated Bluetooth hardware (CIM)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["bluetooth_devices"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -eq 'Bluetooth' } | "
    "Select-Object Name,Status,ConfigManagerErrorCode | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def bluetooth_devices(limit: int = 15) -> str:
    """List Bluetooth devices (paired radios and peripherals)."""
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
        return "Error: bluetooth query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        if not name:
            continue
        code = (rec.get("ConfigManagerErrorCode") or "").strip()
        rows.append(
            [
                name[:50],
                (rec.get("Status") or "").strip() or "-",
                "正常" if code in ("", "0") else f"错误 {code}",
            ]
        )

    if not rows:
        return "未找到蓝牙设备。"
    rows = rows[: max(1, min(int(limit), 50))]
    table = tabulate(rows, headers=["Device", "Status", "State"], tablefmt="simple")
    return f"蓝牙设备 ({len(rows)}):\n{table}"
