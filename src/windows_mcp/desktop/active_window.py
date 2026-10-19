"""Active window — foreground window title, process and PID."""

from __future__ import annotations

import ctypes

__all__ = ["active_window_info"]

_GET_FOREGROUND = ctypes.windll.user32.GetForegroundWindow
_GET_TEXT = ctypes.windll.user32.GetWindowTextW
_GET_TEXT_LEN = ctypes.windll.user32.GetWindowTextLengthW
_GET_PID = ctypes.windll.user32.GetWindowThreadProcessId
_GET_WINPID = ctypes.windll.user32.GetWindowThreadProcessId


def active_window_info() -> str:
    """Report the foreground window's title, process and PID."""
    from tabulate import tabulate

    try:
        hwnd = _GET_FOREGROUND()
        if not hwnd:
            return "没有活动窗口（桌面或锁屏）。"
        length = _GET_TEXT_LEN(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        _GET_TEXT(hwnd, buf, length + 1)
        title = buf.value
        pid = ctypes.c_ulong()
        _GET_PID(hwnd, ctypes.byref(pid))
        proc_name = _proc_name(pid.value)
    except (AttributeError, OSError) as e:
        return f"Error querying active window: {e}."

    rows = [
        ["窗口句柄", hex(hwnd)],
        ["标题", title or "(无标题)"],
        ["PID", str(pid.value)],
        ["进程", proc_name],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"活动窗口:\n{table}"


def _proc_name(pid: int) -> str:
    try:
        import psutil

        return psutil.Process(pid).name()
    except Exception:
        return "-"
