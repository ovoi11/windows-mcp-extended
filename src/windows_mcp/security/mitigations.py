"""Process mitigation status service — ASLR / DEP / CFG and related policies.

Queries the standard Windows API ``GetProcessMitigationPolicy`` via ctypes
(no extra dependencies, no re-implementation of the policy format).
Requires PROCESS_QUERY_LIMITED_INFORMATION on the target process.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes

__all__ = ["get_mitigation_status"]

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
PROCESS_QUERY_INFORMATION = 0x0400

_ProcessDEPPolicy = 0
_ProcessASLRPolicy = 1
_ProcessDynamicCodePolicy = 2
_ProcessStrictHandleCheckPolicy = 3
_ProcessSystemCallDisablePolicy = 4
_ProcessExtensionPointDisablePolicy = 6
_ProcessControlFlowGuardPolicy = 7
_ProcessSignaturePolicy = 8
_ProcessImageLoadPolicy = 10
_ProcessChildProcessPolicy = 13


class _FLAGS(ctypes.Union):
    _fields_ = [("Flags", wintypes.DWORD)]


class _ASLR_POLICY(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("u", _FLAGS),
    ]

    def bits(self) -> dict[str, bool]:
        return {
            "bottom_up_randomization": bool(self.Flags & 0x1),
            "force_relocate_images": bool(self.Flags & 0x2),
            "high_entropy": bool(self.Flags & 0x4),
            "disallow_stripped_images": bool(self.Flags & 0x8),
        }


class _DEP_POLICY(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("u", _FLAGS),
    ]

    def bits(self) -> dict[str, bool]:
        return {
            "enable": bool(self.Flags & 0x1),
            "disable_atl_thunk_emulation": bool(self.Flags & 0x2),
        }


class _CFG_POLICY(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("u", _FLAGS),
    ]

    def bits(self) -> dict[str, bool]:
        return {
            "enable_control_flow_guard": bool(self.Flags & 0x1),
            "enable_export_suppression": bool(self.Flags & 0x2),
            "strict_mode": bool(self.Flags & 0x4),
        }


class _DYNAMIC_CODE_POLICY(ctypes.Structure):
    _anonymous_ = ("u",)
    _fields_ = [
        ("u", _FLAGS),
    ]

    def bits(self) -> dict[str, bool]:
        return {
            "prohibit_dynamic_code": bool(self.Flags & 0x1),
            "allow_thread_opt_out": bool(self.Flags & 0x2),
            "allow_remote_downgrade": bool(self.Flags & 0x4),
        }


def _open_process(pid: int):
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel32.OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_QUERY_INFORMATION,
        False,
        pid,
    )
    if not handle:
        err = ctypes.get_last_error()
        raise PermissionError(f"无法打开进程 PID {pid}（OpenProcess 失败，错误码 {err}，可能需要管理员权限）")
    return kernel32, handle


def _query_policy(kernel32, handle, policy: int, struct_cls):
    buf = struct_cls()
    ok = kernel32.GetProcessMitigationPolicy(handle, policy, ctypes.byref(buf), ctypes.sizeof(buf))
    if not ok:
        return None
    return buf


def get_mitigation_status(pid: int) -> str:
    """Return the mitigation policies of a process as a readable report."""
    try:
        kernel32, handle = _open_process(pid)
    except PermissionError as e:
        return f"Error: {e}"
    except OSError as e:
        return f"Error: 进程不存在或无法访问：{e}"

    from tabulate import tabulate

    try:
        rows: list[list[str]] = []

        aslr = _query_policy(kernel32, handle, _ProcessASLRPolicy, _ASLR_POLICY)
        if aslr is not None:
            b = aslr.bits()
            rows.append(
                [
                    "ASLR",
                    "启用" if b["bottom_up_randomization"] else "未启用",
                    "强制映像重定位: " + ("是" if b["force_relocate_images"] else "否")
                    + " · 高熵: " + ("是" if b["high_entropy"] else "否"),
                ]
            )
        else:
            rows.append(["ASLR", "未知", "查询失败（可能权限不足）"])

        dep = _query_policy(kernel32, handle, _ProcessDEPPolicy, _DEP_POLICY)
        if dep is not None:
            b = dep.bits()
            rows.append(
                [
                    "DEP",
                    "启用" if b["enable"] else "未启用",
                    "ATL Thunk 模拟: " + ("禁用" if b["disable_atl_thunk_emulation"] else "启用"),
                ]
            )
        else:
            rows.append(["DEP", "未知", "查询失败（可能权限不足）"])

        cfg = _query_policy(kernel32, handle, _ProcessControlFlowGuardPolicy, _CFG_POLICY)
        if cfg is not None:
            b = cfg.bits()
            rows.append(
                [
                    "CFG",
                    "启用" if b["enable_control_flow_guard"] else "未启用",
                    "导出抑制: " + ("是" if b["enable_export_suppression"] else "否")
                    + " · 严格模式: " + ("是" if b["strict_mode"] else "否"),
                ]
            )
        else:
            rows.append(["CFG", "未知", "查询失败（可能权限不足）"])

        dynd = _query_policy(kernel32, handle, _ProcessDynamicCodePolicy, _DYNAMIC_CODE_POLICY)
        if dynd is not None:
            b = dynd.bits()
            rows.append(
                [
                    "动态代码",
                    "禁止" if b["prohibit_dynamic_code"] else "允许",
                    "线程 opt-out: " + ("是" if b["allow_thread_opt_out"] else "否"),
                ]
            )
        else:
            rows.append(["动态代码", "未知", "查询失败（可能权限不足）"])

        report = [f"进程缓解状态（PID {pid}）:", ""]
        report.append(
            tabulate(
                rows,
                headers=["策略", "状态", "详情"],
                tablefmt="simple",
            )
        )
        return "\n".join(report)
    finally:
        kernel32.CloseHandle(handle)
