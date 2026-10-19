"""SystemPerformanceScore tool — WinSAT ratings."""

from mcp.types import ToolAnnotations
from windows_mcp.infrastructure import with_analytics
from fastmcp import Context
from windows_mcp.system import system_performance_score


def register(mcp, *, get_desktop, get_analytics):
    @mcp.tool(
        name="SystemPerformanceScore",
        description='Report the Windows Experience Index (WinSAT) scores: overall, CPU, memory, disk, graphics and gaming graphics. Keywords: winsat, performance score, windows experience index, 性能评分. Read-only.',
        annotations=ToolAnnotations(
            title="SystemPerformanceScore",
            readOnlyHint=True,
            destructiveHint=False,
            idempotentHint=False,
            openWorldHint=False,
        ),
    )
    @with_analytics(get_analytics(), "SystemPerformanceScore-Tool")
    def system_performance_score_tool(ctx: Context = None) -> str:
        return system_performance_score()
