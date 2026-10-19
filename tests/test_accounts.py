"""Tests for the user accounts service (UserAccounts)."""

from windows_mcp.system import list_accounts


class TestUserAccounts:
    def test_returns_text(self):
        result = list_accounts(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
