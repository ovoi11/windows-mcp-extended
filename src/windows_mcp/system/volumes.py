"""Storage volumes — mounted drives, filesystems and free space."""

from __future__ import annotations

__all__ = ["list_volumes"]


def list_volumes() -> str:
    """List mounted storage volumes with usage."""
    import psutil
    from tabulate import tabulate

    rows: list[list[str]] = []
    for part in psutil.disk_partitions(all=True):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            free = f"{_fmt(usage.free)} free of {_fmt(usage.total)} ({usage.percent:.1f}% used)"
        except (OSError, PermissionError):
            free = "-"
        rows.append(
            [
                part.device or "-",
                part.mountpoint,
                part.fstype or "-",
                free,
            ]
        )

    if not rows:
        return "未找到磁盘卷。"
    rows.sort(key=lambda r: r[1])
    table = tabulate(rows, headers=["Device", "Mount", "FS", "Capacity"], tablefmt="simple")
    return f"磁盘卷 ({len(rows)}):\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
