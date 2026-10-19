"""Tests for the file hash service (FileHashInfo)."""

import os
import tempfile

from windows_mcp.system import file_hash_info


class TestFileHashInfo:
    def test_missing_path(self):
        assert "Error" in file_hash_info(r"C:\__windows_mcp_no_such_file__")

    def test_invalid_algo(self):
        assert "Error" in file_hash_info("x", algorithm="bogus")  # type: ignore[arg-type]

    def test_sha256_matches(self):
        import hashlib

        content = b"hello windows-mcp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
            f.write(content)
            path = f.name
        try:
            result = file_hash_info(path, algorithm="sha256")
            expected = hashlib.sha256(content).hexdigest()
            assert expected in result
        finally:
            os.unlink(path)
