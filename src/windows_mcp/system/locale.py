"""System locale information — culture, UI language and regional settings."""

from __future__ import annotations

import subprocess

__all__ = ["locale_info"]

_CREATE_NO_WINDOW = 0x08000000

_SCRIPT = (
    "Get-Culture | Select-Object DisplayName,Name,LCID | ConvertTo-Csv -NoTypeInformation;"
    "Get-WinSystemLocale | Select-Object DisplayName,Name,LCID | ConvertTo-Csv -NoTypeInformation;"
    "Get-WinUserLanguageList | Select-Object LanguageTag,Autonym | ConvertTo-Csv -NoTypeInformation"
)


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def locale_info() -> str:
    """Report system locale, culture and user language list."""
    import csv
    import io

    from tabulate import tabulate

    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _SCRIPT],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=90,
        )
    except FileNotFoundError:
        return "Error: powershell.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: locale query timed out."

    text = _decode(proc.stdout or b"")
    cultures: list[dict[str, str]] = []
    user_langs: list[dict[str, str]] = []
    # ConvertTo-Csv blocks: first block is Get-Culture, second Get-WinSystemLocale,
    # third Get-WinUserLanguageList. Re-parse by re-running each object type is
    # simpler: read all CSV rows and bucket them by available keys.
    for rec in csv.DictReader(io.StringIO(text)):
        if "LanguageTag" in rec:
            user_langs.append({k: (v or "").strip() for k, v in rec.items()})
        elif "DisplayName" in rec:
            cultures.append({k: (v or "").strip() for k, v in rec.items()})

    rows: list[list[str]] = []
    for idx, c in enumerate(cultures):
        label = "系统区域" if idx == 1 else "当前区域"
        rows.append([label, c.get("DisplayName") or c.get("Name") or "?", c.get("LCID") or "-"])
    if user_langs:
        rows.append(
            [
                "用户语言",
                ", ".join((l.get("Autonym") or l.get("LanguageTag") or "?") for l in user_langs),
                "-",
            ]
        )

    if not rows:
        return "未获取到区域信息。"
    table = tabulate(rows, headers=["项目", "值", "LCID"], tablefmt="simple")
    return f"区域设置:\n{table}"
