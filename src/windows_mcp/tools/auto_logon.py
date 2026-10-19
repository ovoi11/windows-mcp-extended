"""AutoLogonCheck tool — auto-logon security check."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import auto_logon_check


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="AutoLogonCheck",
        description='Check whether automatic logon is configured and whether a plaintext password is stored. Keywords: autologon, auto login, automatic logon, 自动登录. Read-only; flags a security risk but does not modify anything.',
        annotations=ToolAnnotations(
            title="AutoLogonCheck",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "AutoLogonCheck-Tool")
    def auto_logon_check_tool(ctx: Context = None) -> str:
        return auto_logon_check()
