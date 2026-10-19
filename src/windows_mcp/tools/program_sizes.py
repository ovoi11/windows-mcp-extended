"""InstalledProgramsBySize tool — largest installed programs."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import programs_by_size


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="InstalledProgramsBySize",
        description='List installed programs with their estimated install size, largest first. Keywords: largest programs, program size, uninstall size, 程序大小, 占用空间. Read-only.',
        annotations=ToolAnnotations(
            title="InstalledProgramsBySize",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "InstalledProgramsBySize-Tool")
    def installed_programs_by_size_tool(
        limit: int = 20,
        ctx: Context = None,
    ) -> str:
        return programs_by_size(limit=limit)
