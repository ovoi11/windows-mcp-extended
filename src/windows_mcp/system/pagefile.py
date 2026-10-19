"""Page file information — virtual memory and page file usage."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["pagefile_info"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_PageFileUsage | Select-Object Name,AllocatedBaseSize,"
    "CurrentUsage,PeakUsage | ConvertTo-Csv -NoTypeInformation;"
    "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVirtualMemorySize,"
    "FreeVirtualMemory | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def pagefile_info() -> str:
    """Report page file usage and virtual memory totals."""
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
        return "Error: page file query timed out."

    text = _decode(proc.stdout or b"")
    page_rows: list[list[str]] = []
    vm: dict[str, str] = {}
    for rec in csv.DictReader(io.StringIO(text)):
        if "AllocatedBaseSize" in rec:
            name = (rec.get("Name") or "").strip()
            if name:
                page_rows.append(
                    [
                        name,
                        (rec.get("AllocatedBaseSize") or "").strip() or "-",
                        (rec.get("CurrentUsage") or "").strip() or "-",
                        (rec.get("PeakUsage") or "").strip() or "-",
                    ]
                )
        elif "TotalVirtualMemorySize" in rec:
            vm = {k: (v or "").strip() for k, v in rec.items()}

    sections: list[str] = []
    if page_rows:
        sections.append(
            "页面文件:\n"
            + tabulate(
                page_rows,
                headers=["File", "Alloc(MB)", "Used(MB)", "Peak(MB)"],
                tablefmt="simple",
            )
        )
    else:
        sections.append("页面文件: 未获取到（可能由系统托管）")
    if vm.get("TotalVirtualMemorySize"):
        total = int(vm["TotalVirtualMemorySize"]) / 1024
        free = int(vm.get("FreeVirtualMemory", "0")) / 1024
        sections.append(f"虚拟内存: 总计 {total:.1f} MB，可用 {free:.1f} MB")

    return "虚拟内存状态:\n\n" + "\n\n".join(sections)
