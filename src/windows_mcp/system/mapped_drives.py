"""Mapped drives — network drive mappings (net use, read-only)."""

from __future__ import annotations

import subprocess

__all__ = ["mapped_drives"]

_CREATE_NO_WINDOW = 0x08000000


def mapped_drives() -> str:
    """List network drive mappings (net use, no credentials shown)."""
    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["net.exe", "use"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return "Error: net.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: net use timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    if proc.returncode != 0:
        return f"Error: {(err or text).strip()}"

    rows: list[list[str]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0].endswith(":"):
            rows.append([parts[0], parts[1], " ".join(parts[2:])[:80]])
        elif len(parts) >= 3 and parts[0].endswith(":"):
            rows.append([parts[0], parts[1], "-"])

    if not rows:
        return "当前没有网络驱动器映射。"
    table = tabulate(rows, headers=["Drive", "Share", "Note"], tablefmt="simple")
    return f"网络驱动器 ({len(rows)}):\n{table}"
