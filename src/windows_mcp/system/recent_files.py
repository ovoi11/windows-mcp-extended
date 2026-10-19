"""Recent files — recently opened documents (forensic/read-only)."""

from __future__ import annotations

import winreg

__all__ = ["recent_files"]

_RECENT_KEY = r"Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs"


def recent_files(limit: int = 20) -> str:
    """List recently opened documents (decoded from RecentDocs registry)."""
    from tabulate import tabulate

    entries: list[tuple[str, str, int]] = []  # (extension, filename, order)
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RECENT_KEY) as key:
            j = 0
            while True:
                try:
                    ext = winreg.EnumKey(key, j)
                    j += 1
                except OSError:
                    break
                try:
                    with winreg.OpenKey(key, ext) as sub:
                        k = 0
                        while True:
                            try:
                                _name, value, _type = winreg.EnumValue(sub, k)
                                k += 1
                            except OSError:
                                break
                            fname = _decode_name(value)
                            if fname:
                                entries.append((ext, fname, k))
                except OSError:
                    continue
    except OSError as e:
        return f"Error reading recent files: {e}."

    if not entries:
        return "未找到最近打开的文档记录。"
    entries.sort(key=lambda r: r[2])
    entries = entries[: max(1, min(int(limit), 50))]
    rows = [[ext, fname] for ext, fname, _order in entries]
    table = tabulate(rows, headers=["Ext", "File"], tablefmt="simple")
    return f"最近文档 ({len(rows)} shown):\n{table}"


def _decode_name(value) -> str:
    try:
        if isinstance(value, bytes):
            return value.decode("utf-16-le", errors="ignore").split("\x00")[0]
        return str(value)
    except Exception:
        return ""
