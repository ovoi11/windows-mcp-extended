"""Sleep prevention service — keep the system awake via SetThreadExecutionState.

The ES_CONTINUOUS flag persists until cleared by another call or the process
exits, so an explicit disable call is provided and the state auto-clears when
the MCP server stops. There is no query API for this state, so the current
status is tracked module-scoped for reporting.
"""

from __future__ import annotations

import ctypes

__all__ = [
    "enable_sleep_prevention",
    "disable_sleep_prevention",
    "get_sleep_prevention_status",
]

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_set_state = _kernel32.SetThreadExecutionState
_set_state.restype = ctypes.c_uint
_set_state.argtypes = [ctypes.c_uint]

_active = False
_keep_display = False


def enable_sleep_prevention(*, keep_display: bool = False) -> str:
    """Prevent the system from sleeping (optionally also keep the display on)."""
    global _active, _keep_display
    flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
    if keep_display:
        flags |= ES_DISPLAY_REQUIRED
    _set_state(flags)
    _active = True
    _keep_display = keep_display
    detail = "（同时保持显示器常亮）" if keep_display else ""
    return f"已阻止系统进入睡眠{detail}。此设置在 MCP 服务器退出后自动解除。"


def disable_sleep_prevention() -> str:
    """Clear the sleep-prevention state."""
    global _active, _keep_display
    _set_state(ES_CONTINUOUS)
    _active = False
    _keep_display = False
    return "已解除休眠阻止，系统恢复正常电源策略。"


def get_sleep_prevention_status() -> str:
    """Report whether sleep prevention is currently active."""
    if _active:
        detail = "（含显示器常亮）" if _keep_display else ""
        return f"休眠阻止: 已启用{detail}（MCP 服务器运行期间持续生效）"
    return "休眠阻止: 未启用"
