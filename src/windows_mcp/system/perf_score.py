"""System performance score — WinSAT ratings (WMI)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["system_performance_score"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_WinSAT | Select-Object WinSPRLevel,"
    "CPUScore,MemoryScore,DiskScore,GraphicsScore,GameGraphicsScore | "
    "ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def system_performance_score() -> str:
    """Report the Windows Experience Index (WinSAT) scores."""
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
        return "Error: WinSAT query timed out."

    text = _decode(proc.stdout or b"")
    rec = next(csv.DictReader(io.StringIO(text)), None)
    if rec is None:
        return "未找到 WinSAT 评分（可能尚未运行评估）。"

    labels = [
        ("综合", "WinSPRLevel"),
        ("CPU", "CPUScore"),
        ("内存", "MemoryScore"),
        ("磁盘", "DiskScore"),
        ("显卡", "GraphicsScore"),
        ("游戏显卡", "GameGraphicsScore"),
    ]
    rows: list[list[str]] = []
    for label, field in labels:
        value = (rec.get(field) or "").strip()
        rows.append([label, value if value and value != "0" else "-"])
    table = tabulate(rows, headers=["组件", "评分"], tablefmt="simple")
    return f"系统性能评分 (WinSAT):\n{table}"
