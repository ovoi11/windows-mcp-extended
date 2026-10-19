"""Firewall rules — query Windows Firewall rules (netsh, read-only)."""

from __future__ import annotations

import subprocess

__all__ = ["firewall_rules"]

_CREATE_NO_WINDOW = 0x08000000

_ACTIONS = ("allow", "block")


def firewall_rules(
    name: str | None = None,
    direction: str | None = None,
    action: str | None = None,
    limit: int = 30,
) -> str:
    """Query firewall rules, optionally filtered by name/direction/action."""
    from tabulate import tabulate

    if action and action.lower() not in _ACTIONS:
        return "Error: action must be 'allow' or 'block'."
    try:
        proc = subprocess.run(
            ["netsh.exe", "advfirewall", "firewall", "show", "rule", "name=all"],
            capture_output=True,
            creationflags=_CREATE_NO_WINDOW,
            timeout=120,
        )
    except FileNotFoundError:
        return "Error: netsh.exe not found on this system."
    except subprocess.TimeoutExpired:
        return "Error: firewall rule query timed out."

    text = (proc.stdout or b"").decode("utf-8", errors="replace")
    if proc.returncode != 0:
        return f"Error: {text.splitlines()[0] if text else 'netsh returned an error.'}"

    rows: list[list[str]] = []
    current: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            if current:
                _flush(current, rows, name, direction, action)
                current = {}
            continue
        key, _, value = stripped.partition(":")
        key = key.strip()
        value = value.strip()
        if "规则名称" in key or "Rule Name" in key:
            if current:
                _flush(current, rows, name, direction, action)
            current = {"name": value}
        elif current is not None:
            current[key] = value
    if current:
        _flush(current, rows, name, direction, action)

    if not rows:
        return "未找到匹配的防火墙规则。"
    rows = rows[:limit]
    table = tabulate(rows, headers=["Name", "Dir", "Action", "Program"], tablefmt="simple")
    return f"防火墙规则 ({len(rows)} shown):\n{table}"


def _flush(rule: dict[str, str], rows: list[list[str]], name: str | None, direction: str | None, action: str | None) -> None:
    rule_name = rule.get("name", "")
    if name and name.lower() not in rule_name.lower():
        return
    rule_dir = _pick(rule, "方向", "Direction", "Dir")
    rule_action = _pick(rule, "操作", "Action", "允许", "Block")
    if direction and direction.lower() not in rule_dir.lower():
        return
    if action and action.lower() not in rule_action.lower():
        return
    prog = _pick(rule, "程序", "Program", "-")
    rows.append([rule_name, rule_dir or "-", rule_action or "-", prog or "-"])


def _pick(rule: dict[str, str], *keys: str) -> str:
    for k in keys:
        if k in rule and rule[k]:
            return rule[k]
    return ""
