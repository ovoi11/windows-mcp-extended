"""StorageVolumes tool — list mounted disk volumes."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import list_volumes


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="StorageVolumes",
        description='List mounted storage volumes. Keywords: disk volumes, drives, partitions, free space, mount points, filesystem. Returns device, mount point, filesystem type and used/free capacity. Read-only.',
        annotations=ToolAnnotations(
            title="StorageVolumes",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "StorageVolumes-Tool")
    def storage_volumes_tool(ctx: Context = None) -> str:
        return list_volumes()
