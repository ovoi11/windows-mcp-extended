"""Mouse position — current cursor coordinates (read-only)."""

from __future__ import annotations

import ctypes
import ctypes.wintypes

__all__ = ["mouse_position"]


def mouse_position() -> str:
    """Report the current cursor position in screen coordinates."""
    from tabulate import tabulate

    try:
        point = ctypes.wintypes.POINT()
        ok = ctypes.windll.user32.GetCursorPos(ctypes.byref(point))
        if not ok:
            return "Error: GetCursorPos failed."
        x, y = point.x, point.y
        virtual = _virtual_desktop()
    except (AttributeError, OSError) as e:
        return f"Error querying mouse position: {e}."

    rows = [
        ["X", str(x)],
        ["Y", str(y)],
        ["虚拟桌面", f"{virtual[0]} × {virtual[1]}" if virtual else "-"],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"鼠标位置:\n{table}"


def _virtual_desktop() -> tuple[int, int] | None:
    try:
        w = ctypes.windll.user32.GetSystemMetrics(78)  # SM_XVIRTUALSCREEN
        h = ctypes.windll.user32.GetSystemMetrics(79)  # SM_YVIRTUALSCREEN
        if w and h:
            return w, h
    except (AttributeError, OSError):
        pass
    return None
