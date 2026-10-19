"""Installed applications — enumerate software from the Uninstall registry keys."""

from __future__ import annotations

import winreg

__all__ = ["list_apps"]

_UNINSTALL_KEYS = [
    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
    r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
]


def _iter_uninstall(root: int) -> list[dict[str, str]]:
    apps: list[dict[str, str]] = []
    for key_path in _UNINSTALL_KEYS:
        try:
            with winreg.OpenKey(root, key_path) as key:
                i = 0
                while True:
                    try:
                        sub_name = winreg.EnumKey(key, i)
                        i += 1
                    except OSError:
                        break
                    try:
                        with winreg.OpenKey(key, sub_name) as sub:
                            app: dict[str, str] = {}
                            for field, target in (
                                ("DisplayName", "name"),
                                ("DisplayVersion", "version"),
                                ("Publisher", "publisher"),
                                ("InstallDate", "installed"),
                            ):
                                try:
                                    value, _type = winreg.QueryValueEx(sub, field)
                                    if value:
                                        app[target] = str(value)
                                except OSError:
                                    pass
                            if app.get("name"):
                                apps.append(app)
                    except OSError:
                        continue
        except OSError:
            continue
    return apps


def list_apps(
    name: str | None = None,
    limit: int = 50,
    include_hidden: bool = False,
) -> str:
    """List installed applications (per-machine + current-user)."""
    from tabulate import tabulate

    apps: list[dict[str, str]] = []
    try:
        apps.extend(_iter_uninstall(winreg.HKEY_LOCAL_MACHINE))
    except OSError:
        pass
    try:
        apps.extend(_iter_uninstall(winreg.HKEY_CURRENT_USER))
    except OSError:
        pass

    # De-duplicate by (name, version).
    seen: set[tuple[str, str]] = set()
    unique: list[dict[str, str]] = []
    for app in apps:
        key = (app.get("name", ""), app.get("version", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(app)

    if name:
        needle = name.lower()
        unique = [a for a in unique if needle in a.get("name", "").lower()]

    if not include_hidden:
        unique = [a for a in unique if not a.get("name", "").startswith(("{", "KB"))]

    if not unique:
        return f"No applications found{f' matching {name!r}' if name else ''}."
    unique.sort(key=lambda a: a.get("name", "").lower())
    unique = unique[:limit]
    rows = [
        [a.get("name", "?"), a.get("version", "-"), a.get("publisher", "-"), a.get("installed", "-")]
        for a in unique
    ]
    table = tabulate(rows, headers=["Name", "Version", "Publisher", "Installed"], tablefmt="simple")
    return f"Installed applications ({len(rows)} shown):\n{table}"
