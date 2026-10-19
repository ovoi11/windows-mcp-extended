"""Windows event log reader — query recent events from a log channel."""

from __future__ import annotations

from typing import Literal

__all__ = ["read_event_log"]

_LEVEL_NAMES = {
    0: "INFO",
    1: "ERROR",
    2: "WARNING",
    4: "INFO",
    8: "AUDIT_OK",
    16: "AUDIT_FAIL",
}

_VALID_LOGS = ("Application", "Security", "System")


def read_event_log(
    log: str = "System",
    max_events: int = 20,
    level: Literal["error", "warning", "info"] | None = None,
    source: str | None = None,
) -> str:
    """Read the most recent events from a Windows event log."""
    if log not in _VALID_LOGS:
        return f"Error: log must be one of {_VALID_LOGS}."
    import win32evtlog
    from tabulate import tabulate

    try:
        hand = win32evtlog.OpenEventLog(None, log)
    except Exception as e:
        return f"Error opening event log {log!r}: {e} (may require administrator rights)."

    try:
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(hand, flags, 0)
    except Exception as e:
        return f"Error reading event log {log!r}: {e}."
    finally:
        win32evtlog.CloseEventLog(hand)

    rows = []
    for ev in events:
        evt_level = _LEVEL_NAMES.get(ev.EventType, str(ev.EventType))
        if level == "error" and evt_level != "ERROR":
            continue
        if level == "warning" and evt_level != "WARNING":
            continue
        if level == "info" and evt_level not in ("INFO", "AUDIT_OK"):
            continue
        if source and source.lower() not in (ev.SourceName or "").lower():
            continue
        timestamp = getattr(ev, "TimeGenerated", None)
        time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if timestamp else "?"
        inserts = ev.StringInserts or []
        desc = " ".join(str(x) for x in inserts)[:100] if inserts else ""
        rows.append([time_str, evt_level, ev.SourceName or "?", ev.EventID & 0xFFFF, desc])

    if not rows:
        return f"No events found in {log!r}{f' for source {source!r}' if source else ''}."
    rows = rows[:max_events]
    table = tabulate(rows, headers=["Time", "Level", "Source", "ID", "Description"], tablefmt="simple")
    return f"Event log {log!r} ({len(rows)} shown):\n{table}"
