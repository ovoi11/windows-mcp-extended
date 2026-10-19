"""WindowsLicenseInfo tool — activation/license status."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import windows_license_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="WindowsLicenseInfo",
        description='Report Windows edition, build, license state and the tail of the product key. Keywords: windows license, activation status, product key, windows 激活, 授权状态. Read-only; never changes licensing.',
        annotations=ToolAnnotations(
            title="WindowsLicenseInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "WindowsLicenseInfo-Tool")
    def windows_license_info_tool(ctx: Context = None) -> str:
        return windows_license_info()
