"""HardwareInventory tool — memory, GPU and BIOS details."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import hardware_inventory


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="HardwareInventory",
        description='Report hardware details: memory modules (capacity/speed/manufacturer), graphics adapters (name/driver) and BIOS (manufacturer/version/release date). Keywords: hardware inventory, ram sticks, gpu info, graphics card, bios version, 硬件, 内存条, 显卡. Read-only.',
        annotations=ToolAnnotations(
            title="HardwareInventory",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "HardwareInventory-Tool")
    def hardware_inventory_tool(ctx: Context = None) -> str:
        return hardware_inventory()
