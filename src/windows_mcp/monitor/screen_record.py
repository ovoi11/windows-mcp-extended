"""Screen recording service — record the desktop to MP4 or GIF.

Reuses the project's existing screenshot backend chain
(``desktop.screenshot.capture``: dxcam → mss → pillow) so no screen-capture
logic is re-implemented. Frames are encoded with imageio (+ ffmpeg for MP4).
"""

from __future__ import annotations

import os
import tempfile
import time

import numpy as np

from windows_mcp.desktop.screenshot import capture
from windows_mcp.uia.enums import Rect

__all__ = ["record_screen"]

_MAX_DURATION = 120.0
_MAX_FPS = 30


def _resolve_output(out_path: str | None, fmt: str) -> str:
    if out_path:
        path = os.path.abspath(out_path)
        parent = os.path.dirname(path)
        if parent and not os.path.isdir(parent):
            raise ValueError(f"输出目录不存在：{parent}")
        return path
    suffix = ".gif" if fmt == "gif" else ".mp4"
    fd, tmp = tempfile.mkstemp(prefix="windows-mcp-record-", suffix=suffix)
    os.close(fd)
    return tmp


def _scaled_frame(rect: Rect | None, scale: float):
    img, _ = capture(rect, backend="auto")
    if scale < 1.0:
        w, h = img.size
        img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))))
    return np.asarray(img)


def record_screen(
    duration: float = 5.0,
    fps: int = 10,
    out_path: str | None = None,
    fmt: str = "mp4",
    region: list[int] | None = None,
    scale: float = 1.0,
) -> str:
    """Record the screen for *duration* seconds and return the output file path."""
    if duration <= 0 or duration > _MAX_DURATION:
        return f"Error: duration 必须在 0~{_MAX_DURATION:.0f} 秒之间。"
    if fps <= 0 or fps > _MAX_FPS:
        return f"Error: fps 必须在 1~{_MAX_FPS} 之间。"
    if fmt not in ("mp4", "gif"):
        return 'Error: format 必须是 "mp4" 或 "gif"。'
    if scale <= 0 or scale > 1:
        return "Error: scale 必须在 0~1 之间（1 为原分辨率）。"
    if region and len(region) != 4:
        return "Error: region 必须是 [left, top, right, bottom] 四元素数组。"

    rect = Rect(region[0], region[1], region[2], region[3]) if region else None
    try:
        output = _resolve_output(out_path, fmt)
    except ValueError as e:
        return f"Error: {e}"

    import imageio.v2 as imageio

    frames = 0
    start = time.monotonic()
    interval = 1.0 / fps
    try:
        if fmt == "mp4":
            writer = imageio.get_writer(output, fps=fps, format="FFMPEG")
        else:
            writer = imageio.get_writer(
                output, duration=1000.0 / fps, format="GIF"
            )
        with writer:
            writer.append_data(_scaled_frame(rect, scale))
            frames = 1
            next_frame = time.monotonic() + interval
            while time.monotonic() - start < duration:
                writer.append_data(_scaled_frame(rect, scale))
                frames += 1
                next_frame += interval
                sleep_for = next_frame - time.monotonic()
                if sleep_for > 0:
                    time.sleep(sleep_for)
    except Exception as e:
        if os.path.exists(output):
            try:
                os.remove(output)
            except OSError:
                pass
        return f"Error: 录制失败：{e}"

    size_mb = os.path.getsize(output) / (1024 * 1024)
    elapsed = time.monotonic() - start
    return (
        f"录制完成: {output}\n"
        f"帧数: {frames} · 时长: {elapsed:.1f}s · 实际帧率: {frames / elapsed:.1f} fps · 大小: {size_mb:.2f} MB"
    )
