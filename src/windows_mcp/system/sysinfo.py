"""System information — hardware, OS and manufacturer summary via CIM."""

from __future__ import annotations

import subprocess

__all__ = ["system_info"]

_CREATE_NO_WINDOW = 0x08000000

_SEP = "---SYSMCP_SEP---"

_CIM_SCRIPT = (
    f"Write-Output '{_SEP}';"
    "Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model,"
    "TotalPhysicalMemory,NumberOfLogicalProcessors | ConvertTo-Csv -NoTypeInformation;"
    f"Write-Output '{_SEP}';"
    "Get-CimInstance Win32_Processor | Select-Object -First 1 Name,MaxClockSpeed | "
    "ConvertTo-Csv -NoTypeInformation;"
    f"Write-Output '{_SEP}';"
    "Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,OSArchitecture | "
    "ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def system_info() -> str:
    """Summarize machine hardware and OS information."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _CIM_SCRIPT],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=90,
        )
    except FileNotFoundError:
        return "Error: powershell.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: CIM query timed out."

    import csv
    import io

    text = _decode(proc.stdout or b"")
    blocks = [b.strip() for b in text.split(_SEP) if b.strip()]
    records: list[dict[str, str]] = []
    for block in blocks:
        for rec in csv.DictReader(io.StringIO(block)):
            records.append({k: (v or "").strip() for k, v in rec.items()})

    merged: dict[str, str] = {}
    for rec in records:
        merged.update(rec)

    if not merged:
        return "Error: 未获取到系统信息。"

    rows: list[list[str]] = []
    if merged.get("Manufacturer"):
        rows.append(["制造商", merged["Manufacturer"]])
    if merged.get("Model"):
        rows.append(["型号", merged["Model"]])
    if merged.get("Name"):
        rows.append(["CPU", merged["Name"]])
        if merged.get("MaxClockSpeed"):
            rows[-1][1] += f" @ {int(float(merged['MaxClockSpeed']))} MHz"
    if merged.get("NumberOfLogicalProcessors"):
        rows.append(["逻辑核心", merged["NumberOfLogicalProcessors"]])
    if merged.get("TotalPhysicalMemory"):
        rows.append(["物理内存", f"{int(merged['TotalPhysicalMemory']) / (1024**3):.1f} GB"])
    if merged.get("Caption"):
        rows.append(["操作系统", merged["Caption"]])
    if merged.get("Version"):
        rows.append(["版本", merged["Version"]])
    if merged.get("OSArchitecture"):
        rows.append(["架构", merged["OSArchitecture"]])

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"系统信息:\n{table}"
