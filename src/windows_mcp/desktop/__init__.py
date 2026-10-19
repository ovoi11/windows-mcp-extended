"""Desktop state queries (read-only)."""

from windows_mcp.desktop.active_window import active_window_info
from windows_mcp.desktop.mouse_pos import mouse_position
from windows_mcp.desktop.window_list import window_list

__all__ = ["active_window_info", "mouse_position", "window_list"]
