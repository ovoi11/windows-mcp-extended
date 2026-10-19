"""Device errors — devices with configuration problems (CIM)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["device_errors"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 } | "
    "Select-Object Name,ConfigManagerErrorCode,Status | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def device_errors(limit: int = 20) -> str:
    """List devices reporting configuration errors."""
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
        return "Error: device query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        if not name:
            continue
        code = (rec.get("ConfigManagerErrorCode") or "").strip()
        rows.append(
            [
                name[:60],
                _describe(int(code)) if code.isdigit() else code,
                (rec.get("Status") or "").strip() or "-",
            ]
        )

    if not rows:
        return "未发现存在配置错误的设备。"
    rows = rows[: max(1, min(int(limit), 50))]
    table = tabulate(rows, headers=["Device", "Problem", "Status"], tablefmt="simple")
    return f"设备错误 ({len(rows)}):\n{table}"


def _describe(code: int) -> str:
    if code == 1:
        return "未配置正确"
    if code == 10:
        return "无法启动"
    if code == 22:
        return "已禁用"
    if code == 28:
        return "缺少驱动"
    return f"错误码 {code}"
