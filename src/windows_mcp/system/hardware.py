"""Hardware inventory — memory modules, GPU and BIOS details via CIM."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["hardware_inventory"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,"
    "ConfiguredClockSpeed,Manufacturer,PartNumber | ConvertTo-Csv -NoTypeInformation;"
    "Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,"
    "DriverVersion | ConvertTo-Csv -NoTypeInformation;"
    "Get-CimInstance Win32_BIOS | Select-Object Manufacturer,SMBIOSBIOSVersion,"
    "ReleaseDate | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def hardware_inventory() -> str:
    """Summarize memory modules, GPU(s) and BIOS."""
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
        return "Error: hardware query timed out."

    text = _decode(proc.stdout or b"")
    mem_rows: list[list[str]] = []
    gpu_rows: list[list[str]] = []
    bios_row: dict[str, str] = {}
    for rec in csv.DictReader(io.StringIO(text)):
        if "Capacity" in rec:
            capacity = (rec.get("Capacity") or "").strip()
            if capacity.isdigit():
                mem_rows.append(
                    [
                        f"{int(capacity) / (1024**3):.0f} GB",
                        (rec.get("Speed") or "").strip() or "-",
                        (rec.get("Manufacturer") or "").strip() or "-",
                    ]
                )
        elif "AdapterRAM" in rec:
            name = (rec.get("Name") or "").strip()
            if name:
                gpu_rows.append([name, (rec.get("DriverVersion") or "").strip() or "-"])
        elif "SMBIOSBIOSVersion" in rec:
            bios_row = {k: (v or "").strip() for k, v in rec.items()}

    sections: list[str] = []
    if mem_rows:
        sections.append(
            "内存条:\n"
            + tabulate(mem_rows, headers=["Capacity", "Speed", "Manufacturer"], tablefmt="simple")
        )
    else:
        sections.append("内存条: 未获取到")
    if gpu_rows:
        sections.append(
            "显卡:\n" + tabulate(gpu_rows, headers=["Name", "Driver"], tablefmt="simple")
        )
    else:
        sections.append("显卡: 未获取到")
    if bios_row:
        bios_tbl = tabulate(
            [
                ["制造商", bios_row.get("Manufacturer") or "-"],
                ["版本", bios_row.get("SMBIOSBIOSVersion") or "-"],
                ["发布日期", (bios_row.get("ReleaseDate") or "-")[:10]],
            ],
            headers=["项目", "值"],
            tablefmt="simple",
        )
        sections.append(f"BIOS:\n{bios_tbl}")

    return "硬件清单:\n\n" + "\n\n".join(sections)
