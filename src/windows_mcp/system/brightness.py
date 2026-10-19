"""Display brightness — read the current brightness via WMI (read-only)."""

from __future__ import annotations

import subprocess

__all__ = ["brightness_status"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance -Namespace root/wmi -ClassName WmiMonitorBrightness | "
    "Select-Object CurrentBrightness,Levels | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def brightness_status() -> str:
    """Report current display brightness percentage."""
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
        return "Error: brightness query timed out."

    import csv
    import io

    text = _decode(proc.stdout or b"")
    for rec in csv.DictReader(io.StringIO(text)):
        current = (rec.get("CurrentBrightness") or "").strip()
        levels = (rec.get("Levels") or "").strip()
        if not current:
            continue
        rows = [
            ["当前亮度", f"{current}%"],
            ["亮度档位", levels or "-"],
        ]
        table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
        return f"屏幕亮度:\n{table}"

    return "未获取到亮度信息（可能不支持 WMI 亮度查询或非笔记本/无环境光传感器）。"
