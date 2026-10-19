"""PrinterList tool — enumerate installed printers."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_printers


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="PrinterList",
        description='List installed printers with driver, port and shared state. Keywords: printers, print queue devices, installed printers. Read-only.',
        annotations=ToolAnnotations(
            title="PrinterList",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "PrinterList-Tool")
    def printer_list_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_printers(limit=limit)
