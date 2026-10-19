import ctypes
from ctypes import wintypes

__all__ = ["check_elevation_status", "elevate_process", "verify_process_elevation"]

TOKEN_QUERY = 0x0008
TokenElevation = 20
TokenIntegrityLevel = 25

SE_ERR_ACCESSDENIED = 5
SE_ERR_ASSOCINCOMPLETE = 27
SE_ERR_DDEBUSY = 30
SE_ERR_DDEFAIL = 29
SE_ERR_DDETIMEOUT = 28
SE_ERR_DLLNOTFOUND = 32
SE_ERR_FNF = 2
SE_ERR_NOASSOC = 31
SE_ERR_OOM = 8
SE_ERR_PATHNOTFOUND = 3
SE_ERR_SHARE = 26
_ERROR_MAP = {
    SE_ERR_ACCESSDENIED: "拒绝访问",
    SE_ERR_ASSOCINCOMPLETE: "文件关联不完整",
    SE_ERR_DDEBUSY: "DDE 繁忙",
    SE_ERR_DDEFAIL: "DDE 失败",
    SE_ERR_DDETIMEOUT: "DDE 超时",
    SE_ERR_DLLNOTFOUND: "未找到 DLL",
    SE_ERR_FNF: "未找到文件",
    SE_ERR_NOASSOC: "无关联程序",
    SE_ERR_OOM: "内存不足",
    SE_ERR_PATHNOTFOUND: "未找到路径",
    SE_ERR_SHARE: "共享冲突",
}

_INTEGRITY_NAMES = {0x1000: "低 (Low)", 0x2000: "中 (Medium)", 0x3000: "高 (High)", 0x4000: "系统 (System)"}

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
_shell32 = ctypes.WinDLL("shell32", use_last_error=True)


class _SID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Sid", wintypes.LPVOID),
        ("Attributes", wintypes.DWORD),
    ]


class _TOKEN_ELEVATION(ctypes.Structure):
    _fields_ = [("TokenIsElevated", wintypes.DWORD)]


class _TOKEN_MANDATORY_LABEL(ctypes.Structure):
    _fields_ = [("Label", _SID_AND_ATTRIBUTES)]


def _uac_enabled() -> bool:
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
        ) as key:
            value, _ = winreg.QueryValueEx(key, "EnableLUA")
            return bool(value)
    except OSError:
        return True


def _token_elevation(pid: int) -> dict | None:
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = _kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not handle:
        return None
    try:
        token = wintypes.HANDLE()
        if not _advapi32.OpenProcessToken(handle, TOKEN_QUERY, ctypes.byref(token)):
            return None
        try:
            elev = _TOKEN_ELEVATION()
            ret = wintypes.DWORD()
            ok = _advapi32.GetTokenInformation(
                token, TokenElevation, ctypes.byref(elev), ctypes.sizeof(elev), ctypes.byref(ret)
            )
            elevated = bool(elev.TokenIsElevated) if ok else False

            label = _TOKEN_MANDATORY_LABEL()
            ok2 = _advapi32.GetTokenInformation(
                token, TokenIntegrityLevel, ctypes.byref(label), ctypes.sizeof(label), ctypes.byref(ret)
            )
            integrity = None
            if ok2 and label.Label.Sid:
                sub_auth = _advapi32.GetSidSubAuthorityCount(label.Label.Sid)
                if sub_auth:
                    count = sub_auth.contents.value - 1
                    raw = _advapi32.GetSidSubAuthority(label.Label.Sid, count)
                    integrity = int(raw.contents.value)
            return {"elevated": elevated, "integrity": integrity}
        finally:
            _kernel32.CloseHandle(token)
    finally:
        _kernel32.CloseHandle(handle)


def _describe(token: dict | None) -> str:
    if token is None:
        return "无法读取令牌信息（可能权限不足或进程不存在）"
    parts = [f"提权状态: {'已提权' if token['elevated'] else '未提权'}"]
    integrity = token.get("integrity")
    if integrity is not None:
        name = _INTEGRITY_NAMES.get(integrity, f"未知 (0x{integrity:X})")
        parts.append(f"完整性级别: {name}")
    else:
        parts.append("完整性级别: 未知")
    return " · ".join(parts)


def check_elevation_status() -> str:
    """Report UAC enablement and the current process elevation state."""
    import psutil

    uac = _uac_enabled()
    token = _token_elevation(psutil.Process().pid)
    lines = [
        f"UAC 状态: {'已启用' if uac else '已禁用（注册表 EnableLUA）'}",
        f"当前进程 (PID {psutil.Process().pid}): {_describe(token)}",
    ]
    return "\n".join(lines)


def elevate_process(path: str, args: str = "") -> str:
    """Launch *path* with the ``runas`` verb to request administrator privileges."""
    import os

    if not path or not os.path.exists(path):
        return f"Error: 目标不存在：{path}"
    import win32api

    try:
        result = win32api.ShellExecute(0, "runas", path, args, None, 1)
    except Exception as e:
        return f"Error: 发起提权失败：{e}"
    if isinstance(result, int) and result <= 32:
        reason = _ERROR_MAP.get(result, f"未知错误 {result}")
        return f"Error: 提权请求被拒绝（{reason}）。若 UAC 弹窗被取消，请手动确认后重试。"
    return f"已发起以管理员身份启动: {path}（若出现 UAC 弹窗，请在弹窗中确认；本工具不会自动确认 UAC 提示）"


def verify_process_elevation(pid: int | None = None, name: str | None = None) -> str:
    """Verify elevation/integrity of a specific process."""
    if pid is None and name:
        import psutil

        for p in psutil.process_iter(["pid", "name"]):
            try:
                if p.info["name"] and p.info["name"].lower() == name.lower():
                    pid = p.info["pid"]
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if pid is None:
            return f'Error: 未找到名为 "{name}" 的进程'
    if pid is None:
        return "Error: 必须提供 pid 或 name 参数之一"

    token = _token_elevation(pid)
    if token is None:
        return f"PID {pid}: 无法读取令牌信息（可能权限不足或进程不存在）"
    return f"PID {pid}: {_describe(token)}"
