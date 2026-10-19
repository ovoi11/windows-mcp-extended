"""SoundDevices tool — enumerate audio devices."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_sound_devices


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="SoundDevices",
        description='List sound devices with manufacturer and status. Keywords: audio devices, sound card, speakers, microphone device. Read-only.',
        annotations=ToolAnnotations(
            title="SoundDevices",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "SoundDevices-Tool")
    def sound_devices_tool(
        limit: int = 30,
        ctx: Context = None,
    ) -> str:
        return list_sound_devices(limit=limit)
