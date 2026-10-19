"""Tests for the directory size service (DirectorySize)."""

import os

from windows_mcp.system import directory_size


class TestDirectorySize:
    def test_missing_path(self):
        assert "Error" in directory_size(r"C:\__windows_mcp_no_such_dir__")

    def test_current_dir(self):
        result = directory_size(os.getcwd(), depth=0)
        assert isinstance(result, str)
        assert "目录大小" in result
