"""DomainMembership tool — workgroup vs domain-joined."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import domain_membership


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DomainMembership",
        description='Report whether this machine is domain-joined or in a workgroup, with computer name, domain and hardware vendor. Keywords: domain, workgroup, domain joined, ad domain, 域成员, 工作组. Read-only.',
        annotations=ToolAnnotations(
            title="DomainMembership",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DomainMembership-Tool")
    def domain_membership_tool(ctx: Context = None) -> str:
        return domain_membership()
