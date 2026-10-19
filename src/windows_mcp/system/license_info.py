"""Windows license — activation status and product key presence."""

from __future__ import annotations

import subprocess
import winreg

__all__ = ["windows_license_info"]

_CREATE_NO_WINDOW = 0x08000000
_LICENSE_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"


def windows_license_info() -> str:
    """Report Windows edition, license state and partial product key."""
    from tabulate import tabulate

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _LICENSE_KEY) as key:
            edition = str(winreg.QueryValueEx(key, "EditionID")[0] or "?")
            product_name = str(winreg.QueryValueEx(key, "ProductName")[0] or "?")
            partial = str(winreg.QueryValueEx(key, "DigitalProductId4")[0] or "")
            build = str(winreg.QueryValueEx(key, "CurrentBuild")[0] or "?")
            rows.append(["版本", f"{product_name} ({edition})"])
            rows.append(["构建", build])
            key_tail = _product_key_tail(partial)
            if key_tail:
                rows.append(["产品密钥尾号", key_tail])
    except OSError:
        rows.append(["版本", "读取失败"])

    try:
        proc = subprocess.run(
            ["cscript.exe", "//nologo", r"C:\Windows\System32\slmgr.vbs", "/dli"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
        text = (proc.stdout or b"").decode("utf-8", errors="replace")
        if proc.returncode == 0 and text:
            for line in text.splitlines():
                line = line.strip()
                if line and ":" in line and "Error" not in line:
                    key, _, value = line.partition(":")
                    if key.strip() in ("License Status", "许可证状态"):
                        rows.append(["许可证状态", value.strip()])
                        break
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        rows.append(["许可证状态", "未知（slmgr 不可用）"])

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"Windows 授权信息:\n{table}"


def _product_key_tail(raw) -> str:
    """Extract the last 5 chars of the product key from DigitalProductId4."""
    try:
        data = bytes(raw)
        if not data:
            return ""
        return "".join(chr(b + ord("A")) if 0 < b < 26 else "-" for b in data[-10:-5])
    except Exception:
        return ""
