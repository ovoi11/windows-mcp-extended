""" PowerShell command executor service """

import base64
import ctypes
import ctypes.wintypes
import logging
import os
import winreg
import shutil
import subprocess

from windows_mcp.desktop.utils import is_elevated
from windows_mcp.powershell.utils import run_with_graceful_timeout

__all__ = ["PowerShellExecutor"]

logger = logging.getLogger(__name__)


def _read_reg_env(hkey: int, subkey: str) -> tuple[dict[str, str], str, str]:
    """Read all environment variables from a registry key.

    Returns (vars, path, pathext) where *vars* is a dict of name->value
    (excluding PATH/PATHEXT), and *path*/*pathext* are the raw expanded
    values for those two special keys (empty string if absent).
    """
    variables: dict[str, str] = {}
    path = ""
    pathext = ""

    try:
        with winreg.OpenKey(hkey, subkey) as key:
            i = 0
            while True:
                try:
                    name, value, reg_type = winreg.EnumValue(key, i)
                    if reg_type not in (winreg.REG_SZ, winreg.REG_EXPAND_SZ):
                        i += 1
                        continue
                    if reg_type == winreg.REG_EXPAND_SZ:
                        value = winreg.ExpandEnvironmentStrings(value)
                    upper = name.upper()
                    if upper == "PATH":
                        path = value
                    elif upper == "PATHEXT":
                        pathext = value
                    else:
                        variables[name] = value
                    i += 1
                except OSError:
                    break
    except OSError:
        pass

    return variables, path, pathext


def _dedup_path(*segments: str) -> str:
    """Join PATH segments and deduplicate entries (case-insensitive)."""
    seen = set()
    deduped = []
    for p in ";".join(filter(None, segments)).split(";"):
        norm = p.lower().rstrip("\\")
        if norm and norm not in seen:
            seen.add(norm)
            deduped.append(p)
    return ";".join(deduped)


def _win32_name(dll: str, func: str) -> str:
    """Call a Win32 GetXxxNameW(LPWSTR, LPDWORD) function.

    Only suitable for APIs with the (buffer, &size) calling convention,
    e.g. kernel32.GetComputerNameW and advapi32.GetUserNameW.
    """
    buf = ctypes.create_unicode_buffer(257)
    size = ctypes.wintypes.DWORD(257)
    fn = getattr(ctypes.windll, dll)
    if getattr(fn, func)(buf, ctypes.byref(size)):
        return buf.value
    return ""


_FALLBACK_PATHEXT = ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC;.CPL;.PY;.PYW"


def _prepare_env() -> dict[str, str]:
    """Prepare a complete environment block for the PowerShell subprocess.

    MCP hosts (e.g. Claude Desktop) may launch this server with a stripped
    environment block missing session-level variables. This function starts
    from os.environ and fills in missing variables from:
      1. System-level env vars from the registry (HKLM)
      2. User-level env vars from the registry (HKCU)
      3. Dynamic vars (COMPUTERNAME, USERNAME, etc.) via Win32 API
    Existing values in os.environ are never overwritten, only missing ones
    are supplemented. PATH is special-cased: inherited entries keep their
    priority and registry entries are appended to fill in missing paths.
    """
    env = os.environ.copy()

    env.pop("PYTHONHOME", None)

    try:
        machine_vars, machine_path, machine_pathext = _read_reg_env(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        )
        user_vars, user_path, user_pathext = _read_reg_env(winreg.HKEY_CURRENT_USER, r"Environment")

        for name, value in {**machine_vars, **user_vars}.items():
            if not env.get(name):
                env[name] = value

        if machine_path or user_path:
            env["PATH"] = _dedup_path(env.get("PATH", ""), machine_path, user_path)

        effective_pathext = user_pathext or machine_pathext
        if effective_pathext and ".EXE" not in env.get("PATHEXT", "").upper():
            env["PATHEXT"] = effective_pathext

    except Exception:
        logger.debug("Failed to read environment from registry", exc_info=True)
        if ".EXE" not in env.get("PATHEXT", "").upper():
            env["PATHEXT"] = _FALLBACK_PATHEXT

    if not env.get("COMPUTERNAME"):
        try:
            computer_name = _win32_name("kernel32", "GetComputerNameW")
            if computer_name:
                env["COMPUTERNAME"] = computer_name
        except Exception as e:
            logger.debug("Failed to get COMPUTERNAME via Win32 API: %s", e)

    if not env.get("USERNAME"):
        try:
            user_name = _win32_name("advapi32", "GetUserNameW")
            if user_name:
                env["USERNAME"] = user_name
        except Exception as e:
            logger.debug("Failed to get USERNAME via Win32 API: %s", e)

    user_profile = os.path.expanduser("~")
    env.setdefault("USERPROFILE", user_profile)
    drive, tail = os.path.splitdrive(user_profile)
    env.setdefault("HOMEDRIVE", drive)
    env.setdefault("HOMEPATH", tail)
    env.setdefault("USERDOMAIN", env.get("COMPUTERNAME", ""))

    return env


