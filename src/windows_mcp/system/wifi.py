"""Wi-Fi state — current connection and nearby networks (netsh wlan)."""

from __future__ import annotations

import subprocess

__all__ = ["wifi_status", "wifi_networks"]

_CREATE_NO_WINDOW = 0x08000000


def _run(args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["netsh.exe", "wlan", *args],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=60,
        )
    except FileNotFoundError:
        return -1, "netsh.exe not found on this system."
    except subprocess.TimeoutExpired:
        return -1, "netsh.exe timed out."
    out = (proc.stdout or b"").decode("utf-8", errors="replace")
    err = (proc.stderr or b"").decode("utf-8", errors="replace")
    return proc.returncode, (out + err).strip()


def _parse_kv(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            if key and value:
                rows.append([key, value])
    return rows


def wifi_status() -> str:
    """Report the current Wi-Fi adapter state and active connection."""
    from tabulate import tabulate

    code, text = _run(["show", "interfaces"])
    if code != 0:
        if "error" in text.lower() or "无线" in text:
            return f"Error: {text.splitlines()[0] if text else 'netsh returned an error.'}"
        return f"Wi-Fi 状态:\n{text}"
    rows = _parse_kv(text)
    if not rows:
        return "当前没有 Wi-Fi 接口信息。"
    table = tabulate(rows, headers=["字段", "值"], tablefmt="simple")
    return f"Wi-Fi 状态:\n{table}"


def wifi_networks(limit: int = 20) -> str:
    """List nearby Wi-Fi networks with auth/encryption (mode=bssid for signal)."""
    from tabulate import tabulate

    code, text = _run(["show", "networks", "mode=bssid"])
    if code != 0:
        return f"Error: {text.splitlines()[0] if text else 'netsh returned an error.'}"

    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("ssid"):
            if current:
                entries.append(current)
            _, _, name = stripped.partition(":")
            current = {"SSID": name.strip()}
        elif ":" in stripped and current is not None:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value and key not in ("", "SSID"):
                current[key] = value
    if current:
        entries.append(current)

    if not entries:
        return "附近没有发现 Wi-Fi 网络。"
    rows = []
    for e in entries[:limit]:
        rows.append(
            [
                e.get("SSID", "?"),
                e.get("身份验证", e.get("Authentication", "-")),
                e.get("加密", e.get("Encryption", "-")),
                e.get("信号", e.get("Signal", "-")),
            ]
        )
    table = tabulate(rows, headers=["SSID", "Auth", "Encryption", "Signal"], tablefmt="simple")
    return f"附近 Wi-Fi 网络 ({len(rows)} shown):\n{table}"
