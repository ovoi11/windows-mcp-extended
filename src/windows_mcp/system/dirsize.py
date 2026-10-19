"""Directory size — measure the disk footprint of a folder."""

from __future__ import annotations

import os

__all__ = ["directory_size"]


def directory_size(path: str, depth: int = 1) -> str:
    """Report the total size of a directory and its top-level children."""
    from tabulate import tabulate

    if not os.path.isdir(path):
        return f"Error: path is not a directory: {path}"
    depth = max(0, min(int(depth), 3))

    def walk_size(root: str) -> int:
        total = 0
        try:
            for dirpath, _dirnames, filenames in os.walk(root):
                for fn in filenames:
                    try:
                        total += os.path.getsize(os.path.join(dirpath, fn))
                    except OSError:
                        continue
        except OSError:
            pass
        return total

    grand_total = walk_size(path)
    rows: list[list[str]] = []
    if depth > 0:
        try:
            for entry in sorted(os.listdir(path), key=str.lower):
                full = os.path.join(path, entry)
                try:
                    if os.path.isdir(full):
                        size = walk_size(full)
                        kind = "dir"
                    elif os.path.isfile(full):
                        size = os.path.getsize(full)
                        kind = "file"
                    else:
                        continue
                except OSError:
                    continue
                rows.append([entry, kind, _fmt(size)])
        except OSError as e:
            return f"Error reading directory: {e}."

    table = tabulate(
        [[path, "total", _fmt(grand_total)]] + rows,
        headers=["Path/Item", "Type", "Size"],
        tablefmt="simple",
    )
    return f"目录大小（{path}）:\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
