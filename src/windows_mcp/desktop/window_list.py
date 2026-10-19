"""Window list — enumerate visible top-level windows (read-only)."""

from __future__ import annotations

import ctypes

__all__ = ["window_list"]

_EnumWindows = ctypes.windll.user32.EnumWindows
_EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
_IsWindowVisible = ctypes.windll.user32.IsWindowVisible
_GetWindowTextW = ctypes.windll.user32.GetWindowTextW
_GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
_GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId


def window_list(limit: int = 30) -> str:
    """List visible top-level windows with PID and title."""
    from tabulate import tabulate

    results: list[tuple[int, int, str]] = []

    def _cb(hwnd: int, _lparam: int) -> bool:
        if not _IsWindowVisible(hwnd):
            return True
        length = _GetWindowTextLengthW(hwnd)
        if length <= 0:
            return True
        buf = ctypes.create_unicode_buffer(length + 1)
        _GetWindowTextW(hwnd, buf, length + 1)
        title = buf.value
        if not title:
            return True
        pid = ctypes.c_ulong()
        _GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        results.append((pid.value, hwnd, title[:80]))
        return True

    try:
        _EnumWindows(_EnumWindowsProc(_cb), 0)
    except (AttributeError, OSError) as e:
        return f"Error enumerating windows: {e}."

    results.sort(key=lambda r: r[0])
    results = results[: max(1, min(int(limit), 200))]
    rows = [[str(pid), hex(hwnd), title] for pid, hwnd, title in results]
    table = tabulate(rows, headers=["PID", "HWND", "Title"], tablefmt="simple")
    return f"可见窗口 ({len(rows)} shown):\n{table}"
