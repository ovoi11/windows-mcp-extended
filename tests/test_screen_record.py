"""Tests for the screen recording service (ScreenRecord)."""

import os

from windows_mcp.monitor import record_screen


class TestScreenRecordValidation:
    def test_duration_out_of_range(self):
        assert "Error" in record_screen(duration=0)
        assert "Error" in record_screen(duration=121)

    def test_fps_out_of_range(self):
        assert "Error" in record_screen(fps=0)
        assert "Error" in record_screen(fps=31)

    def test_bad_format(self):
        assert "Error" in record_screen(fmt="avi")

    def test_bad_scale(self):
        assert "Error" in record_screen(scale=0)
        assert "Error" in record_screen(scale=1.5)

    def test_bad_region(self):
        assert "Error" in record_screen(region=[1, 2, 3])

    def test_missing_output_dir(self):
        result = record_screen(
            duration=0.1, out_path=r"C:\no_such_dir_xyz\out.mp4"
        )
        assert "Error" in result


class TestScreenRecordCapture:
    def test_short_gif_capture(self):
        out = os.path.join(
            os.environ.get("TEMP", "."), "windows-mcp-test-record.gif"
        )
        result = record_screen(duration=0.6, fps=4, out_path=out, fmt="gif")
        assert "Error" not in result
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0
        os.unlink(out)
