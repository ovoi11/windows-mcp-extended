"""HardwareDeviceErrors tool — devices with configuration problems."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import device_errors


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="HardwareDeviceErrors",
        description='List hardware devices reporting configuration errors (missing driver, disabled, cannot start, etc). Keywords: device error, device manager problem, missing driver, 设备错误, 设备管理器. Read-only.',
        annotations=ToolAnnotations(
            title="HardwareDeviceErrors",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "HardwareDeviceErrors-Tool")
    def hardware_device_errors_tool(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        return device_errors(limit=limit)
