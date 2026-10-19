"""Recycle bin — size and item count via shell32 (read-only)."""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt

__all__ = ["recycle_bin_info"]

_SHQUERYRB = ctypes.windll.shell32.SHQueryRecycleBinW
_SHQUERYRB.restype = ctypes.c_int


def recycle_bin_info() -> str:
    """Report total size and item count of the recycle bin."""
    from tabulate import tabulate

    try:
        size = wt.DWORD()
        count = wt.DWORD()
        rc = _SHQUERYRB(None, ctypes.byref(size), ctypes.byref(count))
        if rc != 0:
            return f"Error querying recycle bin (code {rc})."
        size_bytes = size.value
        count_items = count.value
    except (AttributeError, OSError) as e:
        return f"Error querying recycle bin: {e}."

    rows = [
        ["条目数", str(count_items)],
        ["占用空间", _fmt(size_bytes)],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"回收站:\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
