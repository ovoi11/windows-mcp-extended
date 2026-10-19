"""Tests for the certificate store service (CertificateInfo)."""

from windows_mcp.system import list_certificates


class TestCertificateInfo:
    def test_my_store_returns_text(self):
        result = list_certificates(store="my", limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""

    def test_root_store(self):
        result = list_certificates(store="root", limit=5)
        assert isinstance(result, str)

    def test_invalid_store_falls_back(self):
        result = list_certificates(limit=3)  # type: ignore[arg-type]
        assert isinstance(result, str)
