"""UserAccounts tool — list local user accounts."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_accounts


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="UserAccounts",
        description='List local Windows user accounts with full name, enabled/disabled state, SID and a marker for the current user. Keywords: user accounts, local users, who is on this pc. Read-only.',
        annotations=ToolAnnotations(
            title="UserAccounts",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "UserAccounts-Tool")
    def user_accounts_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_accounts(limit=limit)
