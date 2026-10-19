"""Wake source — what woke the system (powercfg, read-only)."""

from __future__ import annotations

import subprocess

__all__ = ["wake_source_info"]

_CREATE_NO_WINDOW = 0x08000000


def wake_source_info() -> str:
    """Report the last wake source and pending wake timers."""
    try:
        proc = subprocess.run(
            ["powercfg.exe", "/lastwake"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return "Error: powercfg.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: powercfg timed out."

    last_wake = (proc.stdout or b"").decode("utf-8", errors="replace").strip()
    timers = ""
    try:
        proc2 = subprocess.run(
            ["powercfg.exe", "/waketimers"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
        timers = (proc2.stdout or b"").decode("utf-8", errors="replace").strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        timers = ""

    parts = [f"上次唤醒来源:\n{last_wake or '(无记录)'}"]
    if timers:
        parts.append(f"\n唤醒计时器:\n{timers[:1200]}")
    return "\n".join(parts)
