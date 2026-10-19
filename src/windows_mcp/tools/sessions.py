"""SessionInfo tool — interactive logon sessions."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import session_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="SessionInfo",
        description='List interactive logon sessions (quser). Keywords: who is logged in, logon session, logged in users, 登录会话. Returns username, session name, state and logon time. Read-only.',
        annotations=ToolAnnotations(
            title="SessionInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "SessionInfo-Tool")
    def session_info_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return session_info(limit=limit)
