"""CertificateInfo tool — enumerate certificates in the current user's stores."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_certificates


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="CertificateInfo",
        description='List certificates in the current user\'s stores. Keywords: certificate, cert store, code signing, thumbprint, SSL cert, 证书. store="my" (personal), "root" (trusted roots) or "ca" (intermediate). Returns subject, issuer, expiry date and thumbprint prefix. Read-only.',
        annotations=ToolAnnotations(
            title="CertificateInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "CertificateInfo-Tool")
    def certificate_info_tool(
        store: Literal["my", "root", "ca"] = "my",
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_certificates(store=store, limit=limit)
