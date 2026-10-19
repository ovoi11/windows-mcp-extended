"""Power plan management — list schemes and switch the active one (powercfg)."""

from __future__ import annotations

import re
import subprocess

__all__ = ["list_plans", "get_active_plan", "set_active_plan"]

_GUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_NAME_RE = re.compile(r"\(([^)]*)\)")

_CREATE_NO_WINDOW = 0x08000000


def _run(args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["powercfg.exe", *args],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return -1, "powercfg.exe not found on this system."
    except subprocess.TimeoutExpired:
        return -1, "powercfg.exe timed out."
    out = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    return proc.returncode, (out + err).strip()


def list_plans() -> str:
    """List power schemes (GUID + name + active marker)."""
    from tabulate import tabulate

    code, text = _run(["/list"])
    if code != 0:
        return f"Error listing power plans: {text}"
    rows = []
    for line in text.splitlines():
        guid_match = _GUID_RE.search(line)
        if not guid_match:
            continue
        name_match = _NAME_RE.search(line)
        name = name_match.group(1) if name_match else "?"
        active = "active" if "*" in line else ""
        rows.append([guid_match.group(0), name, active])
    if not rows:
        return "未找到电源方案。"
    table = tabulate(rows, headers=["GUID", "Name", "Active"], tablefmt="simple")
    return f"电源方案 ({len(rows)}):\n{table}"


def get_active_plan() -> str:
    """Report the active power scheme."""
    code, text = _run(["/getactivescheme"])
    if code != 0:
        return f"Error reading active power plan: {text}"
    guid_match = _GUID_RE.search(text)
    name_match = _NAME_RE.search(text)
    guid = guid_match.group(0) if guid_match else "?"
    name = name_match.group(1) if name_match else "?"
    return f"当前电源方案: {name}（{guid}）"


def set_active_plan(guid: str) -> str:
    """Switch to a power scheme by GUID."""
    if not _GUID_RE.fullmatch(guid):
        return "Error: invalid power plan GUID (expected xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx)."
    code, text = _run(["/setactive", guid])
    if code != 0:
        return f"Error switching power plan: {text}"
    return f"电源方案已切换: {guid}"
