"""ElevationControl tool — UAC status, elevation requests and privilege verification."""

from typing import Literal

from mcp.types import ToolAnnotations

from windows_mcp.infrastructure import with_analytics
from windows_mcp.system import (
    check_elevation_status,
    elevate_process,
    verify_process_elevation,
)
from fastmcp import Context


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ElevationControl",
        description='Manage and verify Windows UAC / administrator privilege state. Keywords: UAC, elevation, run as administrator, admin rights, integrity level, elevated process. mode="status" reports whether UAC is enabled and whether the current process is elevated. mode="elevate" relaunches a program with the runas verb so the user can grant admin rights (the UAC consent prompt is always confirmed by the user; this tool never auto-confirms it). mode="verify" checks elevation/integrity of a process by pid or name.',
        annotations=ToolAnnotations(
            title="ElevationControl",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=True,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ElevationControl-Tool")
    def elevation_control_tool(
        mode: Literal["status", "elevate", "verify"] = "status",
        path: str | None = None,
        args: str = "",
        pid: int | None = None,
        name: str | None = None,
        ctx: Context = None,
    ) -> str:
        if mode == "status":
            return check_elevation_status()
        elif mode == "elevate":
            if not path:
                return "Error: elevate 模式需要提供 path 参数（要提权启动的程序）。"
            return elevate_process(path, args=args)
        elif mode == "verify":
            return verify_process_elevation(pid=pid, name=name)
        return 'Error: mode 必须是 "status"、"elevate" 或 "verify"。'
