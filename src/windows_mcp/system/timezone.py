"""Time zone information — current zone, offset and DST status."""

from __future__ import annotations

import subprocess

__all__ = ["timezone_info"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-TimeZone | Select-Object Id,DisplayName,SupportsDaylightSavingTime,"
    "IsDaylightSavingTime,UtcOffset | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def timezone_info() -> str:
    """Report the current time zone, UTC offset and DST state."""
    import csv
    import io

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
        return "Error: timezone query timed out."

    text = _decode(proc.stdout or b"")
    rec = None
    for row in csv.DictReader(io.StringIO(text)):
        rec = {k: (v or "").strip() for k, v in row.items()}
        break

    if not rec:
        return "未获取到时区信息。"

    dst = rec.get("IsDaylightSavingTime")
    dst_state = "是" if dst and dst.lower() == "true" else "否"
    offset = rec.get("UtcOffset") or "-"
    rows = [
        ["时区 ID", rec.get("Id") or "?"],
        ["显示名称", rec.get("DisplayName") or "?"],
        ["UTC 偏移", offset],
        ["支持夏令时", "是" if (rec.get("SupportsDaylightSavingTime") or "").lower() == "true" else "否"],
        ["当前夏令时", dst_state],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"时区信息:\n{table}"
