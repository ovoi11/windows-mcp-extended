"""BluetoothDevices tool — Bluetooth hardware list."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import bluetooth_devices


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="BluetoothDevices",
        description='List Bluetooth devices (paired radios and peripherals) with status. Keywords: bluetooth devices, paired bluetooth, 蓝牙设备. Read-only.',
        annotations=ToolAnnotations(
            title="BluetoothDevices",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "BluetoothDevices-Tool")
    def bluetooth_devices_tool(
        limit: int = 15,
        ctx: Context = None,
    ) -> str:
        return bluetooth_devices(limit=limit)
