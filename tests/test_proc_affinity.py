"""Tests for the process affinity service (ProcessAffinity)."""

import os

from windows_mcp.system import process_affinity


class TestProcessAffinity:
    def test_current_process(self):
        result = process_affinity(os.getpid())
        assert "CPU 亲和性" in result or "不支持" in result

    def test_invalid_pid(self):
        result = process_affinity(999999999)
        assert isinstance(result, str)
        assert result.strip() != ""
