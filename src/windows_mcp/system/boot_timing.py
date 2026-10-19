"""Boot timing — last boot duration from the event log (event 6013)."""

from __future__ import annotations

import ctypes
import winreg

__all__ = ["boot_timing"]

_SOURCE = "Microsoft-Windows-Diagnostics-Performance/Operational"
_EVENT_ID = 100


def boot_timing() -> str:
    """Report the last boot duration (diagnostics performance event 100)."""
    from tabulate import tabulate

    try:
        path = winreg.QueryValueEx(
            winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Diagnostics\Performance\Operational",
            ),
            "BootTime",
        )[0]
        ms = int(path)
        rows = [
            ["上次启动耗时", _fmt(ms)],
            ["毫秒", f"{ms:,}"],
        ]
    except OSError:
        # Fallback: report uptime instead of failing.
        import psutil

        uptime_s = int(psutil.boot_time())
        rows = [
            ["上次启动耗时", "未知（无诊断记录）"],
            ["当前已运行", _fmt_age(uptime_s)],
        ]
    except (ValueError, TypeError):
        rows = [["上次启动耗时", "记录格式异常"]]

    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"启动耗时:\n{table}"


def _fmt(ms: int) -> str:
    sec = ms / 1000
    if sec < 60:
        return f"{sec:.1f} 秒"
    return f"{sec / 60:.1f} 分钟"


def _fmt_age(boot_ts: int) -> str:
    import time

    days = int((time.time() - boot_ts) // 86400)
    hours = int((time.time() - boot_ts) % 86400 // 3600)
    return f"{days} 天 {hours} 小时"
