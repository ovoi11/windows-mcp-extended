"""DNS lookup — resolve a hostname to addresses (system resolver)."""

from __future__ import annotations

import socket

__all__ = ["dns_lookup"]


def dns_lookup(host: str, family: str = "ipv4") -> str:
    """Resolve a hostname using the system DNS resolver."""
    from tabulate import tabulate

    if not host:
        return "Error: host is required."
    family_map = {"ipv4": socket.AF_INET, "ipv6": socket.AF_INET6, "all": socket.AF_UNSPEC}
    af = family_map.get(family, socket.AF_INET)

    try:
        results = socket.getaddrinfo(host, None, af)
    except socket.gaierror as e:
        return f"解析失败 {host!r}: {e}."

    rows: list[list[str]] = []
    seen: set[str] = set()
    for res in results:
        addr = res[4][0]
        if addr in seen:
            continue
        seen.add(addr)
        kind = "IPv6" if res[0] == socket.AF_INET6 else "IPv4"
        rows.append([kind, addr])

    if not rows:
        return f"未解析到 {host!r} 的地址。"
    table = tabulate(rows, headers=["Family", "Address"], tablefmt="simple")
    return f"DNS 解析 {host} ({len(rows)}):\n{table}"
