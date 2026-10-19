"""FileHashInfo tool — compute file digests for integrity checks."""

from typing import Literal

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import file_hash_info


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="FileHashInfo",
        description='Compute the MD5, SHA1 or SHA256 digest of a file. Keywords: file hash, checksum, sha256, md5, verify file integrity, 文件哈希, 校验. Useful for verifying downloaded or distributed files. Read-only; reads the file bytes.',
        annotations=ToolAnnotations(
            title="FileHashInfo",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "FileHashInfo-Tool")
    def file_hash_info_tool(
        path: str,
        algorithm: Literal["md5", "sha1", "sha256"] = "sha256",
        ctx: Context = None,
    ) -> str:
        return file_hash_info(path=path, algorithm=algorithm)
