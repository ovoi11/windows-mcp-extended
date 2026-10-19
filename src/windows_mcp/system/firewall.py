"""Firewall status — Windows Defender Firewall profiles (netsh)."""

from __future__ import annotations

import subprocess

__all__ = ["firewall_status"]

_CREATE_NO_WINDOW = 0x08000000


def _run(args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["netsh.exe", "advfirewall", *args],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return -1, "netsh.exe not found on this system."
    except subprocess.TimeoutExpired:
        return -1, "netsh.exe timed out."
    out = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    return proc.returncode, (out + err).strip()


def firewall_status() -> str:
    """Report the state of each firewall profile."""
    from tabulate import tabulate

    code, text = _run(["show", "allprofiles"])
    if code != 0:
        return f"Error: {text.splitlines()[0] if text else 'netsh returned an error.'}"

    rows: list[list[str]] = []
    current_profile: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if ":" not in stripped:
            if stripped and "设置" not in stripped and "状态" not in stripped:
                # netsh prints profile sections like "域配置文件设置:" — keep the name.
                name = stripped.rstrip(":")
                if name and not any(k in name for k in ("设置", "状态", "策略", "日志")):
                    current_profile = name
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        if "状态" in key or "State" in key:
            rows.append([current_profile or "?", "状态", value])
        elif "入站" in key or "Inbound" in key:
            rows.append([current_profile or "?", "入站", value])
        elif "出站" in key or "Outbound" in key:
            rows.append([current_profile or "?", "出站", value])

    if not rows:
        return f"防火墙状态:\n{text}"
    table = tabulate(rows, headers=["Profile", "Rule", "Value"], tablefmt="simple")
    return f"防火墙状态:\n{table}"
