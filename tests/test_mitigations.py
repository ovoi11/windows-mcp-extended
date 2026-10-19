"""Tests for the mitigation status service (MemoryProtectCheck)."""

import os

from windows_mcp.security import get_mitigation_status


class TestGetMitigationStatus:
    def test_current_process(self):
        result = get_mitigation_status(os.getpid())
        assert "进程缓解状态" in result
        assert "ASLR" in result
        assert "DEP" in result

    def test_missing_pid(self):
        result = get_mitigation_status(999999999)
        assert "Error" in result

    def test_negative_pid(self):
        result = get_mitigation_status(-1)
        assert "Error" in result
