"""InstalledFonts tool — enumerate system fonts."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import installed_fonts


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="InstalledFonts",
        description='List installed font families and their files. Keywords: fonts, installed fonts, font list, 字体, 已装字体. Read-only.',
        annotations=ToolAnnotations(
            title="InstalledFonts",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "InstalledFonts-Tool")
    def installed_fonts_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return installed_fonts(limit=limit)
