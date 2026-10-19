"""File/folder watcher — baseline snapshots and change diffs over a duration."""

from __future__ import annotations

import os
import time

__all__ = ["watch_path", "clear_file_baseline"]

_baseline: dict[str, tuple[int, int]] = {}  # abs path -> (mtime_ns, size)
_baseline_root: str | None = None

_MAX_FILES = 50_000


def _scan(root: str, recursive: bool) -> dict[str, tuple[int, int]]:
    """Scan a folder and return {abs_path: (mtime_ns, size)}."""
    snap: dict[str, tuple[int, int]] = {}
    if os.path.isfile(root):
        st = os.stat(root)
        return {os.path.abspath(root): (st.st_mtime_ns, st.st_size)}
    if not os.path.isdir(root):
        return snap
    walker = os.walk(root) if recursive else [(root, [], os.listdir(root))]
    for dirpath, _dirnames, filenames in walker:
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            try:
                st = os.stat(full)
            except OSError:
                continue
            snap[os.path.abspath(full)] = (st.st_mtime_ns, st.st_size)
            if len(snap) >= _MAX_FILES:
                return snap
    return snap


def _diff(base: dict[str, tuple[int, int]], current: dict[str, tuple[int, int]]) -> tuple[list[str], list[str], list[str]]:
    added = sorted(set(current) - set(base))
    removed = sorted(set(base) - set(current))
    modified = sorted(
        p for p in set(base) & set(current) if base[p] != current[p]
    )
    return added, modified, removed


def clear_file_baseline() -> str:
    """Clear the stored file-watch baseline."""
    global _baseline, _baseline_root
    _baseline = {}
    _baseline_root = None
    return "文件监控基线已清除。"


def watch_path(path: str, duration: float = 10.0, recursive: bool = True) -> str:
    """Watch a path for changes over a duration and report added/modified/removed files.

    The first call stores a baseline and reports it; the second call diffs
    against the stored baseline, then updates it — mirroring ProcessMonitor.
    """
    global _baseline, _baseline_root
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return f"Error: path not found: {path}"
    if duration < 1:
        return "Error: duration must be >= 1 second."

    first = _scan(path, recursive)
    if _baseline_root != path:
        _baseline = {}
        _baseline_root = path
    base = _baseline
    _baseline = first  # update baseline immediately so concurrent calls are safe

    if not base:
        return f"文件监控基线已建立（{len(first)} 个文件）: {path}"

    time.sleep(duration)
    current = _scan(path, recursive)
    added, modified, removed = _diff(base, current)
    _baseline = current

    lines = [f"文件变化（{path}，{duration:g}s 窗口，基线 {len(base)} → 当前 {len(current)}）:"]
    if not (added or modified or removed):
        lines.append("无变化。")
        return "\n".join(lines)
    if added:
        lines.append(f"新增 ({len(added)}):")
        lines.extend(f"  + {p}" for p in added[:50])
    if modified:
        lines.append(f"修改 ({len(modified)}):")
        lines.extend(f"  ~ {p}" for p in modified[:50])
    if removed:
        lines.append(f"删除 ({len(removed)}):")
        lines.extend(f"  - {p}" for p in removed[:50])
    if len(added) + len(modified) + len(removed) > 150:
        lines.append("（其余省略，max_files=50000）")
    return "\n".join(lines)
