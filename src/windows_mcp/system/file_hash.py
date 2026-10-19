"""File hash — MD5/SHA1/SHA256 of a file (integrity verification)."""

from __future__ import annotations

import hashlib
import os

__all__ = ["file_hash_info"]

_ALGOS = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
}


def file_hash_info(
    path: str,
    algorithm: str = "sha256",
    chunk_size: int = 65536,
) -> str:
    """Compute the requested digest of a file. Usable for distribution integrity checks."""
    from tabulate import tabulate

    if not path:
        return "Error: path is required."
    algo = algorithm.lower()
    if algo not in _ALGOS:
        return "Error: algorithm must be one of md5, sha1, sha256."
    if not os.path.isfile(path):
        return f"Error: file not found: {path}"
    if not os.access(path, os.R_OK):
        return f"Error: file is not readable: {path}"

    h = _ALGOS[algo]()
    try:
        with open(path, "rb") as f:
            while True:
                block = f.read(chunk_size)
                if not block:
                    break
                h.update(block)
    except OSError as e:
        return f"Error reading file: {e}."

    size = os.path.getsize(path)
    rows = [
        ["文件", path],
        ["大小", f"{size:,} 字节"],
        [algo.upper(), h.hexdigest()],
    ]
    table = tabulate(rows, headers=["项目", "值"], tablefmt="simple")
    return f"文件哈希:\n{table}"
