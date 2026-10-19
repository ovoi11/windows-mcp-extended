"""Installed programs by size — estimated disk footprint (registry)."""

from __future__ import annotations

import winreg

__all__ = ["programs_by_size"]

_UNINSTALL_KEYS = [
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
    (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
]


def programs_by_size(limit: int = 20) -> str:
    """List installed programs with estimated install size, largest first."""
    from tabulate import tabulate

    programs: dict[str, tuple[int, str]] = {}

    def scan(hive, base: str) -> None:
        try:
            with winreg.OpenKey(hive, base) as key:
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(key, i)
                        i += 1
                    except OSError:
                        break
                    try:
                        with winreg.OpenKey(key, sub) as sk:
                            name = str(winreg.QueryValueEx(sk, "DisplayName")[0] or "")
                            size = int(winreg.QueryValueEx(sk, "EstimatedSize")[0] or 0)
                            if name and size:
                                programs[name] = (size * 1024, "KB→bytes")
                    except OSError:
                        continue
        except OSError:
            return

    for hive, base in _UNINSTALL_KEYS:
        scan(hive, base)

    if not programs:
        return "未找到带大小记录的已安装程序。"
    ranked = sorted(programs.items(), key=lambda kv: kv[1][0], reverse=True)
    ranked = ranked[: max(1, min(int(limit), 50))]
    rows = [[name[:50], _fmt(size)] for name, (size, _) in ranked]
    table = tabulate(rows, headers=["Program", "Est. Size"], tablefmt="simple")
    return f"已安装程序按大小 ({len(rows)} shown):\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
