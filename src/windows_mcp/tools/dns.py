"""DnsLookup tool — resolve a hostname via the system resolver."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import dns_lookup


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="DnsLookup",
        description='Resolve a hostname to IP addresses using the system DNS resolver. Keywords: dns, resolve, hostname, nslookup, domain to ip, 域名解析. family="ipv4" (default), "ipv6" or "all". Read-only; performs a DNS query.',
        annotations=ToolAnnotations(
            title="DnsLookup",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "DnsLookup-Tool")
    def dns_lookup_tool(
        host: str,
        family: Literal["ipv4", "ipv6", "all"] = "ipv4",
        ctx: Context = None,
    ) -> str:
        return dns_lookup(host=host, family=family)
