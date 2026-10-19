"""System status summary — CPU, memory, disk, battery and uptime."""

from __future__ import annotations

__all__ = ["system_status"]


def system_status() -> str:
    """Summarize key system health metrics."""
    import datetime

    import psutil
    from tabulate import tabulate

    rows: list[list[str]] = []

    cpu = psutil.cpu_percent(interval=0.1)
    cores = psutil.cpu_count(logical=True) or 0
    rows.append(["CPU", f"{cpu:.1f}% ({cores} logical cores)"])

    mem = psutil.virtual_memory()
    rows.append(
        [
            "内存",
            f"{_fmt(mem.used)} / {_fmt(mem.total)} ({mem.percent:.1f}% used)",
        ]
    )

    try:
        disk = psutil.disk_usage("C:\\")
        rows.append(
            [
                "磁盘 C:",
                f"{_fmt(disk.used)} / {_fmt(disk.total)} ({disk.percent:.1f}% used)",
            ]
        )
    except OSError:
        rows.append(["磁盘 C:", "不可用"])

    try:
        bat = psutil.sensors_battery()
        if bat:
            plug = "充电中" if bat.power_plugged else "使用电池"
            rows.append(["电池", f"{bat.percent}% ({plug})"])
        else:
            rows.append(["电池", "无电池或不可用"])
    except (AttributeError, OSError):
        rows.append(["电池", "不可用"])

    try:
        boot = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot
        days = uptime.days
        hours, rem = divmod(uptime.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        rows.append(
            [
                "开机时间",
                f"{boot:%Y-%m-%d %H:%M:%S}（已运行 {days} 天 {hours} 小时 {minutes} 分）",
            ]
        )
    except (OSError, ValueError):
        rows.append(["开机时间", "不可用"])

    table = tabulate(rows, headers=["指标", "值"], tablefmt="simple")
    return f"系统状态:\n{table}"


def _fmt(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"
