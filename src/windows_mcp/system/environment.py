"""User environment variables — list, set and delete (HKCU\\Environment)."""

from __future__ import annotations

import os
import winreg
from typing import Literal

__all__ = ["list_environment", "set_environment", "delete_environment"]

_ENV_KEY = r"Environment"
_SCOPE_NAMES = ("user", "process")


def list_environment(scope: Literal["user", "process"] = "user") -> str:
    """List environment variables for the user (registry) or current process."""
    from tabulate import tabulate

    if scope == "process":
        rows = [[k, v[:120]] for k, v in sorted(os.environ.items())]
        if not rows:
            return "当前进程没有环境变量。"
        table = tabulate(rows, headers=["Name", "Value"], tablefmt="simple")
        return f"进程环境变量 ({len(rows)}):\n{table}"

    rows = []
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _ENV_KEY) as key:
            i = 0
            while True:
                try:
                    name, value, _type = winreg.EnumValue(key, i)
                    rows.append([name, value[:120]])
                    i += 1
                except OSError:
                    break
    except FileNotFoundError:
        return "用户环境变量不存在。"
    except OSError as e:
        return f"Error reading user environment: {e}."
    if not rows:
        return "用户环境变量为空。"
    rows.sort(key=lambda r: r[0].lower())
    table = tabulate(rows, headers=["Name", "Value"], tablefmt="simple")
    return f"用户环境变量 ({len(rows)}):\n{table}"


def set_environment(name: str, value: str, scope: Literal["user", "process"] = "user") -> str:
    """Set an environment variable for the user (registry) or current process."""
    if not name:
        return "Error: name is required."
    if scope == "process":
        os.environ[name] = value
        return f"进程环境变量 {name!r} 已设置（仅当前进程生效）。"
    try:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, _ENV_KEY) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
    except OSError as e:
        return f"Error setting user environment {name!r}: {e}."
    return f"用户环境变量 {name!r} 已设置（新进程生效）。"


def delete_environment(name: str, scope: Literal["user", "process"] = "user") -> str:
    """Delete an environment variable for the user (registry) or current process."""
    if not name:
        return "Error: name is required."
    if scope == "process":
        os.environ.pop(name, None)
        return f"进程环境变量 {name!r} 已删除（仅当前进程生效）。"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _ENV_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, name)
    except FileNotFoundError:
        return f"用户环境变量 {name!r} 不存在。"
    except OSError as e:
        return f"Error deleting user environment {name!r}: {e}."
    return f"用户环境变量 {name!r} 已删除（新进程生效）。"
