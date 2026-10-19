"""Domain membership — workgroup vs domain (CIM)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["domain_membership"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-CimInstance Win32_ComputerSystem | Select-Object Name,"
    "Domain,PartOfDomain,Workgroup,Manufacturer,Model | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def domain_membership() -> str:
    """Report whether the machine is domain-joined and its workgroup/domain."""
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
        return "Error: system query timed out."

    text = _decode(proc.stdout or b"")
    rec = next(csv.DictReader(io.StringIO(text)), None)
    if rec is None:
        return "无法读取域成员信息。"

    part_of_domain = (rec.get("PartOfDomain") or "").strip().lower() == "true"
    rows = [
        ["计算机名", (rec.get("Name") or "").strip() or "-"],
        ["域成员", "是" if part_of_domain else "否（工作组）"],
        ["域/工作组", (rec.get("Domain") or rec.get("Workgroup") or "-").strip()],
        ["制造商", (rec.get("Manufacturer") or "").strip()[:40] or "-"],
        ["型号", (rec.get("Model") or "").strip()[:40] or "-"],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"域成员信息:\n{table}"
