"""Tests for the sound devices service (SoundDevices)."""

from windows_mcp.system import list_sound_devices


class TestSoundDevices:
    def test_returns_text(self):
        result = list_sound_devices(limit=5)
        assert isinstance(result, str)
        assert result.strip() != ""
