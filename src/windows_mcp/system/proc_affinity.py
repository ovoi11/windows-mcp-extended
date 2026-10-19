"""Process affinity — CPU affinity of a process (read-only)."""

from __future__ import annotations

__all__ = ["process_affinity"]


def process_affinity(pid: int) -> str:
    """Report the CPU affinity mask of a process."""
    import psutil
    from tabulate import tabulate

    try:
        proc = psutil.Process(pid)
        affinity = proc.cpu_affinity()
        num_cpus = psutil.cpu_count()
    except psutil.NoSuchProcess:
        return f"No process with PID {pid} found."
    except (psutil.AccessDenied, OSError) as e:
        return f"Error reading affinity: {e}."

    if affinity is None:
        return f"CPU 亲和性不支持（PID {pid}）。"
    rows = [
        ["PID", str(pid)],
        ["进程", proc.name()],
        ["允许的 CPU 数", str(len(affinity))],
        ["总 CPU 数", str(num_cpus or "?")],
        ["CPU 列表", ", ".join(str(c) for c in sorted(affinity))],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"进程 CPU 亲和性 (PID {pid}):\n{table}"
