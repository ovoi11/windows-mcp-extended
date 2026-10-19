"""Network adapter configuration — IP, DHCP and DNS settings."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["network_config"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-NetIPConfiguration | Select-Object InterfaceAlias,IPv4Address,IPv4DefaultGateway,"
    "DNSServer | ConvertTo-Csv -NoTypeInformation -Depth 3"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def network_config(limit: int = 20) -> str:
    """List active network adapter IP configurations."""
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
        return "Error: network config query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        alias = (rec.get("InterfaceAlias") or "").strip()
        ipv4 = (rec.get("IPv4Address") or "").strip()
        if not alias and not ipv4:
            continue
        # IPv4Address/DNSServer arrive as nested JSON-ish text from ConvertTo-Csv -Depth.
        gw = (rec.get("IPv4DefaultGateway") or "").strip()[:40]
        dns = (rec.get("DNSServer") or "").strip()[:60]
        ip = _extract_ip(ipv4)
        rows.append([alias or "?", ip or "-", gw or "-", dns or "-"])

    if not rows:
        return "未获取到网络适配器配置。"
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Adapter", "IPv4", "Gateway", "DNS"], tablefmt="simple")
    return f"网络配置 ({len(rows)}):\n{table}"


def _extract_ip(text: str) -> str:
    """Pull the first IPv4 address out of ConvertTo-Csv nested text."""
    if not text:
        return ""
    if "IPAddress=" in text:
        part = text.split("IPAddress=", 1)[1]
        return part.split(";", 1)[0].strip()
    if "Address=" in text:
        part = text.split("Address=", 1)[1]
        return part.split(";", 1)[0].strip()
    return text[:40]
