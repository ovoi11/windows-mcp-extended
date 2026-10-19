"""Tests for the printers service (PrinterList)."""

from windows_mcp.system import list_printers


class TestPrinterList:
    def test_returns_text(self):
        result = list_printers(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
