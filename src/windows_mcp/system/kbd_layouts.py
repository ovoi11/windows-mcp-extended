"""Keyboard layouts — installed layouts and the current user's preload list."""

from __future__ import annotations

import winreg

__all__ = ["list_keyboard_layouts"]

_LAYOUTS_KEY = r"SYSTEM\CurrentControlSet\Control\Keyboard Layouts"
_PRELOAD_KEY = r"Keyboard Layout\Preload"


def list_keyboard_layouts() -> str:
    """List installed keyboard layouts and mark the preloaded ones."""
    from tabulate import tabulate

    # Preload list (HKCU) — ordered input methods for this user.
    preload: list[str] = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _PRELOAD_KEY) as key:
            i = 0
            while True:
                try:
                    _name, value, _type = winreg.EnumValue(key, i)
                    preload.append(str(value))
                    i += 1
                except OSError:
                    break
    except OSError:
        pass

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _LAYOUTS_KEY) as key:
            i = 0
            while True:
                try:
                    klid = winreg.EnumKey(key, i)
                    i += 1
                except OSError:
                    break
                try:
                    with winreg.OpenKey(key, klid) as sub:
                        text = ""
                        layout_file = ""
                        for field in ("Layout Text", "Layout File", "Layout Display Name"):
                            try:
                                value, _ = winreg.QueryValueEx(sub, field)
                                if field == "Layout Text" and value:
                                    text = str(value)
                                elif field == "Layout File" and value:
                                    layout_file = str(value)
                            except OSError:
                                continue
                except OSError:
                    continue
                marker = "预载" if klid in preload else ""
                rows.append([klid, text or "-", layout_file or "-", marker])
    except OSError as e:
        return f"Error reading keyboard layouts: {e}."

    if not rows:
        return "未找到键盘布局。"
    rows.sort(key=lambda r: r[0])
    table = tabulate(rows, headers=["KLID", "Layout", "File", ""], tablefmt="simple")
    return f"键盘布局 ({len(rows)}):\n{table}"
