"""HostsFile tool — read the Windows hosts file (read-only)."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import read_hosts


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="HostsFile",
        description='Read the Windows hosts file (C:\\Windows\\System32\\drivers\\etc\\hosts). Keywords: hosts file, hosts entries, dns override, ip hostname mapping. Returns non-comment IP -> hostname entries. Read-only; entry modification is intentionally not exposed.',
        annotations=ToolAnnotations(
            title="HostsFile",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "HostsFile-Tool")
    def hosts_file_tool(ctx: Context = None) -> str:
        return read_hosts()
