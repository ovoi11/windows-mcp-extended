"""UsbDeviceList tool — enumerate present plug-and-play devices."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_devices


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="UsbDeviceList",
        description='List present plug-and-play devices. Keywords: usb devices, device manager, pnp devices, connected hardware, bluetooth devices, printers, disk drives. Supports optional class filter: all, usb, display, network, storage, bluetooth, printer, audio, keyboard, mouse. Read-only.',
        annotations=ToolAnnotations(
            title="UsbDeviceList",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "UsbDeviceList-Tool")
    def usb_device_list_tool(
        class_name: Literal["all", "usb", "display", "network", "storage", "bluetooth", "printer", "audio", "keyboard", "mouse"] = "all",
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_devices(class_name=class_name, limit=limit)
