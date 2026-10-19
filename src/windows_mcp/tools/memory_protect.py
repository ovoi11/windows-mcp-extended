"""MemoryProtectCheck tool — read a process's mitigation policies (ASLR/DEP/CFG)."""

from mcp.types import ToolAnnotations

from windows_mcp.infrastructure import with_analytics
from windows_mcp.security import get_mitigation_status
from fastmcp import Context


def _resolve_pid(name: str | None, pid: int | None) -> int:
    if pid is not None:
        return pid
    if not name:
        raise ValueError("必须提供 pid 或 name 参数之一")
    import psutil

    for p in psutil.process_iter(["pid", "name"]):
        try:
            if p.info["name"] and p.info["name"].lower() == name.lower():
                return p.info["pid"]
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    raise ValueError(f'未找到名为 "{name}" 的进程')


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="MemoryProtectCheck",
        description='Check the security mitigation policies of a running process: ASLR (bottom-up randomization / force relocate images / high entropy), DEP, Control Flow Guard (CFG), and dynamic-code restrictions. Keywords: ASLR, DEP, CFG, mitigation, exploit protection, hardened process, memory protection. Provide either pid or name. Some policies may require administrator privileges to read.',
        annotations=ToolAnnotations(
            title="MemoryProtectCheck",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "MemoryProtectCheck-Tool")
    def memory_protect_check_tool(
        pid: int | None = None,
        name: str | None = None,
        ctx: Context = None,
    ) -> str:
        try:
            target_pid = _resolve_pid(name, pid)
        except ValueError as e:
            return f"Error: {e}"
        return get_mitigation_status(target_pid)
