"""ScreenRecord tool — record the desktop to MP4 or GIF."""

from typing import Literal

from mcp.types import ToolAnnotations

from windows_mcp.infrastructure import with_analytics
from windows_mcp.monitor import record_screen
from fastmcp import Context


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="ScreenRecord",
        description='Record the desktop (full screen or a region) to an MP4 video or GIF file. Keywords: record screen, screen recording, video capture, GIF, screen cast. duration in seconds (0-120, default 5), fps (1-30, default 10). Provide out_path for a specific output location, otherwise a temp file is used and its path is returned. region=[left, top, right, bottom] records only that rectangle. scale reduces resolution (e.g. 0.5 = half). Use for UI test evidence, demo capture, or regression recording.',
        annotations=ToolAnnotations(
            title="ScreenRecord",
            readOnlyHint=False,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "ScreenRecord-Tool")
    def screen_record_tool(
        duration: float = 5.0,
        fps: int = 10,
        out_path: str | None = None,
        format: Literal["mp4", "gif"] = "mp4",
        region: list[int] | None = None,
        scale: float = 1.0,
        ctx: Context = None,
    ) -> str:
        return record_screen(
            duration=duration,
            fps=fps,
            out_path=out_path,
            fmt=format,
            region=region,
            scale=scale,
        )
