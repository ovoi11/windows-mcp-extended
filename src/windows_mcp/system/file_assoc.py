"""File associations — query extension-to-application mappings (read-only)."""

from __future__ import annotations

import winreg

__all__ = ["list_associations"]

_CLASSES = [
    (winreg.HKEY_LOCAL_MACHINE, r"Software\Classes"),
    (winreg.HKEY_CURRENT_USER, r"Software\Classes"),
]


def _progid_description(progid: str) -> str:
    for root, base in _CLASSES:
        try:
            with winreg.OpenKey(root, base + "\\" + progid) as key:
                value, _ = winreg.QueryValueEx(key, None)
                return str(value) if value else ""
        except OSError:
            continue
    return ""


def list_associations(extension: str | None = None, limit: int = 50) -> str:
    """List file extension associations (.ext -> program)."""
    from tabulate import tabulate

    ext = extension if extension is None or extension.startswith(".") else f".{extension}"
    ext = (ext or "").lower()

    rows: list[list[str]] = []
    seen: set[tuple[str, str]] = set()
    for root, base in _CLASSES:
        try:
            with winreg.OpenKey(root, base) as key:
                i = 0
                while True:
                    try:
                        name = winreg.EnumKey(key, i)
                        i += 1
                    except OSError:
                        break
                    if not name.startswith("."):
                        continue
                    if ext and name.lower() != ext:
                        continue
                    try:
                        with winreg.OpenKey(key, name) as sub:
                            progid, _ = winreg.QueryValueEx(sub, None)
                    except OSError:
                        continue
                    progid = str(progid or "")
                    if not progid:
                        continue
                    key_pair = (name.lower(), progid)
                    if key_pair in seen:
                        continue
                    seen.add(key_pair)
                    rows.append([name, progid, _progid_description(progid)])
        except OSError:
            continue

    if not rows:
        return f"No associations found{f' for {ext!r}' if ext else ''}."
    rows.sort(key=lambda r: r[0])
    rows = rows[:limit]
    table = tabulate(rows, headers=["Extension", "ProgID", "App"], tablefmt="simple")
    return f"File associations ({len(rows)} shown):\n{table}"
