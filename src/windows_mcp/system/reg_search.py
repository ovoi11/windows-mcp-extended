"""Registry search — find keys/values by keyword (bounded walk)."""

from __future__ import annotations

import winreg
from typing import Literal

__all__ = ["search_registry"]

_MAX_ENTRIES = 200
_MAX_DEPTH = 4

_ROOTS = {
    "hklm": winreg.HKEY_LOCAL_MACHINE,
    "hkcu": winreg.HKEY_CURRENT_USER,
}
_ROOT_PATHS = {
    "hklm": r"Software",
    "hkcu": r"Software",
}


def _walk(key, path: str, keyword: str, depth: int, matches: list[tuple[str, str, str]], limit: int) -> None:
    if len(matches) >= limit or depth > _MAX_DEPTH:
        return
    try:
        sub_names: list[str] = []
        i = 0
        while True:
            try:
                sub_names.append(winreg.EnumKey(key, i))
                i += 1
            except OSError:
                break
    except OSError:
        return

    for sub in sub_names:
        if len(matches) >= limit:
            return
        sub_path = f"{path}\\{sub}"
        if keyword.lower() in sub.lower():
            matches.append((sub_path, "key", ""))
        try:
            with winreg.OpenKey(key, sub) as sub_key:
                j = 0
                while True:
                    try:
                        vname, _vval, _vtype = winreg.EnumValue(sub_key, j)
                        j += 1
                    except OSError:
                        break
                    if keyword.lower() in str(vname).lower():
                        matches.append((sub_path, "value", str(vname)))
                if depth + 1 <= _MAX_DEPTH:
                    _walk(sub_key, sub_path, keyword, depth + 1, matches, limit)
        except OSError:
            continue


def search_registry(keyword: str, root: Literal["hklm", "hkcu"] = "hkcu", limit: int = 30) -> str:
    """Search a registry root for keys/values whose name contains *keyword*."""
    from tabulate import tabulate

    if not keyword:
        return "Error: keyword is required."
    limit = max(1, min(int(limit), _MAX_ENTRIES))
    hive = _ROOTS[root]
    base = _ROOT_PATHS[root]

    matches: list[tuple[str, str, str]] = []
    try:
        with winreg.OpenKey(hive, base) as key:
            _walk(key, base, keyword, 0, matches, limit)
    except OSError as e:
        return f"Error searching registry: {e}."

    if not matches:
        return f"在 {root}\\{base} 下未找到包含 {keyword!r} 的键或值。"
    rows = [[path, kind, detail] for path, kind, detail in matches[:limit]]
    table = tabulate(rows, headers=["Path", "Type", "Name"], tablefmt="simple")
    return f"注册表搜索 {keyword!r}（{root}，{len(rows)} shown）:\n{table}"
