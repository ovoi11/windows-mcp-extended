"""Serialized, self-healing access to the comtypes generated-module cache.

comtypes generates Python wrappers for COM type libraries on first use and
stores them in ``comtypes/gen``. When two processes generate that cache
concurrently (e.g. an MCP host spawning multiple server instances), or
generation is interrupted, the cache is left corrupted and every subsequent
startup fails with ImportError/AttributeError.

``safe_get_module`` wraps ``comtypes.client.GetModule`` with
1. a cross-process file lock so only one process generates at a time, and
2. automatic cache clearing + regeneration when corruption is detected.
"""

import errno
import hashlib
import msvcrt
import os
import shutil
import sys
import tempfile
import time
from contextlib import contextmanager
from types import ModuleType
from typing import Iterator, Optional

import comtypes.client

_LOCK_PATH: str = os.path.join(
    tempfile.gettempdir(),
    "comtypes-gen-%s.lock" % hashlib.md5(sys.prefix.encode("utf-8")).hexdigest(),
)

_CONTENTION_ERRNOS: tuple[int, ...] = (errno.EACCES, errno.EDEADLK)

_LOCK_TIMEOUT_SECONDS: float = 120.0


@contextmanager
def comtypes_cache_lock(timeout: float = _LOCK_TIMEOUT_SECONDS) -> Iterator[None]:
    """Cross-process lock serializing comtypes.gen cache generation."""
    fd = os.open(_LOCK_PATH, os.O_CREAT | os.O_RDWR)
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
                break
            except OSError as ex:
                if ex.errno not in _CONTENTION_ERRNOS:
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        "timed out after %.0fs waiting for comtypes cache "
                        "lock %r" % (timeout, _LOCK_PATH)
                    ) from ex
        yield
    finally:
        try:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        os.close(fd)


def _clear_gen_cache() -> None:
    """Best-effort removal of generated modules so comtypes can regenerate."""
    try:
        import comtypes.gen as gen

        gen_dir = os.path.dirname(gen.__file__ or "")
        entries = os.listdir(gen_dir)
    except Exception:
        return
    for name in entries:
        if name == "__init__.py":
            continue
        path = os.path.join(gen_dir, name)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        except OSError:
            pass
    for mod_name in list(sys.modules):
        if mod_name.startswith("comtypes.gen."):
            del sys.modules[mod_name]


def safe_get_module(tlib: str, required_attr: Optional[str] = None) -> ModuleType:
    """``comtypes.client.GetModule`` with locking and corrupt-cache recovery."""
    with comtypes_cache_lock():
        for attempt in (0, 1):
            try:
                module = comtypes.client.GetModule(tlib)
                if required_attr is not None and not hasattr(module, required_attr):
                    raise AttributeError(
                        "generated module %r lacks %r (corrupted cache)"
                        % (getattr(module, "__name__", tlib), required_attr)
                    )
                return module
            except (ImportError, AttributeError):
                if attempt:
                    raise
                _clear_gen_cache()
    raise AssertionError("unreachable")  # pragma: no cover
