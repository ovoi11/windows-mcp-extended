"""Certificate store — enumerate personal/root certificates (Cert:\\CurrentUser)."""

from __future__ import annotations

import csv
import io
import subprocess
from typing import Literal

__all__ = ["list_certificates"]

_CREATE_NO_WINDOW = 0x08000000

_STORES = {"my": "My", "root": "Root", "ca": "CA"}


def _decode(raw: bytes) -> str:
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return raw.decode("utf-16", errors="replace")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def list_certificates(
    store: Literal["my", "root", "ca"] = "my",
    limit: int = 30,
) -> str:
    """List certificates in the current user's store (my/root/ca)."""
    from tabulate import tabulate

    store_name = _STORES.get(store, "My")
    script = (
        f"Get-ChildItem Cert:\\CurrentUser\\{store_name} | "
        "Select-Object Subject,Issuer,Thumbprint,NotBefore,NotAfter | "
        "ConvertTo-Csv -NoTypeInformation"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=90,
        )
    except FileNotFoundError:
        return "Error: powershell.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: certificate query timed out."

    text = _decode(proc.stdout or b"")
    rows: list[list[str]] = []
    for rec in csv.DictReader(io.StringIO(text)):
        subject = (rec.get("Subject") or "").strip()
        thumb = (rec.get("Thumbprint") or "").strip()
        if not subject and not thumb:
            continue
        not_after = (rec.get("NotAfter") or "").strip()[:10]
        rows.append(
            [
                subject or "?",
                (rec.get("Issuer") or "").strip()[:50] or "-",
                not_after or "-",
                thumb[:16] or "-",
            ]
        )

    if not rows:
        return f"证书存储 {store_name!r} 中没有证书。"
    rows = rows[:limit]
    table = tabulate(rows, headers=["Subject", "Issuer", "Expires", "Thumbprint"], tablefmt="simple")
    return f"证书（CurrentUser\\{store_name}，{len(rows)} shown）:\n{table}"
