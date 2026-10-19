"""Installed fonts — enumerate system fonts (registry, read-only)."""

from __future__ import annotations

import winreg

__all__ = ["installed_fonts"]

_FONT_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"


def installed_fonts(limit: int = 30) -> str:
    """List installed font families and their files."""
    from tabulate import tabulate

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _FONT_KEY) as key:
            i = 0
            while True:
                try:
                    name, value, _type = winreg.EnumValue(key, i)
                    i += 1
                except OSError:
                    break
                rows.append([name, str(value)])
    except OSError as e:
        return f"Error reading fonts: {e}."

    if not rows:
        return "未找到已安装字体。"
    rows.sort(key=lambda r: r[0].lower())
    total = len(rows)
    rows = rows[: max(1, min(int(limit), 200))]
    table = tabulate(rows, headers=["Font", "File"], tablefmt="simple")
    return f"已安装字体 {total} 个（显示 {len(rows)}）:\n{table}"
