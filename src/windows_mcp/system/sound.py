"""Sound devices — enumerate audio devices via CIM."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["list_sound_devices"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_SoundDevice | Select-Object Name,Manufacturer,Status,"
    "StatusInfo | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_sound_devices(limit: int = 30) -> str:
    """List sound devices with manufacturer and status."""
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
        return "Error: sound device query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        if not name:
            continue
        manufacturer = (rec.get("Manufacturer") or "").strip()
        status = (rec.get("Status") or "").strip()
        rows.append([name, manufacturer or "-", status or "-"])

    if not rows:
        return "未找到音频设备。"
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "Manufacturer", "Status"], tablefmt="simple")
    return f"音频设备 ({len(rows)}):\n{table}"
