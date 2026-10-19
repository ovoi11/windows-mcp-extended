"""WindowsDefenderStatus tool — Defender protection state."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import defender_status


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="WindowsDefenderStatus",
        description='Report Windows Defender status: antivirus enabled, real-time protection, signature version/update and last scan ages. Keywords: defender, antivirus, real time protection, windows security, 微软杀毒, 实时保护. Read-only.',
        annotations=ToolAnnotations(
            title="WindowsDefenderStatus",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "WindowsDefenderStatus-Tool")
    def windows_defender_status_tool(ctx: Context = None) -> str:
        return defender_status()
