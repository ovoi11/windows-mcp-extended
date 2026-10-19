"""SessionProcesses tool — processes per logon session."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import session_processes


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="SessionProcesses",
        description='Count running processes per Windows logon session (session ID). Keywords: session processes, logon session, session id, 会话进程. Read-only.',
        annotations=ToolAnnotations(
            title="SessionProcesses",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "SessionProcesses-Tool")
    def session_processes_tool(
        limit: int = 15,
        ctx: Context = None,
    ) -> str:
        return session_processes(limit=limit)
