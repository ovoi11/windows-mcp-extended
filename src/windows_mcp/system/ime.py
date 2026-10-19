"""IME / keyboard layout status — read-only query of the active input method."""

from __future__ import annotations

__all__ = ["ime_status"]


def ime_status() -> str:
    """Report the active keyboard layout / input language for this session."""
    import ctypes

    from tabulate import tabulate

    try:
        user32 = ctypes.windll.user32
        # KLF_* not needed; GetKeyboardLayout(0) returns the layout for this thread.
        layout = user32.GetKeyboardLayout(0)  # HKL
        lang_id = layout & 0xFFFF

        # GetKeyboardLayoutNameW returns the KLID string (e.g. "00000804").
        buf = ctypes.create_unicode_buffer(16)
        user32.GetKeyboardLayoutNameW(buf)
        klid = buf.value

        # Locale language display name. The HKL low word IS the language id
        # (LCID), so no MAKELANGID macro is needed.
        name_buf = ctypes.create_unicode_buffer(128)
        locale = lang_id
        if not ctypes.windll.kernel32.GetLocaleInfoW(
            locale, 0x2, name_buf, len(name_buf)  # LOCALE_SENGLANGUAGE
        ):
            lang_name = f"0x{lang_id:04X}"
        else:
            lang_name = name_buf.value
    except (AttributeError, OSError) as e:
        return f"Error querying IME status: {e}."

    rows = [
        ["键盘布局", klid or hex(layout)],
        ["语言", lang_name],
        ["语言 ID", f"0x{lang_id:04X}"],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"输入法 / 键盘布局状态:\n{table}"
