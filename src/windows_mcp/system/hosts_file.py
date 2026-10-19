"""Hosts file reader — parse the Windows hosts file (read-only).

NOTE: 待排障点/风险操作 — modifying the hosts file is a system-level change
that can break DNS resolution. Write operations (add/remove entries) are
intentionally NOT implemented in V5; the recommended safe design is:
  1. backup hosts -> hosts.bak
  2. rewrite with an explicit "## managed by Windows-MCP" marker block
  3. only touch entries inside that marker block
until the user explicitly opts in with a write flag.
"""

from __future__ import annotations

import os

__all__ = ["read_hosts"]

_HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"


def read_hosts() -> str:
    """Return the non-comment entries of the hosts file."""
    from tabulate import tabulate

    if not os.path.exists(_HOSTS_PATH):
        return f"Error: hosts file not found at {_HOSTS_PATH}."
    try:
        with open(_HOSTS_PATH, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError as e:
        return f"Error reading hosts file: {e}."

    rows: list[list[str]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        ip = parts[0]
        hosts = " ".join(parts[1:]) if len(parts) > 1 else "-"
        rows.append([ip, hosts])

    if not rows:
        return f"hosts 文件没有启用的条目（{_HOSTS_PATH}）。"
    table = tabulate(rows, headers=["IP", "Hostnames"], tablefmt="simple")
    return f"hosts 条目 ({len(rows)}):\n{table}"
