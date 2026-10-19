"""Windows Defender status — real-time protection state (PowerShell)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["defender_status"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-MpComputerStatus | Select-Object AntivirusEnabled,RealTimeProtectionEnabled,"
    "AntivirusSignatureVersion,AntivirusSignatureLastUpdated,"
    "QuickScanAge,FullScanAge | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def defender_status() -> str:
    """Report Windows Defender real-time protection and signature status."""
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
        return "Error: Defender query timed out."

    text = _decode(proc.stdout or b"")
    rec = next(csv.DictReader(io.StringIO(text)), None)
    if rec is None:
        return "无法读取 Defender 状态（可能未安装或需权限）。"

    rows = [
        ["反病毒启用", _yesno(rec.get("AntivirusEnabled"))],
        ["实时保护", _yesno(rec.get("RealTimeProtectionEnabled"))],
        ["病毒库版本", (rec.get("AntivirusSignatureVersion") or "").strip() or "-"],
        ["病毒库更新", (rec.get("AntivirusSignatureLastUpdated") or "").strip() or "-"],
        ["上次快速扫描(天)", (rec.get("QuickScanAge") or "").strip() or "-"],
        ["上次全盘扫描(天)", (rec.get("FullScanAge") or "").strip() or "-"],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"Windows Defender 状态:\n{table}"


def _yesno(v) -> str:
    s = str(v or "").strip().lower()
    return "启用" if s == "true" else "禁用" if s == "false" else (s or "-")
