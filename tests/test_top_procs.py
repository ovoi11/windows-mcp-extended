"""Tests for the top processes service (TopProcesses)."""

from windows_mcp.system import top_processes


class TestTopProcesses:
    def test_invalid_by(self):
        assert "Error" in top_processes(by="bogus")  # type: ignore[arg-type]

    def test_returns_text(self):
        result = top_processes(by="cpu", limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
