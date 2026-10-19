"""Proxy settings — user/winhttp proxy configuration (read-only)."""

from __future__ import annotations

import subprocess
import winreg

__all__ = ["proxy_settings"]

_INTERNET_KEY = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
_CREATE_NO_WINDOW = 0x08000000


def proxy_settings() -> str:
    """Report IE/user proxy and WinHTTP proxy settings."""
    from tabulate import tabulate

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _INTERNET_KEY) as key:
            enabled = int(winreg.QueryValueEx(key, "ProxyEnable")[0] or 0)
            server = str(winreg.QueryValueEx(key, "ProxyServer")[0] or "")
            rows.append(["用户代理(IE)", "启用" if enabled else "禁用"])
            rows.append(["代理服务器", server if enabled and server else "-"])
    except OSError:
        rows.append(["用户代理(IE)", "读取失败"])

    try:
        proc = subprocess.run(
            ["netsh.exe", "winhttp", "show", "proxy"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
        text = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
        if proc.returncode == 0 and text:
            rows.append(["WinHTTP 代理", text.splitlines()[0]])
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        rows.append(["WinHTTP 代理", "查询失败"])

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"代理设置:\n{table}"
