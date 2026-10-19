"""Auto logon — whether the system auto-logs-in (security check)."""

from __future__ import annotations

import winreg

__all__ = ["auto_logon_check"]

_WINLOGON = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"


def auto_logon_check() -> str:
    """Report auto-logon configuration (username present, password stored)."""
    from tabulate import tabulate

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _WINLOGON) as key:
            username = str(winreg.QueryValueEx(key, "DefaultUserName")[0] or "")
            has_password = bool(winreg.QueryValueEx(key, "DefaultPassword")[0] or "")
            domain = str(winreg.QueryValueEx(key, "DefaultDomainName")[0] or "")
            rows.append(["自动登录", "已配置" if username else "未配置"])
            rows.append(["用户名", username or "-"])
            rows.append(["域", domain or "-"])
            rows.append(["明文密码存储", "是（安全风险）" if has_password else "否"])
    except OSError:
        rows.append(["自动登录", "读取失败"])

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"自动登录检查:\n{table}"
