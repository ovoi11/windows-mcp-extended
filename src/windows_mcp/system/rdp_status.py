"""Remote desktop status — RDP configuration (registry, read-only)."""

from __future__ import annotations

import winreg

__all__ = ["remote_desktop_status"]

_TERMINAL_KEY = (
    r"SYSTEM\CurrentControlSet\Control\Terminal Server"
)


def remote_desktop_status() -> str:
    """Report whether Remote Desktop is enabled and the listening port."""
    from tabulate import tabulate

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _TERMINAL_KEY) as key:
            denied = int(winreg.QueryValueEx(key, "fDenyTSConnections")[0] or 1)
            rows.append(["远程桌面", "已启用" if denied == 0 else "已禁用"])
    except OSError:
        rows.append(["远程桌面", "读取失败"])

    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _TERMINAL_KEY + r"\WinStations\RDP-Tcp") as key:
            port = int(winreg.QueryValueEx(key, "PortNumber")[0] or 3389)
            rows.append(["监听端口", str(port)])
    except OSError:
        rows.append(["监听端口", "3389（默认）"])

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"远程桌面配置:\n{table}"
