"""Windows service control — list, start, stop and restart services."""

from __future__ import annotations

from typing import Literal

__all__ = ["list_services", "control_service"]

# Service state codes (win32service.SERVICE_*_STATE)
_STATE_NAMES = {
    1: "STOPPED",
    2: "START_PENDING",
    3: "STOP_PENDING",
    4: "RUNNING",
    5: "CONTINUE_PENDING",
    6: "PAUSE_PENDING",
    7: "PAUSED",
}

# Start type codes (win32service.SERVICE_*)
_START_NAMES = {
    0: "BOOT",
    1: "SYSTEM",
    2: "AUTO",
    3: "MANUAL",
    4: "DISABLED",
}

_ACTIONS = ("start", "stop", "restart")


def list_services(
    name: str | None = None,
    state: Literal["running", "stopped"] | None = None,
    limit: int = 50,
) -> str:
    """List Windows services with optional name filter and state filter."""
    import win32service
    from tabulate import tabulate

    scm = win32service.OpenSCManager(
        None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE
    )
    try:
        services = win32service.EnumServicesStatusEx(
            scm,
            win32service.SERVICE_WIN32,
            win32service.SERVICE_STATE_ALL,
        )
    finally:
        win32service.CloseServiceHandle(scm)

    rows = []
    for entry in services:
        if isinstance(entry, dict):  # newer pywin32 returns dict entries
            svc_name = str(entry.get("ServiceName", "") or "")
            display_name = str(entry.get("DisplayName", "") or "")
            svc_state = entry.get("CurrentState", 0)
        else:  # classic tuple: (name, display, type, state, ...)
            svc_name, display_name = str(entry[0]), str(entry[1])
            svc_state = entry[3]
        svc_state_name = _STATE_NAMES.get(svc_state, str(svc_state))
        # EnumServicesStatusEx does not return start type; querying it per
        # service would be slow, so show "-" (start type via ServiceStartName
        # would need QueryServiceConfig per handle).
        if state == "running" and svc_state_name != "RUNNING":
            continue
        if state == "stopped" and svc_state_name not in ("STOPPED", "PAUSED"):
            continue
        if name and name.lower() not in svc_name.lower() and name.lower() not in display_name.lower():
            continue
        rows.append([svc_name, display_name, svc_state_name, "-"])

    if not rows:
        return f"No services found{f' matching "{name}"' if name else ''}."
    rows.sort(key=lambda r: r[0].lower())
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "Display", "State", "Start"], tablefmt="simple")
    return f"Services ({len(rows)} shown):\n{table}"


def control_service(name: str, action: Literal["start", "stop", "restart"]) -> str:
    """Start, stop or restart a Windows service by service name."""
    if action not in _ACTIONS:
        return f"Error: action must be one of {_ACTIONS}."
    import win32service
    import win32serviceutil

    try:
        if action == "start":
            win32serviceutil.StartService(name)
            return f"Service {name!r}: start requested."
        if action == "stop":
            win32serviceutil.StopService(name)
            return f"Service {name!r}: stop requested."
        # restart
        win32serviceutil.RestartService(name)
        return f"Service {name!r}: restart requested."
    except win32service.error as e:
        code = getattr(e, "winerror", None) or getattr(e, "args", (None,))[0]
        if code in (1056, 1058):  # already running / not installed
            hint = "service may already be running, not installed, or access denied"
        else:
            hint = "access denied (try as administrator) or service is not installed"
        return f"Error controlling service {name!r}: {e} ({hint})."
    except Exception as e:  # pragma: no cover - defensive
        return f"Error controlling service {name!r}: {e}."
