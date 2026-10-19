"""Browser extensions — installed browser extensions (security review)."""

from __future__ import annotations

import glob
import json
import os

__all__ = ["browser_extensions"]

_EXT_DIRS = {
    "Edge": [
        r"C:\Users\%s\AppData\Local\Microsoft\Edge\User Data\Default\Extensions",
        r"C:\Users\%s\AppData\Local\Microsoft\Edge\User Data\Profile*\Extensions",
    ],
    "Chrome": [
        r"C:\Users\%s\AppData\Local\Google\Chrome\User Data\Default\Extensions",
        r"C:\Users\%s\AppData\Local\Google\Chrome\User Data\Profile*\Extensions",
    ],
}
_MANIFESTS = ("manifest.json",)


def browser_extensions(limit: int = 20) -> str:
    """List installed Edge/Chrome extensions with names and versions."""
    from tabulate import tabulate

    user = os.environ.get("USERNAME", "")
    rows: list[list[str]] = []
    for browser, patterns in _EXT_DIRS.items():
        for pattern in patterns:
            for ext_root in glob.glob(pattern % user):
                if not os.path.isdir(ext_root):
                    continue
                for ext_id in os.listdir(ext_root):
                    base = os.path.join(ext_root, ext_id)
                    if not os.path.isdir(base):
                        continue
                    manifest = _read_manifest(base)
                    if manifest:
                        name = manifest.get("name", "").replace("__MSG_", "").replace("__", "")[:40]
                        rows.append([browser, name or ext_id[:20], manifest.get("version", "?")])

    if not rows:
        return "未找到浏览器扩展（或无扩展安装）。"
    rows.sort(key=lambda r: (r[0], r[1].lower()))
    rows = rows[: max(1, min(int(limit), 100))]
    table = tabulate(rows, headers=["Browser", "Extension", "Version"], tablefmt="simple")
    return f"浏览器扩展 ({len(rows)} shown):\n{table}"


def _read_manifest(ext_dir: str) -> dict | None:
    for version_dir in sorted(os.listdir(ext_dir), reverse=True):
        mf = os.path.join(ext_dir, version_dir, "manifest.json")
        if os.path.isfile(mf):
            try:
                with open(mf, "r", encoding="utf-8", errors="replace") as f:
                    return json.load(f)
            except (OSError, ValueError):
                return None
    return None
