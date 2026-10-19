"""USB device history — storage devices that were connected (forensics)."""

from __future__ import annotations

import winreg

__all__ = ["usb_device_history"]

_USBSTOR = r"SYSTEM\CurrentControlSet\Enum\USBSTOR"


def usb_device_history(limit: int = 20) -> str:
    """List USB mass-storage devices that have been connected."""
    from tabulate import tabulate

    rows: list[list[str]] = []
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, _USBSTOR) as key:
            i = 0
            while True:
                try:
                    dev_id = winreg.EnumKey(key, i)
                    i += 1
                except OSError:
                    break
                try:
                    with winreg.OpenKey(key, dev_id) as dev_key:
                        # A specific-instance subkey exists only when the device was used.
                        j = 0
                        while True:
                            try:
                                inst = winreg.EnumKey(dev_key, j)
                                j += 1
                            except OSError:
                                break
                        friendly = ""
                        try:
                            friendly = str(winreg.QueryValueEx(dev_key, "FriendlyName")[0])
                        except OSError:
                            pass
                        rows.append([dev_id[:50], friendly[:50], str(j)])
                except OSError:
                    continue
    except OSError as e:
        return f"Error reading USB history: {e}."

    if not rows:
        return "未找到 USB 存储设备历史（可能需要管理员权限）。"
    rows.sort(key=lambda r: r[2], reverse=True)
    rows = rows[: max(1, min(int(limit), 100))]
    table = tabulate(rows, headers=["Device ID", "Friendly Name", "Sessions"], tablefmt="simple")
    return f"USB 存储设备历史 ({len(rows)} shown):\n{table}"
