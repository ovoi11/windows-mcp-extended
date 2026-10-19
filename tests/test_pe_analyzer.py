"""Tests for the PE analyzer service (ParsePE)."""

import math
import os

import pytest

from windows_mcp.security.pe_analyzer import _entropy, analyze_pe, detect_packer


def _sample_pe() -> str:
    candidates = [
        r"C:\Windows\System32\notepad.exe",
        r"C:\Windows\System32\cmd.exe",
        r"C:\Windows\System32\calc.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    pytest.skip("No known Windows PE sample available")


class TestEntropy:
    def test_empty(self):
        assert _entropy(b"") == 0.0

    def test_constant_bytes(self):
        assert _entropy(b"\x00" * 1024) == 0.0

    def test_random_bytes_near_max(self):
        data = bytes(range(256)) * 4
        assert _entropy(data) > 7.9

    def test_known_distribution(self):
        # 4 symbols with equal frequency => exactly 2.0 bits/byte.
        data = bytes([0, 85, 170, 255]) * 256
        assert math.isclose(_entropy(data), 2.0, abs_tol=1e-9)


class TestAnalyzePe:
    def test_smoke_report_headers(self):
        result = analyze_pe(_sample_pe())
        assert "PE 文件分析报告" in result
        assert "入口点" in result
        assert "节区表" in result

    def test_missing_file(self):
        result = analyze_pe(r"C:\definitely\missing\file.exe")
        assert "Error" in result

    def test_invalid_file(self):
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            f.write(b"not a real PE binary at all")
            path = f.name
        try:
            result = analyze_pe(path)
            assert "Error" in result
        finally:
            os.unlink(path)

    def test_detect_packer_on_clean_sample(self):
        import pefile

        with pefile.PE(_sample_pe(), fast_load=False) as pe:
            hits = detect_packer(pe)
        # A system binary may legitimately be signed; just make sure it returns a list.
        assert isinstance(hits, list)
        for hit in hits:
            assert "name" in hit and "evidence" in hit and "confidence" in hit
