"""Network adapters — physical/active NIC details (MAC, speed)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["network_adapters"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_NetworkAdapter -Filter 'PhysicalAdapter = True' | "
    "Select-Object Name,NetConnectionID,InterfaceType,MACAddress,Speed,"
    "NetEnabled,AdapterType | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def network_adapters(limit: int = 15) -> str:
    """List physical network adapters with MAC, type and link speed."""
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
        return "Error: adapter query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        name = (rec.get("Name") or "").strip()
        if not name:
            continue
        mac = (rec.get("MACAddress") or "").strip()
        speed = (rec.get("Speed") or "").strip()
        enabled = (rec.get("NetEnabled") or "").strip()
        rows.append(
            [
                name[:40],
                (rec.get("NetConnectionID") or "").strip() or "-",
                (rec.get("InterfaceType") or "").strip() or "-",
                mac or "-",
                _fmt_speed(int(speed)) if speed and speed.isdigit() else "-",
                "启用" if enabled.lower() == "true" else "禁用",
            ]
        )

    if not rows:
        return "未找到物理网卡。"
    rows = rows[: max(1, min(int(limit), 50))]
    table = tabulate(
        rows,
        headers=["Name", "Connection", "Type", "MAC", "Speed", "State"],
        tablefmt="simple",
    )
    return f"物理网卡 ({len(rows)}):\n{table}"


def _fmt_speed(bps: int) -> str:
    if bps <= 0:
        return "-"
    if bps >= 1_000_000_000:
        return f"{bps / 1_000_000_000:.0f} Gbps"
    return f"{bps / 1_000_000:.0f} Mbps"
