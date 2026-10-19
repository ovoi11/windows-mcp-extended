"""ProcessCommandLine tool — full command lines of running processes."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_process_command_lines


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ProcessCommandLine",
        description='List running processes with their full command lines and executable paths. Keywords: process command line, what is this process, suspicious process, malware check, cmdline. Supports optional process-name filter. Read-only; useful for diagnosing unknown or suspicious processes.',
        annotations=ToolAnnotations(
            title="ProcessCommandLine",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ProcessCommandLine-Tool")
    def process_command_line_tool(
        name: str | None = None,
        limit: int = 50,
        ctx: Context = None,
    ) -> str:
        return list_process_command_lines(name=name, limit=limit)
