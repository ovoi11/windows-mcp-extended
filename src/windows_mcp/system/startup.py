"""Startup programs — list, add and remove HKCU auto-run entries."""

from __future__ import annotations

import winreg

__all__ = ["list_startup", "add_startup", "remove_startup"]

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"


def list_startup() -> str:
    """List current user's auto-run programs (registry Run key)."""
    from tabulate import tabulate

    rows = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            i = 0
            while True:
                try:
                    name, value, _type = winreg.EnumValue(key, i)
                    rows.append([name, value[:120]])
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        return "没有找到启动项（Run 键不存在）。"
    except OSError as e:
        return f"Error reading startup entries: {e}."
    if not rows:
        return "当前用户没有开机自启项。"
    rows.sort(key=lambda r: r[0].lower())
    table = tabulate(rows, headers=["Name", "Command"], tablefmt="simple")
    return f"开机自启项 ({len(rows)}):\n{table}"


def add_startup(name: str, command: str) -> str:
    """Add (or overwrite) a HKCU auto-run entry."""
    if not name or not command:
        return "Error: name and command are required."
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
    except OSError as e:
        return f"Error adding startup entry {name!r}: {e}."
    return f"启动项 {name!r} 已添加: {command}"


def remove_startup(name: str) -> str:
    """Remove a HKCU auto-run entry by name."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        return f"启动项 {name!r} 不存在。"
    except OSError as e:
        return f"Error removing startup entry {name!r}: {e}."
    return f"启动项 {name!r} 已移除。"
