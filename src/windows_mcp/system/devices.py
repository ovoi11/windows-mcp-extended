"""Plug-and-play devices — list present devices via Get-PnpDevice."""

from __future__ import annotations

import csv
import io
import subprocess
from typing import Literal

__all__ = ["list_devices"]

_CREATE_NO_WINDOW = 0x08000000

_CLASS_ALIASES = {
    "usb": "USB",
    "display": "Display",
    "network": "Net",
    "storage": "DiskDrive",
    "bluetooth": "Bluetooth",
    "printer": "Printer",
    "audio": "Media",
    "keyboard": "Keyboard",
    "mouse": "Mouse",
}
_CLASS_NAMES = ("all",) + tuple(_CLASS_ALIASES)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def _run_powershell(script: str) -> tuple[int, str]:
    cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script]
    try:
        proc = subprocess.run(cmd, capture_output=True, creationflags=_CREATE_NO_WINDOW, timeout=90)
    except FileNotFoundError:
        return -1, "powershell.exe not found on this system."
    except subprocess.TimeoutExpired:
        return -1, "powershell.exe timed out."
    err = _decode(proc.stderr or b"")
    return proc.returncode, _decode(proc.stdout or b"") + err


def list_devices(
    class_name: Literal["all", "usb", "display", "network", "storage", "bluetooth", "printer", "audio", "keyboard", "mouse"] = "all",
    limit: int = 30,
) -> str:
    """List present plug-and-play devices, optionally filtered by device class."""
    from tabulate import tabulate

    cls = _CLASS_ALIASES.get(class_name)
    script = "Get-PnpDevice -PresentOnly"
    if cls:
        script += f" -Class '{cls}'"
    script += " | Select-Object Class,FriendlyName,Status | ConvertTo-Csv -NoTypeInformation"

    code, text = _run_powershell(script)
    if code != 0:
        return f"Error enumerating devices: {text.strip() or 'unknown error'}"

    reader = csv.DictReader(io.StringIO(text))
    rows: list[list[str]] = []
    for rec in reader:
        friendly = (rec.get("FriendlyName") or "").strip()
        status = (rec.get("Status") or "").strip()
        dev_class = (rec.get("Class") or "").strip()
        if not friendly and not status:
            continue
        rows.append([dev_class, friendly, status])

    if not rows:
        return f"没有发现{f' {class_name}' if class_name != 'all' else ''}类设备。"
    rows = rows[:limit]
    table = tabulate(rows, headers=["Class", "Name", "Status"], tablefmt="simple")
    return f"设备列表 ({len(rows)} shown):\n{table}"