_WINDOWS_POWERSHELL = os.path.join("System32", "WindowsPowerShell", "v1.0", "powershell.exe")


def _resolve_shell(shell: str | None, env: dict[str, str]) -> str:
    """Resolve the PowerShell executable to launch against the child's PATH.

    Windows looks a bare program name up on the *server's* PATH, not on the
    environment handed to the child, so the PATH repaired by ``_prepare_env()``
    does not decide which executable is found. ``System32\\WindowsPowerShell\\v1.0``
    is not on the default search list either, so when the MCP host strips the
    server's PATH a bare ``powershell`` fails with WinError 2 (#411).

    Args:
        shell: The shell the caller asked for, or ``None`` to prefer ``pwsh`` and
            fall back to Windows PowerShell.
        env: The environment the child will run with.

    Returns:
        An absolute path when the shell can be found; otherwise Windows
        PowerShell's well-known location for a PowerShell request, or the name
        unchanged for any other shell so the launch error names it.
    """
    search_path = env.get("PATH")
    for name in (shell,) if shell else ("pwsh", "powershell"):
        found = shutil.which(name, path=search_path)
        if found:
            return found

    if shell and os.path.basename(shell).lower().removesuffix(".exe") != "powershell":
        return shell
    system_root = env.get("SystemRoot") or os.environ.get("SystemRoot") or r"C:\Windows"
    return os.path.join(system_root, _WINDOWS_POWERSHELL)


class PowerShellExecutor:
    """Static utility class for executing PowerShell commands."""

    @staticmethod
    def execute_command(
            command: str, timeout: int = 10, shell: str | None = None
    ) -> tuple[str, int]:
        try:
            utf8_command = (
                "$OutputEncoding = [System.Text.Encoding]::UTF8; "
                "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
                f"{command}"
            )
            encoded = base64.b64encode(utf8_command.encode("utf-16le")).decode("ascii")
            env = _prepare_env()
            env["NO_COLOR"] = "1"

            shell = _resolve_shell(shell, env)

            args = [shell, "-NoProfile"]
            shell_name = os.path.basename(shell).lower().replace(".exe", "")
            if shell_name == "powershell":
                args.extend(["-OutputFormat", "Text"])
            args.extend(["-EncodedCommand", encoded])

            result = run_with_graceful_timeout(
                args,
                stdin=subprocess.DEVNULL,
                capture_output=True,
                timeout=timeout,
                cwd=os.path.expanduser(path="~"),
                env=env,
            )
            stdout = result.stdout
            stderr = result.stderr
            if isinstance(stdout, bytes):
                stdout = stdout.decode("utf-8", errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode("utf-8", errors="replace")
            output = stdout or stderr
            if result.returncode != 0 and "Access is denied" in output and not is_elevated():
                output += (
                    "\n\nHINT: This command may require an elevated (Administrator) terminal. "
                    "The Windows-MCP server is currently running at a lower integrity level."
                )
            return output, result.returncode
        except subprocess.TimeoutExpired:
            return "Command execution timed out", 1
        except Exception as e:
            logger.warning("PowerShell command failed to run (shell=%s)", shell, exc_info=True)
            return f"Command execution failed: {type(e).__name__}: {e} (shell: {shell})", 1
