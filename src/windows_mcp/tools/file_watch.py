"""WatchFile tool — watch a folder for file changes."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.monitor import clear_file_baseline, watch_path


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="WatchFile",
        description='Watch a file or folder for changes. Keywords: file monitor, folder watch, detect new file, detect modified file, detect deleted file, log tail. First call establishes a baseline; subsequent calls wait `duration` seconds and report files added/modified/removed since the previous call. Use mode="clear" to reset the stored baseline. Read-only monitoring; it never modifies the watched files.',
        annotations=ToolAnnotations(
            title="WatchFile",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "WatchFile-Tool")
    def watch_file_tool(
        path: str,
        duration: float = 10.0,
        recursive: bool = True,
        mode: str = "watch",
        ctx: Context = None,
    ) -> str:
        if mode == "clear":
            return clear_file_baseline()
        return watch_path(path, duration=duration, recursive=recursive)
