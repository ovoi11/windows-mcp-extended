"""Session information — interactive logon sessions (quser)."""

from __future__ import annotations

import csv
import io
import subprocess

__all__ = ["session_info"]

_CREATE_NO_WINDOW = 0x08000000


def session_info(limit: int = 30) -> str:
    """List interactive logon sessions."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["quser.exe", "/fo", "csv", "/nh"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return _query_session_fallback(limit)
    except subprocess.TimeoutExpired:
        return "Error: quser timed out."

    out = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    if proc.returncode != 0:
        if "无用户" in (out + err) or "no user" in (out + err).lower():
            return "当前没有交互式登录会话。"
        return f"Error querying sessions: {(out + err).strip()}"

    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(out)):
        username = (rec.get("USERNAME") or "").strip()
        if not username:
            continue
        rows.append(
            [
                username,
                (rec.get("SESSIONNAME") or "").strip() or "-",
                (rec.get("STATE") or "").strip() or "-",
                (rec.get("LOGON TIME") or "").strip() or "-",
            ]
        )

    if not rows:
        return "当前没有交互式登录会话。"
    rows = rows[:limit]
    table = tabulate(rows, headers=["User", "Session", "State", "Logon Time"], tablefmt="simple")
    return f"登录会话 ({len(rows)}):\n{table}"


def _query_session_fallback(limit: int) -> str:
    """Fallback when quser.exe is unavailable: query CIM logon sessions."""
    from tabulate import tabulate

    script = (
        "Get-CimInstance Win32_LoggedOnUser | ForEach-Object { $_.Antecedent } | "
        "ForEach-Object { ($_ -split '=')[1] } | Sort-Object -Unique | "
        "ConvertTo-Csv -NoTypeInformation"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return "Error: quser.exe / query.exe / powershell.exe 均不可用。"
    except subprocess.TimeoutExpired:
        return "Error: session query timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    users: list[str] = []
    for rec in csv.DictReader(io.StringIO(text)):
        u = (rec.get("Antecedent") or "").strip()
        if u:
            users.append(u)
    users = list(dict.fromkeys(users))[: max(1, min(int(limit), 30))]
    if not users:
        return "当前没有交互式登录会话。"
    rows = [[u] for u in users]
    table = tabulate(rows, headers=["Logged-on User"], tablefmt="simple")
    return f"登录用户 ({len(rows)}):\n{table}"
