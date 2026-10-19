"""Process tree — parent/child relationships of running processes."""

from __future__ import annotations

__all__ = ["process_tree"]


def process_tree(limit: int = 30) -> str:
    """Render a process tree (parent -> children) as an indented list."""
    import psutil
    from tabulate import tabulate

    children: dict[int, list[tuple[int, str]]] = {}
    names: dict[int, str] = {}

    for proc in psutil.process_iter(["pid", "ppid", "name"]):
        try:
            pid = proc.info["pid"]
            ppid = proc.info["ppid"]
            name = proc.info["name"] or "?"
            names[pid] = name
            children.setdefault(ppid, []).append((pid, name))
        except (psutil.NoSuchProcess, psutil.AccessDenied, OSError):
            continue

    rows: list[list[str]] = []
    visited: set[int] = set()

    def walk(pid: int, depth: int) -> None:
        if pid in visited or len(rows) >= limit:
            return
        visited.add(pid)
        rows.append([str(pid), "  " * depth + (names.get(pid) or "?")])
        for child_pid, _ in sorted(children.get(pid, [])):
            walk(child_pid, depth + 1)

    # Roots: processes without a visible parent, or parent not alive.
    all_pids = set(names)
    roots = [p for p in all_pids if names.get(p) and children.get(p)]
    if not roots:
        roots = sorted(all_pids)[:5]
    for root in roots[:5]:
        walk(root, 0)

    if not rows:
        return "无法构建进程树。"
    table = tabulate(rows, headers=["PID", "Process"], tablefmt="simple")
    return f"进程树 (top {len(rows)} nodes):\n{table}"
