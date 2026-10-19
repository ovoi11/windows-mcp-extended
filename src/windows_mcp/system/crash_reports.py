"""Crash reports — recent WER (Windows Error Reporting) entries."""

from __future__ import annotations

import glob
import os
import time

__all__ = ["crash_report_list"]

_WER_DIRS = [
    r"C:\ProgramData\Microsoft\Windows\WER\ReportArchive",
    r"C:\ProgramData\Microsoft\Windows\WER\ReportQueue",
]
_KNOWN_APP = ("Report.wer",)


def crash_report_list(limit: int = 15) -> str:
    """List recent Windows Error Reporting entries (crash/error reports)."""
    from tabulate import tabulate

    reports: list[tuple[float, str, str, str]] = []
    for base in _WER_DIRS:
        if not os.path.isdir(base):
            continue
        for folder in glob.glob(os.path.join(base, "AppCrash_*")) + glob.glob(
            os.path.join(base, "AppHang_*")
        ) + glob.glob(os.path.join(base, "*")):
            if not os.path.isdir(folder):
                continue
            wer_file = os.path.join(folder, "Report.wer")
            if not os.path.isfile(wer_file):
                continue
            try:
                mtime = os.path.getmtime(wer_file)
            except OSError:
                continue
            reports.append((mtime, folder, _extract(folder), _age(mtime)))

    if not reports:
        return "未找到 WER 崩溃报告。"
    reports.sort(key=lambda r: r[0], reverse=True)
    rows = []
    for _mtime, folder, summary, age in reports[: max(1, min(int(limit), 50))]:
        rows.append([age, summary[:60] or os.path.basename(folder), folder[:110]])
    table = tabulate(rows, headers=["Age", "App", "Report"], tablefmt="simple")
    return f"崩溃报告 ({len(rows)} shown):\n{table}"


def _extract(folder: str) -> str:
    wer_file = os.path.join(folder, "Report.wer")
    try:
        with open(wer_file, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("EventType") or line.startswith("Sig[0].Value"):
                    return line.strip().split("=")[-1]
    except OSError:
        pass
    return os.path.basename(folder)


def _age(mtime: float) -> str:
    days = int((time.time() - mtime) // 86400)
    if days < 1:
        return "今天"
    if days < 30:
        return f"{days} 天前"
    return f"{days // 30} 个月前"
