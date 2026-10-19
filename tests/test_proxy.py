"""Tests for the proxy settings service (ProxySettings)."""

from windows_mcp.system import proxy_settings


class TestProxySettings:
    def test_returns_text(self):
        result = proxy_settings()
        assert isinstance(result, str)
        assert result.strip() != ""
