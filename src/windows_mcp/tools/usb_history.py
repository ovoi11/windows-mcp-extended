"""USBDeviceHistory tool — previously connected USB storage devices."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import usb_device_history


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="USBDeviceHistory",
        description='List USB mass-storage devices that have been connected to this machine (from USBSTOR registry), with friendly name and connection sessions. Keywords: usb history, usb devices, forensic, 优盘历史, usb 设备. Read-only.',
        annotations=ToolAnnotations(
            title="USBDeviceHistory",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "USBDeviceHistory-Tool")
    def usb_device_history_tool(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        return usb_device_history(limit=limit)
